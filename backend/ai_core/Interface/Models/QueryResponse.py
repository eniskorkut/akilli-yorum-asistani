"""
Query Response Models - API seviyesi response modelleri

Bu modül, REST API için gerekli olan response modellerini tanımlar.
Pydantic kullanarak otomatik serialization ve validation sağlar.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class QueryResponse(BaseModel):
    """
    Sorgu yanıtı için API modeli
    
    Bu model, Application Layer'dan gelen yanıtları API formatına
    dönüştürür ve kullanıcıya iletir.
    """
    
    success: bool = Field(
        ...,
        description="İşlemin başarılı olup olmadığı",
        example=True
    )
    
    answer: Optional[str] = Field(
        None,
        description="AI'dan gelen yanıt",
        example="Bu ürün genel olarak kaliteli görünüyor..."
    )
    
    question: str = Field(
        ...,
        description="Orijinal soru",
        example="Bu ürün kaliteli mi?"
    )
    
    total_reviews: int = Field(
        ...,
        description="Toplam yorum sayısı",
        example=145
    )
    
    used_reviews: int = Field(
        ...,
        description="Kullanılan yorum sayısı",
        example=145
    )
    
    processing_time: float = Field(
        ...,
        description="İşlem süresi (saniye)",
        example=6.39
    )
    
    timestamp: datetime = Field(
        ...,
        description="İşlem zamanı",
        example="2025-08-05T22:50:49.519461"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Ek bilgiler",
        example={
            "use_mocks": False,
            "max_reviews": None,
            "product_url": None
        }
    )
    
    class Config:
        """Pydantic konfigürasyonu"""
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "Bu ürün genel olarak kaliteli görünüyor...",
                "question": "Bu ürün kaliteli mi?",
                "total_reviews": 145,
                "used_reviews": 145,
                "processing_time": 6.39,
                "timestamp": "2025-08-05T22:50:49.519461",
                "metadata": {
                    "use_mocks": False,
                    "max_reviews": None,
                    "product_url": None
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Hata yanıtı için API modeli
    
    Bu model, API seviyesinde oluşan hataları standart formatta
    kullanıcıya iletir.
    """
    
    success: bool = Field(
        False,
        description="İşlemin başarısız olduğunu belirtir",
        example=False
    )
    
    error: Dict[str, Any] = Field(
        ...,
        description="Hata detayları",
        example={
            "error_code": "VALIDATION_ERROR",
            "message": "Soru boş olamaz",
            "details": "Input validasyonu başarısız",
            "timestamp": "2025-08-05T22:50:49.519461"
        }
    )
    
    class Config:
        """Pydantic konfigürasyonu"""
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "error_code": "VALIDATION_ERROR",
                    "message": "Soru boş olamaz",
                    "details": "Input validasyonu başarısız",
                    "timestamp": "2025-08-05T22:50:49.519461"
                }
            }
        }


class BatchQueryResponse(BaseModel):
    """
    Toplu sorgu yanıtı için API modeli
    
    Birden fazla sorunun yanıtını tek bir response'da döndürür.
    """
    
    success: bool = Field(
        ...,
        description="İşlemin başarılı olup olmadığı",
        example=True
    )
    
    results: List[QueryResponse] = Field(
        ...,
        description="Sorgu sonuçları listesi",
        example=[]
    )
    
    total_questions: int = Field(
        ...,
        description="Toplam soru sayısı",
        example=3
    )
    
    successful_questions: int = Field(
        ...,
        description="Başarılı soru sayısı",
        example=3
    )
    
    failed_questions: int = Field(
        ...,
        description="Başarısız soru sayısı",
        example=0
    )
    
    total_processing_time: float = Field(
        ...,
        description="Toplam işlem süresi",
        example=18.5
    )
    
    timestamp: datetime = Field(
        ...,
        description="İşlem zamanı",
        example="2025-08-05T22:50:49.519461"
    )
    
    class Config:
        """Pydantic konfigürasyonu"""
        json_schema_extra = {
            "example": {
                "success": True,
                "results": [
                    {
                        "success": True,
                        "answer": "Bu ürün kaliteli görünüyor...",
                        "question": "Bu ürün kaliteli mi?",
                        "total_reviews": 145,
                        "used_reviews": 145,
                        "processing_time": 6.39,
                        "timestamp": "2025-08-05T22:50:49.519461",
                        "metadata": {}
                    }
                ],
                "total_questions": 3,
                "successful_questions": 3,
                "failed_questions": 0,
                "total_processing_time": 18.5,
                "timestamp": "2025-08-05T22:50:49.519461"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check yanıtı için API modeli
    
    API'nin sağlık durumunu kontrol etmek için kullanılır.
    """
    
    status: str = Field(
        ...,
        description="API durumu",
        example="healthy"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Kontrol zamanı",
        example="2025-08-05T22:50:49.519461"
    )
    
    version: str = Field(
        ...,
        description="API versiyonu",
        example="1.0.0"
    )
    
    uptime: float = Field(
        ...,
        description="Çalışma süresi (saniye)",
        example=3600.5
    )
    
    services: Dict[str, str] = Field(
        ...,
        description="Servis durumları",
        example={
            "ai_service": "healthy",
            "rag_service": "healthy",
            "database": "healthy"
        }
    )
    
    class Config:
        """Pydantic konfigürasyonu"""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-08-05T22:50:49.519461",
                "version": "1.0.0",
                "uptime": 3600.5,
                "services": {
                    "ai_service": "healthy",
                    "rag_service": "healthy",
                    "database": "healthy"
                }
            }
        } 