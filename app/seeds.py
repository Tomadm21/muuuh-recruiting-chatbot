from datetime import datetime, timedelta
import random
from sqlalchemy import text
from app.db.database import SessionLocal, init_db
from app.models.lead import Lead

def seed_data():
    print("Seeding Database with CRM Candidates...")
    init_db()
    db = SessionLocal()
    
    # Simple Migration Hack for existing DBs
    try:
        db.execute(text("ALTER TABLE leads_v2 ADD COLUMN pipeline_status VARCHAR DEFAULT 'NEW'"))
        db.commit()
        print("Migrated DB: Added pipeline_status column")
    except Exception as e:
        db.rollback() 
        # Column likely exists or other error. Ignore.
    
    base_time = datetime.utcnow()

    leads_data = [
        # 1. Sarah Kone -> QUALIFIED
        {
            "whatsapp_number": "491711112222",
            "name": "Sarah Kone",
            "pipeline_status": "QUALIFIED",
            "position_interest": "(Junior) Conversational AI Developer",
            "qualification_score": 92,
            "conversation_stage": 99,
            "source": "Referral",
            "updated_at": base_time,
            "projects": {"score": 92, "summary": "Strong NLP Background.", "pros": ["CS Master", "3y exp"], "cons": ["Expensive"]}
        },
        # 3. Jonas Weber -> SCREENING
        {
            "whatsapp_number": "491723334444",
            "name": "Jonas Weber",
            "pipeline_status": "SCREENING",
            "position_interest": "Senior Python Backend Dev",
            "qualification_score": 78,
            "conversation_stage": 99,
            "updated_at": base_time,
            "projects": {"score": 78, "summary": "Good Backend Dev.", "pros": ["Solid Python"], "cons": ["No AI"]}
        },
        # 4. Lisa Müller -> NEW
        {
            "whatsapp_number": "491735556666",
            "name": "Lisa Müller",
            "pipeline_status": "NEW",
            "position_interest": "Trainee Recruiting",
            "qualification_score": 65,
            "conversation_stage": 99,
            "updated_at": base_time,
            "projects": {"score": 65, "summary": "Marketing Background.", "pros": ["Communication"], "cons": ["No HR exp"]}
        },
        # 5. Kevin Schulz -> REJECTED
        {
            "whatsapp_number": "491747778888",
            "name": "Kevin Schulz",
            "pipeline_status": "REJECTED",
            "position_interest": "(Junior) Conversational AI Developer",
            "qualification_score": 45,
            "conversation_stage": 99,
            "updated_at": base_time,
            "projects": {"score": 45, "summary": "Ex-Sales. Not technical.", "pros": ["Sales"], "cons": ["No Code"]}
        },
        # 6. Clara Design -> SCREENING
        {
            "whatsapp_number": "491759990000",
            "name": "Clara Design",
            "pipeline_status": "SCREENING",
            "position_interest": "Trainee Recruiting",
            "qualification_score": 55,
            "conversation_stage": 99,
            "updated_at": base_time,
            "projects": {"score": 55, "summary": "Creative, but wrong job.", "pros": ["Design"], "cons": ["Goal Mismatch"]}
        },
        # 7. Dr. Markus Code -> OFFER
        {
            "whatsapp_number": "491761239876",
            "name": "Dr. Markus Code",
            "pipeline_status": "OFFER",
            "position_interest": "Senior Python Backend Dev",
            "qualification_score": 88,
            "conversation_stage": 99,
            "updated_at": base_time,
            "projects": {"score": 88, "summary": "PhD CS. Very strong.", "pros": ["Deep Tech"], "cons": ["Overqualified?"]}
        },
        # 8. James Smith -> QUALIFIED
        {
            "whatsapp_number": "447700900123",
            "name": "James Smith",
            "pipeline_status": "QUALIFIED",
            "position_interest": "(Junior) Conversational AI Developer",
            "qualification_score": 70,
            "conversation_stage": 99,
            "german_level": "A1",
            "updated_at": base_time,
            "projects": {"score": 70, "summary": "Great Dev, English only.", "pros": ["Native English"], "cons": ["No German"]}
        },
        # 9. Ghost -> NEW
        {
            "whatsapp_number": "491778887776",
            "name": "Ghost User",
            "pipeline_status": "NEW",
            "position_interest": "Trainee Recruiting",
            "conversation_stage": 4, 
            "qualification_score": 0, 
            "updated_at": base_time
        },
        # 10. Lena Student -> INTERVIEW
        {
            "whatsapp_number": "491786665554",
            "name": "Lena Student",
            "pipeline_status": "INTERVIEW",
            "position_interest": "(Junior) Conversational AI Developer",
            "qualification_score": 85,
            "conversation_stage": 99,
            "updated_at": base_time,
            "projects": {"score": 85, "summary": "Young Talent.", "pros": ["Motivated"], "cons": ["Intern only"]}
        }
    ]

    for data in leads_data:
        existing = db.query(Lead).filter(Lead.whatsapp_number == data["whatsapp_number"]).first()
        if existing:
            # FORCE UPDATE STATUS
            existing.pipeline_status = data.get("pipeline_status", "NEW")
            existing.conversation_stage = data["conversation_stage"] # Sync stage
            print(f"Updated {data['name']} -> {existing.pipeline_status}")
        else:
            lead = Lead(**data)
            db.add(lead)
            print(f"Added {data['name']}")
    
    db.commit()
    db.close()
    print("Done.")

if __name__ == "__main__":
    seed_data()
