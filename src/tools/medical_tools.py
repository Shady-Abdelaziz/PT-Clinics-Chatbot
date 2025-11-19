"""
Tools for CrewAI Agents
These tools enable agents to interact with the database and knowledge base
"""
from crewai.tools import BaseTool
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.utils import config, ExcelDBManager, VectorDBManager


# Initialize managers
excel_manager = ExcelDBManager(config.EXCEL_DB_PATH)
vector_manager = VectorDBManager(
    qdrant_url=config.QDRANT_URL,
    qdrant_api_key=config.QDRANT_API_KEY,
    collection_name=config.COLLECTION_NAME,
    ollama_base_url=config.OLLAMA_BASE_URL,
    embedding_model=config.EMBEDDING_MODEL
)


# ============================================================================
# Knowledge Search Tool
# ============================================================================

class KnowledgeSearchInput(BaseModel):
    """Input schema for KnowledgeSearchTool"""
    query: str = Field(..., description="Search query about doctors, services, or medical information")


class KnowledgeSearchTool(BaseTool):
    name: str = "Search Knowledge Base"
    description: str = """
    Search the medical center's knowledge base for information about:
    - Doctor details (specialties, experience, education, availability, room numbers, phones)
    - Physical therapy services and procedures
    - Medical center policies and procedures
    - Operating hours and contact information
    
    Use this tool to answer questions about doctors, services, and general information.
    """
    args_schema: Type[BaseModel] = KnowledgeSearchInput
    
    def _run(self, query: str) -> str:
        """Search the knowledge base"""
        try:
            results = vector_manager.search(
                query=query,
                limit=config.RAG_RETRIEVAL_K,
                score_threshold=config.RAG_SCORE_THRESHOLD
            )
            
            if not results:
                return "No relevant information found in the knowledge base."
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(f"Result {i} (Relevance: {result['score']:.2f}):\n{result['text']}\n")
            
            return "\n---\n".join(formatted_results)
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"


# ============================================================================
# Available Slots Tool
# ============================================================================

class AvailableSlotsInput(BaseModel):
    """Input schema for AvailableSlotsTool"""
    doctor_name: str = Field(..., description="Full name of the doctor (e.g., 'Dr. Emily Roberts')")
    date: Optional[str] = Field(None, description="Specific date in YYYY-MM-DD format (optional)")
    limit: int = Field(10, description="Maximum number of slots to return")


class AvailableSlotsTool(BaseTool):
    name: str = "Check Available Appointment Slots"
    description: str = """
    Check available appointment slots for a specific doctor.
    
    Parameters:
    - doctor_name: Full doctor name including title (e.g., 'Dr. Emily Roberts')
    - date: Optional specific date in YYYY-MM-DD format
    - limit: Maximum number of slots to return (default: 10)
    
    Returns a list of available appointment slots with date and time.
    """
    args_schema: Type[BaseModel] = AvailableSlotsInput
    
    def _run(self, doctor_name: str, date: Optional[str] = None, limit: int = 10) -> str:
        """Get available slots"""
        try:
            slots = excel_manager.get_available_slots(doctor_name, date, limit)
            
            if not slots:
                if date:
                    return f"No available slots found for {doctor_name} on {date}."
                else:
                    return f"No available slots found for {doctor_name}."
            
            # Format results
            result = f"Available slots for {doctor_name}:\n\n"
            for slot in slots:
                result += f"📅 Date: {slot['date']}\n⏰ Time: {slot['time']}\n\n"
            
            return result.strip()
        except Exception as e:
            return f"Error checking available slots: {str(e)}"


# ============================================================================
# Book Appointment Tool
# ============================================================================

class BookAppointmentInput(BaseModel):
    """Input schema for BookAppointmentTool"""
    doctor_name: str = Field(..., description="Full name of the doctor")
    date: str = Field(..., description="Appointment date in YYYY-MM-DD format")
    time: str = Field(..., description="Appointment time (e.g., '09:00 AM')")
    patient_name: str = Field(..., description="Patient's full name")
    phone: str = Field(..., description="Patient's phone number")


class BookAppointmentTool(BaseTool):
    name: str = "Book Appointment"
    description: str = """
    Book an appointment for a patient with a specific doctor at a specific date and time.
    
    Required parameters:
    - doctor_name: Full doctor name (e.g., 'Dr. Emily Roberts')
    - date: Appointment date in YYYY-MM-DD format
    - time: Appointment time (e.g., '09:00 AM')
    - patient_name: Patient's full name
    - phone: Patient's phone number with country code
    
    Make sure to check availability first using the Available Slots tool.
    """
    args_schema: Type[BaseModel] = BookAppointmentInput
    
    def _run(self, doctor_name: str, date: str, time: str, patient_name: str, phone: str) -> str:
        """Book an appointment"""
        try:
            success, message = excel_manager.book_appointment(
                doctor_name=doctor_name,
                date=date,
                time=time,
                patient_name=patient_name,
                phone=phone
            )
            return message
        except Exception as e:
            return f"Error booking appointment: {str(e)}"


