import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.core.flow_engine import FlowEngine
from app.models.lead import Lead

@pytest.fixture
def flow_engine():
    return FlowEngine()

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_lead():
    lead = MagicMock(spec=Lead)
    lead.user_id = "test_user_123"
    lead.conversation_stage = 0
    lead.name = "Test User"
    return lead

class TestFlowEngine:
    
    def test_reset_command(self, flow_engine, mock_db):
        """Test that the #reset command correctly resets the state."""
        with patch("app.db.crud.get_or_create_lead") as mock_get_lead:
            mock_lead = MagicMock()
            mock_get_lead.return_value = mock_lead
            
            response = flow_engine.process_message("test_user", "#reset", mock_db)
            
            assert "System zurückgesetzt" in response
            assert mock_lead.conversation_stage == 0
            mock_db.commit.assert_called()

    def test_idle_to_greeted_transition(self, flow_engine, mock_db):
        """Test transition from IDLE (0) to GREETED (1)."""
        with patch("app.db.crud.get_or_create_lead") as mock_get_lead:
            lead = MagicMock(spec=Lead)
            lead.conversation_stage = 0
            mock_get_lead.return_value = lead
            
            # Using the actual _handle_idle through process_message
            response = flow_engine.process_message("test_user", "Hallo", mock_db)
            
            assert "Willkommen im Karriere-Chat" in response
            assert lead.conversation_stage == 1

    @patch("app.services.openai_service.openai_service.classify_flow_input")
    def test_greeted_to_job_selected(self, mock_classify, flow_engine, mock_db):
        """Test transition from GREETED to JOB_SELECTED using 'jobs' input."""
        with patch("app.db.crud.get_or_create_lead") as mock_get_lead:
            lead = MagicMock(spec=Lead)
            lead.conversation_stage = 1
            mock_get_lead.return_value = lead
            
            mock_classify.return_value = {"category": "VALID_ANSWER", "normalized_value": "JOB"}
            
            response = flow_engine.process_message("test_user", "Ich suche einen Job", mock_db)
            
            assert "Hier sind unsere offenen Stellen" in response
            assert lead.conversation_stage == flow_engine.STATE_JOB_SELECTED

    @patch("app.services.openai_service.openai_service.classify_flow_input")
    @patch("app.services.openai_service.openai_service.generate_flow_reply")
    def test_job_selection_transition(self, mock_reply, mock_classify, flow_engine, mock_db):
        """Test selecting a specific job."""
        with patch("app.db.crud.get_or_create_lead") as mock_get_lead:
            with patch("app.db.crud.update_lead") as mock_update:
                lead = MagicMock(spec=Lead)
                lead.conversation_stage = flow_engine.STATE_JOB_SELECTED
                mock_get_lead.return_value = lead
                
                mock_classify.return_value = {"category": "VALID_ANSWER", "normalized_value": "JOB_1"}
                mock_reply.return_value = "Super! Hast du Erfahrung?"
                
                response = flow_engine.process_message("test_user", "1", mock_db)
                
                assert "Super! Hast du Erfahrung?" in response
                assert lead.conversation_stage == flow_engine.STATE_REQ_1
                mock_update.assert_called_with(mock_db, lead, position_interest="(Junior) Conversational AI Developer")

    def test_final_state_completes(self, flow_engine, mock_db):
        """Test that the completed state stays completed."""
        with patch("app.db.crud.get_or_create_lead") as mock_get_lead:
            lead = MagicMock(spec=Lead)
            lead.conversation_stage = flow_engine.STATE_COMPLETED
            mock_get_lead.return_value = lead
            
            response = flow_engine.process_message("test_user", "Hallo?", mock_db)
            
            assert "Bewerbung ist bereits durch" in response
            assert lead.conversation_stage == flow_engine.STATE_COMPLETED
