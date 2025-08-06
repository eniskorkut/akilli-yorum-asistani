const axios = require('axios');

const BASE_URL = 'http://localhost:8080';

// Test fonksiyonları
async function testURLValidation() {
  console.log('🔍 URL doğrulama test ediliyor...');
  
  const testUrls = [
    'https://www.trendyol.com/urun/p-123456',
    'https://www.hepsiburada.com/urun/p-123456',
    'https://www.amazon.com/urun/p-123456', // Desteklenmeyen site
    'https://www.trendyol.com/anasayfa', // Geçersiz ürün sayfası
    'invalid-url'
  ];
  
  for (const url of testUrls) {
    try {
      const response = await axios.post(`${BASE_URL}/api/v1/validate-url`, { url });
      console.log(`✅ ${url}: ${response.data.validation.valid ? 'Geçerli' : 'Geçersiz'} - ${response.data.site_info?.name || 'Bilinmeyen'}`);
    } catch (error) {
      console.error(`❌ ${url}: ${error.response?.data?.error?.message || error.message}`);
    }
  }
}

async function testSupportedSites() {
  console.log('🔍 Desteklenen siteler test ediliyor...');
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/supported-sites`);
    console.log('✅ Desteklenen siteler:', response.data.supported_sites.map(s => s.name));
    return true;
  } catch (error) {
    console.error('❌ Desteklenen siteler testi başarısız:', error.message);
    return false;
  }
}

async function testTrendyolQuery() {
  console.log('🔍 Trendyol sorgu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query`, {
      question: "Bu ürünün kalitesi nasıl?",
      product_url: "https://www.trendyol.com/urun/p-123456",
      max_reviews: 10
    });
    console.log('✅ Trendyol sorgu başarılı:', response.data.success);
    return true;
  } catch (error) {
    console.error('❌ Trendyol sorgu başarısız:', error.response?.data?.error?.message || error.message);
    return false;
  }
}

async function testHepsiburadaQuery() {
  console.log('🔍 Hepsiburada sorgu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query`, {
      question: "Bu ürünün kalitesi nasıl?",
      product_url: "https://www.hepsiburada.com/urun/p-123456",
      max_reviews: 10
    });
    console.log('✅ Hepsiburada sorgu başarılı:', response.data.success);
    return true;
  } catch (error) {
    console.error('❌ Hepsiburada sorgu başarısız:', error.response?.data?.error?.message || error.message);
    return false;
  }
}

async function testInvalidSiteQuery() {
  console.log('🔍 Geçersiz site sorgu test ediliyor...');
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/query`, {
      question: "Bu ürünün kalitesi nasıl?",
      product_url: "https://www.amazon.com/urun/p-123456",
      max_reviews: 10
    });
    console.log('❌ Geçersiz site sorgu başarısız olmalıydı ama başarılı oldu');
    return false;
  } catch (error) {
    if (error.response?.status === 400) {
      console.log('✅ Geçersiz site sorgu doğru şekilde reddedildi');
      return true;
    } else {
      console.error('❌ Geçersiz site sorgu beklenmeyen hata:', error.message);
      return false;
    }
  }
}

// Ana test fonksiyonu
async function runMultiSiteTests() {
  console.log('🚀 Çoklu site testleri başlatılıyor...\n');
  
  const tests = [
    { name: 'URL Doğrulama', fn: testURLValidation },
    { name: 'Desteklenen Siteler', fn: testSupportedSites },
    { name: 'Trendyol Sorgu', fn: testTrendyolQuery },
    { name: 'Hepsiburada Sorgu', fn: testHepsiburadaQuery },
    { name: 'Geçersiz Site Sorgu', fn: testInvalidSiteQuery }
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
    console.log('\n🎉 Tüm çoklu site testleri başarılı!');
  } else {
    console.log('\n⚠️  Bazı testler başarısız oldu.');
  }
}

// Test çalıştır
if (require.main === module) {
  runMultiSiteTests().catch(console.error);
}

module.exports = {
  testURLValidation,
  testSupportedSites,
  testTrendyolQuery,
  testHepsiburadaQuery,
  testInvalidSiteQuery,
  runMultiSiteTests
}; 