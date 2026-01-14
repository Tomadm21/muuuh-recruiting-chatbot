"""Document processing utilities for CV analysis."""
import os
import requests
from typing import Dict, Any, Optional
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO

from app.utils.logger import app_logger


def download_media(media_url: str, auth_token: str) -> Optional[bytes]:
    """
    Download media file from Twilio.
    
    Args:
        media_url: URL to the media file
        auth_token: Twilio auth token for authentication
        
    Returns:
        File content as bytes or None if failed
    """
    try:
        response = requests.get(
            media_url,
            auth=('AC' + auth_token.split('AC')[1] if 'AC' in auth_token else auth_token, auth_token),
            timeout=30
        )
        response.raise_for_status()
        return response.content
    except Exception as e:
        app_logger.error(f"Error downloading media: {e}")
        return None


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF file.
    
    Args:
        file_content: PDF file as bytes
        
    Returns:
        Extracted text
    """
    try:
        pdf_file = BytesIO(file_content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        app_logger.error(f"Error extracting PDF text: {e}")
        return ""


def extract_text_from_docx(file_content: bytes) -> str:
    """
    Extract text from DOCX file.
    
    Args:
        file_content: DOCX file as bytes
        
    Returns:
        Extracted text
    """
    try:
        docx_file = BytesIO(file_content)
        doc = Document(docx_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        app_logger.error(f"Error extracting DOCX text: {e}")
        return ""


def extract_document_text(file_content: bytes, content_type: str) -> str:
    """
    Extract text from document based on content type.
    
    Args:
        file_content: File content as bytes
        content_type: MIME type of the file
        
    Returns:
        Extracted text
    """
    if "pdf" in content_type.lower():
        return extract_text_from_pdf(file_content)
    elif "word" in content_type.lower() or "docx" in content_type.lower():
        return extract_text_from_docx(file_content)
    else:
        app_logger.warning(f"Unsupported content type: {content_type}")
        return ""


def save_document(file_content: bytes, filename: str, lead_id: int) -> str:
    """
    Save document to local storage.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        lead_id: Lead ID for organization
        
    Returns:
        Path to saved file
    """
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create lead-specific directory
        lead_dir = os.path.join(upload_dir, f"lead_{lead_id}")
        os.makedirs(lead_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(lead_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        app_logger.info(f"Saved document to {file_path}")
        return file_path
    except Exception as e:
        app_logger.error(f"Error saving document: {e}")
        return ""
