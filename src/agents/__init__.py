"""
Agents package for Medical Center AI Chatbot
"""
from .medical_agents import (
    medical_chatbot,
    handle_query,
    get_all_agents,
    get_agent_by_role
)
from .crew import (
    medical_crew,
    MedicalCenterCrew,
    create_information_task,
    create_appointment_task
)

__all__ = [
    'medical_chatbot',
    'handle_query',
    'get_all_agents',
    'get_agent_by_role',
    'medical_crew',
    'MedicalCenterCrew',
    'create_information_task',
    'create_appointment_task'
]
