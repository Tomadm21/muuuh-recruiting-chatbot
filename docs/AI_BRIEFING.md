# WhatsApp Recruiting Chatbot - AI Development Briefing

## 🎯 Project Goal

Build a **code-based WhatsApp Recruiting Chatbot** for muuh (Conversational AI agency) as a proof-of-concept for a job application. This chatbot will demonstrate understanding of Conversational AI, customer journeys, and technical implementation skills.

---

## 📋 Project Overview

### Purpose
- **Primary:** Portfolio project for job application to muuh (Junior Conversational AI Developer)
- **Secondary:** Demonstrate production-ready coding skills, API integration, and Conversational AI understanding
- **Impact:** Expected to increase interview chance from ~8% to ~50-60%

### Target Audience
- **Immediate:** muuh hiring team (tech-savvy, Conversational AI experts)
- **Use Case:** Recruiting FAQ automation, candidate screening, lead qualification

### Key Requirements
- ✅ **100% code-based** (Python backend, no Make.com or similar no-code tools)
- ✅ **WhatsApp integration** via WhatsApp Business API or Twilio
- ✅ **AI-powered** conversation using OpenAI GPT-4 or similar
- ✅ **Production-ready** code quality (clean, documented, testable)
- ✅ **Deployable** (can be demonstrated live)
- ✅ **GitHub repo** with professional README

---

## 🏢 Company Context: muuh

### About muuh
- **Industry:** Conversational AI agency (Customer Management)
- **Tech Stack:** Parloa, generative AI, Voice & Chat AI
- **Channels:** Phone, Alexa, WhatsApp, Web-Chat, App-Chat
- **Culture:** Startup mindset, innovation-focused, "mutige und herausragende Köpfe"
- **Size:** Part of MUUUH! Group (evolved from buw, largest owner-managed customer management provider)

### Job Position Requirements
- Conversational AI development for Voice & Chat
- Understanding of RESTful APIs, JSON, Webhooks, SDKs
- Interest in data analysis and success metrics
- Customer-facing work (consulting clients)
- German & English fluency

### Why This Chatbot Matters
- Demonstrates Conversational AI understanding
- Shows initiative and practical skills
- Aligns with muuh's tech stack (WhatsApp, AI, APIs)
- Proves ability to deliver production-ready projects

---

## 🤖 Chatbot Specifications

### Core Features

#### 1. FAQ Answering
**Intents:**
- "Welche Jobs sind offen?" → List open positions
- "Wie bewerbe ich mich?" → Application process
- "Remote möglich?" → Work mode options
- "Was ist das Gehalt?" → Salary ranges
- "Wie läuft der Bewerbungsprozess ab?" → Process steps
- "Welche Benefits gibt es?" → Company benefits
- "Wer ist muuh?" → Company introduction

**Response Style:**
- Friendly, professional
- muuh brand voice (modern, enthusiastic, authentic)
- Short messages (WhatsApp-optimized, max 2-3 sentences per message)
- Emojis allowed (modern, startup-appropriate)

#### 2. Candidate Screening
**Questions to Ask:**
- "Hast du Erfahrung mit Conversational AI?"
- "Kennst du APIs, JSON, Webhooks?"
- "Teilzeit oder Vollzeit?"
- "Remote, Hybrid oder Office?"
- "Dein Profil?" (Name, Email)

**Lead Capture:**
- Name, Email (mandatory)
- Phone (optional)
- Availability (Teilzeit/Vollzeit)
- Experience level (Junior/Mid/Senior)

#### 3. Lead Qualification
**Scoring Logic:**
```
Score Calculation:
- Conversational AI experience: +40 points
- API/Tech knowledge: +30 points
- Immediate availability: +20 points
- Location fit (Osnabrück/Berlin/Remote): +10 points

Qualification Tiers:
- 70-100 points: High Priority → Email notification
- 40-69 points: Medium Priority → Store in DB
- 0-39 points: Low Priority → Polite response
```

#### 4. Smart Conversation Flow
- **Context awareness:** Remember user's previous messages
- **Natural language understanding:** Handle typos, variations
- **Fallback handling:** Graceful responses for unknown intents
- **Multi-turn conversations:** Maintain dialogue state
- **Exit/Restart options:** Allow users to start over

---

## 🏗️ Technical Architecture

### Technology Stack

#### Backend Framework
**Python + FastAPI** (Recommended)
- Modern, async Python web framework
- Built-in API documentation
- Easy WebSocket support
- Fast development

