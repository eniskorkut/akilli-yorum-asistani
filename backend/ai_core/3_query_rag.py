import argparse
import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Custom imports
from Config import Config
from Exceptions import (
    ConfigurationError, 
    RAGServiceError, 
    FileNotFoundError, 
    ModelLoadError, 
    APIError,
    ValidationError
)
from Logger import Logger

def load_index_and_chunks():
    """FAISS index ve chunks dosyalarını güvenli şekilde yükler"""
    try:
        Logger.info("FAISS index ve chunks dosyaları yükleniyor...")
        
        # Config'den dosya yollarını al
        rag_config = Config.get_rag_config()
        index_path = rag_config['index_path']
        chunks_path = rag_config['chunks_path']
        
        # Dosyaların varlığını kontrol et
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index dosyası bulunamadı: {index_path}")
        
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"Chunks dosyası bulunamadı: {chunks_path}")
        
        # Dosyaları yükle
        index = faiss.read_index(index_path)
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        Logger.info(f"Başarıyla yüklendi: {len(chunks)} chunk, index boyutu: {index.ntotal}")
        return index, chunks
        
    except FileNotFoundError as e:
        Logger.error(f"Dosya bulunamama hatası: {e}")
        raise FileNotFoundError(f"Gerekli dosyalar bulunamadı: {e}")
    except Exception as e:
        Logger.error(f"Index ve chunks yükleme hatası: {e}")
        raise RAGServiceError(f"Index ve chunks yüklenemedi: {e}")

def get_top_chunks(question, model, index, chunks, top_k=5):
    """Soru için en alakalı chunk'ları bulur"""
    try:
        Logger.debug(f"Soru için en alakalı {top_k} chunk aranıyor...")
        
        # Input validation
        if not question or not question.strip():
            raise ValidationError("Soru boş olamaz")
        
        if not chunks or len(chunks) == 0:
            raise ValidationError("Chunks listesi boş")
        
        # Embedding oluştur
        q_vec = model.encode([question], convert_to_numpy=True)
        
        # FAISS search
        D, I = index.search(q_vec, min(top_k, len(chunks)))
        top_chunks = [chunks[i] for i in I[0]]
        
        Logger.debug(f"{len(top_chunks)} alakalı chunk bulundu")
        return top_chunks
        
    except Exception as e:
        Logger.error(f"Top chunks bulma hatası: {e}")
        raise RAGServiceError(f"Alakalı chunk'lar bulunamadı: {e}")

def build_improved_prompt(question, top_chunks, product_stats):
    """
    Gemini için geliştirilmiş bir prompt oluşturur.
    
    Args:
        question (str): Kullanıcının sorusu.
        top_chunks (list): RAG ile çekilmiş en ilgili yorum parçaları.
        product_stats (dict): Ortalama puan, yorum sayısı gibi istatistiksel veriler.
    """
    # Tüm yorumları numaralandırarak göster
    context = '\n'.join(f'{i+1}. {c}' for i, c in enumerate(top_chunks))
    
    prompt = (
        "Sen, e-ticaret sitelerindeki ürün yorumlarını analiz eden uzman bir yapay zeka asistanısın. "
        "Görevin, kullanıcı yorumlarını analiz ederek kısa ve öz bir genel değerlendirme sunmaktır.\n\n"
        "**ÜRÜNÜN GENEL PUAN DURUMU:**\n"
        f"- Ortalama Puan: {product_stats.get('ortalamaPuan', 'N/A')} / 5\n"
        f"- Toplam Değerlendirme Sayısı: {product_stats.get('toplamDegerlendirme', 'N/A')}\n"
        f"- Pozitif Yorumlar: {product_stats.get('pozitifYorumlar', 'N/A')}\n"
        f"- Negatif Yorumlar: {product_stats.get('negatifYorumlar', 'N/A')}\n\n"
        "**KULLANICI YORUMLARI:**\n"
        f"{context}\n\n"
        f"**TOPLAM YORUM SAYISI:** {len(top_chunks)} adet yorum bulunmaktadır.\n\n"
        "--- GÖREV ve KURALLAR ---\n"
        "1. **Sadece Sağlanan Bilgiyi Kullan:** Cevabını SADECE yukarıdaki bilgilere dayandır.\n"
        "2. **Kısa ve Öz Ol:** Maksimum 3-4 paragraf yaz.\n"
        "3. **Dengeli Bakış Açısı:** Hem olumlu hem olumsuz yönleri kısaca belirt.\n"
        "4. **Genel Değerlendirme Formatı:**\n"
        "    - **Genel Değerlendirme:** Yorumların genel havasını özetleyen kısa bir paragraf (olumlu/olumsuz yönler dahil).\n"
        "    - **Sonuç:** Kısa bir tavsiye veya özet.\n"
        "5. **Gereksiz Detaylardan Kaçın:** Uzun listeler ve çok fazla alıntı yapma.\n"
        "-----------------------------------\n\n"
        f"**KULLANICININ SORUSU:** {question}\n\n"
        "**GENEL DEĞERLENDİRME (Kısa ve öz, Türkçe):**"
    )
    return prompt

