"""Enhanced lead qualification scoring logic with CV analysis."""
from typing import Dict, Any
from app.utils.logger import app_logger


def calculate_lead_score(lead_data: Dict[str, Any]) -> int:
    """
    Calculate enhanced qualification score for a lead.
    
    NEW Scoring System (0-160 points, normalized to 0-100):
    
    Base Score (0-100):
    - Conversational AI experience: +40 points
    - API/Tech knowledge: +30 points
    - Immediate availability: +20 points
    - Location fit: +10 points
    
    CV Quality Bonus (0-30):
    - Years of experience: +10 (if > 2 years)
    - Relevant projects: +10
    - Certifications: +10
    
    Skill Match Bonus (0-20):
    - From CV analysis
    
    Motivation Bonus (0-10):
    - From cover letter analysis
    
    Args:
        lead_data: Dictionary with lead information
        
    Returns:
        Total score (0-100)
    """
    score = 0
    
    # === BASE SCORE (0-100) ===
    
    # Conversational AI experience (+40)
    if lead_data.get("has_conversational_ai_experience"):
        score += 40
        app_logger.debug("Added 40 points for Conversational AI experience")
    
    # API/Tech knowledge (+30)
    if lead_data.get("has_api_knowledge"):
        score += 30
        app_logger.debug("Added 30 points for API knowledge")
    
    # Availability (+20 for fulltime, +15 for parttime)
    availability = lead_data.get("availability", "").lower()
    if "full" in availability or "vollzeit" in availability:
        score += 20
        app_logger.debug("Added 20 points for fulltime availability")
    elif "part" in availability or "teilzeit" in availability:
        score += 15
        app_logger.debug("Added 15 points for parttime availability")
    
    # Location fit (+10)
    work_mode = lead_data.get("work_mode", "").lower()
    if work_mode in ["remote", "hybrid", "office"]:
        score += 10
        app_logger.debug(f"Added 10 points for {work_mode} work mode fit")
    
    # === CV QUALITY BONUS (0-30) ===
    
    # Years of experience
    years = lead_data.get("years_of_experience", 0)
    if years >= 2:
        score += 10
        app_logger.debug(f"Added 10 points for {years} years of experience")
    
    # Relevant projects
    projects = lead_data.get("projects", [])
    if projects and len(projects) > 0:
        score += 10
        app_logger.debug(f"Added 10 points for {len(projects)} projects")
   
    # Certifications
    certs = lead_data.get("certifications", [])
    if certs and len(certs) > 0:
        score += 10
        app_logger.debug(f"Added 10 points for {len(certs)} certifications")
    
    # === SKILL MATCH BONUS (0-20) ===
    skill_match = lead_data.get("skill_match_score", 0)
    if skill_match > 0:
        # Normalize to max 20 points
        skill_bonus = min(int(skill_match * 0.2), 20)
        score += skill_bonus
        app_logger.debug(f"Added {skill_bonus} points for skill match")
    
    # === MOTIVATION BONUS (0-10) ===
    motivation = lead_data.get("motivation_score", 0)
    if motivation > 0:
        # Normalize to max 10 points
        motivation_bonus = min(int(motivation * 0.1), 10)
        score += motivation_bonus
        app_logger.debug(f"Added {motivation_bonus} points for motivation")
    
    # === NORMALIZE TO 0-100 ===
    # Max possible: 100 + 30 + 20 + 10 = 160
    final_score = min(int((score / 160) * 100), 100)
    
    app_logger.info(f"Calculated enhanced lead score: {score}/160 → {final_score}/100")
    return final_score


def get_priority_tier(score: int) -> str:
    """
    Get priority tier based on score.
    
    Args:
        score: Qualification score
        
    Returns:
        Priority tier: 'high', 'medium', or 'low'
    """
    if score >= 70:
        return "high"
    elif score >= 40:
        return "medium"
    else:
        return "low"


def get_score_feedback(score: int) -> str:
    """
    Get user-friendly feedback based on score.
    
    Args:
        score: Qualification score
        
    Returns:
        Feedback message
    """
    if score >= 90:
        return "🌟 Dein Profil sieht hervorragend aus!"
    elif score >= 70:
        return "✨ Dein Profil passt sehr gut!"
    elif score >= 50:
        return "👍 Dein Profil ist interessant!"
    else:
        return "📝 Vielen Dank für dein Interesse!"
