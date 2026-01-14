from app.db.database import SessionLocal
from app.services.document_service import document_service
from app.services.openai_service import openai_service
from app.models.lead import Lead
from app.utils.logger import app_logger

def run_scoring_pipeline(lead_id: int):
    """
    Background Task:
    1. Downloads CV
    2. Extracts Text
    3. Scores via OpenAI
    4. Updates DB
    """
    app_logger.info(f"Starting Scoring Pipeline for Lead #{lead_id}")
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            app_logger.error("Lead not found in worker")
            return

        if not lead.cv_file_path:
            app_logger.warning("No CV file path to process")
            return

        # 1. Download & Extract
        try:
            file_stream = document_service.download_file_from_url(lead.cv_file_path)
            cv_text = document_service.extract_text_from_pdf(file_stream)
        except Exception as e:
            app_logger.error(f"Download/Extract failed: {e}")
            return # Cannot process
        
        if len(cv_text) < 50:
            app_logger.warning(f"CV text too short or empty. PDF parsing failed?")
            # We can still try to score or just mark error
        
        # 2. AI Grading
        job = lead.position_interest or "General Application"
        result = openai_service.grade_application(cv_text, job)
        
        app_logger.info(f"Scoring Complete: {result.get('score')}")

        # 3. Update DB
        lead.qualification_score = result.get("score", 0)
        lead.projects = result # Storing full JSON (summary, pros, cons)
        
        db.commit()
        
    except Exception as e:
        app_logger.error(f"Worker Error: {e}")
        db.rollback()
    finally:
        db.close()
