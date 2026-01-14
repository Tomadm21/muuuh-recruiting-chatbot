import requests
from io import BytesIO
from PyPDF2 import PdfReader
from app.config import settings
from app.utils.logger import app_logger

class DocumentService:
    """
    Handles downloading and text extraction from documents (CVs).
    """

    def download_file_from_url(self, url: str) -> BytesIO:
        """
        Downloads file from Twilio (or other) URL.
        Uses Twilio Auth if it looks like a Twilio URL.
        """
        try:
            auth = None
            if "twilio.com" in url:
                auth = (settings.twilio_account_sid, settings.twilio_auth_token)
            
            # Remove 'url:' prefix if present (stored in DB)
            clean_url = url.replace("url:", "").strip()
            
            response = requests.get(clean_url, auth=auth, timeout=15)
            response.raise_for_status()
            
            return BytesIO(response.content)
        except Exception as e:
            app_logger.error(f"Error downloading file {url}: {e}")
            raise e

    def extract_text_from_pdf(self, file_stream: BytesIO) -> str:
        """
        Extracts raw text from a PDF stream.
        """
        try:
            reader = PdfReader(file_stream)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text.strip()
        except Exception as e:
            app_logger.error(f"Error extracting PDF text: {e}")
            return ""

document_service = DocumentService()
