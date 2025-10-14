import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # API Settings
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-pro')
    GEMINI_TEMPERATURE = float(os.environ.get('GEMINI_TEMPERATURE', 0.7))
    GEMINI_MAX_TOKENS = int(os.environ.get('GEMINI_MAX_TOKENS', 1000))
    
    # Chatbot Settings
    CHATBOT_PERSONA = os.environ.get('CHATBOT_PERSONA', 'friendly and knowledgeable tutor')
    CHATBOT_CONTEXT_LENGTH = int(os.environ.get('CHATBOT_CONTEXT_LENGTH', 10))
    
    # Test Settings
    DEFAULT_TEST_DURATION = int(os.environ.get('DEFAULT_TEST_DURATION', 30))  # minutes
    DEFAULT_QUESTION_COUNT = int(os.environ.get('DEFAULT_QUESTION_COUNT', 10))