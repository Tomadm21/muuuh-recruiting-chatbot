"""Background tasks for document processing."""
from sqlalchemy.orm import Session
from app.db import crud
from app.utils.document_processor import download_media, extract_document_text, save_document
from app.services.cv_analyzer import cv_analyzer
from app.services.twilio_service import twilio_service
from app.core.scoring import calculate_lead_score, get_score_feedback
from app.utils.logger import app_logger
from app.config import settings

async def process_document_upload(
    message_sid: str,
    media_url: str,
    media_content_type: str,
    user_id: str,
    body: str,
    db: Session
):
    """
    Process document upload in background.
    
    Args:
        message_sid: Twilio message ID
        media_url: URL to media file
        media_content_type: Content type
        user_id: User's WhatsApp number
        body: Message body
        db: Database session
    """
    try:
        app_logger.info(f"Starting background processing for {message_sid}")
        
        # Get lead
        lead = crud.get_or_create_lead(db, user_id)
        
        # Download document
        file_content = download_media(media_url, settings.twilio_auth_token)
        
        if not file_content:
            twilio_service.send_message(user_id, "❌ Konnte das Dokument leider nicht herunterladen. Bitte versuche es nochmal.")
            return

        # Extract text from document
        doc_text = extract_document_text(file_content, media_content_type)
        
        if not doc_text:
            twilio_service.send_message(user_id, "❌ Konnte den Text aus dem Dokument nicht lesen. Bitte sende ein PDF oder DOCX.")
            return

        # Determine document type
        is_cv = any(word in body.lower() for word in ["cv", "lebenslauf", "resume"])
        is_cover = any(word in body.lower() for word in ["anschreiben", "cover", "motivationsschreiben"])
        
        # Default to CV if not specified
        if not is_cv and not is_cover:
            is_cv = True
        
        if is_cv:
            # Analyze CV (Time intensive!)
            cv_data = cv_analyzer.analyze_cv(doc_text)
            
            # Save file
            file_path = save_document(file_content, f"cv_{message_sid}.pdf", lead.id)
            
            # Update lead with CV data
            crud.update_lead(db, lead,
                cv_file_path=file_path,
                first_name=cv_data.get("first_name"),
                last_name=cv_data.get("last_name"),
                email=cv_data.get("email") or lead.email,
                phone=cv_data.get("phone") or lead.phone,
                years_of_experience=cv_data.get("years_of_experience", 0),
                skills=cv_data.get("skills", {}),
                education_level=cv_data.get("education_level"),
                projects=cv_data.get("projects", []),
                certifications=cv_data.get("certifications", []),
                cv_quality_score=cv_data.get("quality_score", 0)
            )
            
            # Calculate skill match
            skill_match = cv_analyzer.calculate_skill_match_score(cv_data.get("skills", {}))
            crud.update_lead(db, lead, skill_match_score=skill_match)
            
            # Recalculate overall score
            new_score = calculate_lead_score({
                "has_conversational_ai_experience": lead.has_conversational_ai_experience,
                "has_api_knowledge": lead.has_api_knowledge,
                "availability": lead.availability,
                "work_mode": lead.work_mode,
                "years_of_experience": cv_data.get("years_of_experience", 0),
                "projects": cv_data.get("projects", []),
                "certifications": cv_data.get("certifications", []),
                "skill_match_score": skill_match,
                "motivation_score": lead.motivation_score
            })
            crud.update_lead(db, lead, qualification_score=new_score)
            
            response = f"✅ Analyse abgeschlossen!\n\n"
            response += f"📊 CV Qualität: {cv_data.get('quality_score', 0)}/100\n"
            response += f"🎯 Dein neuer Score: {new_score}/100\n\n"
            
            # Check if cover letter missing
            if not lead.cover_letter_file_path:
                response += "Hast du auch ein Anschreiben für mich? Das gibt Extrapunkte! 📝"
            else:
                response += "Deine Bewerbung ist jetzt komplett! Das HR-Team meldet sich. 🚀"
                
            twilio_service.send_message(user_id, response)
            
        elif is_cover:
            # Analyze cover letter (Time intensive!)
            cover_data = cv_analyzer.analyze_cover_letter(doc_text)
            
            # Save file
            file_path = save_document(file_content, f"cover_{message_sid}.pdf", lead.id)
            
            # Update lead
            crud.update_lead(db, lead,
                cover_letter_file_path=file_path,
                motivation_score=cover_data.get("motivation_score", 0)
            )
            
            # Recalculate score
            new_score = calculate_lead_score({
                "has_conversational_ai_experience": lead.has_conversational_ai_experience,
                "has_api_knowledge": lead.has_api_knowledge,
                "availability": lead.availability,
                "work_mode": lead.work_mode,
                "years_of_experience": lead.years_of_experience,
                "projects": lead.projects,
                "certifications": lead.certifications,
                "skill_match_score": lead.skill_match_score,
                "motivation_score": cover_data.get("motivation_score", 0)
            })
            crud.update_lead(db, lead, qualification_score=new_score)
            
            feedback = get_score_feedback(new_score)
            
            response = f"✅ Anschreiben analysiert!\n\n"
            response += f"💪 Motivation Score: {cover_data.get('motivation_score', 0)}/100\n"
            response += f"🎯 Dein Finaler Score: {new_score}/100\n\n"
            response += f"{feedback}\n\n"
            response += "Vielen Dank! Ich habe alles weitergeleitet. 📨"
            
            twilio_service.send_message(user_id, response)
            
    except Exception as e:
        app_logger.error(f"Error in background document processing: {e}")
        twilio_service.send_message(user_id, "⚠️ Bei der Analyse gab es ein kleines Problem. Unser HR-Team schaut sich das Dokument manuell an!")
