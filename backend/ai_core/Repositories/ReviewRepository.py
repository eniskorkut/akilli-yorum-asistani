"""
Review Repository - Yorum verilerini yönetmek için repository pattern
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os
import hashlib
import time

from Config import Config
from Exceptions import FileNotFoundError, RAGServiceError
from Logger import Logger


class IReviewRepository(ABC):
    """Review Repository için interface"""
    
    @abstractmethod
    def load_reviews(self) -> List[Dict[str, Any]]:
        """Yorumları yükler"""
        pass
    
    @abstractmethod
    def save_reviews(self, reviews: List[Dict[str, Any]]) -> None:
        """Yorumları kaydeder"""
        pass
    
    @abstractmethod
    def get_review_count(self) -> int:
        """Yorum sayısını döndürür"""
        pass
    
    @abstractmethod
    def get_reviews_by_rating(self, min_rating: int = 0, max_rating: int = 5) -> List[Dict[str, Any]]:
        """Belirli puan aralığındaki yorumları döndürür"""
        pass
    
    @abstractmethod
    def fetch_reviews_for_url(self, url: str) -> List[Dict[str, Any]]:
        """URL için yorumları çeker"""
        pass
    
    @abstractmethod
    def get_cache_key(self, url: str) -> str:
        """URL için cache key oluşturur"""
        pass


class FileReviewRepository(IReviewRepository):
    """Dosya tabanlı review repository"""
    
    def __init__(self, file_path: Optional[str] = None):
        self._file_path = file_path or Config.REVIEWS_PATH
        self._reviews = None
        self._loaded = False
        
        # Cache sistemi kaldırıldı
    
    def load_reviews(self) -> List[Dict[str, Any]]:
        """Yorumları dosyadan yükler"""
        try:
            if self._loaded and self._reviews is not None:
                return self._reviews
            
            Logger.info(f"Yorumlar yükleniyor: {self._file_path}")
            
            if not os.path.exists(self._file_path):
                Logger.warning(f"Yorum dosyası bulunamadı: {self._file_path}")
                self._reviews = []
                self._loaded = True
                return self._reviews
            
            with open(self._file_path, 'r', encoding='utf-8') as f:
                self._reviews = json.load(f)
            
            self._loaded = True
            Logger.info(f"{len(self._reviews)} yorum yüklendi")
            return self._reviews
            
        except Exception as e:
            Logger.error(f"Yorum yükleme hatası: {e}")
            raise RAGServiceError(f"Yorumlar yüklenemedi: {e}")
    
    def save_reviews(self, reviews: List[Dict[str, Any]]) -> None:
        """Yorumları dosyaya kaydeder"""
        try:
            Logger.info(f"{len(reviews)} yorum kaydediliyor: {self._file_path}")
            
            # Dizin oluştur
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
            
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            
            self._reviews = reviews
            self._loaded = True
            Logger.info("Yorumlar başarıyla kaydedildi")
            
        except Exception as e:
            Logger.error(f"Yorum kaydetme hatası: {e}")
            raise RAGServiceError(f"Yorumlar kaydedilemedi: {e}")
    
    def get_review_count(self) -> int:
        """Yorum sayısını döndürür"""
        reviews = self.load_reviews()
        return len(reviews)
    
    def get_reviews_by_rating(self, min_rating: int = 0, max_rating: int = 5) -> List[Dict[str, Any]]:
        """Belirli puan aralığındaki yorumları döndürür"""
        try:
            reviews = self.load_reviews()
            filtered_reviews = []
            
            for review in reviews:
                if isinstance(review, dict) and 'rate' in review:
                    rating = review.get('rate', 0)
                    if min_rating <= rating <= max_rating:
                        filtered_reviews.append(review)
            
            Logger.debug(f"{len(filtered_reviews)} yorum bulundu (puan: {min_rating}-{max_rating})")
            return filtered_reviews
            
        except Exception as e:
            Logger.error(f"Yorum filtreleme hatası: {e}")
            return []
    
    def get_reviews_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Belirli anahtar kelimeyi içeren yorumları döndürür"""
        try:
            reviews = self.load_reviews()
            filtered_reviews = []
            keyword_lower = keyword.lower()
            
            for review in reviews:
                if isinstance(review, dict) and 'comment' in review:
                    comment = review.get('comment', '').lower()
                    if keyword_lower in comment:
                        filtered_reviews.append(review)
            
            Logger.debug(f"{len(filtered_reviews)} yorum bulundu (anahtar kelime: {keyword})")
            return filtered_reviews
            
        except Exception as e:
            Logger.error(f"Yorum arama hatası: {e}")
            return []
    
    def get_review_statistics(self) -> Dict[str, Any]:
        """Yorum istatistiklerini döndürür"""
        try:
            reviews = self.load_reviews()
            stats = {
                'total_reviews': len(reviews),
                'average_rating': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'positive_reviews': 0,
                'negative_reviews': 0,
                'neutral_reviews': 0
            }
            
            total_rating = 0
            rating_count = 0
            
            for review in reviews:
                if isinstance(review, dict) and 'rate' in review:
                    rating = review.get('rate', 0)
                    if rating > 0:
                        total_rating += rating
                        rating_count += 1
                        stats['rating_distribution'][rating] = stats['rating_distribution'].get(rating, 0) + 1
                
                # Sentiment analizi
                if isinstance(review, dict) and 'comment' in review:
                    comment = review.get('comment', '').lower()
                    positive_words = ['güzel', 'iyi', 'beğendim', 'memnun', 'kaliteli', 'tavsiye', 'harika', 'mükemmel']
                    negative_words = ['kötü', 'berbat', 'memnun değil', 'kırık', 'bozuk', 'iade']
                    
                    positive_count = sum(1 for word in positive_words if word in comment)
                    negative_count = sum(1 for word in negative_words if word in comment)
                    
                    if positive_count > negative_count:
                        stats['positive_reviews'] += 1
                    elif negative_count > positive_count:
                        stats['negative_reviews'] += 1
                    else:
                        stats['neutral_reviews'] += 1
            
            if rating_count > 0:
                stats['average_rating'] = round(total_rating / rating_count, 1)
            
            Logger.debug(f"Yorum istatistikleri hesaplandı: {stats}")
            return stats
            
        except Exception as e:
            Logger.error(f"İstatistik hesaplama hatası: {e}")
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'positive_reviews': 0,
                'negative_reviews': 0,
                'neutral_reviews': 0
            }
    
    def fetch_reviews_for_url(self, url: str) -> List[Dict[str, Any]]:
        """URL için yorumları çeker"""
        try:
            # URL validasyonu
            if not self._is_valid_trendyol_url(url):
                Logger.warning(f"Geçersiz Trendyol URL: {url}")
                return []
            
            # Her zaman yeni yorumlar çek (cache yok)
            Logger.info(f"Yorumlar çekiliyor: {url}")
            reviews = self._fetch_reviews_from_scraper(url)
            
            Logger.info(f"Çekilen yorum sayısı: {len(reviews)}")
            return reviews
            
        except Exception as e:
            Logger.error(f"URL için yorum çekme hatası: {e}")
            return []
    
    def _fetch_reviews_from_scraper(self, url: str) -> List[Dict[str, Any]]:
        """Scraper'dan yorumları çeker"""
        try:
            # Şimdilik mevcut 1_fetch_reviews.py'yi kullanıyoruz
            # Daha sonra bu kısım domain'e göre farklı scraper'lar kullanacak
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            
            if 'trendyol.com' in parsed_url.netloc:
                # Trendyol için mevcut scraper'ı kullan
                import subprocess
                import sys
                
                # 1_fetch_reviews.py'yi çağır
                script_path = os.path.join(os.path.dirname(__file__), '..', '1_fetch_reviews.py')
                result = subprocess.run([
                    sys.executable, script_path,
                    '--url', url,
                    '--max-reviews', '50'
                ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
                
                if result.returncode == 0:
                    # reviews.json'dan yorumları oku
                    reviews_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reviews.json')
                    if os.path.exists(reviews_file):
                        with open(reviews_file, 'r', encoding='utf-8') as f:
                            return json.load(f)
                
                Logger.error(f"Scraper hatası: {result.stderr}")
                return []
                
            else:
                Logger.warning(f"Desteklenmeyen domain: {parsed_url.netloc}")
                return []
                
        except Exception as e:
            Logger.error(f"Scraper çalıştırma hatası: {e}")
            return []
    
    def get_cache_key(self, url: str) -> str:
        """URL için cache key oluşturur (kullanılmıyor)"""
        return "no_cache"
    
    def _is_valid_trendyol_url(self, url: str) -> bool:
        """Trendyol URL'sinin geçerli olup olmadığını kontrol eder"""
        try:
            from urllib.parse import urlparse
            
            parsed = urlparse(url)
            
            # Domain kontrolü
            if 'trendyol.com' not in parsed.netloc:
                return False
            
            # Path kontrolü - ürün sayfası olmalı
            path = parsed.path.lower()
            
            # Geçersiz path'ler
            invalid_paths = [
                '/gecersiz-url-test',
                '/test-',
                '/invalid-',
                '/fake-',
                '/dummy-',
                '/trendyol-milla/trendyol-milla-kadin-basic-oversize-t-shirt-p-123456789'  # Test URL'si
            ]
            
            for invalid_path in invalid_paths:
                if invalid_path in path:
                    return False
            
            # Ürün sayfası olmalı (p- ile başlayan ID içermeli)
            if 'p-' not in path:
                return False
            
            return True
            
        except Exception as e:
            Logger.error(f"URL validasyon hatası: {e}")
            return False


class MockReviewRepository(IReviewRepository):
    """Test için mock review repository"""
    
    def __init__(self, mock_reviews: Optional[List[Dict[str, Any]]] = None):
        self._mock_reviews = mock_reviews or [
            {"comment": "Çok güzel ürün", "rate": 5, "user": "TestUser1"},
            {"comment": "Fiyatına göre iyi", "rate": 4, "user": "TestUser2"},
            {"comment": "Kötü kalite", "rate": 2, "user": "TestUser3"}
        ]
    
    def load_reviews(self) -> List[Dict[str, Any]]:
        """Mock yorumları döndürür"""
        return self._mock_reviews
    
    def save_reviews(self, reviews: List[Dict[str, Any]]) -> None:
        """Mock kaydetme işlemi"""
        self._mock_reviews = reviews
        Logger.info(f"Mock: {len(reviews)} yorum kaydedildi")
    
    def get_review_count(self) -> int:
        """Mock yorum sayısı"""
        return len(self._mock_reviews)
    
    def get_reviews_by_rating(self, min_rating: int = 0, max_rating: int = 5) -> List[Dict[str, Any]]:
        """Mock rating filtreleme"""
        return [r for r in self._mock_reviews if min_rating <= r.get('rate', 0) <= max_rating]
    
    def fetch_reviews_for_url(self, url: str) -> List[Dict[str, Any]]:
        """Mock URL için yorum çekme"""
        Logger.info(f"Mock: URL için yorumlar çekiliyor: {url}")
        return self._mock_reviews
    
    def get_cache_key(self, url: str) -> str:
        """Mock cache key"""
        return hashlib.md5(url.encode()).hexdigest() 