**Alternative:** Flask (simpler, more established)

#### WhatsApp Integration
**Option 1: Twilio API for WhatsApp** (Recommended)
- Pros: Well-documented, reliable, sandboxed mode for testing
- Cons: Requires Twilio account (free tier available)
- Webhook-based architecture

**Option 2: WhatsApp Business API** (Direct)
- Pros: Official API, no intermediary
- Cons: More complex setup, requires business verification

#### AI/NLP
**OpenAI GPT-4 or GPT-3.5-turbo**
- Pros: Excellent intent recognition, natural responses
- Use function calling for structured intent extraction

**Alternative:** Anthropic Claude (for variety)

#### Data Storage
**SQLite** (for demo)
- Simple, file-based database
- No server setup required
- Easy to inspect

**Future:** PostgreSQL for production

#### Deployment
**Option 1: Railway.app** (Recommended for demo)
- Free tier available
- Easy Python deployment
- Webhooks work out of the box

**Option 2: Render.com**
**Option 3: Fly.io**

### System Architecture

```
┌─────────────┐
│   WhatsApp  │
│    User     │
└──────┬──────┘
       │ Message
       ↓
┌─────────────────────┐
│   Twilio Webhook    │
│  (Incoming Message) │
└──────┬──────────────┘
       │ POST /webhook
       ↓
┌─────────────────────┐
│   FastAPI Backend   │
│                     │
│  ┌───────────────┐  │
│  │ Message       │  │
│  │ Handler       │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Intent        │  │
│  │ Extraction    │  │
│  │ (OpenAI)      │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Business      │  │
│  │ Logic         │  │
│  │ (Routing)     │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Response      │  │
│  │ Generator     │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Lead Storage  │  │
│  │ (SQLite)      │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │ Response
       ↓
┌─────────────────────┐
│  Twilio API         │
│  (Send Response)    │
└──────┬──────────────┘
       │
       ↓
┌──────────────┐
│  WhatsApp    │
│  User        │
└──────────────┘
```

### Project Structure

```
muuh-recruiting-chatbot/
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── webhook.py           # Twilio webhook endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── intent_handler.py   # Intent extraction + routing
│   │   ├── conversation.py     # Conversation state management
│   │   └── scoring.py          # Lead qualification logic
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py   # OpenAI API integration
│   │   └── twilio_service.py   # Twilio messaging
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── lead.py             # Lead data model
│   │   └── conversation.py     # Conversation data model
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py         # Database connection
│   │   └── crud.py             # CRUD operations
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Logging utilities
│
├── data/
│   ├── intents.json            # Intent definitions and responses
│   └── muuh_info.json          # muuh company data + FAQs
│
├── tests/
│   ├── __init__.py
│   ├── test_intents.py
│   └── test_webhook.py
│
└── scripts/
    ├── setup_db.py             # Database initialization
    └── test_conversation.py    # Manual conversation testing
```

---

## 📊 Data Models

### Lead Model
```python
{
    "id": "uuid",
    "name": "string",
    "email": "string",
    "phone": "string | null",
    "whatsapp_number": "string",
    "experience_level": "junior | mid | senior",
    "has_conversational_ai_experience": "boolean",
    "has_api_knowledge": "boolean",
    "work_mode": "remote | hybrid | office",
    "availability": "fulltime | parttime",
    "position_interest": "string",
    "qualification_score": "integer (0-100)",
    "created_at": "timestamp",
    "conversation_history": "json"
}
```

### Conversation State Model
```python
{
    "user_id": "string (whatsapp_number)",
    "current_intent": "string",
    "context": {
        "collected_info": {},
        "last_question": "string",
        "conversation_stage": "greeting | faq | screening | closing"
    },
    "message_count": "integer",
    "last_interaction": "timestamp"
}
```

### Intent Model
```json
{
    "intent_name": "job_openings",
    "keywords": ["jobs", "stellen", "positionen", "offen"],
    "response_template": "string",
    "requires_context": false,
    "next_action": "null | ask_followup | collect_info"
}
```

---

## 🎯 Conversation Flows

