"""
URL Algılama Modülü
Bu modül, verilen URL'nin hangi e-ticaret sitesine ait olduğunu algılar.
"""

import re
from urllib.parse import urlparse

class URLDetector:
    """URL'den e-ticaret sitesini algılayan sınıf"""
    
    def __init__(self):
        self.supported_sites = {
            'trendyol': {
                'patterns': [
                    r'trendyol\.com',
                    r'trendyol\.com\.tr'
                ],
                'scraper_script': '1_fetch_reviews.py',
                'name': 'Trendyol'
            },
            'hepsiburada': {
                'patterns': [
                    r'hepsiburada\.com',
                    r'hepsiburada\.com\.tr'
                ],
                'scraper_script': '1_fetch_reviews_hepsiburada.py',
                'name': 'Hepsiburada'
            }
        }
    
    def detect_site(self, url):
        """
        URL'den hangi e-ticaret sitesi olduğunu algılar
        
        Args:
            url (str): Kontrol edilecek URL
            
        Returns:
            dict: Site bilgileri veya None
        """
        if not url:
            return None
            
        # URL'yi normalize et
        url = url.strip().lower()
        
        # http/https ekle (yoksa)
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Her site için pattern'leri kontrol et
        for site_key, site_info in self.supported_sites.items():
            for pattern in site_info['patterns']:
                if re.search(pattern, url):
                    return {
                        'site': site_key,
                        'name': site_info['name'],
                        'scraper_script': site_info['scraper_script'],
                        'url': url
                    }
        
        return None
    
    def is_supported(self, url):
        """
        URL'nin desteklenen bir site olup olmadığını kontrol eder
        
        Args:
            url (str): Kontrol edilecek URL
            
        Returns:
            bool: Destekleniyorsa True
        """
        return self.detect_site(url) is not None
    
    def get_supported_sites(self):
        """
        Desteklenen sitelerin listesini döndürür
        
        Returns:
            list: Desteklenen site isimleri
        """
        return [site_info['name'] for site_info in self.supported_sites.values()]
    
    def validate_product_url(self, url):
        """
        URL'nin geçerli bir ürün sayfası olup olmadığını kontrol eder
        
        Args:
            url (str): Kontrol edilecek URL
            
        Returns:
            dict: Doğrulama sonucu
        """
        site_info = self.detect_site(url)
        if not site_info:
            return {
                'valid': False,
                'error': 'Desteklenmeyen site',
                'supported_sites': self.get_supported_sites()
            }
        
        # Site özel doğrulama kuralları
        if site_info['site'] == 'trendyol':
            # Trendyol için ürün sayfası kontrolü
            if not re.search(r'/p-', url):
                return {
                    'valid': False,
                    'error': 'Geçerli bir Trendyol ürün sayfası değil',
                    'site': site_info['name']
                }
        
        elif site_info['site'] == 'hepsiburada':
            # Hepsiburada için ürün sayfası kontrolü
            if not re.search(r'/p-', url):
                return {
                    'valid': False,
                    'error': 'Geçerli bir Hepsiburada ürün sayfası değil',
                    'site': site_info['name']
                }
        
        return {
            'valid': True,
            'site': site_info['name'],
            'scraper_script': site_info['scraper_script']
        }

# Global instance
url_detector = URLDetector()

def detect_site_from_url(url):
    """URL'den site algılama için kolay fonksiyon"""
    return url_detector.detect_site(url)

def is_supported_site(url):
    """Site destekleniyor mu kontrolü için kolay fonksiyon"""
    return url_detector.is_supported(url)

def validate_url(url):
    """URL doğrulama için kolay fonksiyon"""
    return url_detector.validate_product_url(url) 