import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.db.database import SessionLocal, init_db
from app.models.lead import Lead
from app.db.database import Base, engine

def reset_database():
    print("🧹 STARTING DATABASE RESET...")
    db = SessionLocal()
    try:
        # HARD RESET: Drop and Recreate Table to apply Schema Changes (new column)
        print("⚠️ Dropping table 'leads' to enforce schema...")
        Lead.__table__.drop(engine, checkfirst=True)
        print("✅ Table dropped.")
        
        print("🆕 Creating new tables...")
        # Re-import models to ensure Base knows them
        init_db() 
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created (with new 'conversation_stage' column).")
        
        db.commit()
        print("✅ DATABASE RESET & MIGRATION COMPLETE.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
