"""
Query DTOs - Veri transfer objeleri

Bu modül, RAG sorgu sistemi için gerekli olan Data Transfer Objects'leri
tanımlar. Bu objeler, katmanlar arası veri transferini güvenli ve
tutarlı hale getirir.

Sınıflar:
- QueryRequestDTO: Sorgu isteği için DTO
- QueryResponseDTO: Sorgu yanıtı için DTO
- ReviewDTO: Yorum için DTO
- ProductStatsDTO: Ürün istatistikleri için DTO
- ErrorDTO: Hata için DTO
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class QueryRequestDTO:
    """Sorgu isteği için DTO"""
    question: str
    product_url: Optional[str] = None
    max_reviews: Optional[int] = None
    use_mocks: bool = False
    
    def validate(self) -> List[str]:
        """DTO validasyonu"""
        errors = []
        
        if not self.question or not self.question.strip():
            errors.append("Soru boş olamaz")
        
        if len(self.question.strip()) < 3:
            errors.append("Soru en az 3 karakter olmalıdır")
        
        if len(self.question.strip()) > 500:
            errors.append("Soru en fazla 500 karakter olabilir")
        
        if self.max_reviews is not None and (self.max_reviews < 1 or self.max_reviews > 1000):
            errors.append("Maksimum yorum sayısı 1-1000 arasında olmalıdır")
        
        return errors


@dataclass
class QueryResponseDTO:
    """Sorgu yanıtı için DTO"""
    answer: str
    question: str
    total_reviews: int
    used_reviews: int
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """DTO'yu dictionary'e çevirir"""
        return {
            'answer': self.answer,
            'question': self.question,
            'total_reviews': self.total_reviews,
            'used_reviews': self.used_reviews,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': self.metadata
        }


@dataclass
class ReviewDTO:
    """Yorum için DTO"""
    comment: str
    rate: Optional[int] = None
    user: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None
    
    def validate(self) -> List[str]:
        """DTO validasyonu"""
        errors = []
        
        if not self.comment or not self.comment.strip():
            errors.append("Yorum metni boş olamaz")
        
        if self.rate is not None and (self.rate < 1 or self.rate > 5):
            errors.append("Puan 1-5 arasında olmalıdır")
        
        return errors


@dataclass
class ProductStatsDTO:
    """Ürün istatistikleri için DTO"""
    average_rating: float
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    neutral_reviews: int
    rating_distribution: Dict[int, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """DTO'yu dictionary'e çevirir"""
        return {
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews,
            'positive_reviews': self.positive_reviews,
            'negative_reviews': self.negative_reviews,
            'neutral_reviews': self.neutral_reviews,
            'rating_distribution': self.rating_distribution
        }


@dataclass
class ErrorDTO:
    """Hata için DTO"""
    error_code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """DTO'yu dictionary'e çevirir"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        } 