"""CRUD operations for leads."""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.lead import Lead


def create_lead(db: Session, whatsapp_number: str) -> Lead:
    """
    Create a new lead.
    
    Args:
        db: Database session
        whatsapp_number: User's WhatsApp number
        
    Returns:
        Created lead object
    """
    lead = Lead(whatsapp_number=whatsapp_number)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead_by_whatsapp(db: Session, whatsapp_number: str) -> Optional[Lead]:
    """
    Get lead by WhatsApp number.
    
    Args:
        db: Database session
        whatsapp_number: WhatsApp number to search for
        
    Returns:
        Lead object or None if not found
    """
    return db.query(Lead).filter(Lead.whatsapp_number == whatsapp_number).first()


def get_or_create_lead(db: Session, whatsapp_number: str) -> Lead:
    """
    Get existing lead or create new one.
    
    Args:
        db: Database session
        whatsapp_number: User's WhatsApp number
        
    Returns:
        Lead object
    """
    lead = get_lead_by_whatsapp(db, whatsapp_number)
    if not lead:
        lead = create_lead(db, whatsapp_number)
    return lead


def update_lead(db: Session, lead: Lead, **kwargs) -> Lead:
    """
    Update lead with new information.
    
    Args:
        db: Database session
        lead: Lead object to update
        **kwargs: Fields to update
        
    Returns:
        Updated lead object
    """
    for key, value in kwargs.items():
        if hasattr(lead, key):
            setattr(lead, key, value)
    
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return lead


def add_conversation_message(
    db: Session,
    lead: Lead,
    role: str,
    message: str
) -> Lead:
    """
    Add message to conversation history.
    
    Args:
        db: Database session
        lead: Lead object
        role: 'user' or 'bot'
        message: Message content
        
    Returns:
        Updated lead object
    """
    history = lead.conversation_history or []
    history.append({
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    })
    lead.conversation_history = history
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return lead


def get_high_priority_leads(db: Session, min_score: int = 70) -> List[Lead]:
    """
    Get all high-priority leads.
    
    Args:
        db: Database session
        min_score: Minimum qualification score
        
    Returns:
        List of high-priority leads
    """
    return db.query(Lead).filter(Lead.qualification_score >= min_score).all()
