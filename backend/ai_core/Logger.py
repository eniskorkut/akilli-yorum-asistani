import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Uygulama için merkezi logging sistemi"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Logger'ı konfigüre eder"""
        self._logger = logging.getLogger('akilli_yorum_asistani')
        self._logger.setLevel(logging.INFO)
        
        # Eğer handler zaten varsa, tekrar ekleme
        if self._logger.handlers:
            return
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        # File handler
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Logger instance'ını döndürür"""
        if cls._instance is None:
            cls()
        return cls._instance._logger
    
    @classmethod
    def info(cls, message: str):
        """Info seviyesinde log"""
        cls.get_logger().info(message)
    
    @classmethod
    def error(cls, message: str, exc_info: bool = True):
        """Error seviyesinde log"""
        cls.get_logger().error(message, exc_info=exc_info)
    
    @classmethod
    def warning(cls, message: str):
        """Warning seviyesinde log"""
        cls.get_logger().warning(message)
    
    @classmethod
    def debug(cls, message: str):
        """Debug seviyesinde log"""
        cls.get_logger().debug(message)
    
    @classmethod
    def critical(cls, message: str, exc_info: bool = True):
        """Critical seviyesinde log"""
        cls.get_logger().critical(message, exc_info=exc_info) 