def build_prompt(question, top_chunks):
    """Eski prompt fonksiyonu - geriye uyumluluk için"""
    return build_improved_prompt(question, top_chunks, {})

def extract_product_stats(chunks):
    """Yorumlardan ürün istatistiklerini çıkarır"""
    stats = {
        'ortalamaPuan': 0,
        'toplamDegerlendirme': len(chunks),
        'pozitifYorumlar': 0,
        'negatifYorumlar': 0,
        'nötrYorumlar': 0
    }
    
    total_rating = 0
    rating_count = 0
    
    for chunk in chunks:
        # Rating bilgisi varsa topla
        if 'rate' in chunk and chunk['rate'] > 0:
            total_rating += chunk['rate']
            rating_count += 1
        
        # Yorum tonunu analiz et
        text = chunk.lower()
        positive_words = ['güzel', 'iyi', 'beğendim', 'memnun', 'kaliteli', 'tavsiye', 'harika', 'mükemmel']
        negative_words = ['kötü', 'berbat', 'memnun değil', 'kırık', 'bozuk', 'iade']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            stats['pozitifYorumlar'] += 1
        elif negative_count > positive_count:
            stats['negatifYorumlar'] += 1
        else:
            stats['nötrYorumlar'] += 1
    
    if rating_count > 0:
        stats['ortalamaPuan'] = round(total_rating / rating_count, 1)
    
    return stats

def add_review_count_to_response(response_text, total_chunks, used_chunks):
    """AI cevabının sonuna yorum sayısını ekler"""
    review_count_info = f"\n\n---\n📊 **Test Bilgisi**: Bu analiz {used_chunks}/{total_chunks} yorumdan oluşturulmuştur."
    return response_text + review_count_info

