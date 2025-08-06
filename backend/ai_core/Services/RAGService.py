"""
RAG Service - Retrieval-Augmented Generation işlemleri için service layer
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from Config import Config
from Exceptions import RAGServiceError, FileNotFoundError, ModelLoadError, ValidationError
from Logger import Logger
from Services.AIService import IAIService


class IRAGService(ABC):
    """RAG Service için interface"""
    
    @abstractmethod
    def load_index_and_chunks(self) -> tuple:
        """FAISS index ve chunks dosyalarını yükler"""
        pass
    
    @abstractmethod
    def get_top_chunks(self, question: str, top_k: int = 5) -> List[str]:
        """Soru için en alakalı chunk'ları bulur"""
        pass
    
    @abstractmethod
    def extract_product_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Yorumlardan ürün istatistiklerini çıkarır"""
        pass
    
    @abstractmethod
    def build_prompt(self, question: str, top_chunks: List[str], product_stats: Dict[str, Any]) -> str:
        """AI için prompt oluşturur"""
        pass


class RAGService(IRAGService):
    """RAG Service implementasyonu"""
    
    def __init__(self, ai_service: IAIService):
        self._ai_service = ai_service
        self._model = None
        self._index = None
        self._chunks = None
        self._config = Config.get_rag_config()
        self._loaded = False
    
    def _load_sentence_transformer(self) -> None:
        """Sentence Transformer modelini yükler"""
        try:
            if self._model is None:
                Logger.info("Sentence Transformer modeli yükleniyor...")
                model_name = self._config.get('sentence_transformer_model')
                self._model = SentenceTransformer(model_name)
                Logger.info(f"Sentence Transformer modeli yüklendi: {model_name}")
        except Exception as e:
            Logger.error(f"Sentence Transformer yükleme hatası: {e}")
            raise ModelLoadError(f"Sentence Transformer modeli yüklenemedi: {e}")
    
    def load_index_and_chunks(self) -> tuple:
        """FAISS index ve chunks dosyalarını güvenli şekilde yükler"""
        try:
            Logger.info("FAISS index ve chunks dosyaları yükleniyor...")
            
            # Dosya yollarını al
            index_path = self._config['index_path']
            chunks_path = self._config['chunks_path']
            
            # Dosyaların varlığını kontrol et
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"FAISS index dosyası bulunamadı: {index_path}")
            
            if not os.path.exists(chunks_path):
                raise FileNotFoundError(f"Chunks dosyası bulunamadı: {chunks_path}")
            
            # Dosyaları yükle (her zaman yeniden yükle)
            self._index = faiss.read_index(index_path)
            with open(chunks_path, 'r', encoding='utf-8') as f:
                self._chunks = json.load(f)
            
            self._loaded = True
            Logger.info(f"Başarıyla yüklendi: {len(self._chunks)} chunk, index boyutu: {self._index.ntotal}")
            return self._index, self._chunks
            
        except FileNotFoundError as e:
            Logger.error(f"Dosya bulunamama hatası: {e}")
            raise FileNotFoundError(f"Gerekli dosyalar bulunamadı: {e}")
        except Exception as e:
            Logger.error(f"Index ve chunks yükleme hatası: {e}")
            raise RAGServiceError(f"Index ve chunks yüklenemedi: {e}")
    
    def get_top_chunks(self, question: str, top_k: int = 5) -> List[str]:
        """Soru için en alakalı chunk'ları bulur"""
        try:
            Logger.debug(f"Soru için en alakalı {top_k} chunk aranıyor...")
            
            # Input validation
            if not question or not question.strip():
                raise ValidationError("Soru boş olamaz")
            
            if not self._loaded or not self._chunks or len(self._chunks) == 0:
                raise ValidationError("Chunks listesi boş veya yüklenmemiş")
            
            # Sentence Transformer'ı yükle
            self._load_sentence_transformer()
            
            # Embedding oluştur
            q_vec = self._model.encode([question], convert_to_numpy=True)
            
            # FAISS search
            D, I = self._index.search(q_vec, min(top_k, len(self._chunks)))
            top_chunks = [self._chunks[i] for i in I[0]]
            
            Logger.debug(f"{len(top_chunks)} alakalı chunk bulundu")
            return top_chunks
            
        except Exception as e:
            Logger.error(f"Top chunks bulma hatası: {e}")
            raise RAGServiceError(f"Alakalı chunk'lar bulunamadı: {e}")
    
    def extract_product_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Yorumlardan ürün istatistiklerini çıkarır"""
        try:
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
                if isinstance(chunk, dict) and 'rate' in chunk and chunk['rate'] > 0:
                    total_rating += chunk['rate']
                    rating_count += 1
                
                # Yorum tonunu analiz et
                text = str(chunk).lower()
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
            
            Logger.debug(f"Ürün istatistikleri çıkarıldı: {stats}")
            return stats
            
        except Exception as e:
            Logger.warning(f"İstatistik çıkarma hatası, varsayılan değerler kullanılıyor: {e}")
            return {
                'ortalamaPuan': 0,
                'toplamDegerlendirme': len(chunks),
                'pozitifYorumlar': 0,
                'negatifYorumlar': 0,
                'nötrYorumlar': 0
            }
    
    def build_prompt(self, question: str, top_chunks: List[str], product_stats: Dict[str, Any]) -> str:
        """AI için prompt oluşturur"""
        try:
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
            
            Logger.debug("Prompt oluşturuldu")
            return prompt
            
        except Exception as e:
            Logger.error(f"Prompt oluşturma hatası: {e}")
            raise RAGServiceError(f"Prompt oluşturulamadı: {e}")
    
    def query_rag(self, question: str) -> str:
        """Tam RAG sorgu işlemini gerçekleştirir"""
        try:
            Logger.info(f"RAG sorgusu başlatılıyor: {question}")
            
            # Index ve chunks'ları her zaman yeniden yükle (güncel veriler için)
            self._loaded = False  # Force reload
            self.load_index_and_chunks()
            
            # Yorumları formatla
            all_reviews = []
            for i, chunk in enumerate(self._chunks):
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
            
            # Ürün istatistiklerini çıkar
            product_stats = self.extract_product_stats(self._chunks)
            
            # Prompt oluştur
            prompt = self.build_prompt(question, top_chunks, product_stats)
            
            # AI'dan yanıt al
            response = self._ai_service.generate_response(prompt)
            
            # Yanıtı formatla
            final_response = self._add_review_count_to_response(
                response, len(self._chunks), len(top_chunks)
            )
            
            Logger.info("RAG sorgu işlemi başarıyla tamamlandı")
            return final_response
            
        except Exception as e:
            Logger.error(f"RAG sorgu hatası: {e}")
            raise RAGServiceError(f"RAG sorgusu başarısız: {e}")
    
    def _add_review_count_to_response(self, response_text: str, total_chunks: int, used_chunks: int) -> str:
        """AI cevabının sonuna yorum sayısını ekler"""
        review_count_info = f"\n\n---\n📊 **Test Bilgisi**: Bu analiz {used_chunks}/{total_chunks} yorumdan oluşturulmuştur."
        return response_text + review_count_info


class MockRAGService(IRAGService):
    """Test için mock RAG service"""
    
    def __init__(self, mock_chunks: Optional[List[str]] = None):
        self._mock_chunks = mock_chunks or ["Mock yorum 1", "Mock yorum 2", "Mock yorum 3"]
        self._loaded = True
    
    def load_index_and_chunks(self) -> tuple:
        """Mock index ve chunks döndürür"""
        return None, self._mock_chunks
    
    def get_top_chunks(self, question: str, top_k: int = 5) -> List[str]:
        """Mock top chunks döndürür"""
        return self._mock_chunks[:min(top_k, len(self._mock_chunks))]
    
    def extract_product_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock istatistikler döndürür"""
        return {
            'ortalamaPuan': 4.2,
            'toplamDegerlendirme': len(chunks),
            'pozitifYorumlar': 2,
            'negatifYorumlar': 1,
            'nötrYorumlar': 0
        }
    
    def build_prompt(self, question: str, top_chunks: List[str], product_stats: Dict[str, Any]) -> str:
        """Mock prompt döndürür"""
        return f"Mock prompt: {question}"
    
    def query_rag(self, question: str) -> str:
        """Mock RAG sorgu işlemi"""
        Logger.info(f"Mock RAG sorgusu: {question}")
        
        # Mock yanıt
        mock_response = f"Mock AI yanıtı: {question} sorusuna göre bu ürün genel olarak kaliteli görünüyor."
        
        # Mock review count ekle
        final_response = f"{mock_response}\n\n---\n📊 **Test Bilgisi**: Bu analiz 3/3 yorumdan oluşturulmuştur."
        
        Logger.info("Mock RAG sorgu işlemi tamamlandı")
        return final_response 