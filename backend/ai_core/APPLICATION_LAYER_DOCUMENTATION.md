# Application Layer Dokümantasyonu

## Genel Bakış

Bu dokümantasyon, **Adım 3: Use Cases & Application Layer** refactoring çalışmasını detaylandırır. Bu adımda Clean Architecture'ın Application Layer'ını oluşturduk.

## Mimari Yapı

### Katmanlar
```
Application Layer
├── DTOs/           # Data Transfer Objects
├── UseCases/       # İş mantığı katmanı
├── Application/    # Uygulama seviyesi servisler
└── DI/            # Dependency Injection (güncellendi)
```

## Bileşenler

### 1. DTOs (Data Transfer Objects)

#### `QueryDto.py`
**Amaç:** Veri transferi için yapılandırılmış objeler

**Sınıflar:**
- `QueryRequestDTO`: Sorgu isteği için DTO
- `QueryResponseDTO`: Sorgu yanıtı için DTO
- `ReviewDTO`: Yorum için DTO
- `ProductStatsDTO`: Ürün istatistikleri için DTO
- `ErrorDTO`: Hata için DTO

**Özellikler:**
- Built-in validasyon
- Dictionary dönüşümü
- Type safety
- Immutable data structures

**Örnek Kullanım:**
```python
request = QueryRequestDTO(
    question="Bu ürün kaliteli mi?",
    product_url="https://example.com",
    max_reviews=100
)

errors = request.validate()
if errors:
    print(f"Validasyon hataları: {errors}")
```

### 2. Use Cases

#### `QueryUseCase.py`
**Amaç:** İş mantığını kapsülleyen katman

**Sınıflar:**
- `IQueryUseCase`: Interface
- `QueryUseCase`: Gerçek implementasyon
- `MockQueryUseCase`: Test için mock

**Özellikler:**
- Single Responsibility Principle
- Dependency Injection
- Error handling
- Performance monitoring
- Logging

**Örnek Kullanım:**
```python
use_case = QueryUseCase(rag_service, ai_service, review_repository)
response = use_case.execute(request)
```

### 3. Application Services

#### `QueryApplicationService.py`
**Amaç:** Uygulama seviyesi koordinasyon

**Sınıflar:**
- `IQueryApplicationService`: Interface
- `QueryApplicationService`: Gerçek implementasyon
- `MockQueryApplicationService`: Test için mock

**Özellikler:**
- Use case orchestration
- Input validation
- Error handling & formatting
- Response formatting
- Service info

**Örnek Kullanım:**
```python
app_service = QueryApplicationService(use_case)
result = app_service.query_product("Bu ürün kaliteli mi?")
```

## Dependency Injection Güncellemeleri

### Container Genişletmeleri
- Use Case registration
- Application Service registration
- Mock/Production switching
- Service info tracking

### Yeni Methodlar
```python
container.get_query_use_case()
container.get_query_application_service()
container.is_configured()
```

## Test Sistemi

### Test Dosyası: `TestApplicationLayer.py`

**Test Kategorileri:**
1. **DTO Tests**: Validasyon ve dönüşüm testleri
2. **Use Case Tests**: İş mantığı testleri
3. **Application Service Tests**: Uygulama seviyesi testleri
4. **Container Integration Tests**: DI entegrasyon testleri
5. **Full Integration Tests**: Tam pipeline testleri

**Test Coverage:**
- DTO validasyonları
- Use case execution
- Application service methods
- Error handling
- Mock services
- Container configuration

## Kullanım Örnekleri

### 1. Basit Sorgu
```bash
python QueryRagApplication.py --question "Bu ürün kaliteli mi?"
```

### 2. Mock Servislerle
```bash
python QueryRagApplication.py --question "Bu ürün kaliteli mi?" --use-mocks
```

### 3. JSON Formatında
```bash
python QueryRagApplication.py --question "Bu ürün kaliteli mi?" --output-format json
```

### 4. Programatik Kullanım
```python
from DI import configure_container

# Container'ı konfigüre et
container = configure_container(use_mocks=False)

# Application service'i al
app_service = container.get_query_application_service()

# Sorgu yap
result = app_service.query_product("Bu ürün kaliteli mi?")
print(result['answer'])
```

## Performans Metrikleri

### Mock Servisler
- **Response Time**: ~0.1s
- **Memory Usage**: Minimal
- **CPU Usage**: Minimal

### Gerçek Servisler
- **Response Time**: ~6-8s (AI processing)
- **Memory Usage**: ~500MB (model loading)
- **CPU Usage**: Moderate (AI inference)

## Güvenlik

### Input Validation
- Soru uzunluğu kontrolü (3-500 karakter)
- Max reviews limiti (1-1000)
- URL format kontrolü
- XSS prevention

### Error Handling
- Graceful degradation
- Detailed error messages
- Logging & monitoring
- No sensitive data exposure

## Geliştirme Rehberi

### Yeni Use Case Ekleme
1. `UseCases/` klasöründe yeni dosya oluştur
2. Interface ve implementasyon yaz
3. Mock sınıfı ekle
4. Container'a kaydet
5. Test yaz

### Yeni DTO Ekleme
1. `DTOs/` klasöründe yeni dosya oluştur
2. Validasyon methodları ekle
3. `to_dict()` methodu ekle
4. `__init__.py`'a import ekle

### Yeni Application Service Ekleme
1. `Application/` klasöründe yeni dosya oluştur
2. Interface ve implementasyon yaz
3. Error handling ekle
4. Container'a kaydet
5. Test yaz

## Troubleshooting

### Yaygın Hatalar

#### 1. Import Errors
```bash
# Çözüm: Python path'i kontrol et
export PYTHONPATH="${PYTHONPATH}:/path/to/ai_core"
```

#### 2. Configuration Errors
```bash
# Çözüm: Environment variables'ları kontrol et
echo $GEMINI_API_KEY
```

#### 3. Mock Service Issues
```bash
# Çözüm: Container'ı reset et
python -c "from DI import reset_container; reset_container()"
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Gelecek Geliştirmeler

### Planlanan Özellikler
1. **Caching Layer**: Redis/Memory caching
2. **Rate Limiting**: API rate limiting
3. **Metrics**: Prometheus metrics
4. **Health Checks**: Service health monitoring
5. **Circuit Breaker**: Fault tolerance

### Optimizasyonlar
1. **Async Processing**: Async/await support
2. **Batch Processing**: Multiple queries
3. **Streaming**: Real-time responses
4. **Compression**: Response compression

## Changelog

### v1.0.0 (2025-08-05)
- DTOs oluşturuldu
- Use Cases implementasyonu
- Application Services
- DI Container güncellemeleri
- Comprehensive test suite
- PascalCase naming convention
- Documentation

## Katkıda Bulunma

1. Fork yap
2. Feature branch oluştur
3. Değişiklikleri commit et
4. Testleri çalıştır
5. Pull request gönder

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 