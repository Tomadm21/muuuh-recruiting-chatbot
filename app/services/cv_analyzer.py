"""AI-powered CV analysis service."""
import json
from typing import Dict, Any
from openai import OpenAI

from app.config import settings
from app.utils.logger import app_logger


class CVAnalyzer:
    """Service for analyzing CVs and cover letters with AI."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Analyze CV and extract structured information.
        
        Args:
            cv_text: Extracted text from CV
            
        Returns:
            Dictionary with extracted CV data
        """
        try:
            function_schema = {
                "name": "extract_cv_data",
                "description": "Extract structured information from a CV",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "years_of_experience": {"type": "integer"},
                        "education_level": {
                            "type": "string",
                            "enum": ["Abitur", "Ausbildung", "Bachelor", "Master", "PhD", "Other"]
                        },
                        "skills": {
                            "type": "object",
                            "description": "Technical skills mentioned",
                            "properties": {
                                "python": {"type": "boolean"},
                                "javascript": {"type": "boolean"},
                                "apis": {"type": "boolean"},
                                "make_com": {"type": "boolean"},
                                "n8n": {"type": "boolean"},
                                "zapier": {"type": "boolean"},
                                "openai": {"type": "boolean"},
                                "conversational_ai": {"type": "boolean"},
                                "parloa": {"type": "boolean"}
                            }
                        },
                        "projects": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of notable projects"
                        },
                        "certifications": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "quality_score": {
                            "type": "integer",
                            "description": "CV quality score 0-100"
                        }
                    },
                    "required": ["years_of_experience", "skills", "quality_score"]
                }
            }
            
            prompt = f"""Analyze this CV and extract structured information.
            
Be thorough and accurate. Look for:
- Contact information
- Years of professional experience
- Technical skills (especially: Python, JavaScript, APIs, Make.com, n8n, Zapier, OpenAI, Conversational AI, Parloa)
- Projects and achievements
- Education
- Certifications

Rate the CV quality (0-100) based on:
- Completeness
- Professional presentation
- Relevant experience
- Project quality

CV Text:
{cv_text[:4000]}  # Limit to prevent token overload
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                functions=[function_schema],
                function_call={"name": "extract_cv_data"}
            )
            
            result = json.loads(response.choices[0].message.function_call.arguments)
            app_logger.info(f"CV analysis complete. Quality score: {result.get('quality_score', 0)}")
            
            return result
            
        except Exception as e:
            app_logger.error(f"Error analyzing CV: {e}")
            return {
                "years_of_experience": 0,
                "skills": {},
                "quality_score": 0
            }
    
    def analyze_cover_letter(self, letter_text: str) -> Dict[str, Any]:
        """
        Analyze cover letter for motivation and fit.
        
        Args:
            letter_text: Extracted text from cover letter
            
        Returns:
            Dictionary with motivation score and analysis
        """
        try:
            prompt = f"""Analyze this cover letter for a Conversational AI Developer position at muuh.

Rate the motivation and fit (0-100) based on:
- Genuine interest in Conversational AI
- Understanding of muuh's business
- Mentions of Parloa, generative AI, or related technologies
- Quality of writing
- Specific examples and achievements

Cover Letter:
{letter_text[:2000]}

Return a JSON with:
{{"motivation_score": <0-100>, "mentions_muuh": <boolean>, "mentions_parloa": <boolean>, "quality": "low|medium|high"}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            app_logger.info(f"Cover letter analysis complete. Motivation: {result.get('motivation_score', 0)}")
            
            return result
            
        except Exception as e:
            app_logger.error(f"Error analyzing cover letter: {e}")
            return {
                "motivation_score": 0,
                "mentions_muuh": False,
                "mentions_parloa": False,
                "quality": "low"
            }
    
    def calculate_skill_match_score(self, skills: Dict[str, bool]) -> int:
        """
        Calculate skill match score based on extracted skills.
        
        Args:
            skills: Dictionary of skills (skill: boolean)
            
        Returns:
            Skill match score 0-100
        """
        score = 0
        
        # Core skills (5 points each)
        core_skills = ["apis", "python", "javascript"]
        for skill in core_skills:
            if skills.get(skill, False):
                score += 5
        
        # Automation tools (5 points each)
        automation_tools = ["make_com", "n8n", "zapier"]
        for tool in automation_tools:
            if skills.get(tool, False):
                score += 5
        
        # AI skills (10 points each)
        ai_skills = ["openai", "conversational_ai"]
        for skill in ai_skills:
            if skills.get(skill, False):
                score += 10
        
        # Parloa (bonus 15 points)
        if skills.get("parloa", False):
            score += 15
        
        return min(score, 100)


# Global instance
cv_analyzer = CVAnalyzer()
