# 🧪 Test Documentation

Bu dokümantasyon, AI Core modülünün test sistemi hakkında detaylı bilgi içerir.

## 📋 **Test Stratejisi**

### **Test Piramidi**
```
        🔺 E2E Tests (1%)
       🔺🔺 Integration Tests (10%)
    🔺🔺🔺🔺 Unit Tests (89%)
```

### **Test Kategorileri**
1. **Unit Tests**: Tek fonksiyon/sınıf testleri
2. **Integration Tests**: Bileşenler arası testler
3. **End-to-End Tests**: Tam sistem testleri
4. **Performance Tests**: Performans testleri
5. **Security Tests**: Güvenlik testleri

## 🏗️ **Test Mimarisi**

### **Test Dosya Yapısı**
```
ai_core/
├── TestQueryRag.py          # Ana test dosyası
├── RunTests.py              # Test runner
├── tests/                   # Test klasörü (gelecek)
│   ├── unit/               # Unit testler
│   ├── integration/        # Integration testler
│   ├── e2e/               # End-to-end testler
│   └── fixtures/          # Test verileri
└── TEST_DOCUMENTATION.md   # Bu dosya
```

### **Test Framework**
- **Framework**: Python unittest
- **Mock Library**: unittest.mock
- **Assertion Library**: unittest assertions
- **Test Runner**: Custom RunTests.py

## 🧪 **Unit Tests**

### **TestQueryRag.py**

#### **1. TestConfig Sınıfı**
```python
class TestConfig(unittest.TestCase):
    """Config sınıfı için testler"""
```

**Test Metodları:**
- `test_config_validation_success()`: Başarılı konfigürasyon doğrulama
- `test_config_validation_failure()`: Başarısız konfigürasyon doğrulama
- `test_get_model_config()`: Model konfigürasyonu alma
- `test_get_rag_config()`: RAG konfigürasyonu alma

**Test Coverage:**
- ✅ Environment variables
- ✅ Validation logic
- ✅ Configuration methods
- ✅ Error handling

#### **2. TestExceptions Sınıfı**
```python
class TestExceptions(unittest.TestCase):
    """Custom exception sınıfları için testler"""
```

**Test Metodları:**
- `test_api_error_with_details()`: APIError detaylı bilgi testi
- `test_exception_inheritance()`: Exception inheritance testi

**Test Coverage:**
- ✅ Exception creation
- ✅ Exception properties
- ✅ Inheritance hierarchy
- ✅ Error details

#### **3. TestLogger Sınıfı**
```python
class TestLogger(unittest.TestCase):
    """Logger sınıfı için testler"""
```

**Test Metodları:**
- `test_logger_singleton()`: Singleton pattern testi
- `test_logger_methods()`: Logger metodları testi

**Test Coverage:**
- ✅ Singleton pattern
- ✅ Log methods
- ✅ Log levels
- ✅ File output

#### **4. TestRAGFunctions Sınıfı**
```python
class TestRAGFunctions(unittest.TestCase):
    """RAG fonksiyonları için testler"""
```

**Test Metodları:**
- `test_load_index_and_chunks_success()`: Index yükleme başarı testi
- `test_get_top_chunks_validation()`: Top chunks validation testi
- `test_extract_product_stats()`: Ürün istatistikleri testi

**Test Coverage:**
- ✅ File operations
- ✅ Data validation
- ✅ Statistics calculation
- ✅ Error handling

#### **5. TestIntegration Sınıfı**
```python
class TestIntegration(unittest.TestCase):
    """Integration testleri"""
```

**Test Metodları:**
- `test_full_pipeline_mock()`: Tam pipeline mock testi

**Test Coverage:**
- ✅ End-to-end workflow
- ✅ Mock interactions
- ✅ API calls
- ✅ Data flow

## 🔧 **Test Çalıştırma**

### **Komut Satırı**
```bash
# Tüm testleri çalıştır
python RunTests.py

# Sadece unit testler
python -m unittest TestQueryRag.py -v

# Belirli test sınıfı
python -m unittest TestQueryRag.TestConfig -v

# Belirli test metodu
python -m unittest TestQueryRag.TestConfig.test_config_validation_success -v

# Coverage ile test
python -m coverage run -m unittest TestQueryRag.py
python -m coverage report
```

### **RunTests.py Özellikleri**
- **Unit Tests**: Otomatik test dosyası bulma
- **Integration Tests**: Bileşen entegrasyonu testleri
- **Smoke Tests**: Temel fonksiyonalite testleri
- **Error Reporting**: Detaylı hata raporlama
- **Progress Tracking**: Test ilerleme takibi

## 🎯 **Test Coverage**

### **Hedef Coverage**
- **Line Coverage**: %90+
- **Branch Coverage**: %85+
- **Function Coverage**: %95+
- **Statement Coverage**: %90+

