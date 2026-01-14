"""Manual conversation testing script."""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.intent_handler import intent_handler
from app.db.database import SessionLocal
from app.utils.logger import app_logger


async def test_conversation():
    """Test conversation flow interactively."""
    print("=" * 60)
    print("muuh Recruiting Chatbot - Test Conversation")
    print("=" * 60)
    print("Type your messages to test the chatbot.")
    print("Type 'quit' to exit.\n")
    
    # Use a test WhatsApp number
    test_user_id = "whatsapp:+49123456789"
    
    db = SessionLocal()
    
    try:
        while True:
            # Get user input
            user_message = input("\n👤 You: ").strip()
            
            if user_message.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!")
                break
            
            if not user_message:
                continue
            
            # Process message
            try:
                bot_response = await intent_handler.process_message(
                    user_id=test_user_id,
                    message=user_message,
                    db=db
                )
                
                print(f"\n🤖 Bot: {bot_response}")
                
            except Exception as e:
                app_logger.error(f"Error processing message: {e}", exc_info=True)
                print(f"\n❌ Error: {e}")
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_conversation())
