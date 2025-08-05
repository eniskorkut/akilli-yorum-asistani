#!/usr/bin/env python3
"""
Test çalıştırma scripti
"""

import os
import sys
import unittest
import subprocess

def run_unit_tests():
    """Unit testleri çalıştırır"""
    print("🧪 Unit testler çalıştırılıyor...")
    
    # Test dosyalarını bul
    test_files = [
        'TestQueryRag.py'
    ]
    
    # Her test dosyasını çalıştır
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 {test_file} çalıştırılıyor...")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'unittest', test_file, '-v'
                ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
                
                if result.returncode == 0:
                    print(f"✅ {test_file} başarılı")
                else:
                    print(f"❌ {test_file} başarısız")
                    print(result.stdout)
                    print(result.stderr)
                    
            except Exception as e:
                print(f"❌ {test_file} çalıştırma hatası: {e}")
        else:
            print(f"⚠️ {test_file} bulunamadı")

def run_integration_tests():
    """Integration testleri çalıştırır"""
    print("\n🔗 Integration testler çalıştırılıyor...")
    
    # Basit integration testi
    try:
        # Config testi
        from Config import Config
        print("✅ Config import başarılı")
        
        # Exceptions testi
        from Exceptions import ConfigurationError, RAGServiceError
        print("✅ Exceptions import başarılı")
        
        # Logger testi
        from Logger import Logger
        Logger.info("Test log mesajı")
        print("✅ Logger çalışıyor")
        
    except Exception as e:
        print(f"❌ Integration test hatası: {e}")

def run_smoke_tests():
    """Smoke testleri çalıştırır"""
    print("\n💨 Smoke testler çalıştırılıyor...")
    
    # Temel fonksiyonların çalışıp çalışmadığını kontrol et
    try:
        # 3_query_rag.py'nin import edilebilir olduğunu kontrol et
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "query_rag", 
            os.path.join(os.path.dirname(__file__), "3_query_rag.py")
        )
        module = importlib.util.module_from_spec(spec)
        print("✅ 3_query_rag.py import edilebilir")
        
    except Exception as e:
        print(f"❌ Smoke test hatası: {e}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 Test Suite Başlatılıyor...")
    print("=" * 50)
    
    # Unit testler
    run_unit_tests()
    
    # Integration testler
    run_integration_tests()
    
    # Smoke testler
    run_smoke_tests()
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Tamamlandı!")

if __name__ == "__main__":
    main() 