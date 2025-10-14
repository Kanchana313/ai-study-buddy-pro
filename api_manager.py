import requests
import json
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIManager:
    def __init__(self):
        self.config = Config()
        # Gemini API endpoint
        self.api_base = "https://generativelanguage.googleapis.com/v1beta"
        # Gemini API uses a different header
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def make_gemini_request(self, prompt_text, model=None, temperature=None, max_tokens=None):
        """Make a request to Google Gemini API"""
        if not self.config.GEMINI_API_KEY:
            logger.error("Gemini API key not configured")
            return {"error": "Gemini API key not configured"}
        
        # Construct the request payload for Gemini
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt_text
                }]
            }],
            "generationConfig": {
                "temperature": temperature if temperature is not None else self.config.GEMINI_TEMPERATURE,
                "maxOutputTokens": max_tokens if max_tokens is not None else self.config.GEMINI_MAX_TOKENS,
            }
        }
        
        model_name = model or self.config.GEMINI_MODEL
        # The API key is passed as a query parameter
        url = f"{self.api_base}/models/{model_name}:generateContent?key={self.config.GEMINI_API_KEY}"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error making Gemini request: {str(e)}")
            return {"error": str(e)}
    
    def get_chatbot_response(self, messages):
        """Get a response from the chatbot"""
        # Gemini API takes a single prompt text, so we need to format the messages
        # into a single string. We'll create a simple history string.
        prompt_text = ""
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            if role == 'USER':
                prompt_text += f"User: {content}\n"
            elif role == 'ASSISTANT':
                prompt_text += f"Assistant: {content}\n"
            elif role == 'SYSTEM':
                # Add system prompt at the beginning
                prompt_text = f"{content}\n\n{prompt_text}"
        
        response = self.make_gemini_request(prompt_text)
        
        if "error" in response:
            return {"error": response["error"]}
        
        try:
            # Parse the response from Gemini
            content = response["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "content": content,
                "usage": response.get("usageMetadata", {})
            }
        except (KeyError, IndexError):
            return {"error": "Invalid response format from Gemini"}
    
    def generate_test_questions(self, topic, num_questions, difficulty, question_types):
        """Generate test questions on a specific topic"""
        types_str = ", ".join(question_types)
        
        # Simplified prompt to reduce the chance of errors
        prompt = f"""Create a JSON object with a single key "questions". 
        The value should be a list of {num_questions} test questions about {topic}.
        Difficulty: {difficulty}. Types: {types_str}.
        
        Each question must be a JSON object with these keys: "question", "type", "options", "answer", "explanation".
        
        Example:
        {{
          "questions": [
            {{
              "question": "What is 2+2?",
              "type": "multiple choice",
              "options": ["3", "4", "5"],
              "answer": "4",
              "explanation": "2+2 equals 4."
            }}
          ]
        }}
        
        Return only the raw JSON object. No other text."""
        
        # Increased max_tokens to give the AI more room
        response = self.make_gemini_request(prompt, max_tokens=3000)
        
        if "error" in response:
            return {"error": response["error"]}
        
        try:
            # Get the raw text from the AI response
            content = response["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean up common formatting issues
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # --- NEW ROBUST PARSING LOGIC ---
            # Find the last complete question object if the JSON is cut off
            last_complete_obj_end = content.rfind('}')
            if last_complete_obj_end != -1:
                # Find the start of that object
                last_complete_obj_start = content.rfind('{', 0, last_complete_obj_end)
                if last_complete_obj_start != -1:
                    # Try to parse just the part up to the last complete object
                    try:
                        # Create a minimal valid JSON from the last complete object
                        # This is a bit of a hack, but it's better than failing completely
                        partial_json = '{"questions": [' + content[last_complete_obj_start:last_complete_obj_end+1] + ']}'
                        return json.loads(partial_json)
                    except json.JSONDecodeError:
                        # If even that fails, just return the error
                        pass
            
            # If the above fails, try the original parsing
            return json.loads(content)
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Fallback if JSON parsing still fails
            logger.error(f"Failed to parse JSON from Gemini: {e}")
            logger.error(f"Raw response was: {content}")
            return {"error": "Failed to parse test questions from AI response.", "raw_response": content}