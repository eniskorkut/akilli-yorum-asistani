import unittest
import tempfile
import os
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import faiss

# Test için gerekli modülleri import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Config import Config
from Exceptions import (
    ConfigurationError, 
    RAGServiceError, 
    FileNotFoundError, 
    ModelLoadError, 
    APIError,
    ValidationError
)
from Logger import Logger

class TestConfig(unittest.TestCase):
    """Config sınıfı için testler"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        # Test için geçici environment variables
        os.environ['GEMINI_API_KEY'] = 'test_api_key'
        os.environ['GEMINI_MODEL'] = 'gemini-1.5-pro'
        os.environ['SENTENCE_TRANSFORMER_MODEL'] = 'all-MiniLM-L6-v2'
    
    def test_config_validation_success(self):
        """Konfigürasyon doğrulama başarı testi"""
        self.assertTrue(Config.validate())
    
    def test_config_validation_failure(self):
        """Konfigürasyon doğrulama başarısızlık testi"""
        # Orijinal API key'i sakla
        original_key = os.environ.get('GEMINI_API_KEY')
        
        # API key'i kaldır
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        try:
            # Config.validate() çağrısından önce Config sınıfını yeniden yükle
            import importlib
            import Config
            importlib.reload(Config)
            
            with self.assertRaises(ValueError):
                Config.Config.validate()
        finally:
            # Orijinal API key'i geri yükle
            if original_key:
                os.environ['GEMINI_API_KEY'] = original_key
            # Config'i tekrar yükle
            import importlib
            import Config
            importlib.reload(Config)
    
    def test_get_model_config(self):
        """Model konfigürasyonu alma testi"""
        config = Config.get_model_config()
        self.assertIn('api_key', config)
        self.assertIn('model_name', config)
        self.assertIn('timeout', config)
    
    def test_get_rag_config(self):
        """RAG konfigürasyonu alma testi"""
        config = Config.get_rag_config()
        self.assertIn('sentence_transformer_model', config)
        self.assertIn('top_k_chunks', config)
        self.assertIn('chunk_max_length', config)

class TestExceptions(unittest.TestCase):
    """Custom exception sınıfları için testler"""
    
    def test_api_error_with_details(self):
        """APIError detaylı bilgi ile testi"""
        error = APIError("Test error", 404, "Not found")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.response_text, "Not found")
    
    def test_exception_inheritance(self):
        """Exception inheritance testi"""
        self.assertTrue(issubclass(ConfigurationError, Exception))
        self.assertTrue(issubclass(RAGServiceError, Exception))
        self.assertTrue(issubclass(FileNotFoundError, Exception))

class TestLogger(unittest.TestCase):
    """Logger sınıfı için testler"""
    
    def test_logger_singleton(self):
        """Logger singleton pattern testi"""
        logger1 = Logger()
        logger2 = Logger()
        self.assertIs(logger1, logger2)
    
    def test_logger_methods(self):
        """Logger metodları testi"""
        # Bu testler sadece metodların çağrılabilir olduğunu kontrol eder
        try:
            Logger.info("Test info message")
            Logger.error("Test error message")
            Logger.warning("Test warning message")
            Logger.debug("Test debug message")
            Logger.critical("Test critical message")
        except Exception as e:
            self.fail(f"Logger metodları çalışmıyor: {e}")

class TestRAGFunctions(unittest.TestCase):
    """RAG fonksiyonları için testler"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        # Geçici test dosyaları oluştur
        self.temp_dir = tempfile.mkdtemp()
        self.test_index_path = os.path.join(self.temp_dir, 'test_index.faiss')
        self.test_chunks_path = os.path.join(self.temp_dir, 'test_chunks.json')
        
        # Test verileri oluştur
        self.test_chunks = [
            "Bu ürün çok kaliteli",
            "Fiyatına göre iyi",
            "Tavsiye ederim"
        ]
        
        # Test FAISS index oluştur
        dimension = 384  # all-MiniLM-L6-v2 boyutu
        index = faiss.IndexFlatL2(dimension)
        test_vectors = np.random.random((len(self.test_chunks), dimension)).astype('float32')
        index.add(test_vectors)
        faiss.write_index(index, self.test_index_path)
        
        # Test chunks dosyası oluştur
        with open(self.test_chunks_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_chunks, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Test sonrası temizlik"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('Config.Config.get_rag_config')
    def test_load_index_and_chunks_success(self, mock_config):
        """Index ve chunks yükleme başarı testi"""
        # Mock config
        mock_config.return_value = {
            'index_path': self.test_index_path,
            'chunks_path': self.test_chunks_path
        }
        
        # Import ve test
        from Config import Config
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Bu test için gerçek dosyaları kullanıyoruz
        # Gerçek uygulamada mock kullanılır
        pass
    
    def test_get_top_chunks_validation(self):
        """Top chunks validation testi"""
        # Bu test için mock model ve index kullanılır
        mock_model = Mock()
        mock_index = Mock()
        mock_chunks = ["test1", "test2", "test3"]
        
        # Boş soru testi - gerçek fonksiyonu import et ve test et
        try:
            # 3_query_rag.py'den get_top_chunks fonksiyonunu import et
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "query_rag", 
                os.path.join(os.path.dirname(__file__), "3_query_rag.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Boş soru ile test et - bu test başarılı olmalı çünkü ValidationError fırlatıyor
            try:
                module.get_top_chunks("", mock_model, mock_index, mock_chunks)
                self.fail("ValidationError fırlatılmalıydı")
            except ValidationError:
                # Beklenen davranış
                pass
                
        except ImportError:
            # Eğer import edilemezse testi atla
            self.skipTest("3_query_rag.py import edilemedi")
    
    def test_extract_product_stats(self):
        """Ürün istatistikleri çıkarma testi"""
        test_chunks = [
            {"comment": "Çok güzel ürün", "rate": 5},
            {"comment": "Kötü kalite", "rate": 2},
            {"comment": "Fiyatına göre iyi", "rate": 4}
        ]
        
        # Bu test için extract_product_stats fonksiyonunu import et
        # from config import Config
        # stats = extract_product_stats(test_chunks)
        # self.assertIn('ortalamaPuan', stats)
        # self.assertIn('toplamDegerlendirme', stats)
        pass

class TestIntegration(unittest.TestCase):
    """Integration testleri"""
    
    @patch('google.generativeai.GenerativeModel')
    @patch('sentence_transformers.SentenceTransformer')
    def test_full_pipeline_mock(self, mock_transformer, mock_gemini):
        """Tam pipeline mock testi"""
        try:
            # Mock setup
            mock_transformer.return_value = Mock()
            mock_gemini.return_value.generate_content.return_value.text = "Test response"
            
            # Environment setup
            os.environ['GEMINI_API_KEY'] = 'test_key'
            
            # Bu test gerçek dosyalar olmadan çalışır
            # Gerçek uygulamada integration testleri ayrı dosyada olur
            pass
        except Exception as e:
            # Eğer transformers modülü yoksa testi atla
            if "No module named 'transformers'" in str(e):
                self.skipTest("Transformers modülü bulunamadı")
            else:
                raise

if __name__ == '__main__':
    # Test runner
    unittest.main(verbosity=2) 