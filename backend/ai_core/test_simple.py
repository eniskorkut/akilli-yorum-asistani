"""
test_simple.py - Basit API test
"""

import requests

# Test
response = requests.get("http://localhost:8000/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test with API key
headers = {"X-API-Key": "test-api-key"}
response = requests.get("http://localhost:8000/api/v1/health/", headers=headers)
print(f"Health Status: {response.status_code}")
print(f"Health Response: {response.json()}") 