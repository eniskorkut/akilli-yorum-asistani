# Akıllı Yorum Asistanı

Trendyol ve Hepsiburada ürün yorumlarını çekip, kullanıcı sorularını Gemini AI ile yanıtlayan akıllı bir browser extension.

## Özellikler

- **Otomatik Yorum Çekme**: Trendyol ve Hepsiburada ürün sayfalarından yorumları otomatik çeker
- **RAG (Retrieval-Augmented Generation)**: Yorumları analiz edip akıllı yanıtlar üretir
- **Browser Extension**: Chrome extension ile kolay kullanım
- **Çoklu Veri Kaynağı**: API + Web scraping desteği
- **Gerçek Zamanlı Analiz**: Anında soru-cevap
- **Çoklu Site Desteği**: Trendyol ve Hepsiburada entegrasyonu

## Gereksinimler

### Backend
- Python 3.8+
- Node.js 16+
- Chrome/Chromium (Selenium için)

### Python Paketleri
```
requests>=2.31.0
sentence-transformers>=2.2.2
faiss-cpu>=1.7.4
numpy>=1.24.0
python-dotenv>=1.0.0
google-generativeai>=0.3.2
selenium>=4.15.0
webdriver-manager>=4.0.0
```

### Node.js Paketleri
```
express>=4.18.2
cors>=2.8.5
```

## Kurulum

### 1. Backend Kurulumu

```bash
cd akilli-yorum-asistani/backend

# Python paketlerini yükle
pip install -r requirements.txt

# Node.js paketlerini yükle
npm install

# Test sistemini çalıştır
python test_system.py
```

### 2. Gemini API Anahtarı

1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Google hesabınızla giriş yapın
3. "Create API Key" butonuna tıklayın
4. API anahtarınızı kopyalayın

`.env` dosyası oluşturun:
```bash
cd backend/ai_core
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

**Önemli**: `your_actual_api_key_here` kısmını gerçek API anahtarınızla değiştirin!

### 3. Chrome Extension Kurulumu

1. Chrome'da `chrome://extensions/` adresine gidin
2. "Developer mode" açın
3. "Load unpacked" butonuna tıklayın
4. `frontend-extension` klasörünü seçin

## Kullanım

### 1. Backend'i Başlatın

```bash
cd backend
npm start
```

Server `http://localhost:8080` adresinde çalışacak.

### 2. Extension'ı Kullanın

1. Trendyol veya Hepsiburada'da bir ürün sayfasına gidin
2. Extension ikonuna tıklayın
3. İstediğiniz soruyu yazın
4. "Yorumları Çek ve Sor" butonuna tıklayın

### 3. Manuel Test

```bash
# Yorumları çek
python ai_core/1_fetch_reviews.py --url "https://www.trendyol.com/urun-url"
python ai_core/1_fetch_reviews.py --url "https://www.hepsiburada.com/urun-url"
```

## Desteklenen Siteler

- **Trendyol**: API + Selenium fallback ile yorum çekme
- **Hepsiburada**: Selenium ile yorum çekme

## API Endpoints

- `POST /api/v1/query` - Tekil sorgu
- `POST /api/v1/query/batch` - Toplu sorgu
- `GET /api/v1/query/suggestions` - Soru önerileri
- `POST /api/v1/validate-url` - URL doğrulama
- `GET /api/v1/supported-sites` - Desteklenen siteler
- `GET /health` - Sağlık kontrolü

## Proje Yapısı

```
akilli-yorum-asistani/
├── backend/
│   ├── ai_core/
│   │   ├── 1_fetch_reviews.py          # Ana yorum çekme modülü
│   │   ├── hepsiburada_scraper.py      # Hepsiburada scraper
│   │   ├── 2_create_rag_index.py       # RAG index oluşturma
│   │   ├── 3_query_rag.py              # RAG sorgulama
│   │   └── requirements.txt            # Python bağımlılıkları
│   ├── server.js                       # Express.js API sunucusu
│   └── package.json                    # Node.js bağımlılıkları
├── frontend-extension/
│   ├── popup.html                      # Extension arayüzü
│   ├── popup.js                        # Extension mantığı
│   └── manifest.json                   # Extension manifest
└── README.md                           # Bu dosya
```

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Branch'e push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Proje hakkında sorularınız için issue açabilirsiniz. 