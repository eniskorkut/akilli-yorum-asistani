# Akıllı Yorum Asistanı - JavaScript API

Bu proje, ürün yorumlarını analiz eden ve kullanıcı sorularını yanıtlayan bir JavaScript API'sidir. **Trendyol** ve **Hepsiburada** sitelerini destekler.

## 🚀 Özellikler

- **Çoklu Site Desteği**: Trendyol ve Hepsiburada
- **Otomatik Site Algılama**: URL'den hangi site olduğunu otomatik algılar
- **Tekil Sorgu**: Tek bir soru için AI destekli yanıt
- **Toplu Sorgu**: Birden fazla soruyu aynı anda işleme
- **Soru Önerileri**: Kullanıcılara soru önerileri sunma
- **Yorum Çekme**: Otomatik yorum çekme
- **RAG Sistemi**: Retrieval-Augmented Generation ile akıllı yanıtlar

## 📋 Gereksinimler

- Node.js (v14 veya üzeri)
- Python 3.8+ (AI işlemleri için)
- npm veya yarn

## 🛠️ Kurulum

1. **Bağımlılıkları yükleyin:**
```bash
npm install
```

2. **Python bağımlılıklarını yükleyin:**
```bash
cd ai_core
pip install -r requirements.txt
```

3. **Sunucuyu başlatın:**
```bash
npm start
```

## 🔧 Geliştirme

Geliştirme modunda çalıştırmak için:
```bash
npm run dev
```

## 🧪 Test

API'yi test etmek için:
```bash
npm test
```

Çoklu site testleri için:
```bash
node test_multi_site.js
```

## 📡 API Endpoints

### Ana Endpoints

#### `POST /api/v1/query`
Tekil sorgu için kullanılır.

**Request Body:**
```json
{
  "question": "Bu ürünün kalitesi nasıl?",
  "product_url": "https://www.trendyol.com/urun/p-123456",
  "max_reviews": 50,
  "use_mocks": false
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Kullanıcı yorumlarına göre...",
  "question": "Bu ürünün kalitesi nasıl?",
  "total_reviews": 150,
  "used_reviews": 25,
  "processing_time": 2.5,
  "timestamp": 1703123456789,
  "metadata": {}
}
```

#### `POST /api/v1/query/batch`
Toplu sorgu için kullanılır.

#### `GET /api/v1/query/suggestions`
Soru önerileri için kullanılır.

#### `POST /api/v1/validate-url`
URL doğrulama için kullanılır.

**Request Body:**
```json
{
  "url": "https://www.trendyol.com/urun/p-123456"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://www.trendyol.com/urun/p-123456",
  "validation": {
    "valid": true,
    "site": "Trendyol",
    "scraper_script": "1_fetch_reviews.py"
  },
  "site_info": {
    "site": "trendyol",
    "name": "Trendyol",
    "scraper_script": "1_fetch_reviews.py"
  },
  "supported_sites": ["Trendyol", "Hepsiburada"]
}
```

#### `GET /api/v1/supported-sites`
Desteklenen siteleri listeler.

**Response:**
```json
{
  "success": true,
  "supported_sites": [
    {
      "name": "Trendyol",
      "domain": "trendyol.com",
      "example_url": "https://www.trendyol.com/urun/p-123456"
    },
    {
      "name": "Hepsiburada",
      "domain": "hepsiburada.com",
      "example_url": "https://www.hepsiburada.com/urun/p-123456"
    }
  ]
}
```

#### `GET /health`
Sağlık kontrolü için kullanılır.

### Eski Endpoints (Geriye Uyumluluk)

#### `POST /fetch-reviews`
Yorumları çeker.

#### `POST /analyze`
Soru analiz eder.

#### `POST /fetch-and-analyze`
Yorumları çeker ve analiz eder.

## 🏪 Desteklenen Siteler

### Trendyol
- **Domain**: trendyol.com
- **Scraper**: `1_fetch_reviews.py`
- **URL Format**: `https://www.trendyol.com/urun/p-{product_id}`

### Hepsiburada
- **Domain**: hepsiburada.com
- **Scraper**: `1_fetch_reviews_hepsiburada.py`
- **URL Format**: `https://www.hepsiburada.com/urun/p-{product_id}`

## 🔄 İş Akışı

1. **URL Algılama**: URL'den hangi site olduğu otomatik algılanır
2. **URL Doğrulama**: Ürün sayfası olup olmadığı kontrol edilir
3. **Yorum Çekme**: Site özel scraper ile yorumlar çekilir
4. **RAG Index**: Çekilen yorumlar RAG sistemi için indexlenir
5. **Soru Analizi**: Kullanıcı sorusu AI ile analiz edilir
6. **Yanıt Üretimi**: RAG sistemi ile akıllı yanıt üretilir

## 📁 Proje Yapısı

```
backend/
├── server.js                    # Ana Express sunucusu
├── test_api.js                  # API test dosyası
├── test_multi_site.js           # Çoklu site test dosyası
├── package.json                 # Node.js bağımlılıkları
├── ai_core/                     # Python AI modülleri
│   ├── 1_fetch_reviews.py       # Trendyol yorum çekme
│   ├── 1_fetch_reviews_hepsiburada.py # Hepsiburada yorum çekme
│   ├── 2_create_rag_index.py    # RAG index oluşturma
│   ├── 3_query_rag.py           # RAG sorgu
│   ├── url_detector.py          # URL algılama modülü
│   └── requirements.txt         # Python bağımlılıkları
└── README.md                    # Bu dosya
```

## 🚨 Hata Kodları

- `MISSING_QUESTION`: Soru parametresi eksik
- `MISSING_QUESTIONS`: Sorular parametresi eksik
- `MISSING_URL`: URL parametresi eksik
- `INVALID_URL`: Geçersiz URL
- `INTERNAL_ERROR`: Sunucu hatası

## 📝 Loglar

API tüm işlemleri konsola loglar:
- URL algılama sonuçları
- Site doğrulama sonuçları
- Sorgu istekleri
- Python script çıktıları
- Hata mesajları
- İşlem süreleri

## 🔒 Güvenlik

- CORS desteği
- Input validasyonu
- URL doğrulama
- Timeout koruması
- Hata yakalama

## 📈 Performans

- Asenkron işlemler
- Promise tabanlı Python script çağrıları
- Timeout koruması (5 dakika yorum çekme, 2 dakika analiz)
- Batch işlem desteği
- Site özel optimizasyonlar

## 🌐 Eklenti Desteği

Chrome eklentisi şu siteleri destekler:
- Trendyol ürün sayfaları
- Hepsiburada ürün sayfaları

Eklenti otomatik olarak:
- Hangi site olduğunu algılar
- URL'yi doğrular
- Uygun scraper'ı seçer
- Yorumları çeker ve analiz eder

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 