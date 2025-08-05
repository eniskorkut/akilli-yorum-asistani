# 🤖 AI Core Module Documentation

Bu modül, Akıllı Yorum Asistanı'nın AI ve RAG (Retrieval-Augmented Generation) işlemlerini yöneten merkezi bileşendir.

## 📁 **Dosya Yapısı**

```
ai_core/
├── Config.py                 # Konfigürasyon yönetimi
├── Exceptions.py             # Custom exception sınıfları
├── Logger.py                 # Logging sistemi
├── 3_query_rag.py           # Ana RAG sorgu sistemi
├── 2_create_rag_index.py    # RAG index oluşturma
├── 1_fetch_reviews.py       # Yorum çekme sistemi
├── TestQueryRag.py          # Unit testler
├── RunTests.py              # Test çalıştırma scripti
├── README.md                # Bu dosya
├── logs/                    # Log dosyaları
├── index.faiss             # FAISS index dosyası
├── chunks.json             # Metin parçaları
└── reviews.json            # Çekilen yorumlar
```

## 🏗️ **Mimari**

### **SOLID Prensipleri**
- ✅ **Single Responsibility**: Her sınıf tek sorumluluk
- ✅ **Open/Closed**: Genişletilebilir yapı
- ✅ **Liskov Substitution**: Interface uyumluluğu
- ✅ **Interface Segregation**: Küçük interface'ler
- ✅ **Dependency Inversion**: Soyutlamaya bağımlılık

### **Clean Architecture**
```
┌─────────────────────────────────────┐
│           Interface Layer           │
│         (Controllers/API)           │
├─────────────────────────────────────┤
│         Application Layer           │
│         (Use Cases/Services)        │
├─────────────────────────────────────┤
│         Domain Layer                │
│      (Entities/Business Logic)      │
├─────────────────────────────────────┤
│      Infrastructure Layer           │
│    (Repositories/External APIs)     │
└─────────────────────────────────────┘
```

## 🔧 **Bileşenler**

### **1. Config.py**
Merkezi konfigürasyon yönetimi.

```python
from Config import Config

# Konfigürasyon doğrulama
Config.validate()

# AI model konfigürasyonu
model_config = Config.get_model_config()

# RAG konfigürasyonu
rag_config = Config.get_rag_config()
```

**Özellikler:**
- Environment variables desteği
- Validation sistemi
- Merkezi konfigürasyon
- Type hints

### **2. Exceptions.py**
Custom exception sınıfları.

```python
from Exceptions import (
    ConfigurationError,
    RAGServiceError,
    FileNotFoundError,
    ModelLoadError,
    APIError,
    ValidationError
)
```

**Exception Hiyerarşisi:**
```
Exception
├── AIServiceError
├── ConfigurationError
├── RAGServiceError
├── FileNotFoundError
├── ModelLoadError
├── APIError
└── ValidationError
```

### **3. Logger.py**
Merkezi logging sistemi.

```python
from Logger import Logger

Logger.info("Bilgi mesajı")
Logger.error("Hata mesajı")
Logger.warning("Uyarı mesajı")
Logger.debug("Debug mesajı")
Logger.critical("Kritik hata")
```

**Özellikler:**
- Singleton pattern
- Console ve file logging
- Farklı log seviyeleri
- Otomatik log dosyası oluşturma

### **4. 3_query_rag.py**
Ana RAG sorgu sistemi.

```bash
python 3_query_rag.py --question "Bu ürün kaliteli mi?"
```

**İşlem Adımları:**
1. Konfigürasyon doğrulama
2. Gemini API konfigürasyonu
3. Sentence Transformer modeli yükleme
4. FAISS index ve chunks yükleme
5. Yorum formatlama
6. Ürün istatistikleri çıkarma
7. Prompt oluşturma
8. Gemini API çağrısı
9. Yanıt formatlama

## 🧪 **Test Sistemi**

### **Test Çalıştırma**
```bash
# Tüm testleri çalıştır
python RunTests.py

# Sadece unit testler
python -m unittest TestQueryRag.py -v

# Belirli test sınıfı
python -m unittest TestQueryRag.TestConfig -v
```

### **Test Kategorileri**

#### **1. Unit Tests (TestQueryRag.py)**
- **TestConfig**: Konfigürasyon testleri
- **TestExceptions**: Exception sınıfları testleri
- **TestLogger**: Logging sistemi testleri
- **TestRAGFunctions**: RAG fonksiyonları testleri
- **TestIntegration**: Integration testleri

#### **2. Test Coverage**
- ✅ Configuration validation
- ✅ Exception handling
- ✅ Logger functionality
- ✅ RAG operations
- ✅ File operations
- ✅ API interactions

