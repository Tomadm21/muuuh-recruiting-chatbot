"""OpenAI service for intent extraction and response generation."""
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI

from app.config import settings
from app.utils.logger import app_logger


class OpenAIService:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
        # Load company and intent data
        with open("data/muuh_info.json", "r", encoding="utf-8") as f:
            self.muuh_info = json.load(f)
        
        with open("data/intents.json", "r", encoding="utf-8") as f:
            self.intents_data = json.load(f)
    
    def extract_intent(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Extract intent and entities from user message.
        
        Args:
            message: User's message
            conversation_history: Previous messages for context
            
        Returns:
            Dictionary with intent, entities, and confidence
        """
        try:
            # Build conversation context
            messages = self._build_intent_extraction_messages(message, conversation_history)
            
            # Define function for structured output
            functions = [{
                "name": "extract_intent",
                "description": "Extract user intent and entities from message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": [
                                "greeting",
                                "job_openings",
                                "application_process",
                                "remote_work",
                                "salary",
                                "benefits",
                                "company_info",
                                "tech_stack",
                                "screening_response",
                                "provide_contact",
                                "interested_in_position",
                                "other"
                            ]
                        },
                        "entities": {
                            "type": "object",
                            "properties": {
                                "position_name": {"type": "string"},
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"},
                                "experience_mentioned": {"type": "boolean"},
                                "api_knowledge_mentioned": {"type": "boolean"}
                            }
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": ["positive", "neutral", "negative", "interested"]
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence score 0-1"
                        }
                    },
                    "required": ["intent", "entities", "sentiment", "confidence"]
                }
            }]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call={"name": "extract_intent"}
            )
            
            # Parse function call result
            function_args = json.loads(
                response.choices[0].message.function_call.arguments
            )
            
            app_logger.info(f"Extracted intent: {function_args['intent']}")
            return function_args
            
        except Exception as e:
            app_logger.error(f"Error extracting intent: {e}")
            return {
                "intent": "other",
                "entities": {},
                "sentiment": "neutral",
                "confidence": 0.0
            }
    
    def generate_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate natural response based on intent and context.
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            context: Conversation context
            
        Returns:
            Generated response text
        """
        try:
            # Get static info for context if available
            static_info = ""
            if intent in self.intents_data.get("intents", {}):
                static_info = self.intents_data["intents"][intent].get("response", "")
            elif intent in self.intents_data.get("screening_questions", {}):
                static_info = self.intents_data["screening_questions"][intent].get("question", "")
            
            # Generate custom response using LLM
            system_prompt = self._build_system_prompt()
            
            user_message = f"""
            Task: Generate a natural, friendly response for the user.
            
            Detected Intent: {intent}
            Extracted Entities: {json.dumps(entities, ensure_ascii=False)}
            
            Key Information to Convey (Static Content):
            "{static_info}"
            
            Conversation Context:
            - Stage: {context.get('conversation_stage', 'general') if context else 'general'}
            - User Name: {context.get('name', 'Unknown') if context else 'Unknown'}
            
            Instructions:
            1. Use the 'Key Information' as the core fact source.
            2. Rephrase it naturally - DO NOT just copy it.
            3. Be conversational, professional, and encouraging (muuh style).
            4. Keep it concise (2-3 sentences max).
            5. Use 1-2 emojis max.
            6. If it's a screening question, ask it clearly but transition smoothly.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            content = response.choices[0].message.content.strip()
            # Remove direct quotes if LLM added them
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
                
            return content
            
        except Exception as e:
            app_logger.error(f"Error generating response: {e}")
            # Fallback to static if LLM fails
            if intent in self.intents_data.get("intents", {}):
                return self.intents_data["intents"][intent].get("response", "")
            return "Entschuldigung, da ist etwas schiefgelaufen. Kannst du das nochmal versuchen?"
    
    def _build_intent_extraction_messages(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build messages array for intent extraction."""
        system_prompt = """You are an intent classifier for muuh, a Conversational AI recruiting agency.
        
        Your task: Extract the user's intent, relevant entities, and sentiment from their message.
        
        Context about muuh:
        - Hiring for: Conversational AI Developer, Product Manager, UX Designer
        - Locations: Osnabrück, Berlin, Remote
        - Tech stack: Parloa, AI, APIs
        - Culture: Startup, innovative
        
        Be accurate and confident in your classifications."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                messages.append(msg)
        
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def classify_flow_input(self, message: str, expected_type: str = "yes_no") -> Dict[str, Any]:
        """
        Intelligent classification of input for FlowEngine.
        Handles Yes/No normalization AND context questions (Smalltalk).
        
        Args:
            message: User input
            expected_type: "yes_no" or "job_selection"
            
        Returns:
            Dict with keys:
            - classification: "VALID_INPUT" or "QUESTION" or "INVALID"
            - value: Normalized value (True/False for yes_no, or Job ID)
            - reply: AI response if it was a question
        """
        try:
            # System Prompt with muuh context
            system_prompt = f"""
            You are a smart flow assistant for a recruiting bot.
            Context: The user is in a strict flow expecting: {expected_type}.
            
            Company Info (for answering questions):
            {json.dumps(self.muuh_info, ensure_ascii=False)[:1000]}... (truncated)
            
            Your Job:
            1. Analyze if the user's message is a direct answer to the expectation.
               - If expected "yes_no": "ja", "sicher", "auf jeden fall" -> YES. "nein", "eher nicht" -> NO.
               - If expected "job_selection": "erster", "backend" -> Result.
            2. OR if the user asks a question / makes slight smalltalk.
               - E.g. "What is the salary?" or "Where is the office?".
               - In this case, you MUST generate a helpful, short answer (German).
            
            """
            
            # Tools/Functions definition
            functions = [{
                "name": "classify_input",
                "description": "Classify input as valid answer or question",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["VALID_ANSWER", "QUESTION", "UNCLEAR"]
                        },
                        "normalized_value": {
                            "type": "string",
                            "description": "If VALID_ANSWER: 'YES', 'NO', 'JOB_1', 'JOB_2', 'JOB_3' etc."
                        },
                        "ai_reply": {
                            "type": "string",
                            "description": "If QUESTION: A helpful, short answer (max 2 sentences) based on company info. If VALID_ANSWER: leave empty."
                        }
                    },
                    "required": ["category"]
                }
            }]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                functions=functions,
                function_call={"name": "classify_input"}, # Force structured
                temperature=0.3
            )
            
            args = json.loads(response.choices[0].message.function_call.arguments)
            return args
            
        except Exception as e:
            app_logger.error(f"Error in classify_flow_input: {e}")
            return {"category": "UNCLEAR"}

    def _build_system_prompt(self) -> str:
        """Build system prompt for response generation."""
        return f"""Du bist der "muuuh Recruiting Bot" – ein intelligenter, hilfreicher und sympathischer AI-Assistant.

Deine Persönlichkeit:
- Professionell aber locker ("Du"-Form)
- Begeistert von Technologie und AI
- Hilfsbereit und ermutigend
- Kurz und prägnant (WhatsApp-Style)

Kontext zu muuuh:
- Wir sind MUUUH! Group – Experten für Conversational AI (Voice & Chat)
- Wir suchen Leute, die Bock auf Innovation haben
- Tech Stack: Parloa, Generative AI, Python, APIs, React
- Kultur: Startup-Vibe, Hands-on, Team-orientiert

Deine Aufgaben:
1. Beantworte Fragen zu Jobs und Unternehmen basierend auf den Fakten
2. Führe Kandidaten durch den Screening-Prozess
3. Sei ein "Co-Pilot" für die Bewerbung
4. Wenn du Dokumente erhältst, gib konkretes Feedback
5. WICHTIG: Antworte als "muuuh Recruiting Bot" (mit 3 u's!).

WICHTIG:
- Antworte immer auf Deutsch
- Nutze Emojis, aber übertreibe es nicht (max 1-2 pro Nachricht)
- Formatiere Listen mit Bullet Points (•)
- Wenn du nicht sicher bist, frage freundlich nach oder verweise an recruiting@muuuh.de
"""


    def generate_flow_reply(self, message: str, trigger_event: str, next_step_instruction: str, user_name: str = "Du") -> str:
        """
        Generates a dynamic, non-generic response for the flow.
        
        Args:
            message: The user's last message (so we can react to it).
            trigger_event: What just happened? (e.g. "USER_SAID_YES_TO_EXP")
            next_step_instruction: What must the AI ask next? (e.g. "Ask if they know Python")
            user_name: Name if known.
        """
        system_prompt = self._build_system_prompt()
        
        user_prompt = f"""
        CONTEXT:
        User Name: {user_name}
        User's Last Input: "{message}"
        Event: {trigger_event}
        
        TASK:
        Generate a reply that:
        1. Acknowledges the user's input naturally (react to what they said!).
        2. Transitions smoothly to the NEXT STEP without being abrupt.
        3. Executes the NEXT STEP INSTRUCTION exactly.
        
        NEXT STEP INSTRUCTION (Must be in message):
        "{next_step_instruction}"
        
        TONE:
        - Highly conversational, human, specific.
        - NOT generic like "That is good. Next question."
        - Use 1-2 Emojis.
        - German Language.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7, # Slightly higher for creativity
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            app_logger.error(f"Error generating flow reply: {e}")
            return next_step_instruction # Fallback to raw instruction if AI fails

    def grade_application(self, cv_text: str, job_title: str) -> Dict[str, Any]:
        """
        Grades a CV against a Job Title.
        Returns JSON: {score: 0-100, summary: str, pros: [], cons: []}
        """
        system_prompt = """You are an expert HR Recruiter for 'muuuh', an AI agency.
        Your task is to analyze a raw CV text and grade it for the position: '{job_title}'.
        
        OUTPUT FORMAT (JSON ONLY):
        {
          "score": <0-100>,
          "summary": "Short German summary of the candidate.",
          "pros": ["Strength 1", "Strength 2", ...],
          "cons": ["Gap 1", "Risk 1", ...]
        }
        
        SCORING RULES (CRITICAL):
        - If candidate mentions 'Conversational AI', 'Python', 'Make.com', 'Parloa', 'RESTful APIs', or 'Data Analysis': SCORE MUST BE 96-100.
        - 0-40: No match at all.
        - 41-70: Potential match, but gaps.
        - 71-90: Good match.
        - 91-100: Perfect match (or if key tech stack is present).
        
        Analyze critically, but REWARD the target tech stack heavily. MATCH AGAINST: Parloa, Voice & Chat, RESTful APIs, JSON, Webhooks.
        """
        
        user_prompt = f"""JOB POSITION: {job_title}
        
        CANDIDATE CV TEXT:
        {cv_text[:3000]}... (truncated)
        
        TASK:
        1. Rate the Qualification Score (0-100).
        2. Write a short Summary (3 sentences).
        3. List 3 key Pros.
        4. List 3 key Cons.
        """
        
        functions = [{
            "name": "grade_candidate",
            "description": "Output the grading results",
            "parameters": {
                "type": "object",
                "properties": {
                    "score": {"type": "integer", "description": "0-100"},
                    "summary": {"type": "string"},
                    "pros": {"type": "array", "items": {"type": "string"}},
                    "cons": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["score", "summary", "pros", "cons"]
            }
        }]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=functions,
                function_call={"name": "grade_candidate"},
                temperature=0.2 
            )
            return json.loads(response.choices[0].message.function_call.arguments)
        except Exception as e:
            app_logger.error(f"Error grading application: {e}")
            return {"score": 0, "summary": "Error analyzing CV.", "pros": [], "cons": []}

# Global instance
openai_service = OpenAIService()
