# Architecture Documentation

## System Overview

The muuh WhatsApp Recruiting Chatbot is a production-ready conversational AI system built with a modular, scalable architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│                     (WhatsApp Users)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ WhatsApp Messages
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                         │
│                  (Twilio WhatsApp API)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Webhook (POST /webhook)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│                      (FastAPI Backend)                       │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Webhook Handler                          │  │
│  │  • Receive messages                                   │  │
│  │  • Validate requests                                  │  │
│  │  • Route to intent handler                            │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │           Intent Handler                              │  │
│  │  • Extract intent (via OpenAI)                        │  │
│  │  • Route to appropriate handler                       │  │
│  │  • Manage conversation flow                           │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │        Conversation Manager                           │  │
│  │  • Track conversation state                           │  │
│  │  • Maintain message history                           │  │
│  │  • Collect user information                           │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │          Scoring Engine                               │  │
│  │  • Calculate qualification score                      │  │
│  │  • Determine priority tier                            │  │
│  │  • Generate feedback                                  │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │       Response Generator                              │  │
│  │  • Generate natural responses                         │  │
│  │  • Format for WhatsApp                                │  │
│  │  • Send via Twilio                                    │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Store/Retrieve Data
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                   (SQLite Database)                          │
│                                                               │
│  • Leads (candidates)                                        │
│  • Conversation history                                      │
│  • Qualification scores                                      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Webhook Handler (`app/api/webhook.py`)

**Responsibilities:**
- Receive incoming WhatsApp messages from Twilio
- Validate webhook signatures (security)
- Extract message data (sender, content)
- Call intent handler for processing
- Return TwiML response to Twilio

**Flow:**
```python
POST /webhook
├── Validate Twilio signature
├── Extract: From, Body, MessageSid
├── Call intent_handler.process_message()
├── Generate TwiML response
└── Return XML response to Twilio
```

### 2. Intent Handler (`app/core/intent_handler.py`)

**Responsibilities:**
- Orchestrate conversation flow
- Extract intent using OpenAI
- Route to appropriate handler (FAQ, screening, contact)
- Manage conversation stages

**Conversation Stages:**
1. **Greeting**: Initial contact
2. **FAQ**: Answering questions about jobs, company, etc.
3. **Screening**: Collecting qualification information
4. **Closing**: Final response with score feedback

**Intent Types:**
- `greeting`: Hello, Hi, etc.
- `job_openings`: Questions about open positions
- `application_process`: How to apply
- `remote_work`: Work mode questions
- `salary`: Compensation questions
- `benefits`: Company benefits
- `company_info`: About muuh
- `tech_stack`: Technology questions
- `interested_in_position`: User wants to apply
- `provide_contact`: User provides name/email
- `screening_response`: Answers to screening questions

### 3. OpenAI Service (`app/services/openai_service.py`)

**Responsibilities:**
- Intent extraction using GPT-4 function calling
- Natural language response generation
- Entity extraction (name, email, position, etc.)

**Function Calling Schema:**
```json
{
  "intent": "job_openings",
  "entities": {
    "position_name": "Conversational AI Developer",
    "name": "Tom Adomeit",
    "email": "tom@example.com"
  },
  "sentiment": "positive",
  "confidence": 0.95
}
```

**Prompts:**
- **System Prompt**: Defines bot's role, context about muuh, and behavior guidelines
- **Intent Extraction**: Analyzes user message and returns structured intent data
- **Response Generation**: Creates natural, context-aware responses in German

### 4. Conversation Manager (`app/core/conversation.py`)

**Responsibilities:**
- Maintain conversation state per user (in-memory)
- Track message history
- Store collected information
- Manage conversation stage transitions

**State Structure:**
```python
{
  "user_id": "whatsapp:+491234567890",
  "current_intent": "job_openings",
  "context": {
    "collected_info": {
      "has_conversational_ai_experience": true,
      "has_api_knowledge": true,
      "availability": "parttime",
      "work_mode": "remote"
    },
    "last_question": "Kennst du dich mit APIs aus?",
    "conversation_stage": "screening",
    "awaiting_response_for": "api_knowledge"
  },
  "message_count": 5,
  "message_history": [...]
}
```

**Note**: Currently uses in-memory storage. For production with multiple instances, migrate to Redis.

### 5. Scoring Engine (`app/core/scoring.py`)

**Responsibilities:**
- Calculate qualification score (0-100)
- Determine priority tier (high/medium/low)
- Generate user-friendly feedback

**Scoring Algorithm:**
```python
score = 0

# Conversational AI experience: +40
if has_conversational_ai_experience:
    score += 40

# API/Tech knowledge: +30
if has_api_knowledge:
    score += 30

# Availability: +20 (fulltime) or +15 (parttime)
if availability == "fulltime":
    score += 20
elif availability == "parttime":
    score += 15

# Location fit: +10
if work_mode in ["remote", "hybrid", "office"]:
    score += 10

return min(score, 100)
```

**Priority Tiers:**
- **High (70-100)**: Top candidates, immediate HR notification
- **Medium (40-69)**: Qualified leads, stored for review
- **Low (0-39)**: Thank you message, stored

### 6. Twilio Service (`app/services/twilio_service.py`)