### **Mock Sistemi**
```python
@patch('google.generativeai.GenerativeModel')
@patch('sentence_transformers.SentenceTransformer')
def test_full_pipeline_mock(self, mock_transformer, mock_gemini):
    # Mock setup
    mock_transformer.return_value = Mock()
    mock_gemini.return_value.generate_content.return_value.text = "Test response"
```

## 📊 **Performans**

### **Benchmark Sonuçları**
- **Model Yükleme**: ~5 saniye
- **Index Yükleme**: ~0.1 saniye
- **API Çağrısı**: ~7 saniye
- **Toplam İşlem**: ~12 saniye

### **Memory Kullanımı**
- **Sentence Transformer**: ~500MB
- **FAISS Index**: ~50MB
- **Chunks**: ~10MB
- **Toplam**: ~560MB

## 🔒 **Güvenlik**

### **Error Handling**
- ✅ Input validation
- ✅ File existence checks
- ✅ API error handling
- ✅ Graceful degradation
- ✅ Detailed error messages

### **Logging**
- ✅ Sensitive data masking
- ✅ Error tracking
- ✅ Performance monitoring
- ✅ Audit trail

## 🚀 **Kullanım Örnekleri**

### **1. Basit Sorgu**
```bash
python 3_query_rag.py --question "Bu ürün kaliteli mi?"
```

### **2. Programatik Kullanım**
```python
from Config import Config
from Logger import Logger
from Exceptions import RAGServiceError

try:
    # Konfigürasyon doğrula
    Config.validate()
    
    # RAG sorgusu yap
    # ... implementation
    
except RAGServiceError as e:
    Logger.error(f"RAG hatası: {e}")
```

### **3. Custom Konfigürasyon**
```python
import os
os.environ['GEMINI_API_KEY'] = 'your_api_key'
os.environ['TOP_K_CHUNKS'] = '10'
os.environ['CHUNK_MAX_LENGTH'] = '300'
```

## 📝 **Log Formatı**

```
2025-08-05 22:30:11,654 - akilli_yorum_asistani - INFO - RAG sorgu sistemi başlatılıyor...
2025-08-05 22:30:11,655 - akilli_yorum_asistani - INFO - Konfigürasyon doğrulandı
2025-08-05 22:30:11,655 - akilli_yorum_asistani - INFO - Gemini API konfigüre edildi
2025-08-05 22:30:16,533 - akilli_yorum_asistani - INFO - Sentence Transformer modeli yüklendi
2025-08-05 22:30:16,535 - akilli_yorum_asistani - INFO - FAISS index ve chunks dosyaları yükleniyor...
2025-08-05 22:30:16,540 - akilli_yorum_asistani - INFO - Başarıyla yüklendi: 147 chunk
2025-08-05 22:30:16,541 - akilli_yorum_asistani - INFO - 147 yorum formatlandı
2025-08-05 22:30:23,379 - akilli_yorum_asistani - INFO - Gemini API'den yanıt alındı
2025-08-05 22:30:23,379 - akilli_yorum_asistani - INFO - RAG sorgu işlemi başarıyla tamamlandı
```

## 🔧 **Troubleshooting**

### **Yaygın Sorunlar**

#### **1. "No module named 'transformers'"**
```bash
# Yorum environment'ını aktifleştir
conda activate yorum_env

# Paketleri kontrol et
conda list transformers
```

#### **2. "GEMINI_API_KEY not found"**
```bash
# .env dosyası oluştur
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

#### **3. "FAISS index dosyası bulunamadı"**
```bash
# RAG index oluştur
python 2_create_rag_index.py
```

#### **4. "Chunks dosyası bulunamadı"**
```bash
# Yorumları çek
python 1_fetch_reviews.py --url "https://www.trendyol.com/urun-url"
```

## 📈 **Gelecek Geliştirmeler**

### **Planlanan Özellikler**
- [ ] Service Layer implementasyonu
- [ ] Repository Pattern
- [ ] Dependency Injection Container
- [ ] Caching sistemi
- [ ] Async/await desteği
- [ ] Microservices decomposition
- [ ] Docker containerization
- [ ] CI/CD pipeline

### **Performans İyileştirmeleri**
- [ ] Model quantization
- [ ] Index optimization
- [ ] Parallel processing
- [ ] Memory optimization

## 🤝 **Katkıda Bulunma**

1. Fork yapın
2. Feature branch oluşturun
3. Testleri çalıştırın
4. Pull request açın

## 📄 **Lisans**

MIT License - Detaylar için LICENSE dosyasına bakın. 