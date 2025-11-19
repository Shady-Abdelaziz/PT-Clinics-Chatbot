"""
Simple Medical Center Crew
Delegates to the medical chatbot for handling patient requests
"""
from src.agents.medical_agents import medical_chatbot, handle_query
from src.utils import config


def create_information_task(user_query: str):
    """
    Legacy function for compatibility
    Now just returns the query to be processed by the chatbot
    """
    return user_query


def create_appointment_task(user_query: str, task_type: str = "general"):
    """
    Legacy function for compatibility
    Now just returns the query to be processed by the chatbot
    """
    return user_query


class MedicalCenterCrew:
    """Simple crew that delegates to the medical chatbot"""
    
    def __init__(self):
        """Initialize the crew"""
        self.chatbot = medical_chatbot
    
    def handle_query(self, user_query: str) -> str:
        """
        Handle a user query using the medical chatbot
        
        Args:
            user_query: The user's question or request
        
        Returns:
            str: The chatbot's response
        """
        try:
            return handle_query(user_query)
        except Exception as e:
            return f"I apologize, but I encountered an error processing your request: {str(e)}"


# Create global crew instance
medical_crew = MedicalCenterCrew()
