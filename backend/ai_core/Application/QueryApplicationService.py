"""
Query Application Service - Uygulama seviyesi servis

Bu modül, RAG sorgu işlemlerinin uygulama seviyesi koordinasyonunu
sağlar. Clean Architecture'ın Application Layer'ını temsil eder.

Sınıflar:
- IQueryApplicationService: Application Service interface'i
- QueryApplicationService: Gerçek implementasyon
- MockQueryApplicationService: Test için mock implementasyon

Özellikler:
- Use case orchestration
- Input validation
- Error handling & formatting
- Response formatting
- Service info
- Question suggestions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from DTOs.QueryDto import QueryRequestDTO, QueryResponseDTO, ErrorDTO
from UseCases.QueryUseCase import IQueryUseCase
from Exceptions import ValidationError, RAGServiceError, AIServiceError
from Logger import Logger


class IQueryApplicationService(ABC):
    """Query Application Service için interface"""
    
    @abstractmethod
    def query_product(self, question: str, **kwargs) -> Dict[str, Any]:
        """Ürün sorgusu yapar"""
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Servis bilgilerini döndürür"""
        pass


class QueryApplicationService(IQueryApplicationService):
    """Query Application Service implementasyonu"""
    
    def __init__(self, query_use_case: IQueryUseCase):
        self._query_use_case = query_use_case
    
    def query_product(self, question: str, **kwargs) -> Dict[str, Any]:
        """Ürün sorgusu yapar"""
        try:
            Logger.info(f"Application Service: Sorgu başlatılıyor: {question}")
            
            # Request DTO oluştur
            request = QueryRequestDTO(
                question=question,
                product_url=kwargs.get('product_url'),
                max_reviews=kwargs.get('max_reviews'),
                use_mocks=kwargs.get('use_mocks', False)
            )
            
            # Use case'i çalıştır
            response = self._query_use_case.execute(request)
            
            # Response'u dictionary'e çevir
            result = response.to_dict()
            result['success'] = True
            
            Logger.info(f"Application Service: Sorgu başarıyla tamamlandı")
            return result
            
        except ValidationError as e:
            Logger.error(f"Application Service: Validasyon hatası: {e}")
            error_dto = ErrorDTO(
                error_code="VALIDATION_ERROR",
                message=str(e),
                details="Input validasyonu başarısız"
            )
            return {
                'success': False,
                'error': error_dto.to_dict()
            }
            
        except (RAGServiceError, AIServiceError) as e:
            Logger.error(f"Application Service: İş mantığı hatası: {e}")
            error_dto = ErrorDTO(
                error_code="BUSINESS_ERROR",
                message=str(e),
                details="İş mantığı hatası"
            )
            return {
                'success': False,
                'error': error_dto.to_dict()
            }
            
        except Exception as e:
            Logger.error(f"Application Service: Beklenmeyen hata: {e}")
            error_dto = ErrorDTO(
                error_code="INTERNAL_ERROR",
                message="Beklenmeyen bir hata oluştu",
                details=str(e)
            )
            return {
                'success': False,
                'error': error_dto.to_dict()
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Servis bilgilerini döndürür"""
        return {
            'service_name': 'QueryApplicationService',
            'version': '1.0.0',
            'description': 'Ürün sorgu uygulama servisi',
            'use_case_type': type(self._query_use_case).__name__,
            'features': [
                'Product querying',
                'Input validation',
                'Error handling',
                'Response formatting'
            ]
        }
    
    def validate_question(self, question: str) -> Dict[str, Any]:
        """Soru validasyonu yapar"""
        try:
            request = QueryRequestDTO(question=question)
            errors = request.validate()
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'question_length': len(question) if question else 0
            }
            
        except Exception as e:
            Logger.error(f"Question validation error: {e}")
            return {
                'valid': False,
                'errors': [f"Validasyon hatası: {e}"],
                'question_length': 0
            }
    
    def get_question_suggestions(self, partial_question: str) -> Dict[str, Any]:
        """Soru önerileri döndürür"""
        suggestions = [
            "Bu ürün kaliteli mi?",
            "Hangi renk daha popüler?",
            "Fiyatına değer mi?",
            "Beden konusunda nasıl?",
            "Kargo hızlı mı?",
            "İade süreci nasıl?",
            "Kullanıcılar memnun mu?",
            "Hangi yaş grubuna uygun?"
        ]
        
        if partial_question:
            filtered_suggestions = [
                s for s in suggestions 
                if partial_question.lower() in s.lower()
            ]
        else:
            filtered_suggestions = suggestions
        
        return {
            'suggestions': filtered_suggestions[:5],  # En fazla 5 öneri
            'total_suggestions': len(filtered_suggestions)
        }


class MockQueryApplicationService(IQueryApplicationService):
    """Test için mock application service"""
    
    def __init__(self):
        self._mock_responses = {
            "Bu ürün kaliteli mi?": "Mock: Bu ürün genel olarak kaliteli görünüyor.",
            "Hangi renk daha popüler?": "Mock: Mavi renk daha popüler.",
            "Fiyatına değer mi?": "Mock: Fiyatına göre iyi bir ürün."
        }
    
    def query_product(self, question: str, **kwargs) -> Dict[str, Any]:
        """Mock ürün sorgusu"""
        mock_answer = self._mock_responses.get(
            question, 
            f"Mock yanıt: {question} sorusuna göre bu ürün genel olarak iyi."
        )
        
        return {
            'success': True,
            'answer': mock_answer,
            'question': question,
            'total_reviews': 3,
            'used_reviews': 3,
            'processing_time': 0.1,
            'timestamp': '2025-08-05T22:42:12.983',
            'metadata': {
                'use_mocks': True,
                'mock_response': True
            }
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Mock servis bilgileri"""
        return {
            'service_name': 'MockQueryApplicationService',
            'version': '1.0.0',
            'description': 'Mock ürün sorgu uygulama servisi',
            'use_case_type': 'MockQueryUseCase',
            'features': [
                'Mock product querying',
                'Mock input validation',
                'Mock error handling',
                'Mock response formatting'
            ]
        } 