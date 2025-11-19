"""
Configuration loader for Medical Center AI Chatbot
Loads and validates all environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration management for the application"""
    
    def __init__(self):
        """Initialize configuration by loading environment variables"""
        # Load environment variables from .env file
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)
        
        # Google Gemini Configuration (for LLM)
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
        
        # Ollama Configuration (for Embeddings - Local, Free)
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
        
        # Common settings
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        
        # Qdrant Configuration
        self.QDRANT_URL = os.getenv("QDRANT_URL")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        self.COLLECTION_NAME = os.getenv("COLLECTION_NAME", "medical_center_knowledge")
        self.QDRANT_TIMEOUT = int(os.getenv("QDRANT_TIMEOUT", "300"))
        
        # Database Configuration
        self.EXCEL_DB_PATH = os.getenv("EXCEL_DB_PATH", "data/Simple_Clinic_Database.xlsx")
        
        # Medical Center Information
        self.CENTER_NAME = os.getenv("CENTER_NAME", "Medical Center")
        self.CENTER_PHONE = os.getenv("CENTER_PHONE", "(555) 200-1000")
        self.PT_PHONE = os.getenv("PT_PHONE", "(555) 200-2000")
        self.PT_EMAIL = os.getenv("PT_EMAIL", "pt@medicalcenter.com")
        self.CENTER_LOCATION = os.getenv("CENTER_LOCATION", "Cairo, Egypt")
        
        # Retrieval Settings
        self.RAG_RETRIEVAL_K = int(os.getenv("RAG_RETRIEVAL_K", "5"))
        self.RAG_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", "0.3"))
        
        # Crew AI Settings
        self.CREW_VERBOSE = os.getenv("CREW_VERBOSE", "False").lower() == "true"
        self.MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
        
        # Flask Configuration
        self.FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
        self.FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
        self.FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
        
        # Business Hours
        self.WEEKDAY_HOURS = os.getenv("WEEKDAY_HOURS", "Monday-Friday: 7:00 AM - 7:00 PM")
        self.SATURDAY_HOURS = os.getenv("SATURDAY_HOURS", "Saturday: 8:00 AM - 2:00 PM")
        self.SUNDAY_HOURS = os.getenv("SUNDAY_HOURS", "Sunday: Closed")
        
        # Appointment Settings
        self.APPOINTMENT_DURATION = int(os.getenv("APPOINTMENT_DURATION", "30"))
        self.MAX_ADVANCE_BOOKING_DAYS = int(os.getenv("MAX_ADVANCE_BOOKING_DAYS", "30"))
        self.CANCELLATION_NOTICE_HOURS = int(os.getenv("CANCELLATION_NOTICE_HOURS", "24"))
        
        # Validate required configurations
        self._validate()
    
    def _validate(self):
        """Validate that all required configurations are present"""
        required_fields = [
            ("QDRANT_URL", self.QDRANT_URL),
            ("QDRANT_API_KEY", self.QDRANT_API_KEY),
            ("GEMINI_API_KEY", self.GEMINI_API_KEY),
        ]
        
        missing_fields = [field for field, value in required_fields if not value]
        
        if missing_fields:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_fields)}"
            )
    
    def get_business_hours_info(self) -> str:
        """Get formatted business hours information"""
        return f"""
Operating Hours:
- {self.WEEKDAY_HOURS}
- {self.SATURDAY_HOURS}
- {self.SUNDAY_HOURS}

Physical Therapy Department:
- Monday-Friday: 7:00 AM - 7:00 PM
- Saturday: 8:00 AM - 2:00 PM
- Sunday: Closed
        """.strip()


# Global configuration instance
config = Config()