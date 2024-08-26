import requests
from fastapi.testclient import TestClient
from app import app

def test_ask():
    
    client = TestClient(app)
    prompt = "What is capital of France?"
    expected_response = "French capital is Paris."
    response = client.get('/ask', params={"prompt": prompt, "seed": 123})
    assert response.json()['response'] == expected_response
    assert response.status_code == 200
    