def main():
    """Ana fonksiyon - güvenli hata yönetimi ile"""
    try:
        # Argument parsing
        parser = argparse.ArgumentParser()
        parser.add_argument('--question', required=True, help='Kullanıcı sorusu')
        args = parser.parse_args()

        Logger.info("RAG sorgu sistemi başlatılıyor...")
        
        # Konfigürasyonu doğrula
        try:
            Config.validate()
            Logger.info("Konfigürasyon doğrulandı")
        except ValueError as e:
            Logger.critical(f"Konfigürasyon hatası: {e}")
            print(f'Hata: {e}', flush=True)
            exit(1)

        # Gemini API'yi konfigüre et
        try:
            model_config = Config.get_model_config()
            genai.configure(api_key=model_config['api_key'])
            Logger.info("Gemini API konfigüre edildi")
        except Exception as e:
            Logger.error(f"Gemini API konfigürasyon hatası: {e}")
            raise ConfigurationError(f"Gemini API konfigüre edilemedi: {e}")

        # Sentence Transformer modelini yükle
        try:
            rag_config = Config.get_rag_config()
            model = SentenceTransformer(rag_config['sentence_transformer_model'])
            Logger.info(f"Sentence Transformer modeli yüklendi: {rag_config['sentence_transformer_model']}")
        except Exception as e:
            Logger.error(f"Model yükleme hatası: {e}")
            raise ModelLoadError(f"Sentence Transformer modeli yüklenemedi: {e}")

        # Index ve chunks'ları yükle
        try:
            index, chunks = load_index_and_chunks()
        except (FileNotFoundError, RAGServiceError) as e:
            Logger.error(f"Index yükleme hatası: {e}")
            print(f'Hata: {e}', flush=True)
            exit(1)

        # Yorumları formatla
        try:
            all_reviews = []
            for i, chunk in enumerate(chunks):
                if isinstance(chunk, dict):
                    review_text = f"YORUM {i+1}: "
                    if 'comment' in chunk:
                        review_text += chunk['comment']
                    if 'rate' in chunk and chunk['rate'] > 0:
                        review_text += f" (Puan: {chunk['rate']}/5)"
                    if 'user' in chunk and chunk['user'] != 'Anonim':
                        review_text += f" (Kullanıcı: {chunk['user']})"
                    all_reviews.append(review_text)
                elif isinstance(chunk, str):
                    all_reviews.append(f"YORUM {i+1}: {chunk}")
            
            top_chunks = all_reviews
            Logger.info(f"{len(top_chunks)} yorum formatlandı")
        except Exception as e:
            Logger.error(f"Yorum formatlama hatası: {e}")
            raise RAGServiceError(f"Yorumlar formatlanamadı: {e}")

        # Ürün istatistiklerini çıkar
        try:
            product_stats = extract_product_stats(chunks)
            Logger.debug(f"Ürün istatistikleri çıkarıldı: {product_stats}")
        except Exception as e:
            Logger.warning(f"İstatistik çıkarma hatası, varsayılan değerler kullanılıyor: {e}")
            product_stats = {}

        # Prompt oluştur
        try:
            prompt = build_improved_prompt(args.question, top_chunks, product_stats)
            Logger.debug("Prompt oluşturuldu")
        except Exception as e:
            Logger.error(f"Prompt oluşturma hatası: {e}")
            raise RAGServiceError(f"Prompt oluşturulamadı: {e}")

        # Gemini ile yanıt al
        try:
            gemini = genai.GenerativeModel(model_config['model_name'])
            response = gemini.generate_content(prompt)
            
            if not response or not response.text:
                raise APIError("Gemini API'den boş yanıt alındı")
            
            Logger.info("Gemini API'den yanıt alındı")
        except Exception as e:
            Logger.error(f"Gemini API hatası: {e}")
            raise APIError(f"AI yanıtı alınamadı: {e}")

        # Final yanıtı oluştur
        try:
            final_response = add_review_count_to_response(
                response.text.strip(), 
                len(chunks), 
                len(top_chunks)
            )
            print(final_response, flush=True)
            Logger.info("RAG sorgu işlemi başarıyla tamamlandı")
            
        except Exception as e:
            Logger.error(f"Final yanıt oluşturma hatası: {e}")
            print(f'Hata: Final yanıt oluşturulamadı: {e}', flush=True)
            exit(1)

    except (ConfigurationError, ModelLoadError, RAGServiceError, APIError) as e:
        Logger.error(f"Kritik hata: {e}")
        print(f'Hata: {e}', flush=True)
        exit(1)
    except Exception as e:
        Logger.critical(f"Beklenmeyen hata: {e}")
        print(f'Beklenmeyen hata: {e}', flush=True)
        exit(1)

if __name__ == "__main__":
    main()
