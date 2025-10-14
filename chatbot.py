from api_manager import APIManager
from config import Config
from knowledge_base import KnowledgeBase
import json
import re

class ChatBot:
    def __init__(self):
        self.api_manager = APIManager()
        self.config = Config()
        self.conversation_history = {}
        self.knowledge_base = KnowledgeBase()
    
    def get_system_prompt(self):
        """Generate the system prompt for the chatbot"""
        return f"""You are an AI Study Buddy, a {self.config.CHATBOT_PERSONA}. Your goal is to help students understand complex topics in simple terms.

Guidelines:
- Explain concepts clearly and simply
- Use analogies and examples when helpful
- Ask follow-up questions to ensure understanding
- Be encouraging and supportive
- If you don't know something, admit it honestly
- Keep responses concise but thorough
- Adapt your explanations to the student's level of understanding
- Provide study tips and learning strategies when appropriate"""

    def start_conversation(self, session_id):
        """Start a new conversation or retrieve an existing one"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
        return self.conversation_history[session_id]
    
    def add_message(self, session_id, role, content):
        """Add a message to the conversation history"""
        if session_id not in self.conversation_history:
            self.start_conversation(session_id)
        
        self.conversation_history[session_id].append({
            "role": role,
            "content": content
        })
        
        # Keep conversation history within the configured limit
        if len(self.conversation_history[session_id]) > self.config.CHATBOT_CONTEXT_LENGTH + 1:
            # Keep system message and the most recent messages
            system_msg = self.conversation_history[session_id][0]
            recent_msgs = self.conversation_history[session_id][-self.config.CHATBOT_CONTEXT_LENGTH:]
            self.conversation_history[session_id] = [system_msg] + recent_msgs
    
    def get_response(self, session_id, user_message):
        """Get a response from the chatbot"""
        # Check if user is asking for specific information
        if self._is_information_request(user_message):
            topic = self._extract_topic(user_message)
            if topic:
                # Get information from knowledge base
                info = self.knowledge_base.get_information(topic)
                if isinstance(info, str):
                    # Add to conversation
                    self.add_message(session_id, "user", user_message)
                    self.add_message(session_id, "assistant", info)
                    return {"response": info}
        
        # Check if user is asking for an explanation
        if self._is_explanation_request(user_message):
            concept = self._extract_concept(user_message)
            level = self._extract_level(user_message)
            if concept:
                # Get explanation from knowledge base
                explanation = self.knowledge_base.explain_concept(concept, level)
                if isinstance(explanation, str):
                    # Add to conversation
                    self.add_message(session_id, "user", user_message)
                    self.add_message(session_id, "assistant", explanation)
                    return {"response": explanation}
        
        # Check if user is asking for study tips
        if self._is_study_tips_request(user_message):
            topic = self._extract_topic(user_message)
            if topic:
                # Get study tips from knowledge base
                tips = self.knowledge_base.get_study_tips(topic)
                if isinstance(tips, str):
                    # Add to conversation
                    self.add_message(session_id, "user", user_message)
                    self.add_message(session_id, "assistant", tips)
                    return {"response": tips}
        
        # Add user message to conversation
        self.add_message(session_id, "user", user_message)
        
        # Get response from API
        response = self.api_manager.get_chatbot_response(
            self.conversation_history[session_id]
        )
        
        if "error" in response:
            bot_response = f"I'm sorry, I encountered an error: {response['error']}. Please try again later."
        else:
            bot_response = response["content"]
            # Add bot response to conversation
            self.add_message(session_id, "assistant", bot_response)
        
        return {
            "response": bot_response,
            "usage": response.get("usage", {})
        }
    
    def _is_information_request(self, message):
        """Check if the user is requesting information about a topic"""
        info_patterns = [
            r"tell me about",
            r"what is",
            r"information about",
            r"explain",
            r"describe",
            r"define"
        ]
        
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in info_patterns)
    
    def _is_explanation_request(self, message):
        """Check if the user is requesting an explanation"""
        explain_patterns = [
            r"explain",
            r"how does",
            r"why does",
            r"can you explain"
        ]
        
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in explain_patterns)
    
    def _is_study_tips_request(self, message):
        """Check if the user is requesting study tips"""
        tips_patterns = [
            r"study tips",
            r"how to study",
            r"learn",
            r"understand",
            r"memorize"
        ]
        
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in tips_patterns)
    
    def _extract_topic(self, message):
        """Extract the topic from a message"""
        # Simple extraction - in a real app, you might use more sophisticated NLP
        words = message.split()
        
        # Look for patterns like "tell me about X" or "what is X"
        for i, word in enumerate(words):
            if word.lower() in ["about", "is"] and i + 1 < len(words):
                return " ".join(words[i+1:])
        
        # If no pattern found, return the last few words as a guess
        if len(words) > 2:
            return " ".join(words[-2:])
        
        return message
    
    def _extract_concept(self, message):
        """Extract the concept from an explanation request"""
        # Similar to _extract_topic but tailored for explanations
        return self._extract_topic(message)
    
    def _extract_level(self, message):
        """Extract the desired explanation level from a message"""
        message_lower = message.lower()
        
        if "beginner" in message_lower or "simple" in message_lower or "easy" in message_lower:
            return "beginner"
        elif "advanced" in message_lower or "detailed" in message_lower or "expert" in message_lower:
            return "advanced"
        else:
            return "intermediate"
    
    def clear_conversation(self, session_id):
        """Clear the conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
        return self.start_conversation(session_id)