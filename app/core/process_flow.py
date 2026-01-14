from statemachine import StateMachine, State

class RecruitingMachine(StateMachine):
    """
    Strict State Machine for the Muuuh Recruiting Process.
    """
    
    # === STATES ===
    greeting = State(initial=True)
    job_selection = State()
    requirements_check = State()
    data_personal = State()
    data_documents = State()
    data_additional = State()
    closing = State(final=True)

    # === EVENTS (Transitions) ===
    
    # Greeting -> Jobs
    start_job_search = (
        greeting.to(job_selection)
    )
    
    # Jobs -> Requirements
    select_job = (
        job_selection.to(requirements_check)
    )
    
    # Requirements -> Personal Data
    requirements_met = (
        requirements_check.to(data_personal)
    )
    
    # Requirements -> Closing (Fail)
    requirements_failed = (
        requirements_check.to(closing)
    )
    
    # Personal Data -> Documents
    info_collected = (
        data_personal.to(data_documents)
    )
    
    # Documents -> Additional Info
    documents_received = (
        data_documents.to(data_additional)
    )
    
    # Additional Info -> Closing
    analysis_complete = (
        data_additional.to(closing)
    )

    # === ACTIONS ===
    
    def on_enter_greeting(self):
        return "Hallo! 👋 Willkommen beim muuh Recruiting Bot.\n\nWas möchtest du tun?\n1️⃣ Jobs ansehen & bewerben\n2️⃣ Infos über muuh erhalten\n\n(Schreib 'Jobs' oder 'Infos')"

    def on_enter_job_selection(self, job_list=None):
        if not job_list:
            job_list = ["(Junior) Conversational AI Developer", "Senior Python Dev", "Trainee Recruiting"]
        jobs_str = "\n".join([f"• {j}" for j in job_list])
        return f"Wir haben folgende spannende Positionen offen:\n\n{jobs_str}\n\nWelche davon interessiert dich? (Schreib einfach den Namen)"

    def on_enter_requirements_check(self, job_name):
        return f"Gute Wahl: '{job_name}'! 👍\n\nDazu habe ich ein paar Fragen (K.O.-Kriterien):\n\n1️⃣ Hast du bereits Erfahrung mit Chatbots, Voice Assistants oder LLMs?"

    def on_enter_data_personal(self):
        return "Super, das Profil passt grundsätzlich! ✅\n\nLass uns deine Daten aufnehmen.\n\nWie lautet dein **Vor- und Nachname**?"

    def on_enter_data_documents(self):
        return """Perfekt! 📝
Jetzt brauche ich deine Unterlagen. Bitte sende sie mir **nacheinander** als PDF:

1. **Lebenslauf** (CV)
(Bitte jetzt hochladen 📎)"""

    def on_enter_data_additional(self):
        return "Alles klar, Dokumente sind da (oder übersprungen)! ✅\n\nKommen wir zum Schluss:\n\nAb **wann** bist du verfügbar? (Datum)"

    def on_enter_closing(self, score=None):
        if score:
            return f"Analyse fertig! Dein Score: {score}/100. Wir melden uns!"
        return "Danke für dein Interesse! 👋"
