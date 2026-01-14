"""Lead data model."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from app.db.database import Base


class Lead(Base):
    """Lead/candidate data model."""
    
    __tablename__ = "leads_v2" # Force new table creation for schema update
    
    id = Column(Integer, primary_key=True, index=True)
    whatsapp_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Qualification fields
    experience_level = Column(String, nullable=True)  # junior, mid, senior
    has_conversational_ai_experience = Column(Boolean, default=False)
    has_api_knowledge = Column(Boolean, default=False)
    work_mode = Column(String, nullable=True)  # remote, hybrid, office
    availability = Column(String, nullable=True)  # fulltime, parttime
    position_interest = Column(String, nullable=True)
    
    # Document uploads
    cv_file_path = Column(String, nullable=True)
    cover_letter_file_path = Column(String, nullable=True)
    certificate_file_path = Column(String, nullable=True)
    
    # Extracted CV data
    years_of_experience = Column(Integer, default=0)
    skills = Column(JSON, nullable=True)  # {"python": true, "make.com": true, ...}
    education_level = Column(String, nullable=True)  # Bachelor, Master, PhD
    certifications = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    
    # Additional application info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    source = Column(String, nullable=True)  # How they found muuh
    german_level = Column(String, nullable=True)  # A1-C2
    english_level = Column(String, nullable=True)  # A1-C2
    salary_expectation = Column(Integer, nullable=True)
    available_from = Column(String, nullable=True)  # Date string
    
    # AI Analysis scores
    cv_quality_score = Column(Integer, default=0)
    motivation_score = Column(Integer, default=0)
    skill_match_score = Column(Integer, default=0)
    
    # Scoring
    qualification_score = Column(Integer, default=0)
    
    # Conversation tracking
    conversation_stage = Column(Integer, default=0) # Persisted State!
    conversation_history = Column(JSON, default=list)
    
    # CRM Pipeline Status (Kanban)
    # Values: 'NEW', 'SCREENING', 'QUALIFIED', 'INTERVIEW', 'OFFER', 'REJECTED'
    pipeline_status = Column(String, default="NEW")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Lead {self.name or self.whatsapp_number} (Score: {self.qualification_score})>"
