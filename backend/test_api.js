const axios = require('axios');

const BASE_URL = 'http://localhost:8080';

// Test fonksiyonları
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

async function testSingleQuery() {
  console.log('🔍 Tekil sorgu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query`, {
      question: "Bu ürünün kalitesi nasıl?",
      product_url: "https://www.trendyol.com/sr?q=iphone",
      max_reviews: 10
    });
    console.log('✅ Tekil sorgu başarılı:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Tekil sorgu başarısız:', error.response?.data || error.message);
    return false;
  }
}

async function testBatchQuery() {
  console.log('🔍 Toplu sorgu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query/batch`, {
      questions: [
        "Bu ürünün kalitesi nasıl?",
        "Kullanıcılar ne düşünüyor?"
      ],
      product_url: "https://www.trendyol.com/sr?q=iphone",
      max_reviews: 10
    });
    console.log('✅ Toplu sorgu başarılı:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Toplu sorgu başarısız:', error.response?.data || error.message);
    return false;
  }
}

async function testLegacyEndpoints() {
  console.log('🔍 Eski endpoint\'ler test ediliyor...');
  
  try {
    // Fetch reviews test
    const fetchResponse = await axios.post(`${BASE_URL}/fetch-reviews`, {
      product_url: "https://www.trendyol.com/sr?q=iphone"
    });
    console.log('✅ Fetch reviews başarılı:', fetchResponse.data);
    
    // Analyze test
    const analyzeResponse = await axios.post(`${BASE_URL}/analyze`, {
      question: "Bu ürünün kalitesi nasıl?"
    });
    console.log('✅ Analyze başarılı:', analyzeResponse.data);
    
    return true;
  } catch (error) {
    console.error('❌ Eski endpoint\'ler başarısız:', error.response?.data || error.message);
    return false;
  }
}

// Ana test fonksiyonu
async function runAllTests() {
  console.log('🚀 API testleri başlatılıyor...\n');
  
  const tests = [
    { name: 'Health Check', fn: testHealthCheck },
    { name: 'Soru Önerileri', fn: testQuerySuggestions },
    { name: 'Tekil Sorgu', fn: testSingleQuery },
    { name: 'Toplu Sorgu', fn: testBatchQuery },
    { name: 'Eski Endpoint\'ler', fn: testLegacyEndpoints }
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
    console.log('\n🎉 Tüm testler başarılı!');
  } else {
    console.log('\n⚠️  Bazı testler başarısız oldu.');
  }
}

// Test çalıştır
if (require.main === module) {
  runAllTests().catch(console.error);
}

module.exports = {
  testHealthCheck,
  testQuerySuggestions,
  testSingleQuery,
  testBatchQuery,
  testLegacyEndpoints,
  runAllTests
}; 