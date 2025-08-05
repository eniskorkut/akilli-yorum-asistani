"""
Health Controller - API sağlık kontrolü endpoint'leri

Bu modül, API'nin sağlık durumunu kontrol etmek için
endpoint'ler sağlar.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import time
import psutil
import os

from Interface.Models.QueryResponse import HealthResponse
# from Interface.Middleware.Authentication import require_api_key_header
# from Interface.Middleware.RateLimiting import require_rate_limiting
from DI import configure_container
from Logger import Logger


class HealthController:
    """
    API sağlık kontrolü için controller
    
    Bu sınıf, API'nin sağlık durumunu kontrol etmek ve
    sistem bilgilerini döndürmek için endpoint'ler sağlar.
    """
    
    def __init__(self):
        """Controller'ı başlatır"""
        self.router = APIRouter(prefix="/api/v1/health", tags=["Health"])
        self.start_time = time.time()
        self._setup_routes()
        Logger.info("Health Controller başlatıldı")
    
    def _setup_routes(self):
        """Route'ları ayarlar"""
        
        @self.router.get("/", response_model=HealthResponse)
        async def health_check():
            """
            Temel sağlık kontrolü endpoint'i
            
            Bu endpoint, API'nin temel sağlık durumunu kontrol eder.
            
            Args:
                api_key: API key
                rate_limit: Rate limiting kontrolü
                
            Returns:
                HealthResponse: Sağlık durumu
            """
            try:
                Logger.info("Sağlık kontrolü isteği alındı")
                
                # Sistem bilgilerini al
                uptime = time.time() - self.start_time
                memory_usage = psutil.virtual_memory().percent
                cpu_usage = psutil.cpu_percent(interval=1)
                
                # Servis durumlarını kontrol et
                services_status = self._check_services_health()
                
                # Genel durumu belirle
                overall_status = "healthy"
                if memory_usage > 90 or cpu_usage > 90:
                    overall_status = "warning"
                
                if any(status == "unhealthy" for status in services_status.values()):
                    overall_status = "unhealthy"
                
                response = HealthResponse(
                    status=overall_status,
                    timestamp=time.time(),
                    version="1.0.0",
                    uptime=uptime,
                    services=services_status
                )
                
                Logger.info(f"Sağlık kontrolü tamamlandı: {overall_status}")
                return response
                
            except Exception as e:
                Logger.error(f"Sağlık kontrolü hatası: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Sağlık kontrolü başarısız",
                        "message": str(e)
                    }
                )
        
        @self.router.get("/detailed")
        async def detailed_health_check():
            """
            Detaylı sağlık kontrolü endpoint'i
            
            Bu endpoint, API'nin detaylı sağlık durumunu kontrol eder
            ve sistem kaynaklarını raporlar.
            
            Args:
                api_key: API key
                rate_limit: Rate limiting kontrolü
                
            Returns:
                Dict: Detaylı sağlık durumu
            """
            try:
                Logger.info("Detaylı sağlık kontrolü isteği alındı")
                
                # Sistem kaynakları
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                cpu_count = psutil.cpu_count()
                
                # Process bilgileri
                process = psutil.Process(os.getpid())
                process_memory = process.memory_info()
                
                # Servis durumları
                services_status = self._check_services_health()
                
                # Rate limiting bilgileri
                rate_limit_info = self._get_rate_limit_info()
                
                detailed_response = {
                    "status": "healthy",
                    "timestamp": time.time(),
                    "version": "1.0.0",
                    "uptime": time.time() - self.start_time,
                    
                    "system": {
                        "cpu": {
                            "usage_percent": psutil.cpu_percent(interval=1),
                            "count": cpu_count,
                            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                        },
                        "memory": {
                            "total": memory.total,
                            "available": memory.available,
                            "used": memory.used,
                            "percent": memory.percent
                        },
                        "disk": {
                            "total": disk.total,
                            "used": disk.used,
                            "free": disk.free,
                            "percent": (disk.used / disk.total) * 100
                        }
                    },
                    
                    "process": {
                        "pid": process.pid,
                        "memory_rss": process_memory.rss,
                        "memory_vms": process_memory.vms,
                        "cpu_percent": process.cpu_percent(),
                        "num_threads": process.num_threads()
                    },
                    
                    "services": services_status,
                    "rate_limiting": rate_limit_info,
                    
                    "environment": {
                        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                        "platform": os.sys.platform,
                        "working_directory": os.getcwd()
                    }
                }
                
                Logger.info("Detaylı sağlık kontrolü tamamlandı")
                return detailed_response
                
            except Exception as e:
                Logger.error(f"Detaylı sağlık kontrolü hatası: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Detaylı sağlık kontrolü başarısız",
                        "message": str(e)
                    }
                )
        
        @self.router.get("/ready")
        async def readiness_check():
            """
            Readiness kontrolü endpoint'i
            
            Bu endpoint, API'nin istek almaya hazır olup olmadığını kontrol eder.
            Kubernetes ve container orchestration için kullanılır.
            
            Args:
                api_key: API key
                rate_limit: Rate limiting kontrolü
                
            Returns:
                Dict: Readiness durumu
            """
            try:
                Logger.info("Readiness kontrolü isteği alındı")
                
                # Kritik servisleri kontrol et
                services_status = self._check_services_health()
                critical_services = ["ai_service", "rag_service", "database"]
                
                ready = True
                failed_services = []
                
                for service in critical_services:
                    if services_status.get(service) != "healthy":
                        ready = False
                        failed_services.append(service)
                
                response = {
                    "ready": ready,
                    "timestamp": time.time(),
                    "failed_services": failed_services,
                    "services_status": services_status
                }
                
                if ready:
                    Logger.info("Readiness kontrolü: Hazır")
                else:
                    Logger.warning(f"Readiness kontrolü: Hazır değil - {failed_services}")
                
                return response
                
            except Exception as e:
                Logger.error(f"Readiness kontrolü hatası: {e}")
                return {
                    "ready": False,
                    "timestamp": time.time(),
                    "error": str(e)
                }
    
    def _check_services_health(self) -> Dict[str, str]:
        """
        Servis sağlık durumlarını kontrol eder
        
        Returns:
            Dict[str, str]: Servis durumları
        """
        services_status = {}
        
        try:
            # DI Container'ı kontrol et
            container = configure_container(use_mocks=False)
            services_status["di_container"] = "healthy"
            
            # AI Service kontrolü
            try:
                ai_service = container.get_ai_service()
                services_status["ai_service"] = "healthy"
            except Exception as e:
                Logger.warning(f"AI Service sağlık kontrolü başarısız: {e}")
                services_status["ai_service"] = "unhealthy"
            
            # RAG Service kontrolü
            try:
                rag_service = container.get_rag_service()
                services_status["rag_service"] = "healthy"
            except Exception as e:
                Logger.warning(f"RAG Service sağlık kontrolü başarısız: {e}")
                services_status["rag_service"] = "unhealthy"
            
            # Review Repository kontrolü
            try:
                review_repo = container.get_review_repository()
                services_status["review_repository"] = "healthy"
            except Exception as e:
                Logger.warning(f"Review Repository sağlık kontrolü başarısız: {e}")
                services_status["review_repository"] = "unhealthy"
            
            # Application Service kontrolü
            try:
                app_service = container.get_query_application_service()
                services_status["application_service"] = "healthy"
            except Exception as e:
                Logger.warning(f"Application Service sağlık kontrolü başarısız: {e}")
                services_status["application_service"] = "unhealthy"
            
        except Exception as e:
            Logger.error(f"Servis sağlık kontrolü hatası: {e}")
            services_status["di_container"] = "unhealthy"
        
        return services_status
    
    def _get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Rate limiting bilgilerini alır
        
        Returns:
            Dict: Rate limiting bilgileri
        """
        try:
            from Interface.Middleware.RateLimiting import get_rate_limiting_middleware
            rate_limiting = get_rate_limiting_middleware()
            
            # Genel istatistikler
            total_clients = len(rate_limiting.request_history)
            total_requests = sum(len(requests) for requests in rate_limiting.request_history.values())
            
            return {
                "total_clients": total_clients,
                "total_requests": total_requests,
                "limits": {
                    "per_minute": rate_limiting.requests_per_minute,
                    "per_hour": rate_limiting.requests_per_hour,
                    "per_day": rate_limiting.requests_per_day
                }
            }
        except Exception as e:
            Logger.warning(f"Rate limiting bilgileri alınamadı: {e}")
            return {"error": str(e)}


# Global controller instance
health_controller = HealthController()


def get_health_controller() -> HealthController:
    """
    Health controller instance'ını döndürür
    
    Returns:
        HealthController: Controller instance'ı
    """
    return health_controller 