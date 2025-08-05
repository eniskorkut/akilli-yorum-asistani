"""
test_debug.py - Debug test scripti
"""

import requests

# Test 1: Header'ları kontrol et
headers = {"X-API-Key": "test-api-key"}
print(f"Headers: {headers}")

# Test 2: Basit GET isteği
response = requests.get("http://localhost:8000/api/v1/health/", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Test 3: POST isteği
data = {"question": "test", "use_mocks": True}
response = requests.post("http://localhost:8000/api/v1/query/", headers=headers, json=data)
print(f"POST Status: {response.status_code}")
print(f"POST Response: {response.text}") 