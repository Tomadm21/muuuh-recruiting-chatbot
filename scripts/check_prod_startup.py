import os
import sys

# MOCK ENV VARS before importing app
os.environ["OPENAI_API_KEY"] = "sk-test-dummy"
os.environ["TWILIO_ACCOUNT_SID"] = "ACtestdummy"
os.environ["TWILIO_AUTH_TOKEN"] = "testdummytoken"
os.environ["TWILIO_WHATSAPP_NUMBER"] = "whatsapp:+1234567890"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

print("--- STARTING HEALTH CHECK ---")
try:
    print("1. Importing app.config...")
    from app.config import settings
    print("   Settings loaded.")
    
    print("2. Importing app.main...")
    from app.main import app
    print("   App imported successfully.")
    
    print("3. Checking routes...")
    for route in app.routes:
        print(f"   Route: {route.path} [{route.name}]")
        
    print("--- HEALTH CHECK PASSED ---")
except Exception as e:
    print(f"\n!!! CRITICAL FAILURE !!!\n{str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
