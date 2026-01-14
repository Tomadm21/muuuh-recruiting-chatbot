"""Conversation state management."""
from typing import Dict, Optional
from datetime import datetime
from app.models.conversation import ConversationState, ConversationStage


class ConversationManager:
    """Manage conversation states for users."""
    
    def __init__(self):
        """Initialize conversation manager with in-memory storage."""
        self.conversations: Dict[str, ConversationState] = {}
    
    def get_or_create_conversation(self, user_id: str) -> ConversationState:
        """
        Get existing conversation or create new one.
        
        Args:
            user_id: User identifier (WhatsApp number)
            
        Returns:
            ConversationState object
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationState(
                user_id=user_id,
                last_interaction=datetime.utcnow().isoformat()
            )
        else:
            # Update last interaction time
            self.conversations[user_id].last_interaction = datetime.utcnow().isoformat()
        
        return self.conversations[user_id]
    
    def update_conversation(
        self,
        user_id: str,
        **kwargs
    ) -> ConversationState:
        """
        Update conversation state.
        
        Args:
            user_id: User identifier
            **kwargs: Fields to update
            
        Returns:
            Updated ConversationState
        """
        conversation = self.get_or_create_conversation(user_id)
        
        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
            elif hasattr(conversation.context, key):
                setattr(conversation.context, key, value)
        
        conversation.last_interaction = datetime.utcnow().isoformat()
        self.conversations[user_id] = conversation
        
        return conversation
    
    def add_message(
        self,
        user_id: str,
        role: str,
        message: str
    ) -> ConversationState:
        """
        Add message to conversation history.
        
        Args:
            user_id: User identifier
            role: 'user' or 'assistant'
            message: Message content
            
        Returns:
            Updated ConversationState
        """
        conversation = self.get_or_create_conversation(user_id)
        
        conversation.message_history.append({
            "role": role,
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        conversation.message_count += 1
        self.conversations[user_id] = conversation
        
        return conversation
    
    def update_collected_info(
        self,
        user_id: str,
        key: str,
        value: any
    ) -> ConversationState:
        """
        Update collected information in context.
        
        Args:
            user_id: User identifier
            key: Information key
            value: Information value
            
        Returns:
            Updated ConversationState
        """
        conversation = self.get_or_create_conversation(user_id)
        conversation.context.collected_info[key] = value
        self.conversations[user_id] = conversation
        
        return conversation
    
    def get_collected_info(self, user_id: str) -> Dict:
        """
        Get all collected information for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of collected information
        """
        conversation = self.get_or_create_conversation(user_id)
        return conversation.context.collected_info
    
    def set_stage(self, user_id: str, stage: ConversationStage) -> ConversationState:
        """
        Set conversation stage.
        
        Args:
            user_id: User identifier
            stage: New conversation stage
            
        Returns:
            Updated ConversationState
        """
        conversation = self.get_or_create_conversation(user_id)
        conversation.context.conversation_stage = stage
        self.conversations[user_id] = conversation
        
        return conversation
    
    def clear_conversation(self, user_id: str) -> None:
        """
        Clear conversation for a user.
        
        Args:
            user_id: User identifier
        """
        if user_id in self.conversations:
            del self.conversations[user_id]


# Global conversation manager instance
conversation_manager = ConversationManager()
