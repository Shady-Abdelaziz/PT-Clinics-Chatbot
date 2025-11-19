# 🏥 Medical Center AI Chatbot - Project Summary

## Overview

An intelligent medical center chatbot built with **Google Gemini 2.5 Flash** that helps patients with:
- Information about doctors and services
- Appointment booking and management
- Knowledge base queries (RAG)
- Physical therapy information

**Status**: ✅ Production Ready (Gemini Migration Complete)
**Last Updated**: November 19, 2025
**LLM**: Google Gemini 2.5 Flash

---

## Key Features

### 1. Conversational AI (Gemini 2.5 Flash)
- Natural language understanding
- Context-aware responses (10-message memory)
- Function calling for complex tasks
- Low temperature (0.1) for accuracy
- Fast response times (Flash model)

### 2. Knowledge Base (RAG)
- Semantic search using Qdrant vector database
- Local embeddings via Ollama (privacy-focused)
- PDF document processing
- Doctor information, policies, procedures

### 3. Appointment Management
- Check doctor availability
- Book appointments
- Cancel appointments
- Search existing appointments
- Excel-based database

### 4. Web Interface
- Responsive design (mobile/desktop)
- Real-time chat interface
- Session-based conversations
- Conversation history

---

## Technology Stack

### Core Technologies
| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | Google Gemini 2.5 Flash | Conversational AI |
| **Embeddings** | Ollama (nomic-embed-text) | Vector generation (local) |
| **Vector DB** | Qdrant Cloud | Semantic search |
| **Backend** | Flask (Python 3.8+) | Web server |
| **Database** | Excel (openpyxl) | Appointment data |
| **Frontend** | HTML/CSS/JavaScript | User interface |

### Why Gemini 2.5 Flash?
- ⚡ Fastest Gemini model (optimized for speed)
- 🧠 Advanced reasoning capabilities
- 🆓 Generous free tier (15 RPM, 1M TPM)
- 🎯 High accuracy for medical information
- 📚 Large context window (1M tokens in Pro)
- 💰 Cost-effective ($0.075 per 1M tokens)

---

## Project Structure

```
medical-center-chatbot/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── medical_agents.py      # Gemini LLM integration
│   │   └── crew.py                # Simplified crew wrapper
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   └── medical_tools.py       # Knowledge & appointment tools
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py              # Gemini configuration
│   │   ├── excel_manager.py       # Appointment database
│   │   └── vector_db_manager.py   # Qdrant + Ollama embeddings
│   │
│   └── app.py                     # Flask web server
│
├── data/
│   ├── Doctor_Information_Guide.pdf
│   ├── Physical_Therapy_Clinic_Guide.pdf
│   └── Simple_Clinic_Database.xlsx
│
├── templates/
│   └── index.html                 # Web UI
│
├── static/
│   ├── css/
│   └── js/
│
├── .env                           # Configuration (Gemini API key)
├── requirements.txt               # Python dependencies
├── index_documents.py             # Document indexing script
├── verify_setup.py                # Setup verification
└── test_booking_fix.py            # Test suite

```

---

## Core Components

### 1. Medical Chatbot (`medical_agents.py`)

**Key Class**: `MedicalCenterChatbot`

**Features**:
- Conversation memory (10 messages)
- Function call detection and execution
- Gemini 2.5 Flash integration
- Parameter extraction (dates, times, names)
- Error handling

**Function Calls**:
```python
# Supported functions:
- search_knowledge: "query"
- get_doctors
- check_availability: "doctor" [date]
- book_appointment: doctor date time name phone
- cancel_appointment: doctor name [date] [time]
- search_appointments: [patient] [doctor] [date]
```

### 2. Gemini Integration

**API Configuration**:
```python
GEMINI_API_KEY = "AIzaSy..."
GEMINI_MODEL = "gemini-2.5-flash-latest"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
```

**Key Method**: `_call_gemini_llm(messages)`
- Converts to Gemini format (systemInstruction + contents)
- Handles role conversion (assistant → model)
- Error handling and retry logic
- Response parsing

