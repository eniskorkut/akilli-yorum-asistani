"""
Authentication Middleware - API kimlik doğrulama

Bu modül, API isteklerinin kimlik doğrulamasını sağlar.
API key tabanlı authentication kullanır.
"""

from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
from datetime import datetime, timedelta
import jwt
from Logger import Logger


class AuthenticationMiddleware:
    """
    API kimlik doğrulama middleware'i
    
    Bu sınıf, API isteklerinin güvenliğini sağlar ve
    kullanıcı kimlik doğrulamasını yapar.
    """
    
    def __init__(self):
        """Middleware'i başlatır"""
        self.security = HTTPBearer()
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # API key'leri (production'da database'den gelmeli)
        self.api_keys = {
            "test-api-key": "test-user",
            "demo-api-key": "demo-user"
        }
    
    def verify_api_key(self, api_key: str) -> bool:
        """
        API key'i doğrular
        
        Args:
            api_key: Doğrulanacak API key
            
        Returns:
            bool: API key geçerli mi
        """
        return api_key in self.api_keys
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """
        JWT access token oluşturur
        
        Args:
            data: Token'a eklenecek veri
            expires_delta: Token geçerlilik süresi
            
        Returns:
            str: JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """
        JWT token'ı doğrular
        
        Args:
            token: Doğrulanacak JWT token
            
        Returns:
            dict: Token payload'ı
            
        Raises:
            HTTPException: Token geçersizse
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            Logger.warning("Token süresi dolmuş")
            raise HTTPException(status_code=401, detail="Token süresi dolmuş")
        except jwt.JWTError:
            Logger.warning("Geçersiz token")
            raise HTTPException(status_code=401, detail="Geçersiz token")
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """
        Mevcut kullanıcıyı alır
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            dict: Kullanıcı bilgileri
            
        Raises:
            HTTPException: Kimlik doğrulama başarısızsa
        """
        token = credentials.credentials
        
        try:
            payload = self.verify_token(token)
            username = payload.get("sub")
            
            if username is None:
                Logger.warning("Token'da kullanıcı adı bulunamadı")
                raise HTTPException(status_code=401, detail="Geçersiz token")
            
            return {"username": username, "payload": payload}
            
        except HTTPException:
            raise
        except Exception as e:
            Logger.error(f"Kimlik doğrulama hatası: {e}")
            raise HTTPException(status_code=401, detail="Kimlik doğrulama başarısız")
    
    def require_api_key(self, api_key: str) -> bool:
        """
        API key gerektiren endpoint'ler için
        
        Args:
            api_key: API key header'ı
            
        Returns:
            bool: API key geçerli mi
            
        Raises:
            HTTPException: API key geçersizse
        """
        if not api_key:
            Logger.warning("API key bulunamadı")
            raise HTTPException(status_code=401, detail="API key gerekli")
        
        if not self.verify_api_key(api_key):
            Logger.warning(f"Geçersiz API key: {api_key}")
            raise HTTPException(status_code=401, detail="Geçersiz API key")
        
        Logger.info(f"API key doğrulandı: {api_key}")
        return True


# Global authentication instance
auth_middleware = AuthenticationMiddleware()


def get_auth_middleware() -> AuthenticationMiddleware:
    """
    Authentication middleware instance'ını döndürür
    
    Returns:
        AuthenticationMiddleware: Middleware instance'ı
    """
    return auth_middleware


def require_authentication():
    """
    Authentication gerektiren endpoint'ler için dependency
    
    Returns:
        function: FastAPI dependency function
    """
    return auth_middleware.get_current_user


 