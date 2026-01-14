"""
IntentHandler - DEPRECATED / NEWTURALIZED.
Now bypassed by FlowEngine.
Kept as stub to prevent ImportErrors in legacy logging or tests.
"""
from typing import Any, Dict
from sqlalchemy.orm import Session

class IntentHandler:
    """Deprecated stub."""
    
    def __init__(self):
        pass
    
    async def process_message(self, *args, **kwargs) -> str:
        return "System Upgrade: Please define FlowEngine."

# Global instance
intent_handler = IntentHandler()
