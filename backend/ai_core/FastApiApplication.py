"""
FastApiApplication.py - Ana FastAPI uygulaması

Bu dosya, RAG sorgu sistemi için ana FastAPI uygulamasını oluşturur.
Tüm endpoint'leri, middleware'leri ve konfigürasyonu bir araya getirir.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import time
import os
from typing import Dict, Any

from Interface.Controllers.QueryController import get_query_controller
from Interface.Controllers.HealthController import get_health_controller
# from Interface.Middleware.Authentication import get_auth_middleware
# from Interface.Middleware.RateLimiting import get_rate_limiting_middleware
from Config import Config
from Logger import Logger


class FastApiApplication:
    """
    Ana FastAPI uygulaması
    
    Bu sınıf, tüm API bileşenlerini bir araya getirir ve
    production-ready bir FastAPI uygulaması oluşturur.
    """
    
    def __init__(self):
        """Uygulamayı başlatır"""
        self.app = FastAPI(
            title="Akıllı Yorum Asistanı API",
            description="""
            Akıllı Yorum Asistanı API - E-ticaret ürün yorumlarını analiz eden AI destekli API.
            
            Bu API, ürün yorumlarını analiz ederek kullanıcı sorularına AI destekli yanıtlar verir.
            
            ## Özellikler
            
            * **RAG (Retrieval-Augmented Generation)** - Yorumlardan bilgi çıkarımı
            * **Multi-site Support** - Birden fazla e-ticaret sitesi desteği
            * **Real-time Analysis** - Gerçek zamanlı yorum analizi
            * **Batch Processing** - Toplu sorgu işleme
            * **Rate Limiting** - İstek sınırlama
            * **Authentication** - API key tabanlı kimlik doğrulama
            
            ## Kullanım
            
            API key ile kimlik doğrulama yaparak sorgularınızı gönderebilirsiniz.
            
            ```bash
            curl -X POST "http://localhost:8000/api/v1/query/" \\
                 -H "x-api-key: your-api-key" \\
                 -H "Content-Type: application/json" \\
                 -d '{"question": "Bu ürün kaliteli mi?"}'
            ```
            """,
            version="1.0.0",
            contact={
                "name": "Akıllı Yorum Asistanı",
                "email": "support@akilliyorum.com"
            },
            license_info={
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            },
            docs_url=None,  # Custom docs
            redoc_url="/redoc"
        )
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_exception_handlers()
        self._setup_openapi()
        
        Logger.info("FastAPI uygulaması başlatıldı")
    
    def _setup_middleware(self):
        """Middleware'leri ayarlar"""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Production'da spesifik domain'ler belirtilmeli
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Production'da spesifik host'lar belirtilmeli
        )
        
        # Request timing middleware
        @self.app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            """İstek işleme süresini hesaplar"""
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """İstekleri loglar"""
            start_time = time.time()
            
            # İstek bilgilerini logla
            Logger.info(f"HTTP {request.method} {request.url.path} - {request.client.host}")
            
            response = await call_next(request)
            
            # Yanıt bilgilerini logla
            process_time = time.time() - start_time
            Logger.info(f"HTTP {response.status_code} - {process_time:.3f}s")
            
            return response
    
    def _setup_routes(self):
        """Route'ları ayarlar"""
        
        # Ana sayfa
        @self.app.get("/", tags=["Root"])
        async def root():
            """
            Ana sayfa
            
            API'nin ana sayfası ve genel bilgiler.
            """
            return {
                "message": "Akıllı Yorum Asistanı API'ye Hoş Geldiniz",
                "version": "1.0.0",
                "status": "running",
                "documentation": "/docs",
                "health_check": "/api/v1/health/"
            }
        
        # API bilgileri
        @self.app.get("/api/info", tags=["API Info"])
        async def api_info():
            """
            API bilgileri
            
            API hakkında detaylı bilgiler.
            """
            return {
                "name": "Akıllı Yorum Asistanı API",
                "version": "1.0.0",
                "description": "E-ticaret ürün yorumlarını analiz eden AI destekli API",
                "features": [
                    "RAG (Retrieval-Augmented Generation)",
                    "Multi-site Support",
                    "Real-time Analysis",
                    "Batch Processing",
                    "Rate Limiting",
                    "Authentication"
                ],
                "endpoints": {
                    "query": "/api/v1/query/",
                    "batch_query": "/api/v1/query/batch",
                    "suggestions": "/api/v1/query/suggestions",
                    "health": "/api/v1/health/",
                    "health_detailed": "/api/v1/health/detailed",
                    "readiness": "/api/v1/health/ready"
                },
                "authentication": "API Key (x-api-key header)",
                "rate_limiting": {
                    "per_minute": 60,
                    "per_hour": 1000,
                    "per_day": 10000
                }
            }
        
        # Controller'ları ekle
        query_controller = get_query_controller()
        health_controller = get_health_controller()
        
        self.app.include_router(query_controller.router)
        self.app.include_router(health_controller.router)
    
    def _setup_exception_handlers(self):
        """Exception handler'ları ayarlar"""
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            """HTTP exception'ları işler"""
            Logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "error_code": f"HTTP_{exc.status_code}",
                        "message": exc.detail,
                        "timestamp": time.time()
                    }
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Genel exception'ları işler"""
            Logger.error(f"General Exception: {exc}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "error_code": "INTERNAL_ERROR",
                        "message": "Beklenmeyen bir hata oluştu",
                        "details": str(exc),
                        "timestamp": time.time()
                    }
                }
            )
    
    def _setup_openapi(self):
        """OpenAPI dokümantasyonunu özelleştirir"""
        
        def custom_openapi():
            """Özelleştirilmiş OpenAPI şeması"""
            if self.app.openapi_schema:
                return self.app.openapi_schema
            
            openapi_schema = get_openapi(
                title="Akıllı Yorum Asistanı API",
                version="1.0.0",
                description="""
                Akıllı Yorum Asistanı API - E-ticaret ürün yorumlarını analiz eden AI destekli API.
                
                Bu API, ürün yorumlarını analiz ederek kullanıcı sorularına AI destekli yanıtlar verir.
                """,
                routes=self.app.routes
            )
            
            # Security şeması ekle
            openapi_schema["components"]["securitySchemes"] = {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "x-api-key"
                }
            }
            
            # Global security ekle
            openapi_schema["security"] = [{"ApiKeyAuth": []}]
            
            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema
        
        self.app.openapi = custom_openapi
        
        # Custom docs endpoint
        @self.app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            """Özelleştirilmiş Swagger UI"""
            return get_swagger_ui_html(
                openapi_url=self.app.openapi_url,
                title="Akıllı Yorum Asistanı API - Dokümantasyon",
                swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css"
            )
    
    def get_app(self) -> FastAPI:
        """
        FastAPI uygulamasını döndürür
        
        Returns:
            FastAPI: Uygulama instance'ı
        """
        return self.app


# Global application instance
fastapi_app = FastApiApplication()


def get_fastapi_app() -> FastAPI:
    """
    FastAPI uygulaması instance'ını döndürür
    
    Returns:
        FastAPI: Uygulama instance'ı
    """
    return fastapi_app.get_app()


# Uvicorn için app instance'ı
app = get_fastapi_app()


if __name__ == "__main__":
    import uvicorn
    
    # Konfigürasyonu doğrula
    try:
        Config.validate()
        Logger.info("Konfigürasyon doğrulandı")
    except Exception as e:
        Logger.critical(f"Konfigürasyon hatası: {e}")
        exit(1)
    
    # Uygulamayı başlat
    Logger.info("FastAPI uygulaması başlatılıyor...")
    
    uvicorn.run(
        "FastApiApplication:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Reload'ı kapatarak hızlandır
        log_level="info"
    ) 