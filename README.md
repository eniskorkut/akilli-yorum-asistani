# 🤖 Akıllı Yorum Asistanı

Trendyol ürün yorumlarını çekip, kullanıcı sorularını Gemini AI ile yanıtlayan akıllı bir browser extension.

## 🚀 Özellikler

- **Otomatik Yorum Çekme**: Trendyol ürün sayfalarından yorumları otomatik çeker
- **RAG (Retrieval-Augmented Generation)**: Yorumları analiz edip akıllı yanıtlar üretir
- **Browser Extension**: Chrome extension ile kolay kullanım
- **Çoklu Veri Kaynağı**: API + Web scraping desteği
- **Gerçek Zamanlı Analiz**: Anında soru-cevap

## 📋 Gereksinimler

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

## 🛠️ Kurulum

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

## 🚀 Kullanım

### 1. Backend'i Başlatın

```bash
cd backend
npm start
```

Server `http://localhost:8080` adresinde çalışacak.

### 2. Extension'ı Kullanın

1. Trendyol'da bir ürün sayfasına gidin
2. Extension ikonuna tıklayın
3. İstediğiniz soruyu yazın
4. "Yorumları Çek ve Sor" butonuna tıklayın

### 3. Manuel Test

```bash
# Yorumları çek
python ai_core/1_fetch_reviews.py --url "https://www.trendyol.com/urun-url"

# RAG index oluştur
python ai_core/2_create_rag_index.py

# Soru sor
python ai_core/3_query_rag.py --question "Bu ürün kaliteli mi?"
```

## 📁 Proje Yapısı

```
akilli-yorum-asistani/
├── backend/
│   ├── ai_core/
│   │   ├── 1_fetch_reviews.py      # Yorum çekme
│   │   ├── 2_create_rag_index.py   # RAG index oluşturma
│   │   ├── 3_query_rag.py          # AI sorgulama
│   │   ├── 3_query_rag_test.py     # Test modu
│   │   ├── reviews.json            # Çekilen yorumlar
│   │   ├── chunks.json             # Metin parçaları
│   │   └── index.faiss             # FAISS index
│   ├── server.js                   # Express server
│   ├── package.json
│   ├── requirements.txt
│   └── test_system.py              # Test scripti
└── frontend-extension/
    ├── manifest.json               # Extension manifest
    ├── popup.html                  # UI
    └── popup.js                    # Frontend logic
```

## 🔧 API Endpoints

### POST /fetch-reviews
Yorumları çeker ve RAG index'ini günceller.

**Request:**
```json
{
  "product_url": "https://www.trendyol.com/urun-url"
}
```

### POST /analyze
Mevcut yorumlardan soru yanıtlar.

**Request:**
```json
{
  "question": "Bu ürün kaliteli mi?"
}
```

### POST /fetch-and-analyze
Yorumları çeker ve soruyu yanıtlar (tek seferde).

**Request:**
```json
{
  "question": "Bu ürün kaliteli mi?",
  "product_url": "https://www.trendyol.com/urun-url"
}
```

## 🧠 RAG Sistemi

1. **Yorum Çekme**: Trendyol API'si veya Selenium ile
2. **Metin Bölme**: Yorumları anlamlı parçalara bölme
3. **Embedding**: Sentence transformers ile vektörleştirme
4. **Indexleme**: FAISS ile hızlı arama
5. **Retrieval**: En alakalı parçaları bulma
6. **Generation**: Gemini ile yanıt üretme

## 🐛 Sorun Giderme

### Yorumlar Çekilmiyor
- Trendyol URL'sinin doğru olduğundan emin olun
- Selenium Chrome driver'ının yüklü olduğunu kontrol edin
- Network bağlantınızı kontrol edin

### AI Yanıt Vermiyor
- Gemini API anahtarınızı kontrol edin
- `.env` dosyasının doğru konumda olduğunu kontrol edin
- API quota limitinizi kontrol edin

### Extension Çalışmıyor
- Backend'in çalıştığından emin olun (`localhost:8080`)
- Extension'ı yeniden yükleyin
- Chrome console'da hata mesajlarını kontrol edin

## 📝 Örnek Kullanım

```
Kullanıcı: "Bu ürün kaliteli mi?"
AI: "Yorumlara göre bu ürün genellikle kaliteli olarak değerlendiriliyor. 
5 yıldızlı yorumlarda 'çok kaliteli', 'harika ürün' gibi ifadeler kullanılmış. 
Ancak bazı kullanıcılar boyut konusunda sıkıntı yaşamış. 
Genel olarak fiyatına değer bir ürün olduğu belirtiliyor."

Kullanıcı: "Hangi renk daha popüler?"
AI: "Yorumlarda en çok bahsedilen renkler mavi ve siyah. 
Mavi renk için 'çok güzel', 'harika renk' gibi olumlu yorumlar var. 
Siyah renk de kullanıcılar tarafından beğenilmiş."
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🙏 Teşekkürler

- Google Gemini AI
- Trendyol API
- Sentence Transformers
- FAISS
- Chrome Extension API 