"""
Interface Module - REST API Interface Layer

Bu modül, Clean Architecture'ın Interface Layer'ını temsil eder.
REST API endpoint'leri, middleware'ler ve modelleri içerir.
"""

from .Controllers.QueryController import get_query_controller
from .Controllers.HealthController import get_health_controller
from .Middleware.Authentication import get_auth_middleware
from .Middleware.RateLimiting import get_rate_limiting_middleware

__all__ = [
    'get_query_controller',
    'get_health_controller',
    'get_auth_middleware',
    'get_rate_limiting_middleware'
] 