### Flow 1: FAQ Only
```
User: "Hallo!"
Bot: "Hi! 👋 Ich bin der muuh Recruiting-Bot. Ich helfe dir bei Fragen zu 
     unseren Jobs und dem Bewerbungsprozess. Was möchtest du wissen?"

User: "Welche Stellen sind offen?"
Bot: "Aktuell suchen wir:
     • (Junior) Conversational AI Developer
     • Senior Product Manager
     • UX Designer
     
     Interessiert dich eine dieser Positionen?"

User: "Conversational AI Developer"
Bot: "Super! 🚀 Die Position ist in Osnabrück, Berlin oder Remote.
     Tech-Stack: Parloa, APIs, generative KI.
     
     Mehr Infos findest du hier: [Link zu Jobposting]
     
     Möchtest du dich bewerben oder weitere Fragen stellen?"

User: "Danke, das reicht!"
Bot: "Gerne! Bei weiteren Fragen melde dich einfach. Viel Erfolg! 🎯"
```

### Flow 2: Full Screening
```
User: "Ich interessiere mich für die AI Developer Stelle"
Bot: "Großartig! 🎉 Um dich besser kennenzulernen: 
     Hast du schon Erfahrung mit Conversational AI oder verwandten Themen?"

User: "Ja, ich arbeite mit ChatGPT und APIs"
Bot: "Perfect! Das passt gut. 
     Kennst du dich auch mit RESTful APIs, JSON und Webhooks aus?"

User: "Ja, nutze ich täglich"
Bot: "Excellent! 👏 Suchst du Vollzeit oder Teilzeit?"

User: "Teilzeit, 20-30h"
Bot: "Passt! Wir bieten beides an.
     
     Magst du mir noch deinen Namen und Email geben? 
     Dann kann ich dich direkt an unser HR-Team weiterleiten. 📧"

User: "Tom Adomeit, tom@example.com"
Bot: "Vielen Dank, Tom! Ich habe deine Daten weitergeleitet.
     Dein Profil sieht sehr gut aus (Score: 90/100)! 🌟
     
     Das HR-Team wird sich innerhalb von 2-3 Tagen bei dir melden.
     
     Viel Erfolg! 🚀"

[System: Email notification to HR with lead data]
```

---

## 🔧 Implementation Details

### 1. OpenAI Integration

**Function Calling for Intent Extraction:**
```python
# Example OpenAI function definition
functions = [
    {
        "name": "extract_intent",
        "description": "Extract user intent from message",
        "parameters": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["job_openings", "application_process", 
                            "company_info", "screening_response", 
                            "provide_contact", "other"]
                },
                "entities": {
                    "type": "object",
                    "properties": {
                        "position_name": {"type": "string"},
                        "name": {"type": "string"},
                        "email": {"type": "string"}
                    }
                },
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "neutral", "negative"]
                }
            }
        }
    }
]
```

**Prompt Engineering:**
```
You are a friendly recruiting assistant for muuh, a Conversational AI agency.

Context about muuh:
- Tech-focused company building Voice & Chat AI solutions
- Open positions: Conversational AI Developer, Product Manager, UX Designer
- Locations: Osnabrück, Berlin, Remote
- Culture: Startup mindset, innovative, collaborative

Your tasks:
1. Answer questions about muuh and open positions
2. Screen candidates (experience, skills, availability)
3. Collect contact info for qualified leads
4. Be helpful, friendly, and concise

Guidelines:
- Keep responses short (2-3 sentences max)
- Use emojis sparingly (modern, professional)
- Speak German (user's language)
- Be encouraging and positive
```

### 2. Twilio Webhook Handler

**Endpoint: POST /webhook**
```python
from fastapi import Request, Form
from twilio.twiml.messaging_response import MessagingResponse

@app.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),  # User's WhatsApp number
    Body: str = Form(...),  # Message text
    MessageSid: str = Form(...)  # Message ID
):
    # 1. Get or create conversation state
    # 2. Extract intent using OpenAI
    # 3. Route to appropriate handler
    # 4. Generate response
    # 5. Update conversation state
    # 6. Save lead if applicable
    # 7. Return TwiML response
    
    response = MessagingResponse()
    response.message(bot_reply)
    return Response(content=str(response), media_type="application/xml")
```

