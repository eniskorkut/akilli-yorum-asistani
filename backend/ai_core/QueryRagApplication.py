"""
QueryRagApplication.py - Application Layer kullanan RAG sorgu sistemi

Bu dosya, Clean Architecture'ın Application Layer'ını kullanarak
RAG (Retrieval-Augmented Generation) sorgularını gerçekleştirir.

Özellikler:
- Application Service kullanımı
- Dependency Injection Container
- Gelişmiş hata yönetimi
- JSON ve Text output formatları
- Mock ve gerçek servis desteği

Kullanım:
    python QueryRagApplication.py --question "Bu ürün kaliteli mi?"
    python QueryRagApplication.py --question "Bu ürün kaliteli mi?" --use-mocks
    python QueryRagApplication.py --question "Bu ürün kaliteli mi?" --output-format json
"""

import argparse
import sys
import json

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
    """
    Ana fonksiyon - Application Layer ile güvenli hata yönetimi
    
    Bu fonksiyon:
    1. Komut satırı argümanlarını parse eder
    2. Konfigürasyonu doğrular
    3. DI Container'ı konfigüre eder
    4. Application Service'i alır
    5. Sorguyu gerçekleştirir
    6. Sonucu formatlar ve döndürür
    """
    try:
        # Komut satırı argümanlarını parse et
        parser = argparse.ArgumentParser(
            description='RAG sorgu sistemi - Application Layer kullanarak ürün yorumlarını analiz eder'
        )
        parser.add_argument('--question', required=True, help='Kullanıcı sorusu')
        parser.add_argument('--use-mocks', action='store_true', help='Mock servisleri kullan')
        parser.add_argument('--product-url', help='Ürün URL\'si')
        parser.add_argument('--max-reviews', type=int, help='Maksimum yorum sayısı')
        parser.add_argument('--output-format', choices=['text', 'json'], default='text', help='Çıktı formatı')
        args = parser.parse_args()

        Logger.info("Application Layer ile RAG sorgu sistemi başlatılıyor...")
        
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

        # Application Service'i al
        try:
            app_service = container.get_query_application_service()
            Logger.info("Application Service alındı")
        except Exception as e:
            Logger.error(f"Application Service alma hatası: {e}")
            raise RAGServiceError(f"Application Service alınamadı: {e}")

        # Sorgu parametrelerini hazırla
        kwargs = {}
        if args.product_url:
            kwargs['product_url'] = args.product_url
        if args.max_reviews:
            kwargs['max_reviews'] = args.max_reviews
        if args.use_mocks:
            kwargs['use_mocks'] = True

        # Application Service ile sorgu yap
        try:
            result = app_service.query_product(args.question, **kwargs)
            
            # Çıktı formatını belirle ve sonucu yazdır
            if args.output_format == 'json':
                # JSON formatında çıktı - API entegrasyonu için
                print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
            else:
                # Text formatında çıktı - kullanıcı dostu
                if result.get('success'):
                    print(result.get('answer', ''), flush=True)
                else:
                    error = result.get('error', {})
                    print(f"Hata: {error.get('message', 'Bilinmeyen hata')}", flush=True)
            
            Logger.info("Application Service sorgu işlemi başarıyla tamamlandı")
            
        except Exception as e:
            Logger.error(f"Application Service sorgu hatası: {e}")
            print(f'Hata: {e}', flush=True)
            sys.exit(1)

    except (ConfigurationError, ModelLoadError, RAGServiceError, APIError) as e:
        # Konfigürasyon, model yükleme, RAG servis veya API hataları
        Logger.error(f"Kritik hata: {e}")
        print(f'Hata: {e}', flush=True)
        sys.exit(1)
    except Exception as e:
        # Beklenmeyen hatalar - genellikle sistem seviyesi
        Logger.critical(f"Beklenmeyen hata: {e}")
        print(f'Beklenmeyen hata: {e}', flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 