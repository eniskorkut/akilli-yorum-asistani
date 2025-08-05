class AIServiceError(Exception):
    """AI servis hataları için base exception"""
    pass

class ConfigurationError(Exception):
    """Konfigürasyon hataları için exception"""
    pass

class RAGServiceError(Exception):
    """RAG servis hataları için exception"""
    pass

class FileNotFoundError(Exception):
    """Dosya bulunamama hataları için exception"""
    pass

class ModelLoadError(Exception):
    """Model yükleme hataları için exception"""
    pass

class APIError(Exception):
    """API çağrı hataları için exception"""
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class ValidationError(Exception):
    """Veri doğrulama hataları için exception"""
    pass 