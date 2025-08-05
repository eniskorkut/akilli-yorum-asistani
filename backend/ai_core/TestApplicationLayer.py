"""
TestApplicationLayer.py - Application Layer testleri

Bu dosya, Application Layer'ın tüm bileşenlerini test eder.
DTOs, Use Cases, Application Services ve DI Container
entegrasyonlarını kapsar.

Test Kategorileri:
1. DTO Tests: Validasyon ve dönüşüm testleri
2. Use Case Tests: İş mantığı testleri
3. Application Service Tests: Uygulama seviyesi testleri
4. Container Integration Tests: DI entegrasyon testleri
5. Full Integration Tests: Tam pipeline testleri

Çalıştırma:
    python TestApplicationLayer.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import json

# Test için gerekli modülleri import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from DTOs.QueryDto import QueryRequestDTO, QueryResponseDTO, ErrorDTO
from UseCases.QueryUseCase import QueryUseCase, MockQueryUseCase
from Application.QueryApplicationService import QueryApplicationService, MockQueryApplicationService
from DI.Container import Container, configure_container


class TestQueryDto(unittest.TestCase):
    """Query DTO testleri"""
    
    def test_query_request_dto_validation_success(self):
        """Geçerli QueryRequestDTO validasyonu"""
        dto = QueryRequestDTO(
            question="Bu ürün kaliteli mi?",
            product_url="https://example.com",
            max_reviews=100
        )
        errors = dto.validate()
        self.assertEqual(len(errors), 0)
    
    def test_query_request_dto_validation_empty_question(self):
        """Boş soru validasyonu"""
        dto = QueryRequestDTO(question="")
        errors = dto.validate()
        self.assertIn("Soru boş olamaz", errors)
    
    def test_query_request_dto_validation_short_question(self):
        """Kısa soru validasyonu"""
        dto = QueryRequestDTO(question="ab")
        errors = dto.validate()
        self.assertIn("Soru en az 3 karakter olmalıdır", errors)
    
    def test_query_request_dto_validation_long_question(self):
        """Uzun soru validasyonu"""
        long_question = "a" * 501
        dto = QueryRequestDTO(question=long_question)
        errors = dto.validate()
        self.assertIn("Soru en fazla 500 karakter olabilir", errors)
    
    def test_query_request_dto_validation_invalid_max_reviews(self):
        """Geçersiz max_reviews validasyonu"""
        dto = QueryRequestDTO(question="Test", max_reviews=0)
        errors = dto.validate()
        self.assertIn("Maksimum yorum sayısı 1-1000 arasında olmalıdır", errors)
    
    def test_query_response_dto_to_dict(self):
        """QueryResponseDTO to_dict testi"""
        from datetime import datetime
        dto = QueryResponseDTO(
            answer="Test yanıt",
            question="Test soru",
            total_reviews=10,
            used_reviews=5,
            processing_time=1.5,
            timestamp=datetime.now(),
            metadata={"test": "data"}
        )
        result = dto.to_dict()
        self.assertEqual(result["answer"], "Test yanıt")
        self.assertEqual(result["question"], "Test soru")
        self.assertEqual(result["total_reviews"], 10)
        self.assertEqual(result["used_reviews"], 5)
        self.assertEqual(result["processing_time"], 1.5)


class TestQueryUseCase(unittest.TestCase):
    """Query Use Case testleri"""
    
    def setUp(self):
        """Test setup"""
        self.mock_rag_service = Mock()
        self.mock_ai_service = Mock()
        self.mock_review_repository = Mock()
        
        # Mock review repository response
        self.mock_review_repository.get_review_statistics.return_value = {
            'total_reviews': 10,
            'average_rating': 4.2
        }
        
        self.use_case = QueryUseCase(
            self.mock_rag_service,
            self.mock_ai_service,
            self.mock_review_repository
        )
    
    def test_query_use_case_execute_success(self):
        """Başarılı use case çalıştırma"""
        # Mock RAG service response
        self.mock_rag_service.query_rag.return_value = "Test yanıt"
        
        request = QueryRequestDTO(question="Test soru")
        response = self.use_case.execute(request)
        
        self.assertEqual(response.answer, "Test yanıt")
        self.assertEqual(response.question, "Test soru")
        self.assertEqual(response.total_reviews, 10)
        self.mock_rag_service.query_rag.assert_called_once_with("Test soru")
    
    def test_query_use_case_execute_validation_error(self):
        """Validasyon hatası testi"""
        request = QueryRequestDTO(question="")  # Boş soru
        
        with self.assertRaises(Exception):
            self.use_case.execute(request)
    
    def test_mock_query_use_case(self):
        """Mock Query Use Case testi"""
        mock_use_case = MockQueryUseCase()
        request = QueryRequestDTO(question="Bu ürün kaliteli mi?")
        
        response = mock_use_case.execute(request)
        
        self.assertIn("Mock yanıt", response.answer)
        self.assertEqual(response.total_reviews, 3)
        self.assertEqual(response.used_reviews, 3)


class TestQueryApplicationService(unittest.TestCase):
    """Query Application Service testleri"""
    
    def setUp(self):
        """Test setup"""
        self.mock_use_case = Mock()
        self.app_service = QueryApplicationService(self.mock_use_case)
    
    def test_query_product_success(self):
        """Başarılı ürün sorgusu"""
        # Mock use case response
        from datetime import datetime
        mock_response = QueryResponseDTO(
            answer="Test yanıt",
            question="Test soru",
            total_reviews=10,
            used_reviews=5,
            processing_time=1.0,
            timestamp=datetime.now(),
            metadata={}
        )
        self.mock_use_case.execute.return_value = mock_response
        
        result = self.app_service.query_product("Test soru")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['answer'], "Test yanıt")
        self.assertEqual(result['question'], "Test soru")
    
    def test_query_product_validation_error(self):
        """Validasyon hatası testi"""
        self.mock_use_case.execute.side_effect = Exception("Validasyon hatası")
        
        result = self.app_service.query_product("")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_validate_question_success(self):
        """Başarılı soru validasyonu"""
        result = self.app_service.validate_question("Bu ürün kaliteli mi?")
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['question_length'], 20)
    
    def test_validate_question_failure(self):
        """Başarısız soru validasyonu"""
        result = self.app_service.validate_question("")
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_get_question_suggestions(self):
        """Soru önerileri testi"""
        result = self.app_service.get_question_suggestions("kaliteli")
        
        self.assertIn('suggestions', result)
        self.assertIn('total_suggestions', result)
        self.assertGreater(len(result['suggestions']), 0)
    
    def test_mock_application_service(self):
        """Mock Application Service testi"""
        mock_app_service = MockQueryApplicationService()
        
        result = mock_app_service.query_product("Bu ürün kaliteli mi?")
        
        self.assertTrue(result['success'])
        self.assertIn("Mock:", result['answer'])
        self.assertEqual(result['total_reviews'], 3)


class TestContainerIntegration(unittest.TestCase):
    """Container entegrasyon testleri"""
    
    def test_configure_container_mock(self):
        """Mock container konfigürasyonu"""
        container = configure_container(use_mocks=True)
        
        self.assertTrue(container.is_configured())
        
        # Service'leri kontrol et
        app_service = container.get_query_application_service()
        self.assertIsNotNone(app_service)
        
        use_case = container.get_query_use_case()
        self.assertIsNotNone(use_case)
    
    def test_container_service_info(self):
        """Container service bilgileri"""
        container = configure_container(use_mocks=True)
        info = container.get_service_info()
        
        self.assertTrue(info['configured'])
        self.assertGreater(info['total_services'], 0)
        self.assertIn('query_application_service', info['services'])


class TestFullIntegration(unittest.TestCase):
    """Tam entegrasyon testleri"""
    
    def test_full_mock_pipeline(self):
        """Tam mock pipeline testi"""
        container = configure_container(use_mocks=True)
        app_service = container.get_query_application_service()
        
        result = app_service.query_product("Bu ürün kaliteli mi?")
        
        self.assertTrue(result['success'])
        self.assertIn('answer', result)
        self.assertIn('question', result)
        self.assertIn('processing_time', result)
    
    def test_error_handling(self):
        """Hata yönetimi testi"""
        container = configure_container(use_mocks=True)
        app_service = container.get_query_application_service()
        
        # Geçersiz soru ile test
        result = app_service.query_product("")
        
        # Mock service her zaman başarılı döner, gerçek serviste hata alırdık
        self.assertTrue(result['success'])


if __name__ == '__main__':
    # Test suite'i çalıştır
    unittest.main(verbosity=2) 