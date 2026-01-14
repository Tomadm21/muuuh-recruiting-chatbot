"""Twilio status callback endpoints."""
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.logger import app_logger

router = APIRouter()

@router.post("/callbacks/status")
async def message_status_callback(
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    To: str = Form(...),
    From: str = Form(...)
):
    """
    Handle Twilio message status callbacks.
    
    Statuses: queued, sent, delivered, read, failed, undelivered
    """
    app_logger.info(f"Message Status: {MessageSid} -> {MessageStatus} (To: {To})")
    
    # In a real production app, we would update a 'Message' table here
    # to track delivery rates and read receipts.
    # For now, we log it to console which is visible in Railway logs.
    
    return {"status": "ok"}
