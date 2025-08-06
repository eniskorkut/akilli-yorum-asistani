"""
URL Fetcher Service - Dinamik URL çekme servisi

Bu servis, kullanıcının şu anki sayfa URL'sini almak ve
ürün yorumlarını çekmek için kullanılır.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlparse
import re

from Logger import Logger
from Exceptions import ValidationError


class IURLFetcherService(ABC):
    """URL Fetcher Service için interface"""
    
    @abstractmethod
    def get_current_url(self) -> str:
        """Şu anki URL'yi döndürür"""
        pass
    
    @abstractmethod
    def extract_product_info(self, url: str) -> Dict[str, Any]:
        """URL'den ürün bilgilerini çıkarır"""
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """URL'nin geçerli olup olmadığını kontrol eder"""
        pass


class URLFetcherService(IURLFetcherService):
    """URL Fetcher Service implementasyonu"""
    
    def __init__(self):
        self.supported_domains = [
            'trendyol.com',
            'www.trendyol.com',
            'hepsiburada.com',
            'www.hepsiburada.com'
        ]
    
    def get_current_url(self) -> str:
        """Şu anki URL'yi döndürür (Chrome extension'dan gelecek)"""
        # Bu method Chrome extension'dan gelen URL'yi kullanacak
        # Şimdilik None döndürüyoruz, extension'dan gelecek
        return None
    
    def extract_product_info(self, url: str) -> Dict[str, Any]:
        """URL'den ürün bilgilerini çıkarır"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            if 'trendyol.com' in domain:
                return self._extract_trendyol_info(url)
            elif 'hepsiburada.com' in domain:
                return self._extract_hepsiburada_info(url)
            else:
                raise ValidationError(f"Desteklenmeyen domain: {domain}")
                
        except Exception as e:
            Logger.error(f"URL ayrıştırma hatası: {e}")
            raise ValidationError(f"URL ayrıştırılamadı: {e}")
    
    def _extract_trendyol_info(self, url: str) -> Dict[str, Any]:
        """Trendyol URL'sinden ürün bilgilerini çıkarır"""
        try:
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            query_params = dict(parsed_url.parse_qsl())
            
            # Product slug'ı çıkar
            product_slug = path
            
            # Merchant ID'yi çıkar
            merchant_id = query_params.get('merchantId')
            
            return {
                'domain': 'trendyol.com',
                'product_slug': product_slug,
                'merchant_id': merchant_id,
                'full_url': url
            }
            
        except Exception as e:
            Logger.error(f"Trendyol URL ayrıştırma hatası: {e}")
            raise ValidationError(f"Trendyol URL ayrıştırılamadı: {e}")
    
    def _extract_hepsiburada_info(self, url: str) -> Dict[str, Any]:
        """Hepsiburada URL'sinden ürün bilgilerini çıkarır"""
        try:
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            
            # Hepsiburada için product ID'yi çıkar
            # Örnek: /urun/urun-adi-p-123456
            product_id_match = re.search(r'-p-(\d+)(?:$|\?)', path)
            product_id = product_id_match.group(1) if product_id_match else None
            
            return {
                'domain': 'hepsiburada.com',
                'product_id': product_id,
                'product_path': path,
                'full_url': url
            }
            
        except Exception as e:
            Logger.error(f"Hepsiburada URL ayrıştırma hatası: {e}")
            raise ValidationError(f"Hepsiburada URL ayrıştırılamadı: {e}")
    
    def validate_url(self, url: str) -> bool:
        """URL'nin geçerli olup olmadığını kontrol eder"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Desteklenen domain kontrolü
            if not any(supported in domain for supported in self.supported_domains):
                return False
            
            # URL format kontrolü
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
            
            return True
            
        except Exception:
            return False


class MockURLFetcherService(IURLFetcherService):
    """Test için mock URL Fetcher Service"""
    
    def __init__(self, mock_url: Optional[str] = None):
        self.mock_url = mock_url or "https://www.trendyol.com/harmana/hindiba-kahvesi-p-288620006?merchantId=936059"
    
    def get_current_url(self) -> str:
        return self.mock_url
    
    def extract_product_info(self, url: str) -> Dict[str, Any]:
        return {
            'domain': 'trendyol.com',
            'product_slug': 'harmana/hindiba-kahvesi-p-288620006',
            'merchant_id': '936059',
            'full_url': url
        }
    
    def validate_url(self, url: str) -> bool:
        return 'trendyol.com' in url or 'hepsiburada.com' in url 