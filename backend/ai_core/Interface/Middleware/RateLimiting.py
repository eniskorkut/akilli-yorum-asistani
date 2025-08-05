"""
Rate Limiting Middleware - API rate limiting

Bu modül, API isteklerinin rate limiting'ini sağlar.
Kullanıcı bazında istek sayısını sınırlar.
"""

from fastapi import HTTPException, Request
from typing import Dict, Tuple
import time
from collections import defaultdict
from Logger import Logger


class RateLimitingMiddleware:
    """
    API rate limiting middleware'i
    
    Bu sınıf, API isteklerinin hızını sınırlar ve
    abuse'u önler.
    """
    
    def __init__(self):
        """Middleware'i başlatır"""
        # Rate limiting ayarları
        self.requests_per_minute = 60  # Dakikada maksimum istek sayısı
        self.requests_per_hour = 1000  # Saatte maksimum istek sayısı
        self.requests_per_day = 10000  # Günde maksimum istek sayısı
        
        # İstek geçmişi (production'da Redis kullanılmalı)
        self.request_history: Dict[str, list] = defaultdict(list)
        
        # IP bazlı rate limiting
        self.ip_requests_per_minute = 30
        self.ip_requests_per_hour = 500
        
        Logger.info("Rate limiting middleware başlatıldı")
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        İstemci kimliğini alır
        
        Args:
            request: FastAPI request objesi
            
        Returns:
            str: İstemci kimliği (IP + User-Agent)
        """
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # API key varsa onu da ekle
        api_key = request.headers.get("x-api-key", "")
        
        return f"{client_ip}:{user_agent}:{api_key}"
    
    def _clean_old_requests(self, client_id: str, window_seconds: int):
        """
        Eski istekleri temizler
        
        Args:
            client_id: İstemci kimliği
            window_seconds: Zaman penceresi (saniye)
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Eski istekleri filtrele
        self.request_history[client_id] = [
            req_time for req_time in self.request_history[client_id]
            if req_time > cutoff_time
        ]
    
    def _check_rate_limit(self, client_id: str, limit: int, window_seconds: int) -> bool:
        """
        Rate limit kontrolü yapar
        
        Args:
            client_id: İstemci kimliği
            limit: Maksimum istek sayısı
            window_seconds: Zaman penceresi (saniye)
            
        Returns:
            bool: Rate limit aşıldı mı
        """
        self._clean_old_requests(client_id, window_seconds)
        
        current_requests = len(self.request_history[client_id])
        
        if current_requests >= limit:
            Logger.warning(f"Rate limit aşıldı: {client_id} - {current_requests}/{limit}")
            return False
        
        return True
    
    def _add_request(self, client_id: str):
        """
        İsteği geçmişe ekler
        
        Args:
            client_id: İstemci kimliği
        """
        current_time = time.time()
        self.request_history[client_id].append(current_time)
    
    def check_rate_limits(self, request: Request) -> bool:
        """
        Tüm rate limit'leri kontrol eder
        
        Args:
            request: FastAPI request objesi
            
        Returns:
            bool: Rate limit'ler geçerli mi
            
        Raises:
            HTTPException: Rate limit aşıldıysa
        """
        client_id = self._get_client_identifier(request)
        
        # Dakikalık limit kontrolü
        if not self._check_rate_limit(client_id, self.requests_per_minute, 60):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Dakikada maksimum {self.requests_per_minute} istek gönderebilirsiniz",
                    "retry_after": 60
                }
            )
        
        # Saatlik limit kontrolü
        if not self._check_rate_limit(client_id, self.requests_per_hour, 3600):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Saatte maksimum {self.requests_per_hour} istek gönderebilirsiniz",
                    "retry_after": 3600
                }
            )
        
        # Günlük limit kontrolü
        if not self._check_rate_limit(client_id, self.requests_per_day, 86400):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Günde maksimum {self.requests_per_day} istek gönderebilirsiniz",
                    "retry_after": 86400
                }
            )
        
        # İsteği geçmişe ekle
        self._add_request(client_id)
        
        Logger.debug(f"Rate limit kontrolü geçti: {client_id}")
        return True
    
    def get_rate_limit_info(self, request: Request) -> Dict:
        """
        Rate limit bilgilerini döndürür
        
        Args:
            request: FastAPI request objesi
            
        Returns:
            Dict: Rate limit bilgileri
        """
        client_id = self._get_client_identifier(request)
        
        # Mevcut istek sayılarını hesapla
        current_time = time.time()
        
        minute_requests = len([
            req_time for req_time in self.request_history[client_id]
            if req_time > current_time - 60
        ])
        
        hour_requests = len([
            req_time for req_time in self.request_history[client_id]
            if req_time > current_time - 3600
        ])
        
        day_requests = len([
            req_time for req_time in self.request_history[client_id]
            if req_time > current_time - 86400
        ])
        
        return {
            "client_id": client_id,
            "limits": {
                "per_minute": self.requests_per_minute,
                "per_hour": self.requests_per_hour,
                "per_day": self.requests_per_day
            },
            "current_usage": {
                "per_minute": minute_requests,
                "per_hour": hour_requests,
                "per_day": day_requests
            },
            "remaining": {
                "per_minute": max(0, self.requests_per_minute - minute_requests),
                "per_hour": max(0, self.requests_per_hour - hour_requests),
                "per_day": max(0, self.requests_per_day - day_requests)
            }
        }


# Global rate limiting instance
rate_limiting_middleware = RateLimitingMiddleware()


def get_rate_limiting_middleware() -> RateLimitingMiddleware:
    """
    Rate limiting middleware instance'ını döndürür
    
    Returns:
        RateLimitingMiddleware: Middleware instance'ı
    """
    return rate_limiting_middleware


 