# ============================================================================
# Cancel Appointment Tool
# ============================================================================

class CancelAppointmentInput(BaseModel):
    """Input schema for CancelAppointmentTool"""
    doctor_name: str = Field(..., description="Full name of the doctor")
    patient_name: str = Field(..., description="Patient's full name")
    date: Optional[str] = Field(None, description="Appointment date in YYYY-MM-DD format (optional)")
    time: Optional[str] = Field(None, description="Appointment time (optional)")


class CancelAppointmentTool(BaseTool):
    name: str = "Cancel Appointment"
    description: str = """
    Cancel an appointment for a patient with a specific doctor.
    
    Required parameters:
    - doctor_name: Full doctor name (e.g., 'Dr. Emily Roberts')
    - patient_name: Patient's full name
    
    Optional parameters:
    - date: Specific appointment date in YYYY-MM-DD format
    - time: Specific appointment time
    
    If date and time are not provided, all appointments for this patient with this doctor will be cancelled.
    """
    args_schema: Type[BaseModel] = CancelAppointmentInput
    
    def _run(self, doctor_name: str, patient_name: str, date: Optional[str] = None, time: Optional[str] = None) -> str:
        """Cancel an appointment"""
        try:
            success, message = excel_manager.cancel_appointment(
                doctor_name=doctor_name,
                patient_name=patient_name,
                date=date,
                time=time
            )
            return message
        except Exception as e:
            return f"Error cancelling appointment: {str(e)}"


# ============================================================================
# Search Appointments Tool
# ============================================================================

class SearchAppointmentsInput(BaseModel):
    """Input schema for SearchAppointmentsTool"""
    patient_name: Optional[str] = Field(None, description="Patient's full name")
    doctor_name: Optional[str] = Field(None, description="Doctor's full name")
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")


class SearchAppointmentsTool(BaseTool):
    name: str = "Search Appointments"
    description: str = """
    Search for existing appointments based on criteria.
    
    Parameters (all optional):
    - patient_name: Patient's full name
    - doctor_name: Doctor's full name
    - date: Specific date in YYYY-MM-DD format
    
    Returns a list of matching appointments.
    """
    args_schema: Type[BaseModel] = SearchAppointmentsInput
    
    def _run(self, patient_name: Optional[str] = None, doctor_name: Optional[str] = None, date: Optional[str] = None) -> str:
        """Search for appointments"""
        try:
            appointments = excel_manager.search_appointments(
                patient_name=patient_name,
                doctor_name=doctor_name,
                date=date
            )
            
            if not appointments:
                return "No appointments found matching the criteria."
            
            # Format results
            result = f"Found {len(appointments)} appointment(s):\n\n"
            for appt in appointments:
                result += f"👨‍⚕️ Doctor: {appt['doctor']}\n"
                result += f"👤 Patient: {appt['patient_name']}\n"
                result += f"📅 Date: {appt['date']}\n"
                result += f"⏰ Time: {appt['time']}\n"
                result += f"📞 Phone: {appt['phone']}\n"
                result += f"Status: {appt['status']}\n\n"
            
            return result.strip()
        except Exception as e:
            return f"Error searching appointments: {str(e)}"


# ============================================================================
# Get All Doctors Tool
# ============================================================================

class GetDoctorsInput(BaseModel):
    """Input schema for GetDoctorsTool"""
    pass


class GetDoctorsTool(BaseTool):
    name: str = "Get All Doctors"
    description: str = """
    Get a list of all available doctors in the medical center.
    Use this to show patients what doctors are available.
    """
    args_schema: Type[BaseModel] = GetDoctorsInput
    
    def _run(self) -> str:
        """Get all doctors"""
        try:
            doctors = excel_manager.get_all_doctors()
            
            if not doctors:
                return "No doctors found in the system."
            
            result = "Available Doctors:\n\n"
            for i, doctor in enumerate(doctors, 1):
                result += f"{i}. {doctor}\n"
            
            return result.strip()
        except Exception as e:
            return f"Error getting doctors list: {str(e)}"


# Export all tools
knowledge_search_tool = KnowledgeSearchTool()
available_slots_tool = AvailableSlotsTool()
book_appointment_tool = BookAppointmentTool()
cancel_appointment_tool = CancelAppointmentTool()
search_appointments_tool = SearchAppointmentsTool()
get_doctors_tool = GetDoctorsTool()
