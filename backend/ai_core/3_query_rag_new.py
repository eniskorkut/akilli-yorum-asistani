"""
3_query_rag_new.py - Service Layer kullanan yeni RAG sorgu sistemi
"""

import argparse
import sys

from Config import Config
from Exceptions import (
    ConfigurationError, 
    RAGServiceError, 
    FileNotFoundError, 
    ModelLoadError, 
    APIError,
    ValidationError
)
from Logger import Logger
from DI import configure_container


def main():
    """Ana fonksiyon - Service Layer ile güvenli hata yönetimi"""
    try:
        # Argument parsing
        parser = argparse.ArgumentParser()
        parser.add_argument('--question', required=True, help='Kullanıcı sorusu')
        parser.add_argument('--use-mocks', action='store_true', help='Mock servisleri kullan')
        args = parser.parse_args()

        Logger.info("Service Layer ile RAG sorgu sistemi başlatılıyor...")
        
        # Konfigürasyonu doğrula
        try:
            Config.validate()
            Logger.info("Konfigürasyon doğrulandı")
        except ValueError as e:
            Logger.critical(f"Konfigürasyon hatası: {e}")
            print(f'Hata: {e}', flush=True)
            sys.exit(1)

        # DI Container'ı konfigüre et
        try:
            container = configure_container(use_mocks=args.use_mocks)
            Logger.info("DI Container konfigüre edildi")
            
            # Service bilgilerini logla
            service_info = container.get_service_info()
            Logger.info(f"Service bilgileri: {service_info}")
            
        except Exception as e:
            Logger.error(f"DI Container konfigürasyon hatası: {e}")
            raise ConfigurationError(f"DI Container konfigüre edilemedi: {e}")

        # RAG Service'i al
        try:
            rag_service = container.get_rag_service()
            Logger.info("RAG Service alındı")
        except Exception as e:
            Logger.error(f"RAG Service alma hatası: {e}")
            raise RAGServiceError(f"RAG Service alınamadı: {e}")

        # RAG sorgusu yap
        try:
            response = rag_service.query_rag(args.question)
            print(response, flush=True)
            Logger.info("RAG sorgu işlemi başarıyla tamamlandı")
            
        except Exception as e:
            Logger.error(f"RAG sorgu hatası: {e}")
            print(f'Hata: {e}', flush=True)
            sys.exit(1)

    except (ConfigurationError, ModelLoadError, RAGServiceError, APIError) as e:
        Logger.error(f"Kritik hata: {e}")
        print(f'Hata: {e}', flush=True)
        sys.exit(1)
    except Exception as e:
        Logger.critical(f"Beklenmeyen hata: {e}")
        print(f'Beklenmeyen hata: {e}', flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 