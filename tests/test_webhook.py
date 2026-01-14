"""Test webhook endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestWebhook:
    """Test webhook endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "muuh Recruiting Chatbot API" in response.json()["message"]
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_webhook_validation(self):
        """Test webhook GET endpoint for validation."""
        response = client.get("/webhook")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_webhook_post_missing_params(self):
        """Test webhook POST with missing parameters."""
        response = client.post("/webhook", data={})
        assert response.status_code == 422  # Validation error


# Note: Full webhook integration tests require Twilio credentials
# To run: pytest tests/test_webhook.py -v
