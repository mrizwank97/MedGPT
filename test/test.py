from fastapi.testclient import TestClient
from app.app import app
import os
import pytest

client = TestClient(app)

def test_ask():
    print(os.getcwd())
    prompt = "What is capital of France?"
    expected_response = "French capital is Paris."
    response = client.get("/ask", params={"prompt": prompt, "seed": 123})
    print(response.json())
    assert response.json()["response"] == expected_response
    assert response.status_code == 200