**Request Format**:
```python
{
    "systemInstruction": {
        "parts": [{"text": system_prompt}]
    },
    "contents": [
        {"role": "user", "parts": [{"text": "..."}]},
        {"role": "model", "parts": [{"text": "..."}]}
    ],
    "generationConfig": {
        "temperature": 0.1,
        "maxOutputTokens": 4096
    }
}
```

### 3. Vector Database (`vector_db_manager.py`)

**Components**:
- Qdrant client for vector storage/search
- Ollama client for local embeddings
- Document processing (PDF, Excel)
- Text chunking

**Workflow**:
```
PDF → Extract Text → Chunk → Embed (Ollama) → Store (Qdrant)
Query → Embed (Ollama) → Search (Qdrant) → Results
```

### 4. Appointment Manager (`excel_manager.py`)

**Operations**:
- `get_available_slots()` - List free time slots
- `book_appointment()` - Reserve a slot
- `cancel_appointment()` - Free up a slot
- `search_appointments()` - Find bookings

**Excel Structure**:
- One sheet per doctor
- Columns: Date, Time, Patient_Name, Phone, Status
- Status: "Available" or "Reserved"

---

## Data Flow

### User Query → Response Flow

```
1. User sends message via Web UI
   ↓
2. Flask API receives request (/api/chat)
   ↓
3. Medical Chatbot processes query
   ↓
4. Add to conversation memory (context)
   ↓
5. Call Gemini 2.5 Flash with context
   ↓
6. Detect function call (if any)
   ↓
7. Execute function:
   - Knowledge search → Qdrant
   - Appointments → Excel
   - Doctor info → Excel/Qdrant
   ↓
8. Format results
   ↓
9. Call Gemini again for natural response
   ↓
10. Add response to memory
   ↓
11. Return to user via Web UI
```

### Appointment Booking Flow

```
User: "Book Dr. Sarah on Dec 12 at 10 AM"
   ↓
Gemini: Detects booking intent
   ↓
Check: All params present? (doctor, date, time, name, phone)
   ├─ NO → Ask for missing info
   └─ YES → Continue
       ↓
   check_availability(doctor, date)
       ├─ NOT AVAILABLE → Suggest alternatives
       └─ AVAILABLE → Continue
           ↓
       book_appointment(doctor, date, time, name, phone)
           ↓
       Update Excel (Status = "Reserved")
           ↓
       Confirmation to user
```

---

## Setup & Installation

### Prerequisites
1. Python 3.8+
2. Ollama (for embeddings)
3. Google Gemini API key
4. Qdrant Cloud account

### Installation Steps

```bash
# 1. Clone repository
git clone <repository-url>
cd medical-center-chatbot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install and start Ollama
# Visit: https://ollama.ai/
ollama serve
ollama pull nomic-embed-text

# 5. Get Gemini API key
# Visit: https://aistudio.google.com/
# Create API key

# 6. Configure .env
cp .env.example .env
# Edit .env and add:
# GEMINI_API_KEY=your_actual_key_here
# GEMINI_MODEL=gemini-2.5-flash-latest

# 7. Verify setup
python verify_setup.py

# 8. Index documents
python index_documents.py

# 9. Run application
python src/app.py

# 10. Open browser
# Visit: http://localhost:5000
```

---

## Configuration

### Environment Variables (.env)

```env
# Google Gemini API (LLM)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-latest

# Ollama (Embeddings - Local)
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text:latest

# LLM Settings
LLM_TEMPERATURE=0.1  # Focused responses for medical accuracy

# Qdrant Vector Database
QDRANT_URL=https://...qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key
COLLECTION_NAME=medical_center_knowledge

# Medical Center Info
CENTER_NAME=Medical Center
CENTER_PHONE=(555) 200-1000
CENTER_LOCATION=Cairo, Egypt

# Retrieval Settings
RAG_RETRIEVAL_K=25
RAG_SCORE_THRESHOLD=0.0001

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

---

## API Endpoints

### Flask REST API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve web UI |
| `/api/chat` | POST | Process chat message |
| `/api/history` | GET | Get conversation history |
| `/api/clear` | POST | Clear conversation |
| `/api/info` | GET | Get medical center info |

### Example API Call

```bash
# Chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "When is Dr. Sarah available?"}'

