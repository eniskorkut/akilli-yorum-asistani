// Akilli Yorum Asistani - Express.js API Server
// Bu dosya Express.js server'ını içerir ve AI destekli yorum analizi API'sini sağlar
// Backend: Node.js + Express.js
// AI Core: Python + RAG (Retrieval-Augmented Generation)
//
// Özellikler:
// - Trendyol ve Hepsiburada yorum çekme
// - RAG (Retrieval-Augmented Generation) sistemi
// - RESTful API endpoints
// - CORS desteği
// - Hata yönetimi
//
// API Endpoints:
// - POST /api/v1/query - Tekil sorgu
// - POST /api/v1/query/batch - Toplu sorgu
// - GET /api/v1/query/suggestions - Soru önerileri
// - POST /api/v1/validate-url - URL doğrulama
// - GET /api/v1/supported-sites - Desteklenen siteler
// - GET /health - Sağlık kontrolü
//
// Kullanım:
// npm start
// node server.js
//
// Gereksinimler:
// - express
// - cors
// - child_process
//
// Lisans: MIT
// Yazar: Akıllı Yorum Asistanı Projesi
const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = 8080;

// CORS ayarlarını genişlet
app.use(cors({
  origin: ['http://localhost:3000', 'http://127.0.0.1:3000', 'chrome-extension://*', 'moz-extension://*', 'http://localhost:8080', 'http://127.0.0.1:8080'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin'],
  credentials: true,
  optionsSuccessStatus: 200
}));

app.use(express.json());

// Preflight istekleri için
app.options('*', cors());

// URL algılama fonksiyonu
function detectSiteFromURL(url) {
  if (!url) return null;
  
  const urlLower = url.toLowerCase();
  
  if (urlLower.includes('trendyol.com')) {
    return {
      site: 'trendyol',
      name: 'Trendyol',
      scraper_script: '1_fetch_reviews.py'
    };
  } else if (urlLower.includes('hepsiburada.com')) {
    return {
      site: 'hepsiburada',
      name: 'Hepsiburada',
      scraper_script: '1_fetch_reviews_hepsiburada.py'
    };
  }
  
  return null;
}

// URL doğrulama fonksiyonu
function validateProductURL(url) {
  const siteInfo = detectSiteFromURL(url);
  if (!siteInfo) {
    return {
      valid: false,
      error: 'Desteklenmeyen site',
      supported_sites: ['Trendyol', 'Hepsiburada']
    };
  }
  
  // Site özel doğrulama kuralları
  if (siteInfo.site === 'trendyol') {
    // Trendyol için daha esnek kurallar
    const trendyolPatterns = [
      /\/p-/,
      /\/urun\//,
      /\/brand\//,
      /\/sr\?q=/,
      /\/kategori\//,
      /\/[^\/]+-[^\/]+-p-\d+/,
      /\/[^\/]+\/[^\/]+-p-\d+/
    ];
    
    const isValidTrendyol = trendyolPatterns.some(pattern => pattern.test(url));
    if (!isValidTrendyol) {
      return {
        valid: false,
        error: `Geçerli bir ${siteInfo.name} ürün sayfası değil. Lütfen bir ürün sayfasında olduğunuzdan emin olun.`,
        site: siteInfo.name
      };
    }
  } else if (siteInfo.site === 'hepsiburada') {
    // Hepsiburada için daha esnek kurallar
    const hepsiburadaPatterns = [
      /\/p-/,
      /\/[^\/]+-p-[A-Z0-9]+/,
      /\/[^\/]+\/[^\/]+-p-[A-Z0-9]+/,
      /\/[^\/]+-[^\/]+-p-[A-Z0-9]+/,
      /\/[^\/]+-[^\/]+-[^\/]+-p-[A-Z0-9]+/
    ];
    
    const isValidHepsiburada = hepsiburadaPatterns.some(pattern => pattern.test(url));
    if (!isValidHepsiburada) {
      return {
        valid: false,
        error: `Geçerli bir ${siteInfo.name} ürün sayfası değil. Lütfen bir ürün sayfasında olduğunuzdan emin olun.`,
        site: siteInfo.name
      };
    }
  }
  
  return {
    valid: true,
    site: siteInfo.name,
    scraper_script: siteInfo.scraper_script
  };
}

// Hata yakalama middleware'i
app.use((err, req, res, next) => {
  console.error('Hata:', err);
  res.status(500).json({
    success: false,
    error: {
      error_code: "INTERNAL_ERROR",
      message: "Sunucu hatası",
      details: err.message,
      timestamp: Date.now()
    }
  });
});

// Ana sorgu endpoint'i (Python API'sinin yerini alır)
app.post('/api/v1/query', async (req, res) => {
  const { question, product_url, max_reviews = 50, use_mocks = false } = req.body;
  
  if (!question) {
    return res.status(400).json({ 
      success: false, 
      error: {
        error_code: "MISSING_QUESTION",
        message: "Soru zorunludur",
        timestamp: Date.now()
      }
    });
  }

  console.log(`Sorgu isteği alındı: ${question}`);
  const startTime = Date.now();

  try {
    // Eğer product_url varsa, önce URL'yi doğrula ve yorumları çek
    if (product_url) {
      const validation = validateProductURL(product_url);
      if (!validation.valid) {
        return res.status(400).json({
          success: false,
          error: {
            error_code: "INVALID_URL",
            message: validation.error,
            supported_sites: validation.supported_sites,
            timestamp: Date.now()
          }
        });
      }
      
      console.log(`Geçerli ${validation.site} ürün sayfası: ${product_url}`);
      await fetchReviews(product_url, max_reviews);
      await updateRagIndex();
    }

    // Soruyu analiz et
    const result = await analyzeQuestion(question);
    const processingTime = (Date.now() - startTime) / 1000;

    res.json({
      success: true,
      answer: result.answer,
      question: question,
      total_reviews: result.total_reviews || 0,
      used_reviews: result.used_reviews || 0,
      processing_time: processingTime,
      timestamp: Date.now(),
      metadata: result.metadata || {}
    });

  } catch (error) {
    console.error('Sorgu hatası:', error);
    res.status(500).json({
      success: false,
      error: {
        error_code: "INTERNAL_ERROR",
        message: "Beklenmeyen bir hata oluştu",
        details: error.message,
        timestamp: Date.now()
      }
    });
  }
});

// Toplu sorgu endpoint'i
app.post('/api/v1/query/batch', async (req, res) => {
  const { questions, product_url, max_reviews = 50, use_mocks = false } = req.body;
  
  if (!questions || !Array.isArray(questions) || questions.length === 0) {
    return res.status(400).json({ 
      success: false, 
      error: {
        error_code: "MISSING_QUESTIONS",
        message: "Sorular zorunludur ve array olmalıdır",
        timestamp: Date.now()
      }
    });
  }

  console.log(`Toplu sorgu isteği alındı: ${questions.length} soru`);
  const startTime = Date.now();

  try {
    // Eğer product_url varsa, önce yorumları çek
    if (product_url) {
      await fetchReviews(product_url, max_reviews);
      await updateRagIndex();
    }

    // Her soru için işlem yap
    const results = [];
    let successfulCount = 0;
    let failedCount = 0;

    for (const question of questions) {
      try {
        const result = await analyzeQuestion(question);
        
        results.push({
          success: true,
          answer: result.answer,
          question: question,
          total_reviews: result.total_reviews || 0,
          used_reviews: result.used_reviews || 0,
          processing_time: result.processing_time || 0,
          timestamp: Date.now(),
          metadata: result.metadata || {}
        });
        successfulCount++;
      } catch (error) {
        console.error(`Soru işleme hatası: ${question} - ${error.message}`);
        
        results.push({
          success: false,
          answer: null,
          question: question,
          total_reviews: 0,
          used_reviews: 0,
          processing_time: 0,
          timestamp: Date.now(),
          metadata: { error: { message: error.message } }
        });
        failedCount++;
      }
    }

    const totalProcessingTime = (Date.now() - startTime) / 1000;

    res.json({
      success: successfulCount > 0,
      results: results,
      total_questions: questions.length,
      successful_questions: successfulCount,
      failed_questions: failedCount,
      total_processing_time: totalProcessingTime,
      timestamp: Date.now()
    });

  } catch (error) {
    console.error('Toplu sorgu hatası:', error);
    res.status(500).json({
      success: false,
      error: {
        error_code: "INTERNAL_ERROR",
        message: "Beklenmeyen bir hata oluştu",
        details: error.message,
        timestamp: Date.now()
      }
    });
  }
});

// Soru önerileri endpoint'i
app.get('/api/v1/query/suggestions', (req, res) => {
  const { partial_question = "" } = req.query;
  
  console.log(`Soru önerisi isteği alındı: ${partial_question}`);

  // Basit soru önerileri
  const suggestions = [
    "Bu ürünün kalitesi nasıl?",
    "Kullanıcılar bu ürün hakkında ne düşünüyor?",
    "Bu ürünün avantajları ve dezavantajları neler?",
    "Bu ürünü kimler öneriyor?",
    "Bu ürünün fiyat/performans oranı nasıl?",
    "Kullanıcıların en çok şikayet ettiği konular neler?",
    "Bu ürün hangi durumlarda önerilir?",
    "Kullanıcıların en beğendiği özellikler neler?"
  ];

  // Kısmi soruya göre filtrele
  const filteredSuggestions = suggestions.filter(suggestion => 
    suggestion.toLowerCase().includes(partial_question.toLowerCase())
  );

  res.json({
    suggestions: filteredSuggestions.slice(0, 5),
    partial_question: partial_question,
    total_suggestions: filteredSuggestions.length
  });
});

// URL doğrulama endpoint'i
app.post('/api/v1/validate-url', (req, res) => {
  const { url } = req.body;
  
  if (!url) {
    return res.status(400).json({
      success: false,
      error: {
        error_code: "MISSING_URL",
        message: "URL zorunludur",
        timestamp: Date.now()
      }
    });
  }
  
  const validation = validateProductURL(url);
  const siteInfo = detectSiteFromURL(url);
  
  res.json({
    success: true,
    url: url,
    validation: validation,
    site_info: siteInfo,
    supported_sites: ['Trendyol', 'Hepsiburada'],
    timestamp: Date.now()
  });
});

// Desteklenen siteler endpoint'i
app.get('/api/v1/supported-sites', (req, res) => {
  res.json({
    success: true,
    supported_sites: [
      {
        name: 'Trendyol',
        domain: 'trendyol.com',
        example_url: 'https://www.trendyol.com/urun/p-123456'
      },
      {
        name: 'Hepsiburada',
        domain: 'hepsiburada.com',
        example_url: 'https://www.hepsiburada.com/urun/p-123456'
      }
    ],
    timestamp: Date.now()
  });
});

// Yorumları çekme fonksiyonu
function fetchReviews(productUrl, maxReviews = 50) {
  return new Promise((resolve, reject) => {
    console.log(`Yorumlar çekiliyor: ${productUrl}`);

    // URL'den site algıla
    const siteInfo = detectSiteFromURL(productUrl);
    if (!siteInfo) {
      reject(new Error('Desteklenmeyen site. Sadece Trendyol ve Hepsiburada desteklenir.'));
      return;
    }

    console.log(`Algılanan site: ${siteInfo.name}`);

    // Python path'ini düzelt
    const pythonPath = process.platform === 'win32' ? 'python' : '/opt/anaconda3/envs/yorum_env/bin/python';
    
    // Tek bir script kullan - site algılama Python tarafında yapılacak
    const py = spawn(pythonPath, [
      '1_fetch_reviews.py',
      '--url', productUrl,
      '--max-reviews', maxReviews.toString()
    ], {
      cwd: path.join(__dirname, 'ai_core'),
      timeout: 300000 // 5 dakika timeout
    });

    let output = '';
    let errorOutput = '';

    py.stdout.on('data', (data) => {
      output += data.toString();
      console.log('Python output:', data.toString());
    });

    py.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error('Python error:', data.toString());
    });

    py.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python script hatası: ${code}`);
        console.error(`Error output: ${errorOutput}`);
        reject(new Error(`Yorumlar çekilemedi: ${errorOutput}`));
      } else {
        console.log('Yorumlar başarıyla çekildi');
        resolve(output);
      }
    });

    py.on('error', (error) => {
      console.error(`Python spawn hatası: ${error.message}`);
      reject(new Error(`Yorum çekme hatası: ${error.message}`));
    });
  });
}

// RAG index'ini güncelleme fonksiyonu
function updateRagIndex() {
  return new Promise((resolve, reject) => {
    console.log('RAG index güncelleniyor...');
    
    const pythonPath = process.platform === 'win32' ? 'python' : '/opt/anaconda3/envs/yorum_env/bin/python';
    
    const py = spawn(pythonPath, ['2_create_rag_index.py'], {
      cwd: path.join(__dirname, 'ai_core'),
      timeout: 120000 // 2 dakika timeout
    });

    let output = '';
    let errorOutput = '';

    py.stdout.on('data', (data) => {
      output += data.toString();
      console.log('RAG output:', data.toString());
    });

    py.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error('RAG error:', data.toString());
    });

    py.on('close', (code) => {
      if (code !== 0) {
        console.error(`RAG script hatası: ${code}`);
        console.error(`Error output: ${errorOutput}`);
        reject(new Error(`RAG index güncellenemedi: ${errorOutput}`));
      } else {
        console.log('RAG index başarıyla güncellendi');
        resolve(output);
      }
    });

    py.on('error', (error) => {
      console.error(`RAG spawn hatası: ${error.message}`);
      reject(new Error(`RAG index güncelleme hatası: ${error.message}`));
    });
  });
}

// Soru analiz etme fonksiyonu
function analyzeQuestion(question) {
  return new Promise((resolve, reject) => {
    console.log(`Soru analiz ediliyor: ${question}`);

    const pythonPath = process.platform === 'win32' ? 'python' : '/opt/anaconda3/envs/yorum_env/bin/python';

    const py = spawn(pythonPath, [
      '3_query_rag.py',
      '--question', question
    ], {
      cwd: path.join(__dirname, 'ai_core'),
      timeout: 120000 // 2 dakika timeout
    });

    let output = '';
    let errorOutput = '';

    py.stdout.on('data', (data) => {
      output += data.toString();
    });

    py.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    py.on('close', (code) => {
      if (code !== 0) {
        console.error(`Query script hatası: ${code}`);
        console.error(`Error output: ${errorOutput}`);
        reject(new Error(`Soru analiz edilemedi: ${errorOutput}`));
      } else {
        // Çıktıyı parse etmeye çalış
        try {
          const cleanOutput = output.trim();
          const result = {
            answer: cleanOutput,
            total_reviews: 0,
            used_reviews: 0,
            processing_time: 0,
            metadata: {}
          };
          resolve(result);
        } catch (parseError) {
          resolve({
            answer: output.trim(),
            total_reviews: 0,
            used_reviews: 0,
            processing_time: 0,
            metadata: {}
          });
        }
      }
    });

    py.on('error', (error) => {
      console.error(`Query spawn hatası: ${error.message}`);
      reject(new Error(`Soru analiz hatası: ${error.message}`));
    });
  });
}

// Eski endpoint'ler (geriye uyumluluk için)
app.post('/fetch-reviews', (req, res) => {
  const { product_url } = req.body;
  if (!product_url) {
    return res.status(400).json({ error: 'product_url zorunludur.' });
  }

  fetchReviews(product_url)
    .then(() => updateRagIndex())
    .then(() => {
      res.json({ 
        success: true, 
        message: 'Yorumlar çekildi ve RAG index güncellendi'
      });
    })
    .catch(error => {
      res.status(500).json({ 
        error: 'İşlem başarısız', 
        details: error.message 
      });
    });
});

app.post('/analyze', (req, res) => {
  const { question } = req.body;
  if (!question) {
    return res.status(400).json({ error: 'question zorunludur.' });
  }

  analyzeQuestion(question)
    .then(result => {
      res.json({ answer: result.answer });
    })
    .catch(error => {
      res.status(500).json({ 
        error: 'Analiz hatası', 
        details: error.message 
      });
    });
});

app.post('/fetch-and-analyze', async (req, res) => {
  const { question, product_url } = req.body;
  if (!question || !product_url) {
    return res.status(400).json({ error: 'question ve product_url zorunludur.' });
  }

  try {
    await fetchReviews(product_url);
    await updateRagIndex();
    const result = await analyzeQuestion(question);
    
    res.json({ 
      answer: result.answer
    });
  } catch (error) {
    res.status(500).json({ 
      error: 'İşlem başarısız', 
      details: error.message 
    });
  }
});

// Test endpoint'i (eklenti testi için)
app.get('/test', (req, res) => {
  res.json({ 
    message: 'Backend çalışıyor!', 
    timestamp: Date.now(),
    cors: 'enabled'
  });
});

// Health check endpoint'i
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: Date.now(),
    service: 'Akıllı Yorum Asistanı API'
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`API endpoints:`);
  console.log(`  POST /api/v1/query - Tekil sorgu`);
  console.log(`  POST /api/v1/query/batch - Toplu sorgu`);
  console.log(`  GET /api/v1/query/suggestions - Soru önerileri`);
  console.log(`  GET /health - Sağlık kontrolü`);
  console.log(`  POST /fetch-reviews - Yorumları çek (eski)`);
  console.log(`  POST /analyze - Analiz et (eski)`);
  console.log(`  POST /fetch-and-analyze - Çek ve analiz et (eski)`);
});