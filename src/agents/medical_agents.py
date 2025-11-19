"""
Simple Medical Center Chatbot
Direct LLM calls with conversation memory
"""
import requests
import json
from typing import List, Dict, Any, Optional
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


class ConversationMemory:
    """Simple conversation memory with window=10"""
    
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.messages = []
    
    def add_user_message(self, message: str):
        """Add user message to memory"""
        self.messages.append({"role": "user", "content": message})
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def add_ai_message(self, message: str):
        """Add AI message to memory"""
        self.messages.append({"role": "assistant", "content": message})
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get conversation context"""
        return self.messages[-self.max_messages:]
    
    def clear(self):
        """Clear memory"""
        self.messages = []


class MedicalCenterChatbot:
    """Simple medical center chatbot with direct function calls"""
    
    def __init__(self):
        self.memory = ConversationMemory(max_messages=10)
    
    def _match_doctor_name(self, partial_name: str) -> Optional[str]:
        """
        Match a partial doctor name to a full doctor name
        
        Args:
            partial_name: Partial name like "sarah", "dr sarah", "martinez"
            
        Returns:
            Full doctor name or None if no match found
        """
        if not partial_name:
            return None
        
        # Get all doctors
        all_doctors = excel_manager.get_all_doctors()
        
        # Clean up the partial name
        search_name = partial_name.lower().strip()
        search_name = search_name.replace("dr.", "").replace("dr", "").strip()
        
        # Try exact match first
        for doctor in all_doctors:
            if doctor.lower() == search_name or doctor.lower() == f"dr. {search_name}":
                return doctor
        
        # Try partial match (any word in the search matches any word in doctor name)
        search_words = search_name.split()
        for doctor in all_doctors:
            doctor_lower = doctor.lower()
            # Check if any search word is in the doctor name
            if any(word in doctor_lower for word in search_words):
                return doctor
        
        return None
    
    def _normalize_time_for_comparison(self, time_str: str) -> Optional[str]:
        """
        Normalize time to a standard format for comparison purposes only.
        Converts various time formats to 24-hour HH:MM format for comparison.
        
        Args:
            time_str: Time in various formats like "10", "10:00", "10 AM", "10:00 AM"
            
        Returns:
            Normalized time in 24-hour format like "10:00" or "14:30"
        """
        import re
        
        time_str = time_str.strip().upper()
        
        # If already in 24-hour format (HH:MM)
        if re.match(r'^\d{2}:\d{2}$', time_str):
            return time_str
        
        # If in 12-hour format with AM/PM (HH:MM AM/PM)
        match = re.match(r'^(\d{1,2}):(\d{2})\s*([AP]M)$', time_str)
        if match:
            hour = int(match.group(1))
            minutes = match.group(2)
            am_pm = match.group(3)
            
            # Convert to 24-hour
            if am_pm == 'PM' and hour != 12:
                hour += 12
            elif am_pm == 'AM' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minutes}"
        
        # If just hour with AM/PM
        match = re.match(r'^(\d{1,2})\s*([AP]M)$', time_str)
        if match:
            hour = int(match.group(1))
            am_pm = match.group(2)
            
            # Convert to 24-hour
            if am_pm == 'PM' and hour != 12:
                hour += 12
            elif am_pm == 'AM' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:00"
        
        # If just a number
        match = re.match(r'^(\d{1,2})$', time_str)
        if match:
            hour = int(match.group(1))
            if hour <= 23:
                return f"{hour:02d}:00"
        
        return None
    
    def _normalize_time(self, time_str: str) -> Optional[str]:
        """
        Normalize time format to 24-hour format (HH:MM)
        
        Args:
            time_str: Time in various formats like "10", "10:00", "10 AM", "10:00 AM"
            
        Returns:
            Normalized time like "10:00" or "14:30" in 24-hour format
        """
        import re
        
        time_str = time_str.strip().upper()
        
        # If already in correct format (HH:MM) - 24-hour
        if re.match(r'^\d{2}:\d{2}$', time_str):
            return time_str
        
        # If in 12-hour format with AM/PM (HH:MM AM/PM)
        match = re.match(r'^(\d{1,2}):(\d{2})\s*([AP]M)$', time_str)
        if match:
            hour = int(match.group(1))
            minutes = match.group(2)
            am_pm = match.group(3)
            
            # Convert to 24-hour
            if am_pm == 'PM' and hour != 12:
                hour += 12
            elif am_pm == 'AM' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minutes}"
        
        # If just hour with AM/PM
        match = re.match(r'^(\d{1,2})\s*([AP]M)$', time_str)
        if match:
            hour = int(match.group(1))
            am_pm = match.group(2)
            
            # Convert to 24-hour
            if am_pm == 'PM' and hour != 12:
                hour += 12
            elif am_pm == 'AM' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:00"
        
        # If just a number (assume 24-hour for times 0-23, 12-hour for 1-12)
        match = re.match(r'^(\d{1,2})$', time_str)
        if match:
            hour = int(match.group(1))
            if hour <= 23:
                # Already in 24-hour format
                return f"{hour:02d}:00"
            else:
                # Invalid hour
                return None
        
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normalize date format to match Excel format (YYYY-MM-DD)
        
        Args:
            date_str: Date in various formats like "November 12, 2025", "12 November 2025", "2025-11-12"
            
        Returns:
            Normalized date like "2025-11-12" or None if invalid
        """
        import re
        from datetime import datetime
        
        date_str = date_str.strip()
        
        # If already in correct format (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # Month names mapping
        months = {
            'january': '01', 'jan': '01',
            'february': '02', 'feb': '02',
            'march': '03', 'mar': '03',
            'april': '04', 'apr': '04',
            'may': '05',
            'june': '06', 'jun': '06',
            'july': '07', 'jul': '07',
            'august': '08', 'aug': '08',
            'september': '09', 'sep': '09',
            'october': '10', 'oct': '10',
            'november': '11', 'nov': '11',
            'december': '12', 'dec': '12'
        }
        
        # Try format: "November 12, 2025" or "November 12 2025"
        match = re.match(r'([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})', date_str, re.IGNORECASE)
        if match:
            month_name, day, year = match.groups()
            month_num = months.get(month_name.lower())
            if month_num:
                day_num = int(day)
                if 1 <= day_num <= 31:
                    return f"{year}-{month_num}-{day_num:02d}"
        
        # Try format: "12 November 2025"
        match = re.match(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', date_str, re.IGNORECASE)
        if match:
            day, month_name, year = match.groups()
            month_num = months.get(month_name.lower())
            if month_num:
                day_num = int(day)
                if 1 <= day_num <= 31:
                    return f"{year}-{month_num}-{day_num:02d}"
        
        return None
    
    def _call_gemini_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call Google Gemini LLM directly"""
        try:
            # Convert messages to Gemini format
            # Gemini uses 'contents' with 'role' (user/model) and 'parts' structure
            gemini_contents = []
            system_instruction = None
            
            for msg in messages:
                role = msg['role']
                content = msg['content']
                
                # Extract system message separately
                if role == 'system':
                    system_instruction = content
                    continue
                
                # Convert role names (assistant -> model for Gemini)
                gemini_role = 'model' if role == 'assistant' else 'user'
                
                gemini_contents.append({
                    'role': gemini_role,
                    'parts': [{'text': content}]
                })
            
            # Build the API payload
            payload = {
                'contents': gemini_contents,
                'generationConfig': {
                    'temperature': config.LLM_TEMPERATURE,
                    'maxOutputTokens': 4096,
                }
            }
            
            # Add system instruction if present
            if system_instruction:
                payload['systemInstruction'] = {
                    'parts': [{'text': system_instruction}]
                }
            
            # Make API call
            url = f"{config.GEMINI_BASE_URL}/models/{config.GEMINI_MODEL}:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{url}?key={config.GEMINI_API_KEY}",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract text from Gemini response
                if 'candidates' in data and len(data['candidates']) > 0:
                    candidate = data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        text_parts = [part.get('text', '') for part in candidate['content']['parts']]
                        return ''.join(text_parts)
                return "Sorry, I couldn't generate a response."
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', error_msg)
                except:
                    pass
                return f"Error: {response.status_code} - {error_msg}"
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _extract_function_call(self, message: str) -> Dict[str, Any]:
        """Extract function call from LLM response"""
        import re
        
        # First, try to extract XML-like tags with various formats
        xml_patterns = {
            "search_knowledge": [
                r"<search_knowledge>.*?<query>(.*?)</query>.*?</search_knowledge>",
                r"<search_knowledge>(.*?)</search_knowledge>"
            ],
            "get_doctors": [
                r"<get_doctors\s*/?>",
                r"<get_doctors>(.*?)</get_doctors>"
            ],
            "check_availability": [
                r"<check_availability>.*?doctor_name:\s*([^<\n]+).*?</check_availability>",
                r"<check_availability>.*?<doctor_name>(.*?)</doctor_name>(?:.*?<date>(.*?)</date>)?.*?</check_availability>",
                r"<check_availability>.*?<doctor>(.*?)</doctor>(?:.*?<date>(.*?)</date>)?.*?</check_availability>",
                r"<check_availability>(.*?)</check_availability>"
            ],
            "book_appointment": [
                r"<book_appointment>(.*?)</book_appointment>"
            ],
            "cancel_appointment": [
                r"<cancel_appointment>(.*?)</cancel_appointment>"
            ],
            "search_appointments": [
                r"<search_appointments>.*?<patient_name>(.*?)</patient_name>.*?</search_appointments>",
                r"<search_appointments>(.*?)</search_appointments>"
            ]
        }
        
        for function_name, patterns in xml_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message, re.IGNORECASE | re.DOTALL)
                if match:
                    if function_name == "search_knowledge":
                        args = match.group(1).strip()
                    elif function_name == "get_doctors":
                        args = ""
                    elif function_name == "check_availability":
                        if "doctor_name:" in pattern:
                            # Format: doctor_name: sarah
                            args = match.group(1).strip()
                        elif len(match.groups()) >= 2:
                            # Format with doctor and date tags
                            doctor = match.group(1).strip() if match.group(1) else ""
                            date = match.group(2).strip() if match.group(2) else ""
                            args = f"{doctor} {date}".strip()
                        else:
                            # Simple format
                            args = match.group(1).strip() if match.group(1) else ""
                    elif function_name == "search_appointments":
                        args = match.group(1).strip()
                    else:
                        args = match.group(1).strip() if match.group(1) else ""
                    return {"function": function_name, "args": args}
        
        # Fallback: Look for simple patterns like "search_knowledge: doctor information"
        # These patterns will match even if there's text before/after
        simple_patterns = {
            "search_knowledge": r"search_knowledge:\s*(.+?)(?:\n|$)",
            "get_doctors": r"get_doctors\s*(?:\n|$)",
            "check_availability": r"check_availability:\s*(.+?)(?:\n|$)",
            "book_appointment": r"book_appointment:\s*(.+?)(?:\n|$)",
            "cancel_appointment": r"cancel_appointment:\s*(.+?)(?:\n|$)",
            "search_appointments": r"search_appointments:\s*(.+?)(?:\n|$)"
        }
        
        for function_name, pattern in simple_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE | re.MULTILINE)
            if match:
                args = match.group(1).strip() if len(match.groups()) > 0 and match.group(1) else ""
                return {"function": function_name, "args": args}
        
        return None
    
    def _execute_function(self, function_name: str, args: str) -> str:
        """Execute function based on extracted call"""
        try:
            if function_name == "search_knowledge":
                query = args.strip()
                if not query:
                    return "Please provide a search query."
                
                results = vector_manager.search(
                    query=query,
                    limit=config.RAG_RETRIEVAL_K,
                    score_threshold=config.RAG_SCORE_THRESHOLD
                )
                
                if not results:
                    return f"I couldn't find information about '{query}'. Please try asking about our doctors, services, or policies."
                
                formatted_info = []
                for i, result in enumerate(results, 1):
                    formatted_info.append(f"📋 Information {i}: {result['text']}")
                
                return "\n".join(formatted_info)
            
            elif function_name == "get_doctors":
                doctors = excel_manager.get_all_doctors()
                if not doctors:
                    return "I don't have access to our current doctor list right now."
                
                doctor_list = "\n".join([f"👨‍⚕️ {doctor}" for doctor in doctors])
                return f"Here are our available doctors:\n\n{doctor_list}"
            
            elif function_name == "check_availability":
                # Simple extraction - assume format: "doctor_name" or "doctor_name date"
                parts = args.split()
                if not parts:
                    return "Please specify which doctor you want to check."
                
                # Try to match the doctor name
                partial_name = " ".join(parts[:-1]) if len(parts) > 1 and parts[-1].count('-') == 2 else " ".join(parts)
                doctor_name = self._match_doctor_name(partial_name)
                
                if not doctor_name:
                    return f"I couldn't find a doctor matching '{partial_name}'. Please check the name and try again."
                
                # Check if last part is a date
                date = None
                if len(parts) > 1 and parts[-1].count('-') == 2:
                    date = parts[-1]
                
                # Get ALL available slots (increased limit to 50)
                slots = excel_manager.get_available_slots(doctor_name, date, limit=50)
                if not slots:
                    if date:
                        return f"No available appointments for {doctor_name} on {date}."
                    else:
                        return f"No available appointments for {doctor_name}."
                
                # Group slots by date for better presentation
                from collections import defaultdict
                slots_by_date = defaultdict(list)
                for slot in slots:
                    slots_by_date[slot['date']].append(slot['time'])
                
                result = f"Available appointments for {doctor_name}:\n\n"
                for date_key in sorted(slots_by_date.keys()):
                    times = slots_by_date[date_key]
                    result += f"📅 {date_key}:\n"
                    result += f"   Times: {', '.join(times)}\n"
                    result += f"   Total slots: {len(times)}\n\n"
                
                result += f"Total available slots: {len(slots)}"
                return result
            
            elif function_name == "book_appointment":
                # Simple extraction - assume format: "doctor_name date time patient_name phone"
                # WHERE patient_name and phone are COMPLETE fields, not split
                parts = args.split()
                if len(parts) < 5:
                    return "To book an appointment, I need: doctor name, date, time, patient name, and phone number."
                
                # Try to match doctor name (could be multiple words)
                # Assume date is in YYYY-MM-DD format, find it
                date_idx = None
                for i, part in enumerate(parts):
                    if part.count('-') == 2:  # Likely a date
                        date_idx = i
                        break
                
                if date_idx is None:
                    return "Please provide a valid date in YYYY-MM-DD format."
                
                # Extract doctor name (everything before date)
                partial_doctor_name = " ".join(parts[:date_idx])
                doctor_name = self._match_doctor_name(partial_doctor_name)
                
                if not doctor_name:
                    return f"I couldn't find a doctor matching '{partial_doctor_name}'."
                
                # Extract date
                date = parts[date_idx]
                
                # Extract time (might be 1 or 2 parts: "10:00" or "10:00" "AM")
                time_idx = date_idx + 1
                if time_idx >= len(parts):
                    return "Missing time information."
                
                time_raw = parts[time_idx]
                patient_name_idx = time_idx + 1
                
                # Handle time with AM/PM (might be 2 parts: "10:00" "AM")
                if patient_name_idx < len(parts) and parts[patient_name_idx].upper() in ['AM', 'PM']:
                    time_raw = f"{time_raw} {parts[patient_name_idx]}"
                    patient_name_idx += 1
                
                if patient_name_idx >= len(parts):
                    return "Missing patient name."
                
                # Patient name is ONE complete field (even if it contains spaces)
                # It goes from patient_name_idx to the second-to-last part
                # Phone is the last part
                remaining_parts = parts[patient_name_idx:]
                if len(remaining_parts) < 2:
                    return "Missing phone number."
                
                # Last part is phone, everything else is patient name
                phone = remaining_parts[-1]
                patient_name = " ".join(remaining_parts[:-1])
                
                if not all([time_raw, patient_name, phone]):
                    return "To book an appointment, I need: doctor name, date, time, patient name, and phone number."
                
                # CRITICAL FIX: Verify slot is actually available BEFORE attempting to book
                # This prevents booking errors when conversation context is lost
                available_slots = excel_manager.get_available_slots(doctor_name, date, limit=100)
                
                # Normalize the time format for comparison
                time_normalized = self._normalize_time_for_comparison(time_raw)
                if not time_normalized:
                    return f"Invalid time format: '{time_raw}'. Please use format like '10:00 AM' or '02:30 PM'."
                
                # Check if requested time slot exists and is available
                slot_available = False
                matching_time_in_excel = None
                for slot in available_slots:
                    slot_time_normalized = self._normalize_time_for_comparison(slot['time'])
                    if slot['date'] == date and slot_time_normalized == time_normalized:
                        slot_available = True
                        matching_time_in_excel = slot['time']  # Use the exact format from Excel
                        break
                
                if not slot_available:
                    # Slot not available - provide helpful alternatives
                    if available_slots:
                        from collections import defaultdict
                        slots_by_date = defaultdict(list)
                        for slot in available_slots[:20]:  # Show up to 20 alternative slots
                            slots_by_date[slot['date']].append(slot['time'])
                        
                        alternatives = f"I apologize, but {doctor_name} isn't available on {date} at {time_raw}. Here are alternative slots:\n\n"
                        for date_key in sorted(slots_by_date.keys())[:5]:  # Show up to 5 dates
                            times = slots_by_date[date_key]
                            alternatives += f"📅 {date_key}:\n   {', '.join(times[:10])}\n\n"  # Show up to 10 times per date
                        
                        return alternatives
                    else:
                        return f"I apologize, but {doctor_name} has no available slots at this time. Please try another doctor or check back later."
                
                # Slot is confirmed available - proceed with booking using Excel's exact time format
                success, message = excel_manager.book_appointment(
                    doctor_name=doctor_name,
                    date=date,
                    time=matching_time_in_excel,  # Use exact format from Excel
                    patient_name=patient_name,
                    phone=phone
                )
                return message
            
            elif function_name == "search_appointments":
                # Simple extraction - look for patient name
                patient_name = args.strip()
                if not patient_name:
                    return "Please provide a patient name to search."
                
                appointments = excel_manager.search_appointments(patient_name=patient_name)
                if not appointments:
                    return f"I didn't find any appointments for {patient_name}."
                
                result = f"Found {len(appointments)} appointment(s) for {patient_name}:\n\n"
                for appt in appointments:
                    result += f"👨‍⚕️ Doctor: {appt['doctor']}\n"
                    result += f"📅 Date: {appt['date']} at {appt['time']}\n"
                    result += f"📞 Phone: {appt['phone']}\n\n"
                
                return result
            
            elif function_name == "cancel_appointment":
                # Parse arguments: doctor_name patient_name optional_date optional_time
                # LLM typically produces: "doctor_name patient_name date time"
                # Or: "doctor_name patient_name date" 
                # Or: "doctor_name patient_name"
                
                parts = args.split()
                if len(parts) < 2:
                    return "To cancel an appointment, I need: doctor name and patient name."
                
                # Initialize variables
                partial_doctor_name = None
                patient_name = None
                date_pattern = None
                time_pattern = None
                
                # Try to find a date pattern in the entire string first
                
                # Look for YYYY-MM-DD format (4 digits - 2 digits - 2 digits)
                import re
                yyyy_mm_dd_pattern = r'\b\d{4}-\d{1,2}-\d{1,2}\b'
                yyyy_mm_dd_match = re.search(yyyy_mm_dd_pattern, args)
                if yyyy_mm_dd_match:
                    date_pattern = yyyy_mm_dd_match.group()
                    
                    # Extract everything before the date as potential doctor + patient
                    before_date = args[:yyyy_mm_dd_match.start()].strip()
                    # Extract everything after the date as potential time
                    after_date = args[yyyy_mm_dd_match.end():].strip()
                    
                    # If there's content after the date, it might be time
                    if after_date:
                        time_pattern = after_date
                
                # Look for month names as date indicators if we didn't find YYYY-MM-DD
                if not date_pattern:
                    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                                  'july', 'august', 'september', 'october', 'november', 'december',
                                  'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                    
                    for i, part in enumerate(parts):
                        if part.lower().strip(',') in month_names:
                            # Found a month name
                            month_idx = i
                            date_parts = [part]  # Start with month name
                            
                            # Check if we have a day before the month (format: "12 November")
                            if i > 0:
                                prev_part = parts[i-1].replace(',', '')
                                if prev_part.isdigit() and 1 <= int(prev_part) <= 31:
                                    date_parts.insert(0, parts[i-1])  # Add day before month
                                    before_date_parts_end = i - 1  # Everything before the day
                                else:
                                    before_date_parts_end = i  # Everything before the month
                            else:
                                before_date_parts_end = i
                            
                            # Check if we have a year after the month (format: "November 2025")
                            if i + 1 < len(parts) and parts[i+1].replace(',', '').isdigit() and len(parts[i+1]) == 4:
                                date_parts.append(parts[i+1])  # Add year
                                after_date_parts_start = i + 2  # Everything after the year
                            else:
                                after_date_parts_start = i + 1  # Everything after the month
                            
                            date_pattern = " ".join(date_parts)
                            
                            # Extract everything before the date pattern
                            before_parts = parts[:before_date_parts_end]
                            if before_parts:
                                before_date = " ".join(before_parts)
                            else:
                                before_date = ""
                            
                            # Extract everything after the date
                            after_parts = parts[after_date_parts_start:]
                            if after_parts:
                                time_pattern = " ".join(after_parts)
                            
                            break
                
                # Now parse doctor and patient from the "before_date" part
                if date_pattern:
                    # We have a date, so doctor+patient is everything before the date
                    before_date_parts = before_date.split() if before_date else []
                    
                    # Try to find doctor name in the first 1-3 words of before_date
                    for doctor_word_count in [1, 2, 3]:
                        if doctor_word_count <= len(before_date_parts):
                            candidate_doctor = " ".join(before_date_parts[:doctor_word_count])
                            matched_doctor = self._match_doctor_name(candidate_doctor)
                            if matched_doctor:
                                partial_doctor_name = candidate_doctor
                                # Patient name is everything after doctor in before_date
                                if doctor_word_count < len(before_date_parts):
                                    patient_name = " ".join(before_date_parts[doctor_word_count:])
                                break
                else:
                    # No date found, everything is doctor + patient
                    before_date_parts = parts
                    
                    # Try to match doctor from first 1-3 words
                    for doctor_word_count in [1, 2, 3]:
                        if doctor_word_count <= len(before_date_parts):
                            candidate_doctor = " ".join(before_date_parts[:doctor_word_count])
                            matched_doctor = self._match_doctor_name(candidate_doctor)
                            if matched_doctor:
                                partial_doctor_name = candidate_doctor
                                # Patient name is everything after doctor
                                if doctor_word_count < len(before_date_parts):
                                    patient_name = " ".join(before_date_parts[doctor_word_count:])
                                break
                
                if not partial_doctor_name:
                    return f"I couldn't find a doctor in '{args}'. Please provide a valid doctor name."
                
                if not patient_name:
                    return "Please provide a patient name to cancel."
                
                # Match doctor name to full name
                doctor_name = self._match_doctor_name(partial_doctor_name)
                if not doctor_name:
                    return f"I couldn't find a doctor matching '{partial_doctor_name}'."
                
                # Normalize date if provided
                date = None
                if date_pattern:
                    # Try direct format first
                    if date_pattern.count('-') == 2 and re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_pattern):
                        date = date_pattern
                    else:
                        date = self._normalize_date(date_pattern)
                
                # Normalize time if provided
                time = None
                if time_pattern:
                    time = self._normalize_time(time_pattern)
                
                success, message = excel_manager.cancel_appointment(
                    doctor_name=doctor_name,
                    patient_name=patient_name.strip(),
                    date=date,
                    time=time
                )
                return message
            
            else:
                return f"I don't know how to execute: {function_name}"
        
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """Process user message and return response"""
        # Add user message to memory
        self.memory.add_user_message(user_message)
        
        # Create system message
        system_message = f"""You are a helpful medical center chatbot assistant.

Your role is to:
- Help patients with information about doctors, services, and policies
- Assist with appointment booking, cancellation, and inquiries  
- Provide accurate, professional responses
- Be conversational and natural

Available information:
- Operating Hours: {config.WEEKDAY_HOURS}, {config.SATURDAY_HOURS}, {config.SUNDAY_HOURS}
- Center Phone: {config.CENTER_PHONE}
- Physical Therapy: {config.PT_PHONE} / {config.PT_EMAIL}
- Location: {config.CENTER_LOCATION}

IMPORTANT: When you need to look up specific information, use ONLY ONE of these function formats:

1. To search for information about doctors, services, or policies:
   search_knowledge: your search query here

2. To get list of all doctors:
   get_doctors

3. To check doctor availability (you can use partial names like "sarah" or "dr sarah"):
   check_availability: doctor_name optional_date

4. To search for appointments:
   search_appointments: patient_name

5. To book an appointment:
   book_appointment: doctor_name date time patient_name phone

6. To cancel an appointment:
   cancel_appointment: doctor_name patient_name date time

IMPORTANT FOR BOOKING:
- Store the COMPLETE patient name as ONE field: "Shady Abdelaziz" (not "Shady")
- Store the COMPLETE phone number as ONE field: "01067110557" (not split)
- Use 24-hour time format: "10:00" (not "10:00 AM")
- If user says "shady abdelaziz 01067110557", then:
  * doctor_name = "sarah"
  * date = "2025-11-12"
  * time = "10:00" (24-hour format)
  * patient_name = "Shady Abdelaziz"  ← COMPLETE NAME
  * phone = "01067110557"             ← COMPLETE PHONE

IMPORTANT FOR CANCELLATION:
- Use the EXACT patient name that was used during booking
- Use 24-hour time format for time
- If booking used "Shady Abdelaziz" at "10:00", cancellation must use "Shady Abdelaziz" at "10:00"

BOOKING WORKFLOW:
- When a user wants to book an appointment, FIRST check availability using check_availability
- Show them available slots
- When user provides date and time, collect their name and phone number
- Once you have ALL information (doctor, date, time, name, phone), immediately call the booking function
- Then book using: book_appointment: doctor_name YYYY-MM-DD HH:MM AM/PM patient_name phone
- IMPORTANT: Always use full time format like "10:00 AM" not just "10"
- Remember the conversation context - if user already told you their name, use it!

CRITICAL RULES FOR FUNCTION CALLS:
IMPORTANT: When you need to call a function, output ONLY the function call on a single line
- Do NOT add any text before or after the function call
- Do NOT explain what you're doing
- Do NOT say "Let me book this for you" or similar phrases
- JUST output: function_name: arguments
- Example: book_appointment: sarah 2025-11-13 10:00 AM Shady Abdelaziz 01067110557

CRITICAL BOOKING VALIDATION:
- BEFORE confirming an appointment with a patient, ALWAYS check if the requested slot is actually available
- If user specifies a date and time (e.g., "13 november 10 am"), FIRST use check_availability to verify it's free
- If the slot is NOT available, tell the user and suggest alternatives
- If the slot IS available, then ask for patient details and proceed with booking

RULES:
- Use ONLY the simple format shown above (function_name: arguments)
- Do NOT use XML tags or other formats
- When you call a function, ONLY output the function call, nothing else
- After getting function results, provide a friendly response to the user
- For doctor names, you can use partial names (e.g., "sarah" instead of "Dr. Sarah Martinez")
- REMEMBER the conversation history - don't ask for information the user already provided
- When booking, use the EXACT time format from available slots (e.g., "10:00 AM")

Always be helpful and provide accurate information."""
        
        # Get conversation context
        context = self.memory.get_context()
        
        # Prepare messages for LLM
        messages = [{"role": "system", "content": system_message}]
        messages.extend(context)
        
        # Call LLM
        llm_response = self._call_gemini_llm(messages)
        
        # Check if LLM wants to call a function
        function_call = self._extract_function_call(llm_response)
        
        if function_call:
            # Execute the function
            function_result = self._execute_function(
                function_call["function"], 
                function_call["args"]
            )
            
            # Now ask LLM to format the result nicely for the user
            # IMPORTANT: Include full conversation history
            follow_up_messages = [{"role": "system", "content": system_message}]
            follow_up_messages.extend(context)  # Add conversation history
            follow_up_messages.append({
                "role": "assistant", 
                "content": f"[Function Result: {function_result}]"
            })
            follow_up_messages.append({
                "role": "user", 
                "content": "Based on the function result above, provide a helpful response to my original question. Remember our conversation context."
            })
            
            final_response = self._call_gemini_llm(follow_up_messages)
            
            # Add to memory
            self.memory.add_ai_message(final_response)
            return final_response
        
        else:
            # No function call, just return the response
            self.memory.add_ai_message(llm_response)
            return llm_response


# Global chatbot instance
medical_chatbot = MedicalCenterChatbot()


# ============================================================================
# Export functions
# ============================================================================

def handle_query(user_query: str) -> str:
    """Main function to handle user queries"""
    return medical_chatbot.chat(user_query)


def get_all_agents():
    """Return empty list since we're using simple chatbot now"""
    return []


def get_agent_by_role(role: str):
    """Return None since we're using simple chatbot now"""
    return None