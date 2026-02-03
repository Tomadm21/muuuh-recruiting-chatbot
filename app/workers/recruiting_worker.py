"""Unified recruitment worker for processing document uploads and scoring."""
from sqlalchemy.orm import Session
from app.db import crud
from app.db.database import SessionLocal
from app.services.document_service import document_service
from app.services.openai_service import openai_service
from app.services.twilio_service import twilio_service
from app.core.scoring import calculate_lead_score, get_score_feedback
from app.utils.logger import app_logger
from app.models.lead import Lead

async def run_unified_recruiting_pipeline(lead_id: int, media_url: str = None, media_content_type: str = None, body: str = ""):
    """
    Unified background task:
    1. Downloads/Extracts documents if media_url provided.
    2. Analyzes CV/Cover and updates lead data.
    3. Calculates final scores.
    4. Sends feedback to candidate.
    """
    app_logger.info(f"🚀 Starting Unified Pipeline for Lead #{lead_id}")
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            app_logger.error("Lead not found in worker")
            return

        # 1. Document Processing (Optional)
        if media_url:
            file_io = document_service.download_file_from_url(media_url)
            file_content = file_io.getvalue()
            doc_text = document_service.extract_text(file_content, media_content_type or "application/pdf")
            
            if not doc_text:
                twilio_service.send_message(lead.whatsapp_number, "⚠️ Konnte das Dokument nicht lesen. Bitte sende ein PDF.")
                return

            # Determine type
            is_cover = any(w in body.lower() for w in ["anschreiben", "cover", "motivationsschreiben"])
            
            if is_cover:
                analysis = openai_service.analyze_cover_letter(doc_text)
                crud.update_lead(db, lead, 
                                 cover_letter_file_path=f"archived_url:{media_url[:100]}", 
                                 motivation_score=analysis.get("motivation_score", 0))
            else:
                analysis = openai_service.analyze_cv(doc_text)
                skill_match = openai_service.calculate_skill_match_score(analysis.get("skills", {}))
                crud.update_lead(db, lead,
                    cv_file_path=f"archived_url:{media_url[:100]}",
                    first_name=analysis.get("first_name") or lead.name,
                    years_of_experience=analysis.get("years_of_experience", 0),
                    skills=analysis.get("skills", {}),
                    cv_quality_score=analysis.get("quality_score", 0),
                    skill_match_score=skill_match
                )

        # 2. Final Scoring & Feedback
        db.refresh(lead)
        new_score = calculate_lead_score({
            "has_conversational_ai_experience": lead.has_conversational_ai_experience,
            "has_api_knowledge": lead.has_api_knowledge,
            "availability": lead.availability,
            "work_mode": lead.work_mode,
            "years_of_experience": lead.years_of_experience or 0,
            "skill_match_score": lead.skill_match_score or 0,
            "motivation_score": lead.motivation_score or 0
        })
        
        crud.update_lead(db, lead, qualification_score=new_score)
        
        # 3. Notify Candidate
        if lead.conversation_stage == 99:
            feedback = get_score_feedback(new_score)
            twilio_service.send_message(lead.whatsapp_number, f"✅ Deine Bewerbung wurde analysiert!\n🎯 Score: {new_score}/100\n\n{feedback}")

    except Exception as e:
        app_logger.error(f"❌ Worker Error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()