### **Coverage Raporu**
```bash
# Coverage kurulumu
pip install coverage

# Coverage çalıştırma
coverage run -m unittest TestQueryRag.py

# Coverage raporu
coverage report

# HTML raporu
coverage html
```

## 🧩 **Mock Sistemi**

### **Mock Stratejisi**
```python
# External dependencies mock
@patch('google.generativeai.GenerativeModel')
@patch('sentence_transformers.SentenceTransformer')

# File system mock
@patch('builtins.open', mock_open(read_data='test data'))

# Environment variables mock
@patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
```

### **Mock Örnekleri**

#### **1. API Mock**
```python
def test_gemini_api_mock(self):
    with patch('google.generativeai.GenerativeModel') as mock_gemini:
        mock_gemini.return_value.generate_content.return_value.text = "Test response"
        # Test implementation
```

#### **2. File System Mock**
```python
def test_file_operations_mock(self):
    with patch('builtins.open', mock_open(read_data='{"test": "data"}')):
        # Test implementation
```

#### **3. Environment Mock**
```python
def test_environment_variables_mock(self):
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
        # Test implementation
```

## 📊 **Test Metrikleri**

### **Performans Metrikleri**
- **Test Execution Time**: < 30 saniye
- **Memory Usage**: < 100MB
- **CPU Usage**: < 50%

### **Kalite Metrikleri**
- **Test Reliability**: %99+
- **False Positives**: < 1%
- **False Negatives**: < 1%

## 🔍 **Test Debugging**

### **Debug Modu**
```python
# Debug modunda test çalıştırma
python -m unittest TestQueryRag.py -v --debug

# PDB ile debug
python -m pdb -m unittest TestQueryRag.py
```

### **Log Seviyeleri**
```python
# Test sırasında log seviyesini ayarla
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Test Isolation**
```python
def setUp(self):
    """Her test öncesi temizlik"""
    # Test environment setup
    
def tearDown(self):
    """Her test sonrası temizlik"""
    # Test environment cleanup
```

## 🚨 **Test Hataları**

### **Yaygın Test Hataları**

#### **1. Import Errors**
```bash
# Çözüm: Environment kontrolü
conda activate yorum_env
python -c "import transformers; print('OK')"
```

#### **2. File Not Found**
```bash
# Çözüm: Test dosyalarını oluştur
python -c "import os; os.makedirs('test_data', exist_ok=True)"
```

#### **3. Mock Failures**
```python
# Çözüm: Mock path'ini kontrol et
@patch('module.path.to.target')
def test_method(self, mock_target):
    # Implementation
```

### **Test Troubleshooting**

#### **1. Test Çalışmıyor**
```bash
# Environment kontrolü
conda info --envs
conda activate yorum_env

# Paket kontrolü
pip list | grep transformers
```

#### **2. Mock Çalışmıyor**
```python
# Mock path'ini kontrol et
import module
print(module.__file__)
```

#### **3. Coverage Düşük**
```bash
# Coverage analizi
coverage report --show-missing
```

## 📈 **Test Geliştirme**

### **Yeni Test Ekleme**
1. **Test Sınıfı Oluştur**
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        # Setup code
        
    def test_feature_functionality(self):
        # Test implementation
        
    def tearDown(self):
        # Cleanup code
```

2. **Test Dosyasına Ekle**
```python
# TestQueryRag.py'ye ekle
class TestNewFeature(unittest.TestCase):
    # Implementation
```

3. **Test Runner'a Ekle**
```python
# RunTests.py'ye ekle
test_files = [
    'TestQueryRag.py',
    'TestNewFeature.py'  # Yeni test dosyası
]
```

### **Test Best Practices**
- ✅ **Arrange-Act-Assert** pattern kullan
- ✅ **Test isolation** sağla
- ✅ **Meaningful test names** kullan
- ✅ **Mock external dependencies**
- ✅ **Test data fixtures** kullan
- ✅ **Error scenarios** test et

## 🔄 **CI/CD Integration**

### **GitHub Actions**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python RunTests.py
```

### **Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: run-tests
        name: Run Tests
        entry: python RunTests.py
        language: system
        pass_filenames: false
```

## 📚 **Test Kaynakları**

### **Dokümantasyon**
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [coverage.py](https://coverage.readthedocs.io/)

### **Best Practices**
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Unit Testing](https://en.wikipedia.org/wiki/Unit_testing)
- [Integration Testing](https://en.wikipedia.org/wiki/Integration_testing)

## 🤝 **Test Katkıları**

### **Test Yazma Rehberi**
1. **Test senaryosunu belirle**
2. **Test verilerini hazırla**
3. **Mock'ları ayarla**
4. **Test'i yaz**
5. **Test'i çalıştır**
6. **Coverage'ı kontrol et**

### **Code Review Checklist**
- [ ] Test coverage yeterli mi?
- [ ] Mock'lar doğru mu?
- [ ] Test isolation sağlanmış mı?
- [ ] Error scenarios test edilmiş mi?
- [ ] Performance impact var mı? 