**Responsibilities:**
- Send WhatsApp messages via Twilio API
- Validate webhook signatures
- Format messages for WhatsApp (line breaks, emojis)

**Message Flow:**
```
Bot Response
    ↓
Format for WhatsApp (add line breaks)
    ↓
Twilio Client.messages.create()
    ↓
WhatsApp User Receives Message
```

## Data Models

### Lead Model (Database)

```python
class Lead(Base):
    id: int (primary key)
    whatsapp_number: str (unique)
    name: str (nullable)
    email: str (nullable)
    phone: str (nullable)
    
    # Qualification
    experience_level: str
    has_conversational_ai_experience: bool
    has_api_knowledge: bool
    work_mode: str (remote/hybrid/office)
    availability: str (fulltime/parttime)
    position_interest: str
    qualification_score: int (0-100)
    
    # Metadata
    conversation_history: json
    created_at: datetime
    updated_at: datetime
```

### Conversation State (In-Memory)

```python
class ConversationState(BaseModel):
    user_id: str
    current_intent: Optional[str]
    context: ConversationContext
    message_count: int
    message_history: List[Dict]
    last_interaction: Optional[str]
```

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint, API info |
| GET | `/health` | Health check |
| GET | `/webhook` | Webhook validation |
| POST | `/webhook` | Receive WhatsApp messages |

### Webhook Request (from Twilio)

```
POST /webhook
Content-Type: application/x-www-form-urlencoded

From=whatsapp:+491234567890
Body=Hallo!
MessageSid=SM...
AccountSid=AC...
```

### Webhook Response (to Twilio)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Hi! 👋 Ich bin der muuh Recruiting-Bot...</Message>
</Response>
```

## Security

### 1. Webhook Validation
- Twilio signature verification using `X-Twilio-Signature` header
- Prevents unauthorized webhook calls

### 2. Environment Variables
- All secrets stored in environment variables
- Never committed to git
- Loaded via `pydantic-settings`

### 3. Input Validation
- FastAPI automatic validation
- Pydantic models for type safety
- SQLAlchemy ORM prevents SQL injection

## Error Handling

### Levels

1. **Graceful Degradation**: If OpenAI fails, use fallback responses
2. **User-Friendly Messages**: Never expose technical errors to users
3. **Logging**: All errors logged with full stack traces
4. **Recovery**: Webhook always returns valid TwiML

### Example

```python
try:
    bot_response = await intent_handler.process_message(...)
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    bot_response = "Entschuldigung, da ist etwas schiefgelaufen..."
```

## Performance Considerations

### Current Implementation
- **Conversation State**: In-memory (single instance)
- **Database**: SQLite (file-based)
- **Response Time**: ~1-3 seconds (mostly OpenAI API)

### Optimization Opportunities

1. **Caching**: Cache frequent responses (FAQ)
2. **Connection Pooling**: Reuse HTTP connections
3. **Async Operations**: Already using async/await
4. **Database**: Upgrade to PostgreSQL for production

### Scalability Path

```
Current (MVP)          →    Production (Scale)
─────────────────────      ───────────────────────
In-Memory State        →    Redis (distributed)
SQLite Database        →    PostgreSQL (managed)
Single Instance        →    Multiple Instances
No Caching             →    Redis Cache
Blocking DB            →    Async DB (asyncpg)
```

## Deployment Architecture

### Railway/Render (Recommended)

```
GitHub Repo
    ↓
Automatic Build
    ↓
Deploy to Container
    ↓
HTTPS Endpoint
    ↓
Twilio Webhook
```

### Docker (Self-Hosted)

```
Dockerfile
    ↓
Build Image
    ↓
Run Container
    ↓
Reverse Proxy (nginx)
    ↓
HTTPS (Let's Encrypt)
    ↓
Twilio Webhook
```

## Monitoring & Logging

### Logging Levels
- **INFO**: Normal operations (message received, intent detected)
- **WARNING**: Unexpected but handled (unknown intent, missing data)
- **ERROR**: Failures (API errors, database errors)

### Log Format
```
2024-01-13 10:30:45 - muuh_chatbot - INFO - Received message from whatsapp:+49... : Hallo!
2024-01-13 10:30:46 - muuh_chatbot - INFO - Extracted intent: greeting
2024-01-13 10:30:46 - muuh_chatbot - INFO - Sending response: Hi! 👋 ...
```

### Metrics to Track (Future)
- Messages per day
- Conversations started
- Conversations completed
- Average qualification score
- High-priority leads per week
- Response time (p50, p95, p99)
- Error rate

## Future Architecture Enhancements

### Phase 1: Production Hardening
- Redis for conversation state
- PostgreSQL for database
- Email notifications (SMTP)
- Rate limiting
- Request retries

### Phase 2: Advanced Features
- Admin dashboard (React/Next.js)
- Analytics and reporting
- Multi-language support
- Calendar integration
- Voice call support

### Phase 3: Scale
- Kubernetes deployment
- Horizontal auto-scaling
- Message queue (RabbitMQ/Celery)
- CDN for static assets
- Multi-region deployment

---

This architecture is designed to be **simple for MVP**, yet **scalable for production**. Every component can be upgraded independently without major refactoring.
