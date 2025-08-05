"""
test_simple_endpoint.py - Basit endpoint test
"""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/test")
async def test_endpoint(request: Request):
    headers = dict(request.headers)
    return {"headers": headers, "message": "test"}

client = TestClient(app)

# Test
response = client.get("/test", headers={"X-API-Key": "test-api-key"})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}") 