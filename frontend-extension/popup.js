// Akilli Yorum Asistani - Chrome Extension Frontend
// Bu dosya Chrome extension'ının popup arayüzünü yönetir
// Frontend: HTML + CSS + JavaScript
// Backend: Express.js API ile iletişim
//
// Özellikler:
// - Trendyol ve Hepsiburada site algılama
// - Gerçek zamanlı URL kontrolü
// - Modern UI/UX tasarımı
// - API entegrasyonu
// - Hata yönetimi
//
// Kullanım:
// Chrome extension olarak yüklenir
// Desteklenen sitelerde otomatik çalışır
//
// Gereksinimler:
// - Chrome Extension API
// - Fetch API
// - Modern JavaScript (ES6+)
//
// Lisans: MIT
// Yazar: Akıllı Yorum Asistanı Projesi

// UI elementleri
const questionInput = document.getElementById('question-input');
const askBtn = document.getElementById('ask-btn');
const statusDiv = document.getElementById('status');
const resultsContainer = document.getElementById('results-container');
const resultsContent = document.getElementById('results-content');
const siteInfoDiv = document.getElementById('site-info');
const siteNameSpan = document.getElementById('site-name');

// Butonu devre dışı bırak
function setButtonDisabled(disabled) {
  askBtn.disabled = disabled;
  if (disabled) {
    askBtn.innerHTML = '<span class="icon"></span>Analiz Ediliyor...';
    askBtn.style.background = 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)';
  } else {
    askBtn.innerHTML = '<span class="icon"></span>Sor ve Analiz Et';
    askBtn.style.background = 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)';
  }
}

// Durum mesajı göster
function showStatus(message, type = 'info') {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
  
  // Smooth fade in effect
  statusDiv.style.opacity = '0';
  statusDiv.style.transform = 'translateY(10px)';
  
  setTimeout(() => {
    statusDiv.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    statusDiv.style.opacity = '1';
    statusDiv.style.transform = 'translateY(0)';
  }, 10);
}

