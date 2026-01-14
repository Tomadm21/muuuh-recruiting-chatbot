"""Test intent extraction and response generation."""
import pytest
from app.services.openai_service import openai_service


class TestIntentExtraction:
    """Test intent extraction functionality."""
    
    def test_greeting_intent(self):
        """Test greeting intent detection."""
        messages = ["Hallo", "Hi", "Hey", "Guten Tag"]
        
        for msg in messages:
            result = openai_service.extract_intent(msg)
            assert result["intent"] == "greeting"
            assert result["confidence"] > 0.7
    
    def test_job_openings_intent(self):
        """Test job openings intent detection."""
        messages = [
            "Welche Jobs sind offen?",
            "Welche Stellen habt ihr?",
            "Was für Positionen gibt es?"
        ]
        
        for msg in messages:
            result = openai_service.extract_intent(msg)
            assert result["intent"] == "job_openings"
    
    def test_application_process_intent(self):
        """Test application process intent detection."""
        messages = [
            "Wie bewerbe ich mich?",
            "Wie läuft der Bewerbungsprozess ab?",
            "Was ist der Prozess?"
        ]
        
        for msg in messages:
            result = openai_service.extract_intent(msg)
            assert result["intent"] == "application_process"
    
    def test_entity_extraction(self):
        """Test entity extraction from messages."""
        # Test email extraction
        result = openai_service.extract_intent(
            "Mein Name ist Tom und meine Email ist tom@example.com"
        )
        assert "email" in result["entities"]
        assert result["entities"]["email"] == "tom@example.com"
        
        # Test name extraction
        assert "name" in result["entities"]
        assert "tom" in result["entities"]["name"].lower()


# Note: These tests require OPENAI_API_KEY to be set
# To run: pytest tests/test_intents.py -v
