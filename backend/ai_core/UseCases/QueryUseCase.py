"""
Query Use Case - Sorgu iş mantığı

Bu modül, RAG sorgu işlemlerinin iş mantığını kapsüller.
Clean Architecture'ın Use Case katmanını temsil eder ve
iş kurallarını uygular.

Sınıflar:
- IQueryUseCase: Use Case interface'i
- QueryUseCase: Gerçek implementasyon
- MockQueryUseCase: Test için mock implementasyon

Özellikler:
- Single Responsibility Principle
- Dependency Injection
- Error handling
- Performance monitoring
- Logging
"""

from abc import ABC, abstractmethod
from typing import Optional
import time
from datetime import datetime

from DTOs.QueryDto import QueryRequestDTO, QueryResponseDTO, ErrorDTO
from Services.RAGService import IRAGService
from Services.AIService import IAIService
from Repositories.ReviewRepository import IReviewRepository
from Exceptions import RAGServiceError, AIServiceError, ValidationError
from Logger import Logger


class IQueryUseCase(ABC):
    """Query Use Case için interface"""
    
    @abstractmethod
    def execute(self, request: QueryRequestDTO) -> QueryResponseDTO:
        """Use case'i çalıştırır"""
        pass


class QueryUseCase(IQueryUseCase):
    """Query Use Case implementasyonu"""
    
    def __init__(self, 
                 rag_service: IRAGService,
                 ai_service: IAIService,
                 review_repository: IReviewRepository):
        self._rag_service = rag_service
        self._ai_service = ai_service
        self._review_repository = review_repository
    
    def execute(self, request: QueryRequestDTO) -> QueryResponseDTO:
        """Use case'i çalıştırır"""
        start_time = time.time()
        
        try:
            Logger.info(f"Query Use Case başlatılıyor: {request.question}")
            
            # Input validasyonu
            validation_errors = request.validate()
            if validation_errors:
                raise ValidationError(f"Validasyon hataları: {', '.join(validation_errors)}")
            
            # RAG sorgusu yap
            answer = self._rag_service.query_rag(request.question)
            
            # İstatistikleri al
            review_stats = self._review_repository.get_review_statistics()
            total_reviews = review_stats.get('total_reviews', 0)
            
            # Processing time hesapla
            processing_time = time.time() - start_time
            
            # Metadata oluştur
            metadata = {
                'use_mocks': request.use_mocks,
                'max_reviews': request.max_reviews,
                'product_url': request.product_url,
                'review_stats': review_stats
            }
            
            # Response DTO oluştur
            response = QueryResponseDTO(
                answer=answer,
                question=request.question,
                total_reviews=total_reviews,
                used_reviews=total_reviews,  # Şimdilik tüm yorumları kullanıyoruz
                processing_time=processing_time,
                timestamp=datetime.now(),
                metadata=metadata
            )
            
            Logger.info(f"Query Use Case başarıyla tamamlandı: {processing_time:.2f}s")
            return response
            
        except (ValidationError, RAGServiceError, AIServiceError) as e:
            Logger.error(f"Query Use Case hatası: {e}")
            raise
        except Exception as e:
            Logger.error(f"Beklenmeyen hata: {e}")
            raise RAGServiceError(f"Query işlemi başarısız: {e}")


class MockQueryUseCase(IQueryUseCase):
    """Test için mock query use case"""
    
    def __init__(self):
        self._mock_responses = {
            "Bu ürün kaliteli mi?": "Mock yanıt: Bu ürün genel olarak kaliteli görünüyor.",
            "Hangi renk daha popüler?": "Mock yanıt: Mavi renk daha popüler.",
            "Fiyatına değer mi?": "Mock yanıt: Fiyatına göre iyi bir ürün."
        }
    
    def execute(self, request: QueryRequestDTO) -> QueryResponseDTO:
        """Mock use case çalıştırır"""
        start_time = time.time()
        
        # Mock yanıt
        mock_answer = self._mock_responses.get(
            request.question, 
            f"Mock yanıt: {request.question} sorusuna göre bu ürün genel olarak iyi."
        )
        
        processing_time = time.time() - start_time
        
        return QueryResponseDTO(
            answer=mock_answer,
            question=request.question,
            total_reviews=3,
            used_reviews=3,
            processing_time=processing_time,
            timestamp=datetime.now(),
            metadata={
                'use_mocks': True,
                'mock_response': True
            }
        ) 