// Sonuçları göster
function showResults(content) {
  resultsContent.textContent = content;
  resultsContainer.style.display = 'block';
  
  // Smooth animation
  resultsContainer.style.opacity = '0';
  resultsContainer.style.transform = 'translateY(20px)';
  
  setTimeout(() => {
    resultsContainer.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    resultsContainer.style.opacity = '1';
    resultsContainer.style.transform = 'translateY(0)';
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 50);
}

// Sonuçları gizle
function hideResults() {
  resultsContainer.style.display = 'none';
}

// Professional loading animasyonu
function showLoadingAnimation() {
  const loadingStates = [
    'Yorumlar çekiliyor',
    'Veriler analiz ediliyor',
    'AI modeli çalışıyor',
    'Sonuçlar hazırlanıyor'
  ];
  
  let stateIndex = 0;
  let dotCount = 0;
  
  const interval = setInterval(() => {
    if (!askBtn.disabled) {
      clearInterval(interval);
      return;
    }
    
    const dots = '.'.repeat(dotCount + 1);
    const loadingText = `${loadingStates[stateIndex]}${dots}`;
    showStatus(loadingText, 'loading');
    
    dotCount++;
    if (dotCount > 3) {
      dotCount = 0;
      stateIndex = (stateIndex + 1) % loadingStates.length;
    }
  }, 800);
  
  return interval;
}

// API çağrısı yap
async function makeApiCall(endpoint, data) {
    try {
    const response = await fetch(`http://localhost:8080/api/v1/${endpoint}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data),
        // Timeout ayarı - 10 dakika
        signal: AbortSignal.timeout(600000)
      });
    
    if (!response.ok) {
      const errorData = await response.json();
      const errorMessage = errorData.error?.message || errorData.error || `HTTP ${response.status}`;
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error.name === 'TimeoutError') {
      throw new Error('İşlem çok uzun sürdü. Lütfen tekrar deneyin.');
    }
    if (error.message.includes('[object Object]')) {
      throw new Error('API yanıtı işlenemedi. Lütfen tekrar deneyin.');
    }
    throw new Error(`API hatası: ${error.message}`);
  }
}

// Aktif sekmenin URL'sini al
async function getCurrentTabUrl() {
  try {
    const tabs = await chrome.tabs.query({active: true, currentWindow: true});
    return tabs[0]?.url || '';
  } catch (error) {
    throw new Error('Sekme URL\'si alınamadı');
  }
}

// Site algılama fonksiyonu
function detectSiteFromUrl(url) {
  if (!url) return null;
  
  const urlLower = url.toLowerCase();
  
  if (urlLower.includes('trendyol.com')) {
    return {
      site: 'trendyol',
      name: 'Trendyol',
      icon: 'trendyol'
    };
  } else if (urlLower.includes('hepsiburada.com')) {
    return {
      site: 'hepsiburada',
      name: 'Hepsiburada',
      icon: 'hepsiburada'
    };
  }
  
  return null;
}

// Site bilgisini göster
function showSiteInfo(siteInfo) {
  if (siteInfo) {
    siteNameSpan.textContent = `Şu sitedesiniz: ${siteInfo.name}`;
    const siteIcon = siteInfoDiv.querySelector('.site-icon');
    siteIcon.className = `site-icon ${siteInfo.icon}`;
    siteInfoDiv.style.display = 'block';
  } else {
    siteInfoDiv.style.display = 'none';
  }
}

// Sayfa yüklendiğinde site bilgisini kontrol et
async function checkCurrentSite() {
  try {
    const currentUrl = await getCurrentTabUrl();
    const siteInfo = detectSiteFromUrl(currentUrl);
    showSiteInfo(siteInfo);
  } catch (error) {
    console.log('Site bilgisi alınamadı:', error);
    siteInfoDiv.style.display = 'none';
  }
}

// Ana fonksiyon: Yorumları çek ve sor
async function askAndAnalyze() {
  try {
    const question = questionInput.value.trim();
    if (!question) {
      showStatus('❌ Lütfen bir soru girin.', 'error');
      return;
    }
    
    setButtonDisabled(true);
    hideResults();
    const loadingInterval = showLoadingAnimation();
    
    const productUrl = await getCurrentTabUrl();
    
    // URL doğrulama
    const validationResponse = await fetch('http://localhost:8080/api/v1/validate-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ url: productUrl })
    });
    
    const validationData = await validationResponse.json();
    
    if (!validationData.success || !validationData.validation.valid) {
      throw new Error(validationData.validation.error || 'Geçersiz ürün sayfası');
    }
    
    const siteName = validationData.site_info.name;
    showStatus(`✅ ${siteName} ürün sayfası algılandı. Yorumlar çekiliyor...`, 'info');
    
    const data = await makeApiCall('query', { 
      question, 
      product_url: productUrl 
    });
    
    clearInterval(loadingInterval);
    showStatus(`✅ ${siteName} yorumları analiz edildi!`, 'success');
    
    // Sadece "Genel Değerlendirme" ve "Test Bilgisi" kısımlarını çıkar
    let generalEvaluation = '';
    let testInfo = '';
    if (data.answer) {
      const lines = data.answer.split('\n');
      let inGeneralSection = false;
      let inTestSection = false;
      
      for (const line of lines) {
        const cleanLine = line.replace(/\*\*/g, '').trim(); // Yıldızları kaldır
        
        if (cleanLine.includes('Genel Değerlendirme') || cleanLine.includes('GENEL DEĞERLENDİRME')) {
          inGeneralSection = true;
          inTestSection = false;
          continue;
        } else if (cleanLine.includes('Test Bilgisi') || cleanLine.includes('TEST BİLGİSİ')) {
          inGeneralSection = false;
          inTestSection = true;
          continue;
        } else if (cleanLine.includes('Sonuç:') || cleanLine.includes('SONUÇ:')) {
          // Sonuç kısmını atla
          break;
        } else if (inGeneralSection && cleanLine === '') {
          // Boş satırla genel değerlendirme biter
          inGeneralSection = false;
        } else if (inGeneralSection) {
          generalEvaluation += cleanLine + '\n';
        } else if (inTestSection) {
          testInfo += cleanLine + '\n';
        }
      }
    }
    
    // Eğer "Genel Değerlendirme" bulunamazsa, tüm cevabı göster
    if (!generalEvaluation.trim()) {
      generalEvaluation = data.answer.replace(/\*\*/g, ''); // Yıldızları kaldır
    }
    
    // Temiz format: Genel Değerlendirme + Test Bilgisi
    let formattedResponse = generalEvaluation.trim();
    if (testInfo.trim()) {
      formattedResponse += '\n\n' + testInfo.trim();
    }
    
    showResults(formattedResponse);
    
  } catch (error) {
    showStatus('❌ Hata: ' + error.message, 'error');
  } finally {
    setButtonDisabled(false);
  }
}

// Event listeners
askBtn.addEventListener('click', askAndAnalyze);

// Enter tuşu ile soru sor
questionInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    askAndAnalyze();
  }
});

// Enhanced focus management with professional animations
questionInput.addEventListener('focus', () => {
  questionInput.style.borderColor = '#3b82f6';
  questionInput.style.transform = 'translateY(-1px)';
  questionInput.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.1)';
});

questionInput.addEventListener('blur', () => {
  questionInput.style.borderColor = '#e2e8f0';
  questionInput.style.transform = 'translateY(0)';
  questionInput.style.boxShadow = 'none';
});

// Professional button hover effects
askBtn.addEventListener('mouseenter', () => {
  if (!askBtn.disabled) {
    askBtn.style.transform = 'translateY(-2px)';
  }
});

askBtn.addEventListener('mouseleave', () => {
  if (!askBtn.disabled) {
    askBtn.style.transform = 'translateY(0)';
  }
});

// Sayfa yüklendiğinde durumu kontrol et
document.addEventListener('DOMContentLoaded', async () => {
  try {
    // Site bilgisini kontrol et ve göster
    await checkCurrentSite();
    
    const url = await getCurrentTabUrl();
    const siteInfo = detectSiteFromUrl(url);
    
    if (siteInfo) {
      showStatus(`✅ ${siteInfo.name} sayfasında bulunuyorsunuz. Soru sorun, yorumları otomatik çekip analiz edelim.`, 'success');
    } else {
      showStatus('⚠️ Desteklenen bir e-ticaret sitesinde değilsiniz. (Trendyol veya Hepsiburada)', 'warning');
    }
  } catch (error) {
    showStatus('❌ Sayfa durumu kontrol edilemedi.', 'error');
  }
});
