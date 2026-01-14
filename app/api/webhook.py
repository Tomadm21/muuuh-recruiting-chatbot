"""Twilio webhook endpoints."""
from fastapi import APIRouter, Form, Response, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from typing import Optional

from app.db.database import get_db
from app.utils.logger import app_logger
from app.services.twilio_service import twilio_service
from app.db import crud
from app.core.flow_engine import flow_engine
from app.core.worker import run_scoring_pipeline

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(""),
    MessageSid: str = Form(...),
    NumMedia: int = Form(0),
    MediaUrl0: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle incoming WhatsApp messages via FlowEngine.
    """
    user_id = From
    twiml_response = MessagingResponse()
    
    try:
        app_logger.info(f"msg from {user_id}: {Body} (Media: {NumMedia})")
        
        # 1. Get/Create Lead
        lead = crud.get_or_create_lead(db, user_id)
        current_state = lead.conversation_stage or 0
        
        # 2. Log
        user_msg_content = Body
        if NumMedia > 0: user_msg_content = f"[MEDIA] {MediaUrl0}"
        crud.add_conversation_message(db, lead, "user", user_msg_content)

        # 3. Determine Response
        response_text = ""
        engine_msg = Body

        if NumMedia > 0 and MediaUrl0:
            # Handle File Upload
            if current_state == 8: # CV
                 crud.update_lead(db, lead, cv_file_path=f"url:{MediaUrl0}")
                 engine_msg = "UPLOAD_DONE"
            elif current_state == 9: # Cover
                 crud.update_lead(db, lead, cover_letter_file_path=f"url:{MediaUrl0}")
                 engine_msg = "UPLOAD_DONE"
            else:
                 # Unexpected file
                 response_text = "Danke für die Datei! Ich kann sie gerade nicht zuordnen, aber sie ist gespeichert."
        
        if not response_text:
            response_text = flow_engine.process_message(user_id, engine_msg, db)

        # 4. Trigger Scoring (If Completed)
        db.refresh(lead)
        if lead.conversation_stage == 99 and lead.qualification_score == 0:
             app_logger.info(f"Triggering Background Scoring for {user_id}")
             background_tasks.add_task(run_scoring_pipeline, lead.id)

        # 5. Send Response
        if response_text:
            twilio_service.send_message(user_id, response_text)
            crud.add_conversation_message(db, lead, "bot", response_text)
            
    except Exception as e:
        app_logger.error(f"WEBHOOK ERROR: {str(e)}", exc_info=True)
        try:
             twilio_service.send_message(user_id, f"⚠️ Fehler: {str(e)}")
        except: pass
            
    return Response(content=str(twiml_response), media_type="application/xml")

@router.get("/webhook")
async def whatsapp_webhook_validation():
    return {"status": "ok", "message": "Webhook active"}
