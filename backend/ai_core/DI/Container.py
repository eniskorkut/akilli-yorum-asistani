"""
Dependency Injection Container - Service'leri yönetmek için DI container
"""

from typing import Dict, Any, Optional, Type
import os

from Config import Config
from Exceptions import ConfigurationError
from Logger import Logger
from Services.AIService import IAIService, GeminiAIService, MockAIService
from Services.RAGService import IRAGService, RAGService, MockRAGService
from Repositories.ReviewRepository import IReviewRepository, FileReviewRepository, MockReviewRepository
from UseCases.QueryUseCase import IQueryUseCase, QueryUseCase, MockQueryUseCase
from Application.QueryApplicationService import IQueryApplicationService, QueryApplicationService, MockQueryApplicationService


class Container:
    """Dependency Injection Container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._configured = False
    
    def configure(self, use_mocks: bool = False) -> None:
        """Container'ı konfigüre eder"""
        try:
            Logger.info("DI Container konfigüre ediliyor...")
            
            # Environment kontrolü
            if use_mocks or os.getenv('USE_MOCKS', 'false').lower() == 'true':
                self._configure_mocks()
            else:
                self._configure_production()
            
            self._configured = True
            Logger.info("DI Container başarıyla konfigüre edildi")
            
        except Exception as e:
            Logger.error(f"DI Container konfigürasyon hatası: {e}")
            raise ConfigurationError(f"DI Container konfigüre edilemedi: {e}")
    
    def _configure_production(self) -> None:
        """Production konfigürasyonu"""
        Logger.info("Production konfigürasyonu uygulanıyor...")
        
        # AI Service
        self._services['ai_service'] = GeminiAIService()
        
        # Review Repository
        self._services['review_repository'] = FileReviewRepository()
        
        # RAG Service
        self._services['rag_service'] = RAGService(
            ai_service=self._services['ai_service']
        )
        
        # Query Use Case
        self._services['query_use_case'] = QueryUseCase(
            rag_service=self._services['rag_service'],
            ai_service=self._services['ai_service'],
            review_repository=self._services['review_repository']
        )
        
        # Query Application Service
        self._services['query_application_service'] = QueryApplicationService(
            query_use_case=self._services['query_use_case']
        )
    
    def _configure_mocks(self) -> None:
        """Mock konfigürasyonu"""
        Logger.info("Mock konfigürasyonu uygulanıyor...")
        
        # Mock AI Service
        mock_ai = MockAIService({
            "Bu ürün kaliteli mi?": "Mock yanıt: Bu ürün genel olarak kaliteli görünüyor.",
            "Hangi renk daha popüler?": "Mock yanıt: Mavi renk daha popüler."
        })
        
        # Mock Review Repository
        mock_reviews = [
            {"comment": "Çok güzel ürün", "rate": 5, "user": "TestUser1"},
            {"comment": "Fiyatına göre iyi", "rate": 4, "user": "TestUser2"},
            {"comment": "Kötü kalite", "rate": 2, "user": "TestUser3"}
        ]
        mock_repo = MockReviewRepository(mock_reviews)
        
        # Mock RAG Service
        mock_rag = MockRAGService()
        
        # Mock Query Use Case
        mock_use_case = MockQueryUseCase()
        
        # Mock Query Application Service
        mock_app_service = MockQueryApplicationService()
        
        self._services['ai_service'] = mock_ai
        self._services['review_repository'] = mock_repo
        self._services['rag_service'] = mock_rag
        self._services['query_use_case'] = mock_use_case
        self._services['query_application_service'] = mock_app_service
    
    def get(self, service_name: str) -> Any:
        """Service'i döndürür"""
        if not self._configured:
            self.configure()
        
        if service_name not in self._services:
            raise ConfigurationError(f"Service bulunamadı: {service_name}")
        
        return self._services[service_name]
    
    def get_ai_service(self) -> IAIService:
        """AI Service'i döndürür"""
        return self.get('ai_service')
    
    def get_rag_service(self) -> IRAGService:
        """RAG Service'i döndürür"""
        return self.get('rag_service')
    
    def get_review_repository(self) -> IReviewRepository:
        """Review Repository'yi döndürür"""
        return self.get('review_repository')
    
    def get_query_use_case(self) -> IQueryUseCase:
        """Query Use Case'i döndürür"""
        return self.get('query_use_case')
    
    def get_query_application_service(self) -> IQueryApplicationService:
        """Query Application Service'i döndürür"""
        return self.get('query_application_service')
    
    def register_singleton(self, service_name: str, instance: Any) -> None:
        """Singleton service kaydeder"""
        self._singletons[service_name] = instance
        Logger.debug(f"Singleton service kaydedildi: {service_name}")
    
    def get_singleton(self, service_name: str) -> Any:
        """Singleton service'i döndürür"""
        if service_name not in self._singletons:
            raise ConfigurationError(f"Singleton service bulunamadı: {service_name}")
        
        return self._singletons[service_name]
    
    def register_service(self, service_name: str, service_class: Type, **kwargs) -> None:
        """Yeni service kaydeder"""
        try:
            instance = service_class(**kwargs)
            self._services[service_name] = instance
            Logger.debug(f"Service kaydedildi: {service_name}")
        except Exception as e:
            Logger.error(f"Service kaydetme hatası: {e}")
            raise ConfigurationError(f"Service kaydedilemedi: {service_name}")
    
    def has_service(self, service_name: str) -> bool:
        """Service'in varlığını kontrol eder"""
        return service_name in self._services
    
    def get_all_services(self) -> Dict[str, Any]:
        """Tüm service'leri döndürür"""
        return self._services.copy()
    
    def clear(self) -> None:
        """Container'ı temizler"""
        self._services.clear()
        self._singletons.clear()
        self._configured = False
        Logger.info("DI Container temizlendi")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Service bilgilerini döndürür"""
        info = {
            'configured': self._configured,
            'total_services': len(self._services),
            'total_singletons': len(self._singletons),
            'services': list(self._services.keys()),
            'singletons': list(self._singletons.keys())
        }
        
        # Her service'in tipini ekle
        service_types = {}
        for name, service in self._services.items():
            service_types[name] = type(service).__name__
        
        info['service_types'] = service_types
        return info
    
    def is_configured(self) -> bool:
        """Container'ın konfigüre edilip edilmediğini kontrol eder"""
        return self._configured


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Global container instance'ını döndürür"""
    global _container
    if _container is None:
        _container = Container()
    return _container


def configure_container(use_mocks: bool = False) -> Container:
    """Container'ı konfigüre eder ve döndürür"""
    container = get_container()
    container.configure(use_mocks=use_mocks)
    return container


def reset_container() -> None:
    """Global container'ı sıfırlar"""
    global _container
    if _container:
        _container.clear()
    _container = None 