# Response
{
  "response": "Dr. Sarah Martinez has the following available slots...",
  "session_id": "uuid-here",
  "timestamp": "2025-11-19T..."
}
```

---

## Testing

### Run Test Suite

```bash
# Test booking functionality
python test_booking_fix.py

# Verify setup
python verify_setup.py
```

### Manual Testing Checklist

- [ ] General questions (hours, location, contact)
- [ ] Doctor information queries
- [ ] Check doctor availability
- [ ] Book appointment
- [ ] Cancel appointment
- [ ] Search appointments
- [ ] Long conversation context
- [ ] Error handling

---

## Performance

### Gemini 2.5 Flash Metrics

**Response Times**:
- Simple queries: ~1-2 seconds
- Function calls: ~2-4 seconds
- Knowledge search: ~3-5 seconds

**Rate Limits (Free Tier)**:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

**Costs (Paid Tier)**:
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- Very cost-effective for chatbot use

---

## Troubleshooting

### Common Issues

**1. "API key not valid"**
- Check GEMINI_API_KEY in .env
- Verify key is active in Google AI Studio
- Ensure no extra spaces

**2. "Cannot connect to Ollama"**
- Start Ollama: `ollama serve`
- Install embedding model: `ollama pull nomic-embed-text`
- Check OLLAMA_BASE_URL in .env

**3. "Qdrant connection failed"**
- Verify QDRANT_URL and QDRANT_API_KEY
- Check internet connection
- Ensure Qdrant Cloud is accessible

**4. "No available slots"**
- Check Excel file exists: `data/Simple_Clinic_Database.xlsx`
- Verify doctor names match exactly
- Ensure Status column has "Available" entries

---

## Deployment

### Production Checklist

- [ ] Set `FLASK_DEBUG=False`
- [ ] Use production WSGI server (Gunicorn)
- [ ] Configure SSL/HTTPS (nginx)
- [ ] Set up monitoring/logging
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting
- [ ] Set up backups
- [ ] Configure CORS properly

### Example Gunicorn Deployment

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.app:app
```

---

## Security Considerations

### API Key Security
- Store in environment variables
- Never commit to version control
- Rotate keys periodically
- Monitor usage in Google AI Studio

### Data Privacy
- Embeddings generated locally (Ollama)
- Patient data in local Excel file
- HTTPS for production
- Input validation and sanitization

---

## Future Enhancements

### Planned Features
1. **Voice Interface** - Speech-to-text and text-to-speech
2. **Multi-language** - Arabic, English, French support
3. **SMS Integration** - Appointment reminders
4. **Analytics Dashboard** - Usage metrics and insights
5. **Native Function Calling** - Use Gemini's function calling API
6. **Database Migration** - Move from Excel to PostgreSQL
7. **Authentication** - Staff login for management

---

## Resources

### Documentation
- **This Project**: See ARCHITECTURE.md, DIAGRAMS.md
- **Gemini API**: https://ai.google.dev/gemini-api/docs
- **Google AI Studio**: https://aistudio.google.com/
- **Ollama**: https://ollama.ai/
- **Qdrant**: https://qdrant.tech/documentation/

### Getting Help
- Check verify_setup.py for configuration issues
- Review test_booking_fix.py for functionality tests
- See MIGRATION_GUIDE.md for migration details
- Check logs in console output

---

## Contributors

Development Team
- Architecture & Implementation
- Gemini API Integration
- Testing & Documentation

---

## License

[Your License Here]

---

## Changelog

### Version 2.0.0 (November 19, 2025)
- ✅ Migrated from OpenRouter/DeepSeek to Google Gemini 2.5 Flash
- ✅ Updated all components for Gemini API
- ✅ Improved response times with Flash model
- ✅ Enhanced documentation
- ✅ Updated test suite

### Version 1.0.0 (Initial Release)
- Initial implementation with DeepSeek
- Core chatbot functionality
- Appointment management
- Knowledge base RAG

---

**Project Status**: ✅ Active Development
**LLM Provider**: Google Gemini 2.5 Flash
**Last Updated**: November 19, 2025