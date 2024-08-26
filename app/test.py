from app.testclient import TestClient
from app import app

client = TestClient(app)


def test_ask():
    prompt = "What is capital of France?"
    expected_response = "French capital is Paris."
    response = client.get("/ask", params={"prompt": prompt, "seed": 123})
    print(response)
    assert response.json()["response"] == expected_response
    assert response.status_code == 200
