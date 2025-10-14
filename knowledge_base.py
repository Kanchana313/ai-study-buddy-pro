import json
import os
from api_manager import APIManager

class KnowledgeBase:
    def __init__(self):
        self.api_manager = APIManager()
        self.cache_file = "knowledge_cache.json"
        self.knowledge_cache = self._load_cache()
    
    def _load_cache(self):
        """Load knowledge cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_cache(self):
        """Save knowledge cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.knowledge_cache, f)
        except IOError:
            pass
    
    def get_information(self, query):
        """Get information about a topic"""
        # Check cache first
        cache_key = query.lower().strip()
        if cache_key in self.knowledge_cache:
            return self.knowledge_cache[cache_key]
        
        # Generate information using API
        prompt = f"Provide comprehensive information about {query}. Include key concepts, examples, and important details."
        
        messages = [
            {"role": "system", "content": "You are a knowledgeable AI assistant that provides accurate and comprehensive information on various topics."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.api_manager.get_chatbot_response(messages)
        
        if "error" in response:
            return {"error": response["error"]}
        
        # Cache the response
        self.knowledge_cache[cache_key] = response["content"]
        self._save_cache()
        
        return response["content"]
    
    def explain_concept(self, concept, level="beginner"):
        """Explain a concept at a specific level"""
        level_instructions = {
            "beginner": "Explain this concept as if to someone with no prior knowledge. Use simple language and relatable examples.",
            "intermediate": "Explain this concept for someone with some basic knowledge. Use appropriate terminology but still be clear.",
            "advanced": "Explain this concept for someone with advanced knowledge. Be detailed and comprehensive."
        }
        
        prompt = f"{level_instructions.get(level, level_instructions['beginner'])}\n\nExplain: {concept}"
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that explains concepts clearly at different levels of understanding."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.api_manager.get_chatbot_response(messages)
        
        if "error" in response:
            return {"error": response["error"]}
        
        return response["content"]
    
    def get_study_tips(self, topic):
        """Get study tips for a specific topic"""
        prompt = f"Provide effective study tips and strategies for learning about {topic}. Include techniques for understanding, memorizing, and applying the knowledge."
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that provides effective study tips and learning strategies."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.api_manager.get_chatbot_response(messages)
        
        if "error" in response:
            return {"error": response["error"]}
        
        return response["content"]