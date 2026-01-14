"""Pydantic models for conversation state management."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from enum import Enum


class ConversationStage(str, Enum):
    """Conversation stages matching RecruitingMachine."""
    GREETING = "greeting"
    JOB_SELECTION = "job_selection"
    REQUIREMENTS_CHECK = "requirements_check"
    DATA_PERSONAL = "data_personal"
    DATA_DOCUMENTS = "data_documents"
    DATA_ADDITIONAL = "data_additional"
    CLOSING = "closing"


class ConversationContext(BaseModel):
    """Context information for ongoing conversation."""
    collected_info: Dict[str, Any] = {}
    last_question: Optional[str] = None
    conversation_stage: ConversationStage = ConversationStage.GREETING
    awaiting_response_for: Optional[str] = None  # What info we're waiting for


class ConversationState(BaseModel):
    """Complete conversation state for a user."""
    user_id: str  # WhatsApp number
    current_intent: Optional[str] = None
    context: ConversationContext = ConversationContext()
    message_count: int = 0
    message_history: List[Dict[str, str]] = []
    last_interaction: Optional[str] = None
