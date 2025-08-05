"""
Query Request Models - API seviyesi request modelleri

Bu modül, REST API için gerekli olan request modellerini tanımlar.
Pydantic kullanarak otomatik validation ve serialization sağlar.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class OutputFormat(str, Enum):
    """Çıktı formatı enum'u"""
    TEXT = "text"
    JSON = "json"


class QueryRequest(BaseModel):
    """
    Sorgu isteği için API modeli
    
    Bu model, kullanıcıdan gelen sorgu isteklerini validate eder
    ve Application Layer'a uygun formatta iletir.
    """
    
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Kullanıcının sormak istediği soru",
        example="Bu ürün kaliteli mi?"
    )
    
    product_url: Optional[str] = Field(
        None,
        description="Ürün URL'si (opsiyonel)",
        example="https://www.trendyol.com/urun/12345"
    )
    
    max_reviews: Optional[int] = Field(
        None,
        ge=1,
        le=1000,
        description="Maksimum yorum sayısı (1-1000 arası)",
        example=100
    )
    
    use_mocks: bool = Field(
        False,
        description="Mock servisleri kullan (test için)",
        example=False
    )
    
    output_format: OutputFormat = Field(
        OutputFormat.TEXT,
        description="Çıktı formatı",
        example=OutputFormat.TEXT
    )
    
    @validator('question')
    def validate_question(cls, v):
        """Soru validasyonu"""
        if not v or not v.strip():
            raise ValueError('Soru boş olamaz')
        
        if len(v.strip()) < 3:
            raise ValueError('Soru en az 3 karakter olmalıdır')
        
        if len(v.strip()) > 500:
            raise ValueError('Soru en fazla 500 karakter olabilir')
        
        return v.strip()
    
    @validator('product_url')
    def validate_product_url(cls, v):
        """Ürün URL validasyonu"""
        if v is None:
            return v
        
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Geçerli bir URL olmalıdır')
        
        return v
    
    class Config:
        """Pydantic konfigürasyonu"""
        json_schema_extra = {
            "example": {
                "question": "Bu ürün kaliteli mi?",
                "product_url": "https://www.trendyol.com/urun/12345",
                "max_reviews": 100,
                "use_mocks": False,
                "output_format": "text"
            }
        }


class BatchQueryRequest(BaseModel):
    """
    Toplu sorgu isteği için API modeli
    
    Birden fazla soruyu aynı anda işlemek için kullanılır.
    """
    
    questions: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="Sorgu listesi (maksimum 10 soru)",
        example=["Bu ürün kaliteli mi?", "Hangi renk daha popüler?"]
    )
    
    product_url: Optional[str] = Field(
        None,
        description="Ürün URL'si (tüm sorular için geçerli)",
        example="https://www.trendyol.com/urun/12345"
    )
    
    max_reviews: Optional[int] = Field(
        None,
        ge=1,
        le=1000,
        description="Maksimum yorum sayısı",
        example=100
    )
    
    use_mocks: bool = Field(
        False,
        description="Mock servisleri kullan",
        example=False
    )
    
    @validator('questions')
    def validate_questions(cls, v):
        """Soru listesi validasyonu"""
        if not v:
            raise ValueError('En az bir soru olmalıdır')
        
        if len(v) > 10:
            raise ValueError('Maksimum 10 soru gönderilebilir')
        
        # Her soruyu validate et
        for i, question in enumerate(v):
            if not question or not question.strip():
                raise ValueError(f'{i+1}. soru boş olamaz')
            
            if len(question.strip()) < 3:
                raise ValueError(f'{i+1}. soru en az 3 karakter olmalıdır')
            
            if len(question.strip()) > 500:
                raise ValueError(f'{i+1}. soru en fazla 500 karakter olabilir')
        
        return [q.strip() for q in v]
    
    class Config:
        """Pydantic konfigürasyonu"""
        json_schema_extra = {
            "example": {
                "questions": [
                    "Bu ürün kaliteli mi?",
                    "Hangi renk daha popüler?",
                    "Fiyatına değer mi?"
                ],
                "product_url": "https://www.trendyol.com/urun/12345",
                "max_reviews": 100,
                "use_mocks": False
            }
        } 