### 3. Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
DATABASE_URL=sqlite:///./muuh_chatbot.db
ENVIRONMENT=development
HR_EMAIL=recruiting@muuuh.de
```

### 4. muuh Company Data

**File: data/muuh_info.json**
```json
{
    "company": {
        "name": "MUUUH! Group",
        "tagline": "Kundenmanagement der Zukunft",
        "focus": "Conversational AI für Voice & Chat",
        "channels": ["Phone", "Alexa", "WhatsApp", "Web-Chat", "App-Chat"],
        "tech_stack": ["Parloa", "Generative AI", "RESTful APIs"],
        "culture": ["Startup mindset", "innovative", "collaborative", "gestaltungsspielraum"]
    },
    "positions": [
        {
            "title": "(Junior) Conversational AI Developer",
            "location": ["Osnabrück", "Berlin", "Remote"],
            "type": ["Vollzeit", "Teilzeit"],
            "requirements": [
                "Interesse an Conversational AI",
                "RESTful APIs, JSON, Webhooks",
                "Deutsch & Englisch fließend"
            ],
            "responsibilities": [
                "Conversational AI Entwicklung",
                "Kundenberatung",
                "Projektbegleitung"
            ],
            "link": "https://muuuh-gmbh.jobs.personio.de/job/2375560"
        }
    ],
    "benefits": [
        "Individuelle Weiterbildungsbudgets",
        "Moderne Offices (höhenverstellbare Schreibtische)",
        "Teamevents (hauseigene Disco, Bar)",
        "Fitnessstudio & Sporthalle",
        "20% Arbeitgeberzuschuss Altersvorsorge",
        "JobBike & Zug-Ticket Zuschuss"
    ],
    "process": [
        "1. Bewerbung einreichen",
        "2. Screening (1-2 Tage)",
        "3. Telefon-Interview mit HR",
        "4. Technical Interview",
        "5. Meet the Team",
        "6. Angebot"
    ]
}
```

---

## ✅ Success Criteria

### Functional Requirements
- ✅ Bot responds to WhatsApp messages within 2-3 seconds
- ✅ Handles 5-10 core intents accurately
- ✅ Collects lead info (name, email, experience)
- ✅ Scores leads based on qualification criteria
- ✅ Stores leads in database
- ✅ Sends email notification for high-priority leads

### Technical Requirements
- ✅ Clean, PEP 8 compliant Python code
- ✅ Type hints for all functions
- ✅ Comprehensive docstrings
- ✅ Unit tests for core functions (>70% coverage)
- ✅ Environment variables for secrets
- ✅ Logging for debugging
- ✅ Error handling (graceful fallbacks)

### Documentation Requirements
- ✅ README with:
  - Project description
  - Setup instructions
  - Architecture diagram
  - API documentation
  - Example conversations
  - Deployment guide
- ✅ Code comments for complex logic
- ✅ `.env.example` with all required variables

### Demo Requirements
- ✅ Live, deployable application
- ✅ Test WhatsApp number for demo
- ✅ Screenshot/video of conversation flow
- ✅ GitHub repo with clean commit history

---

## 📦 Deliverables

### 1. GitHub Repository
- Complete source code
- Professional README
- Clean commit history
- MIT License

### 2. Live Demo
- Deployed application (Railway/Render)
- Test WhatsApp number
- Demo video (Loom, 2-3 min)

### 3. Documentation
- **README.md:**
  - Problem statement
  - Solution overview
  - Tech stack
  - Setup guide
  - Architecture diagram
  - Example conversations
  - Future improvements
- **ARCHITECTURE.md:**
  - Detailed technical design
  - Data flow diagrams
  - API endpoints
- **DEPLOYMENT.md:**
  - Step-by-step deployment guide

### 4. Metrics Dashboard (Bonus)
- Simple web UI showing:
  - Total conversations
  - Qualified leads
  - Average qualification score
  - Most common intents

---

## 🚀 Development Phases

### Phase 1: Foundation (2-3h)
- ✅ Project setup + dependencies
- ✅ FastAPI basic structure
- ✅ Twilio webhook integration
- ✅ OpenAI integration
- ✅ Basic echo bot (test Twilio connection)

### Phase 2: Core Logic (2-3h)
- ✅ Intent extraction with OpenAI
- ✅ Response generation
- ✅ Conversation state management
- ✅ 5-10 core intents implemented

### Phase 3: Lead Management (1-2h)
- ✅ Database setup (SQLite)
- ✅ Lead model + CRUD operations
- ✅ Scoring logic
- ✅ Email notifications

### Phase 4: Polish (1-2h)
- ✅ Error handling
- ✅ Logging
- ✅ Testing
- ✅ Documentation

### Phase 5: Deployment (1h)
- ✅ Deploy to Railway/Render
- ✅ Configure Twilio webhook
- ✅ Test live
- ✅ Record demo video

**Total Estimated Time: 7-11 hours**

---

## 🎓 Code Quality Standards

### Python Style
- Follow PEP 8
- Use type hints
- Max line length: 88 (Black formatter)
- Docstrings for all functions

### Git Commits
- Conventional commits format
- Small, atomic commits
- Descriptive messages

### Testing
- Unit tests for business logic
- Integration tests for webhook
- Test coverage >70%

### Security
- No hardcoded secrets
- Input validation
- Rate limiting (basic)
- Sanitize user input

---

## 📚 Reference Materials

### muuh Job Posting
**URL:** https://muuuh-gmbh.jobs.personio.de/job/2375560

**Key Points:**
- Position: (Junior) Conversational AI Developer
- Tech: Parloa, APIs, generative KI
- Channels: Voice & Chat (Phone, Alexa, WhatsApp, Web, App)
- Culture: Startup, Gestaltungsspielraum, mutig

### Candidate Profile (Tom Adomeit)
**Strengths:**
- Make.com Automation expert
- AI Tools (ChatGPT, Claude)
- Production projects (LinkedIn Outreach, Lead Enrichment)
- APIs, JSON, Webhooks knowledge
- Fast learner

**Experience:**
- Industry Stocks: Automation Specialist
- Upwork: Make.com Developer
- Make.com Advanced certified

**Availability:** 20-30h/week (Teilzeit)
**Languages:** German (native), English (fluent)

---

## 🎯 Project Goals for AI Developer

### What to Optimize For
1. **Code Quality:** Clean, professional, production-ready
2. **Functionality:** All core features working reliably
3. **Documentation:** Clear, comprehensive, easy to follow
4. **Demo Impact:** Impressive live demonstration
5. **Tech Showcase:** Show understanding of APIs, AI, webhooks

### What to Avoid
- Over-engineering (keep it simple but complete)
- Hardcoded values (use config/environment variables)
- Poor error handling (graceful fallbacks essential)
- Messy code (follow Python best practices)
- Incomplete documentation (README is critical)

### Key Differentiators
- ✅ Actually works (live demo)
- ✅ Professional code quality
- ✅ muuh-specific content (shows research)
- ✅ Production-ready architecture
- ✅ Demonstrates Conversational AI understanding

---

## 📝 Additional Context

### Why This Matters
This chatbot is **not just a project**, it's a **job application differentiator**. 

**Statistics:**
- Standard application (CV + Cover Letter): ~5-8% interview rate
- With GitHub portfolio: ~20-25% interview rate
- **With this chatbot: ~50-60% interview rate** (+10x improvement!)

### Hiring Manager Perspective
When muuh's hiring team sees this:
1. "This candidate researched our company"
2. "They understand Conversational AI practically"
3. "They can code production-ready systems"
4. "They took initiative beyond the application"
5. "They'd fit our startup culture (self-driven)"

### Success Metrics
- Mentioned in interview: ✅ SUCCESS
- Asked technical questions about it: ✅✅ GREAT
- Hiring team tests it live: ✅✅✅ EXCELLENT
- Gets job offer: 🎉 MISSION COMPLETE

---

## 🔗 Useful Resources

### Documentation
- **Twilio WhatsApp API:** https://www.twilio.com/docs/whatsapp/api
- **OpenAI Function Calling:** https://platform.openai.com/docs/guides/function-calling
- **FastAPI:** https://fastapi.tiangolo.com/
- **Railway Deployment:** https://docs.railway.app/

### Code Examples
- Twilio WhatsApp Python: https://www.twilio.com/docs/whatsapp/quickstart/python
- FastAPI Webhooks: https://fastapi.tiangolo.com/advanced/webhooks/

---

## ✨ Final Notes for AI Developer

This is a **high-impact, time-sensitive project**. Your goal: Build a chatbot that **wows the muuh hiring team** and demonstrates Tom's skills.

**Priorities:**
1. **Functionality first:** Make it work reliably
2. **Documentation second:** README must be excellent
3. **Code quality third:** Clean, professional code
4. **Polish fourth:** Nice-to-haves if time permits

**Timeline:** Aim to complete in **1-2 days of focused work** (7-11 hours total)

**Remember:** This chatbot could be the difference between getting the interview or not. Make it count! 🚀

---

**Good luck building! The muuh team is going to love this.** 💪
