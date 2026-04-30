import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_bp_service(mocker):
    # Mock the bp_service instance in app.api.bp_router
    mock_service = AsyncMock()
    mock_service.handle_chat.return_value = {
        "text": "API response",
        "intent": "general"
    }
    mocker.patch("app.api.bp_router.bp_service", mock_service)
    return mock_service

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to BP AI Agent Service"}

def test_get_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    assert "bedrock_api_key" in response.json()

def test_chat_endpoint():
    response = client.post("/api/v1/bp/chat", json={
        "user_id": "test_user",
        "message": "hello",
        "user_token": "test_token"
    })
    
    assert response.status_code == 200
    assert response.json()["text"] == "API response"
    assert response.json()["intent"] == "general"

def test_chat_endpoint_error(mocker):
    mock_service = AsyncMock()
    mock_service.handle_chat.side_effect = Exception("API Error")
    mocker.patch("app.api.bp_router.bp_service", mock_service)
    
    response = client.post("/api/v1/bp/chat", json={
        "user_id": "test_user",
        "message": "hello",
        "user_token": "test_token"
    })
    
    assert response.status_code == 500
    assert "API Error" in response.json()["detail"]
