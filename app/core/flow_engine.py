import re
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.db import crud
from app.models.lead import Lead
from app.services.openai_service import openai_service

class FlowEngine:
    """
    The 'Iron Logic' engine.
    Manages conversation flow.
    """

    # STATE CONSTANTS
    STATE_IDLE = 0
    STATE_GREETED = 1
    STATE_JOB_SELECTED = 2
    STATE_REQ_1 = 3
    STATE_REQ_2 = 4
    STATE_REQ_3 = 5
    STATE_NAME = 6
    STATE_PHONE = 7
    STATE_CV = 8
    STATE_COVER = 9
    STATE_ADDITIONAL_AVAILABILITY = 10
    STATE_ADDITIONAL_SALARY = 11
    STATE_ADDITIONAL_SOURCE = 12
    STATE_ADDITIONAL_LANG = 13
    STATE_COMPLETED = 99

    def __init__(self):
        # Dispatch table for state handlers
        self._handlers = {
            self.STATE_IDLE: self._handle_idle,
            self.STATE_GREETED: self._handle_greeted,
            self.STATE_JOB_SELECTED: self._handle_job_selected,
            self.STATE_REQ_1: self._handle_req_1,
            self.STATE_REQ_2: self._handle_req_2,
            self.STATE_REQ_3: self._handle_req_3,
            self.STATE_NAME: self._handle_name,
            self.STATE_PHONE: self._handle_phone,
            self.STATE_CV: self._handle_cv,
            self.STATE_COVER: self._handle_cover,
            self.STATE_ADDITIONAL_AVAILABILITY: self._handle_avail,
            self.STATE_ADDITIONAL_SALARY: self._handle_salary,
            self.STATE_ADDITIONAL_SOURCE: self._handle_source,
            self.STATE_ADDITIONAL_LANG: self._handle_lang,
            self.STATE_COMPLETED: self._handle_completed,
        }

    def process_message(self, user_id: str, message: str, db: Session) -> str:
        # 1. GLOBAL RESET
        if message.strip().lower() in ["#reset", "#start", "reset", "start", "restart"]:
            self._reset_state(user_id, db)
            return "🔄 System zurückgesetzt.\n\nHallo! 👋 Willkommen beim muuuh Recruiting Bot.\n\nWas möchtest du tun?\n1️⃣ Jobs ansehen\n2️⃣ Infos über muuuh erhalten"

        # 2. LOAD STATE
        lead = crud.get_or_create_lead(db, user_id)
        current_state = lead.conversation_stage or 0
        
        # 3. ROUTING
        handler = self._handlers.get(current_state, self._handle_idle)
        new_state, response = handler(message, lead, db)
        
        # 4. SAVE STATE
        lead.conversation_stage = new_state
        db.commit()
        db.refresh(lead)
        
        return response

    def _reset_state(self, user_id: str, db: Session):
        lead = crud.get_or_create_lead(db, user_id)
        lead.conversation_stage = 0
        db.commit()

    def _handle_idle(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        return self.STATE_GREETED, "Hallo! 👋 \n\nWillkommen im Karriere-Chat von **muuuh!** 🐮\n\nSuchst du einen **Job** 💼 oder möchtest du **Infos** ℹ️?"

    def _handle_greeted(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        msg_lower = message.lower().strip()
        analysis = openai_service.classify_flow_input(message, "job_or_info")
        cat = analysis.get("category")
        val = analysis.get("normalized_value")

        if (cat == "VALID_ANSWER" and val == "JOB") or "job" in msg_lower or "1" in msg_lower:
            return self.STATE_JOB_SELECTED, "Klasse! Hier sind unsere offenen Stellen: 🚀\n\n1️⃣ **(Junior) Conversational AI Developer** 🤖\n2️⃣ **Senior Python Backend Dev** 🐍\n3️⃣ **Trainee Recruiting** 🎓\n\nWelche Position findest du spannend?"
        elif (cat == "VALID_ANSWER" and val == "INFO") or "info" in msg_lower or "2" in msg_lower:
            return self.STATE_GREETED, "Wir sind **muuuh!** – eine innovative Agentur aus Osnabrück. 🐮\nWir lieben Kommunikation und Technologie.\n\nMöchtest du unsere Jobs sehen? Schreib uns einfach!"
        elif cat == "QUESTION":
            return self.STATE_GREETED, f"{analysis.get('ai_reply')}\n\n(Möchtest du dir die Jobs anschauen?)"
        else:
            return self.STATE_GREETED, "Entschuldige, ich habe das nicht verstanden. 😅\nGeht es dir um **Jobs** oder **Infos**?"

    def _handle_job_selected(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        msg_lower = message.lower().strip()
        analysis = openai_service.classify_flow_input(message, "job_selection")
        cat = analysis.get("category")
        
        if cat == "QUESTION":
            return self.STATE_JOB_SELECTED, f"{analysis.get('ai_reply')}\n\n(Welchen Job meintest du?)"
        
        job_name = message
        valid_job = False
        
        if "1" in message or (analysis.get("normalized_value") == "JOB_1") or "junior" in msg_lower: 
            job_name = "(Junior) Conversational AI Developer"
            valid_job = True
        elif "2" in message or (analysis.get("normalized_value") == "JOB_2") or "backend" in msg_lower: 
            job_name = "Senior Backend Dev"
            valid_job = True
        elif "3" in message or (analysis.get("normalized_value") == "JOB_3") or "trainee" in msg_lower: 
            job_name = "Trainee Recruiting"
            valid_job = True
        
        if not valid_job:
            return self.STATE_JOB_SELECTED, "Das habe ich nicht ganz verstanden. Welche Stelle meinst du? 👇"

        crud.update_lead(db, lead, position_interest=job_name)
        
        reply = openai_service.generate_flow_reply(
            message=message,
            trigger_event=f"USER_SELECTED_JOB_{job_name}",
            next_step_instruction=f"Confirm the choice '{job_name}' enthusiastically. Then ask Question 1 (K.O.): Do they have experience with Chatbots or LLMs (e.g. OpenAI)? (Ask for Yes/No)",
            user_name=lead.name or "Du"
        )
        return self.STATE_REQ_1, reply

    def _handle_req_1(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        analysis = openai_service.classify_flow_input(message, "yes_no")
        cat = analysis.get("category")
        
        if cat == "VALID_ANSWER":
            if analysis.get("normalized_value") == "YES":
                crud.update_lead(db, lead, has_conversational_ai_experience=True)
                reply = openai_service.generate_flow_reply(
                    message=message,
                    trigger_event="USER_HAS_AI_EXPERIENCE",
                    next_step_instruction="React positively to their AI experience. Then ask Question 2: Are they fit in Python and APIs? (Ask for Yes/No)",
                    user_name=lead.name or "Du"
                )
                return self.STATE_REQ_2, reply
            else:
                return self.STATE_COMPLETED, "Schade! Für diese Position setzen wir Vorerfahrung voraus. 😕\n\nAber bewirb dich gerne initiativ über unsere Website!\n\n(Session beendet)"
        elif cat == "QUESTION":
            return self.STATE_REQ_1, f"{analysis.get('ai_reply')}\n\n(Aber zur Frage: Hast du Erfahrung? Ja oder Nein?)"
        else:
            return self.STATE_REQ_1, "Bitte antworte mit **Ja**, **Nein** oder stelle eine Frage."

    def _handle_req_2(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        analysis = openai_service.classify_flow_input(message, "yes_no")
        cat = analysis.get("category")

        if cat == "VALID_ANSWER":
            if analysis.get("normalized_value") == "YES":
                crud.update_lead(db, lead, has_api_knowledge=True)
                reply = openai_service.generate_flow_reply(
                    message=message,
                    trigger_event="USER_KNOWS_PYTHON_AND_API",
                    next_step_instruction="Great! Now Question 3: Do they have a mindset for Innovation & Dynamics? (Ask for Yes/No)",
                    user_name=lead.name or "Du"
                )
                return self.STATE_REQ_3, reply
            else:
                return self.STATE_COMPLETED, "Danke für deine Ehrlichkeit! Leider sind Python-Kenntnisse hier essenziell. Vielleicht passt eine andere Stelle? 👋"
        elif cat == "QUESTION":
            return self.STATE_REQ_2, f"{analysis.get('ai_reply')}\n\n(Zurück zur Frage: Bist du fit in Python? Ja/Nein)"
        else:
            return self.STATE_REQ_2, "Bitte antworte mit **Ja** oder **Nein**."

    def _handle_req_3(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        analysis = openai_service.classify_flow_input(message, "yes_no")
        cat = analysis.get("category")
        
        if cat == "VALID_ANSWER":
            if analysis.get("normalized_value") == "YES":
                reply = openai_service.generate_flow_reply(
                    message=message,
                    trigger_event="USER_HAS_INNOVATION_MINDSET",
                    next_step_instruction="Celebrate that they are a perfect match! Now ask for their First and Last Name to save the application.",
                    user_name=lead.name or "Du"
                )
                return self.STATE_NAME, reply
            else:
                return self.STATE_COMPLETED, "Alles klar, danke für das Gespräch! Wir suchen jemanden mit genau diesem Drive. Alles Gute! 👋"
        elif cat == "QUESTION":
            return self.STATE_REQ_3, f"{analysis.get('ai_reply')}\n\n(Bist du bereit dich einzuarbeiten? Ja/Nein)"
        else:
            return self.STATE_REQ_3, "Bitte antworte mit **Ja** oder **Nein**."

    def _handle_name(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        if len(message) < 3:
            return self.STATE_NAME, "Bitte gib deinen vollständigen Namen ein."
        crud.update_lead(db, lead, name=message)
        return self.STATE_PHONE, f"Danke {message}! Wie lautet deine **Telefonnummer**?"

    def _handle_phone(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        crud.update_lead(db, lead, phone=message)
        return self.STATE_CV, "Perfekt! 📱\n\nJetzt brauche ich deinen **Lebenslauf (CV)** als PDF.\nBitte jetzt hochladen! 📎"

    def _handle_cv(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        if lead.cv_file_path or message == "UPLOAD_DONE":
            return self.STATE_COVER, "CV erhalten! ✅\n\nHast du ein **Anschreiben**? (Upload oder schreib 'weiter')"
        msg_lower = message.lower().strip()
        if "weiter" in msg_lower or "kein" in msg_lower:
            return self.STATE_CV, "Für eine Bewerbung brauchen wir zwingend deinen **Lebenslauf**. Bitte lade ihn hoch! 🙏"
        return self.STATE_CV, "Bitte lade erst deinen Lebenslauf (PDF) hoch! 📄"

    def _handle_cover(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        msg_lower = message.lower().strip()
        if lead.cover_letter_file_path or message == "UPLOAD_DONE":
            pass
        elif "weiter" in msg_lower or "nein" in msg_lower:
            pass
        else:
            return self.STATE_COVER, "Bitte lade das Anschreiben hoch oder schreibe **weiter**."

        return self.STATE_ADDITIONAL_AVAILABILITY, "Alles angekommen! ✅\n\nAb **wann** bist du verfügbar?"

    def _handle_avail(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        crud.update_lead(db, lead, availability=message)
        return self.STATE_ADDITIONAL_SALARY, "Notiert. 🗓️\n\nWas ist deine **Gehaltsvorstellung**? (€/Jahr)"

    def _handle_salary(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        val = re.sub(r'[^0-9]', '', message)
        if val:
            crud.update_lead(db, lead, salary_expectation=int(val))
        return self.STATE_ADDITIONAL_SOURCE, "Wie bist du auf uns **aufmerksam geworden**?"

    def _handle_source(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        crud.update_lead(db, lead, source=message)
        return self.STATE_ADDITIONAL_LANG, "Wie sind deine **Deutschkenntnisse**? (A1-C2)"

    def _handle_lang(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        crud.update_lead(db, lead, german_level=message)
        return self.STATE_COMPLETED, self._final_report(lead)

    def _handle_completed(self, message: str, lead: Lead, db: Session) -> Tuple[int, str]:
        return self.STATE_COMPLETED, "Bewerbung ist bereits durch! 👋"

    def _final_report(self, lead: Lead) -> str:
        return f"✅ **Vielen Dank, {lead.name}!**\n\nDeine Daten wurden erfolgreich übermittelt:\n\n👤 Name: {lead.name}\n📞 Tel: {lead.phone}\n💼 Job: {lead.position_interest}\n\nWir prüfen deine Unterlagen und melden uns so schnell wie möglich bei dir! 🚀\n\nDein muuuh Recruiting Team"

flow_engine = FlowEngine()
