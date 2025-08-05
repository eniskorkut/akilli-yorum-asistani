"""
test_api_quick.py - Hızlı API test scripti

Bu script, API'nin temel fonksiyonlarını hızlıca test eder.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key"

def test_api():
    """API'yi test eder"""
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"Debug: Headers: {headers}")
    
    print("🚀 API Test Başlatılıyor...")
    
    try:
        # 1. Ana sayfa testi
        print("\n1. Ana sayfa testi...")
        response = requests.get(f"{BASE_URL}/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 2. API bilgileri testi
        print("\n2. API bilgileri testi...")
        response = requests.get(f"{BASE_URL}/api/info", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 3. Health check testi
        print("\n3. Health check testi...")
        response = requests.get(f"{BASE_URL}/api/v1/health/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 4. Mock sorgu testi
        print("\n4. Mock sorgu testi...")
        data = {
            "question": "Bu ürün kaliteli mi?",
            "use_mocks": True
        }
        response = requests.post(f"{BASE_URL}/api/v1/query/", headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 5. Soru önerileri testi
        print("\n5. Soru önerileri testi...")
        response = requests.get(f"{BASE_URL}/api/v1/query/suggestions?partial_question=kaliteli", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        print("\n✅ Tüm testler başarılı!")
        
    except requests.exceptions.ConnectionError:
        print("❌ API'ye bağlanılamadı. API çalışıyor mu?")
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_api() 