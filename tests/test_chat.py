import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

def test_chat_empty_messages():
    with TestClient(app) as client:
        response = client.post("/chat", json={"messages": []})
        assert response.status_code == 400
        assert "Messages array cannot be empty" in response.json()["detail"]

def test_chat_schema_compliance():
    if not settings.OPENROUTER_API_KEY:
        pytest.skip("OPENROUTER_API_KEY not set")

    with TestClient(app) as client:
        response = client.post("/chat", json={
            "messages": [
                {"role": "user", "content": "I am hiring a Java developer."}
            ]
        })
        print(f"STATUS CODE: {response.status_code}")
        print(f"RESPONSE BODY: {response.json()}")
        assert response.status_code == 200
        data = response.json()

        assert "reply" in data
        assert "recommendations" in data
        assert "end_of_conversation" in data

        assert isinstance(data["reply"], str)
        assert data["recommendations"] is None or isinstance(data["recommendations"], list)
        assert isinstance(data["end_of_conversation"], bool)
