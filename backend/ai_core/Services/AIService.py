"""
AI Service - Gemini API ile etkileşim için service layer
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import google.generativeai as genai

from Config import Config
from Exceptions import AIServiceError, ConfigurationError, APIError
from Logger import Logger


class IAIService(ABC):
    """AI Service için interface"""
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Prompt'a göre yanıt üretir"""
        pass
    
    @abstractmethod
    def configure(self, api_key: str, model_name: str) -> None:
        """AI servisini konfigüre eder"""
        pass


class GeminiAIService(IAIService):
    """Gemini AI Service implementasyonu"""
    
    def __init__(self):
        self._model = None
        self._configured = False
        self._config = Config.get_model_config()
    
    def configure(self, api_key: Optional[str] = None, model_name: Optional[str] = None) -> None:
        """Gemini AI servisini konfigüre eder"""
        try:
            Logger.info("Gemini AI Service konfigüre ediliyor...")
            
            # API key kontrolü
            api_key = api_key or self._config.get('api_key')
            if not api_key:
                raise ConfigurationError("Gemini API anahtarı bulunamadı")
            
            # Model adı kontrolü
            model_name = model_name or self._config.get('model_name')
            if not model_name:
                raise ConfigurationError("Model adı bulunamadı")
            
            # Gemini'yi konfigüre et
            genai.configure(api_key=api_key)
            
            # Model'i yükle
            self._model = genai.GenerativeModel(model_name)
            self._configured = True
            
            Logger.info(f"Gemini AI Service başarıyla konfigüre edildi: {model_name}")
            
        except Exception as e:
            Logger.error(f"Gemini AI Service konfigürasyon hatası: {e}")
            raise ConfigurationError(f"Gemini AI Service konfigüre edilemedi: {e}")
    
    def generate_response(self, prompt: str) -> str:
        """Prompt'a göre yanıt üretir"""
        try:
            if not self._configured or not self._model:
                self.configure()
            
            if not prompt or not prompt.strip():
                raise AIServiceError("Prompt boş olamaz")
            
            Logger.debug(f"AI yanıtı isteniyor, prompt uzunluğu: {len(prompt)}")
            
            # Gemini'den yanıt al
            response = self._model.generate_content(prompt)
            
            if not response or not response.text:
                raise APIError("Gemini API'den boş yanıt alındı")
            
            Logger.info("Gemini AI'den yanıt başarıyla alındı")
            return response.text.strip()
            
        except Exception as e:
            Logger.error(f"AI yanıt üretme hatası: {e}")
            if isinstance(e, (AIServiceError, APIError)):
                raise
            raise AIServiceError(f"AI yanıtı üretilemedi: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Model bilgilerini döndürür"""
        return {
            'configured': self._configured,
            'model_name': self._config.get('model_name'),
            'api_key_set': bool(self._config.get('api_key'))
        }


class MockAIService(IAIService):
    """Test için mock AI service"""
    
    def __init__(self, mock_responses: Optional[Dict[str, str]] = None):
        self._mock_responses = mock_responses or {}
        self._configured = True
    
    def configure(self, api_key: Optional[str] = None, model_name: Optional[str] = None) -> None:
        """Mock service için konfigürasyon (her zaman başarılı)"""
        self._configured = True
        Logger.info("Mock AI Service konfigüre edildi")
    
    def generate_response(self, prompt: str) -> str:
        """Mock yanıt üretir"""
        if not prompt or not prompt.strip():
            raise AIServiceError("Prompt boş olamaz")
        
        # Eğer prompt için özel yanıt varsa onu kullan
        if prompt in self._mock_responses:
            return self._mock_responses[prompt]
        
        # Varsayılan mock yanıt
        return f"Mock AI yanıtı: {prompt[:50]}..."
    
    def add_mock_response(self, prompt: str, response: str) -> None:
        """Mock yanıt ekler"""
        self._mock_responses[prompt] = response 