import os
from typing import Optional
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    """Uygulama konfigürasyonu için merkezi sınıf"""
    
    # AI Model Konfigürasyonu
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
    
    # RAG Konfigürasyonu
    SENTENCE_TRANSFORMER_MODEL: str = os.getenv('SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2')
    TOP_K_CHUNKS: int = int(os.getenv('TOP_K_CHUNKS', '5'))
    CHUNK_MAX_LENGTH: int = int(os.getenv('CHUNK_MAX_LENGTH', '200'))
    
    # Dosya Yolları
    SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    INDEX_PATH: str = os.path.join(SCRIPT_DIR, 'index.faiss')
    CHUNKS_PATH: str = os.path.join(SCRIPT_DIR, 'chunks.json')
    REVIEWS_PATH: str = os.path.join(SCRIPT_DIR, 'reviews.json')
    
    # Timeout Ayarları
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    MODEL_LOAD_TIMEOUT: int = int(os.getenv('MODEL_LOAD_TIMEOUT', '60'))
    
    @classmethod
    def validate(cls) -> bool:
        """Konfigürasyon geçerliliğini kontrol eder"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True
    
    @classmethod
    def get_model_config(cls) -> dict:
        """AI model konfigürasyonunu döndürür"""
        return {
            'api_key': cls.GEMINI_API_KEY,
            'model_name': cls.GEMINI_MODEL,
            'timeout': cls.API_TIMEOUT
        }
    
    @classmethod
    def get_rag_config(cls) -> dict:
        """RAG sistemi konfigürasyonunu döndürür"""
        return {
            'sentence_transformer_model': cls.SENTENCE_TRANSFORMER_MODEL,
            'top_k_chunks': cls.TOP_K_CHUNKS,
            'chunk_max_length': cls.CHUNK_MAX_LENGTH,
            'index_path': cls.INDEX_PATH,
            'chunks_path': cls.CHUNKS_PATH
        } 