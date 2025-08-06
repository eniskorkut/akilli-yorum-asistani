const axios = require('axios');

const BASE_URL = 'http://localhost:8080';

// Sadece JavaScript endpoint'lerini test eden fonksiyonlar
async function testHealthCheck() {
  console.log('🔍 Health check test ediliyor...');
  try {
    const response = await axios.get(`${BASE_URL}/health`);
    console.log('✅ Health check başarılı:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Health check başarısız:', error.message);
    return false;
  }
}

async function testQuerySuggestions() {
  console.log('🔍 Soru önerileri test ediliyor...');
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/query/suggestions?partial_question=kalite`);
    console.log('✅ Soru önerileri başarılı:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Soru önerileri başarısız:', error.message);
    return false;
  }
}

async function testQuerySuggestionsEmpty() {
  console.log('🔍 Boş soru önerileri test ediliyor...');
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/query/suggestions`);
    console.log('✅ Boş soru önerileri başarılı:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Boş soru önerileri başarısız:', error.message);
    return false;
  }
}

async function testQuerySuggestionsMultiple() {
  console.log('🔍 Çoklu soru önerileri test ediliyor...');
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/query/suggestions?partial_question=ürün`);
    console.log('✅ Çoklu soru önerileri başarılı:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Çoklu soru önerileri başarısız:', error.message);
    return false;
  }
}

async function testSingleQueryValidation() {
  console.log('🔍 Tekil sorgu validasyonu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query`, {
      // question eksik - hata vermeli
      product_url: "https://www.trendyol.com/sr?q=iphone"
    });
    console.log('❌ Tekil sorgu validasyonu başarısız: Hata vermedi');
    return false;
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Tekil sorgu validasyonu başarılı: Hata döndü');
      return true;
    } else {
      console.error('❌ Tekil sorgu validasyonu beklenmeyen hata:', error.message);
      return false;
    }
  }
}

async function testBatchQueryValidation() {
  console.log('🔍 Toplu sorgu validasyonu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query/batch`, {
      // questions eksik - hata vermeli
      product_url: "https://www.trendyol.com/sr?q=iphone"
    });
    console.log('❌ Toplu sorgu validasyonu başarısız: Hata vermedi');
    return false;
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Toplu sorgu validasyonu başarılı: Hata döndü');
      return true;
    } else {
      console.error('❌ Toplu sorgu validasyonu beklenmeyen hata:', error.message);
      return false;
    }
  }
}

async function testBatchQueryValidationEmpty() {
  console.log('🔍 Boş toplu sorgu validasyonu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query/batch`, {
      questions: [], // Boş array - hata vermeli
      product_url: "https://www.trendyol.com/sr?q=iphone"
    });
    console.log('❌ Boş toplu sorgu validasyonu başarısız: Hata vermedi');
    return false;
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Boş toplu sorgu validasyonu başarılı: Hata döndü');
      return true;
    } else {
      console.error('❌ Boş toplu sorgu validasyonu beklenmeyen hata:', error.message);
      return false;
    }
  }
}

// Ana test fonksiyonu
async function runJsOnlyTests() {
  console.log('🚀 JavaScript API testleri başlatılıyor...\n');
  
  const tests = [
    { name: 'Health Check', fn: testHealthCheck },
    { name: 'Soru Önerileri (Kalite)', fn: testQuerySuggestions },
    { name: 'Soru Önerileri (Boş)', fn: testQuerySuggestionsEmpty },
    { name: 'Soru Önerileri (Çoklu)', fn: testQuerySuggestionsMultiple },
    { name: 'Tekil Sorgu Validasyonu', fn: testSingleQueryValidation },
    { name: 'Toplu Sorgu Validasyonu', fn: testBatchQueryValidation },
    { name: 'Boş Toplu Sorgu Validasyonu', fn: testBatchQueryValidationEmpty }
  ];
  
  let passedTests = 0;
  let totalTests = tests.length;
  
  for (const test of tests) {
    console.log(`\n📋 ${test.name} testi çalıştırılıyor...`);
    const result = await test.fn();
    if (result) {
      passedTests++;
    }
    console.log('─'.repeat(50));
  }
  
  console.log(`\n📊 Test Sonuçları:`);
  console.log(`✅ Başarılı: ${passedTests}/${totalTests}`);
  console.log(`❌ Başarısız: ${totalTests - passedTests}/${totalTests}`);
  
  if (passedTests === totalTests) {
    console.log('\n🎉 Tüm JavaScript testleri başarılı!');
    console.log('💡 Python bağımlılıkları yüklenirse AI işlemleri de çalışacak.');
  } else {
    console.log('\n⚠️  Bazı JavaScript testleri başarısız oldu.');
  }
}

// Test çalıştır
if (require.main === module) {
  runJsOnlyTests().catch(console.error);
}

module.exports = {
  testHealthCheck,
  testQuerySuggestions,
  testSingleQueryValidation,
  testBatchQueryValidation,
  runJsOnlyTests
}; 