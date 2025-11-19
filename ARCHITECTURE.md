# 🏗️ Medical Center AI Chatbot - Architecture Documentation

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Layers](#architecture-layers)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Sequence Diagrams](#sequence-diagrams)
- [Database Design](#database-design)
- [Deployment Architecture](#deployment-architecture)
- [Scalability Considerations](#scalability-considerations)

---

## System Overview

The Medical Center AI Chatbot is built on a modern, modular architecture that separates concerns across multiple layers, enabling maintainability, scalability, and extensibility.

### Architecture Principles

1. **Separation of Concerns**: Clear boundaries between UI, business logic, AI processing, and data storage
2. **Modularity**: Independent components that can be updated or replaced
3. **Scalability**: Designed to handle growing user load and data volume
4. **Privacy-First**: Optional local processing for sensitive medical data
5. **Hybrid Approach**: Combines cloud services with local AI models

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Web UI (HTML/CSS/JavaScript)                                       │ │
│  │  • Single-page application                                          │ │
│  │  • Responsive design (mobile/tablet/desktop)                        │ │
│  │  • Real-time chat interface with WebSocket support potential        │ │
│  │  • Session-based conversation tracking                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↕ REST API (JSON)
┌─────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Flask Web Framework                                                │ │
│  │  • RESTful API endpoints                                            │ │
│  │  • Request/response handling                                        │ │
│  │  • Session management (UUID-based)                                  │ │
│  │  • Error handling and validation                                    │ │
│  │  • CORS configuration                                               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Business Logic Controllers                                         │ │
│  │  • Chat endpoint controller                                         │ │
│  │  • History management controller                                    │ │
│  │  • Information retrieval controller                                 │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI PROCESSING LAYER                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Medical Chatbot Engine                                             │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │  Conversation Manager                                         │  │ │
│  │  │  • Context window management (10 messages)                    │  │ │
│  │  │  • Message history storage                                    │  │ │
│  │  │  • Session state tracking                                     │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │  Query Processing Pipeline                                    │  │ │
│  │  │  1. Query Analysis                                            │  │ │
│  │  │  2. Intent Classification                                     │  │ │
│  │  │  3. Function Call Detection                                   │  │ │
│  │  │  4. Parameter Extraction                                      │  │ │
│  │  │  5. Function Execution                                        │  │ │
│  │  │  6. Response Generation                                       │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │  Function Orchestrator                                        │  │ │
│  │  │  • Function registry                                          │  │ │
│  │  │  • Dynamic function routing                                   │  │ │
│  │  │  • Error handling and fallbacks                               │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                          INTEGRATION LAYER                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  LLM Service Adapter (OpenRouter)                                   │ │
│  │  • API client with retry logic                                      │ │
│  │  • Request/response transformation                                  │ │
│  │  • Token usage tracking                                             │ │
│  │  • Model: tngtech/deepseek-r1t2-chimera:free                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Embedding Service Adapter (Ollama)                                 │ │
│  │  • Local HTTP client                                                │ │
│  │  • Batch processing support                                         │ │
│  │  • Connection pooling                                               │ │
│  │  • Model: nomic-embed-text:latest                                   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                             TOOL LAYER                                   │
│  ┌──────────────┬──────────────┬─────────────┬──────────────────────┐  │
│  │  Knowledge   │  Appointment │   Doctor    │     Database         │  │
│  │  Search      │  Management  │  Management │     Operations       │  │
│  │  Tool        │  Tools       │   Tools     │     Tools            │  │
│  │              │              │             │                      │  │
│  │  • Semantic  │  • Check     │  • List     │  • CRUD operations   │  │
│  │    search    │    slots     │    doctors  │  • Validation        │  │
│  │  • RAG       │  • Book      │  • Get      │  • Formatting        │  │
│  │    pipeline  │    appt      │    details  │  • Color coding      │  │
│  │  • Score     │  • Cancel    │  • Search   │                      │  │
│  │    threshold │    appt      │    by spec  │                      │  │
│  │    filter    │  • Search    │             │                      │  │
│  └──────────────┴──────────────┴─────────────┴──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA ACCESS LAYER                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Vector Database Manager                                            │ │
│  │  • Qdrant client wrapper                                            │ │
│  │  • Collection management                                            │ │
│  │  • Index operations                                                 │ │
│  │  • Search query optimization                                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Excel Database Manager                                             │ │
│  │  • File I/O operations                                              │ │
│  │  • Sheet management                                                 │ │
│  │  • Cell formatting                                                  │ │
│  │  • Data validation                                                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Document Processor                                                 │ │
│  │  • PDF text extraction                                              │ │
│  │  • Text chunking                                                    │ │
│  │  • Metadata management                                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                     ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                   │
│  ┌──────────────┬──────────────────────────┬─────────────────────────┐ │
│  │   Qdrant     │      Excel File          │    PDF Documents        │ │
│  │   Cloud      │      Database            │    Repository           │ │
│  │              │                          │                         │ │
│  │  • Vector    │  • Appointment           │  • Doctor info          │ │
│  │    embeddings│    schedules             │  • PT procedures        │ │
│  │  • Metadata  │  • Patient data          │  • Center policies      │ │
│  │  • Indexes   │  • Doctor sheets         │  • Guidelines           │ │
│  └──────────────┴──────────────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Presentation Layer

#### Web UI Component
- **Technology**: HTML5, CSS3, JavaScript (Vanilla)
- **Features**:
  - Gradient background design
  - Responsive layout (Flexbox/Grid)
  - Message bubbles with animations
  - Typing indicators
  - Auto-scroll on new messages
  - Clear conversation button
  
#### Communication Protocol
```javascript
// POST request structure
{
  method: 'POST',
  url: '/api/chat',
  headers: { 'Content-Type': 'application/json' },
  body: {
    message: "user query"
  }
}

// Response structure
{
  response: "AI response text",
  session_id: "uuid",
  timestamp: "ISO 8601 timestamp"
}
```

---

### 2. Application Layer

#### Flask Application (`app.py`)

**Responsibilities**:
- HTTP request handling
- Session management
- API endpoint routing
- Error handling
- Response formatting

**Key Endpoints**:
```python
GET  /                 → Serve web UI
POST /api/chat        → Process user messages
GET  /api/history     → Get conversation history
POST /api/clear       → Clear conversation
GET  /api/info        → Get center information
```

**Session Management**:
```python
# UUID-based session tracking
session['session_id'] = str(uuid.uuid4())

# In-memory conversation storage
conversations = {
    'session-uuid': [
        {'role': 'user', 'content': '...', 'timestamp': '...'},
        {'role': 'assistant', 'content': '...', 'timestamp': '...'}
    ]
}
```

---

### 3. AI Processing Layer

#### Medical Chatbot Engine (`src/agents/medical_agents.py`)

**Core Components**:

1. **Conversation Memory**
   ```python
   class ConversationMemory:
       max_messages: int = 10  # Sliding window
       messages: List[Dict]     # Message history
       
       def add_user_message(message: str)
       def add_ai_message(message: str)
       def get_context() → List[Dict]
   ```

2. **Query Processing Pipeline**
   ```
   User Query
       ↓
   1. Load conversation context (last 10 messages)
       ↓
   2. Inject system prompt with:
      - Available functions
      - Medical center info
      - Conversation rules
       ↓
   3. Send to LLM (OpenRouter)
       ↓
   4. Extract function call (if any)
       ↓
   5. Execute function
       ↓
   6. Format result with LLM
       ↓
   7. Update conversation memory
       ↓
   Response
   ```

3. **Function Call System**
   ```python
   # Extraction patterns
   XML_PATTERN = r"<function_name>(.*?)</function_name>"
   TEXT_PATTERN = r"function_name:\s*(.+?)(?:\n|$)"
   
   # Function registry
   functions = {
       'search_knowledge': _execute_knowledge_search,
       'check_availability': _execute_availability_check,
       'book_appointment': _execute_booking,
       'cancel_appointment': _execute_cancellation,
       'search_appointments': _execute_search,
       'get_doctors': _execute_get_doctors
   }
   ```

---

### 4. Integration Layer

#### LLM Service (OpenRouter)

**Configuration**:
```python
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "tngtech/deepseek-r1t2-chimera:free"
TEMPERATURE = 0.1
MAX_TOKENS = 4080
```

**Request Structure**:
```json
{
  "model": "tngtech/deepseek-r1t2-chimera:free",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "temperature": 0.1,
  "max_tokens": 4080,
  "thinking": {"type": "disabled"}
}
```

#### Embedding Service (Ollama)

**Configuration**:
```python
BASE_URL = "http://localhost:11434"
MODEL = "nomic-embed-text:latest"
EMBEDDING_DIM = 768
```

**Request Structure**:
```json
{
  "model": "nomic-embed-text",
  "prompt": "text to embed"
}
```

**Response**:
```json
{
  "embedding": [0.123, -0.456, ..., 0.789]  // 768 dimensions
}
```

---

### 5. Tool Layer

#### Knowledge Search Tool

**Purpose**: Semantic search across medical documents

**Implementation**:
```python
def search_knowledge(query: str) → str:
    # 1. Generate query embedding
    embedding = ollama.embed_query(query)
    
    # 2. Search Qdrant
    results = qdrant.search(
        collection="medical_center_knowledge",
        query_vector=embedding,
        limit=10,
        score_threshold=0.1
    )
    
    # 3. Format results
    formatted = format_search_results(results)
    
    return formatted
```

#### Appointment Management Tools

**Tools**:
1. `check_availability(doctor_name, date?)` → List of available slots
2. `book_appointment(doctor, date, time, patient, phone)` → Booking confirmation
3. `cancel_appointment(doctor, patient, date?, time?)` → Cancellation confirmation
4. `search_appointments(patient?, doctor?, date?)` → List of appointments

**Excel Operations**:
```python
# Read schedule
schedule = excel_manager.read_sheet(doctor_name)

# Book appointment
excel_manager.write_cell(sheet, row, col, patient_name)
excel_manager.apply_color(sheet, row, "green")

# Cancel appointment
excel_manager.clear_cell(sheet, row, col)
excel_manager.apply_color(sheet, row, "white")
```

---

### 6. Data Access Layer

#### Vector Database Manager (`src/utils/vector_db_manager.py`)

**Responsibilities**:
- Qdrant connection management
- Document indexing
- Embedding generation
- Semantic search

**Key Methods**:
```python
class VectorDBManager:
    def recreate_collection()
    def extract_text_from_pdf(file_path) → str
    def process_pdf_file(file_path) → List[Dict]
    def upload_documents(documents)
    def search(query, limit, score_threshold) → List[Dict]
    def index_all_files(pdf_files, excel_files)
```

#### Excel Database Manager (`src/utils/excel_manager.py`)

**Responsibilities**:
- Excel file operations
- Appointment CRUD
- Schedule management
- Data validation

**Key Methods**:
```python
class ExcelDBManager:
    def get_all_doctors() → List[str]
    def get_available_slots(doctor, date?, limit?) → List[Dict]
    def book_appointment(doctor, date, time, patient, phone) → Tuple[bool, str]
    def cancel_appointment(doctor, patient, date?, time?) → Tuple[bool, str]
    def search_appointments(patient?, doctor?, date?) → List[Dict]
```

---

## Data Flow

### Information Query Flow

```
User: "Who is Dr. Sarah Martinez?"
  ↓
[Web UI] → POST /api/chat
  ↓
[Flask] → chat_endpoint()
  ↓
[Session Manager] → Load conversation context
  ↓
[Medical Chatbot] → Process query with context
  ↓
[OpenRouter LLM] → Analyze query, detect intent
  ↓ (Function call detected)
[Function Extractor] → Extract: search_knowledge("Dr. Sarah Martinez")
  ↓
[Knowledge Search Tool] → Execute search
  ↓
[Ollama] → Generate query embedding (768 dims)
  ↓
[Qdrant] → Search with cosine similarity
  ↓ (Returns top 10 results)
[Knowledge Search Tool] → Format results
  ↓
[Medical Chatbot] → Call LLM again to format response
  ↓
[OpenRouter LLM] → Generate natural language response
  ↓
[Conversation Memory] → Update history
  ↓
[Flask] → JSON response
  ↓
[Web UI] → Display message
```

### Appointment Booking Flow

```
User: "Book with Dr. Sarah on Nov 20 at 10 AM for John Doe (555-1234)"
  ↓
[Web UI] → POST /api/chat
  ↓
[Flask] → chat_endpoint()
  ↓
[Medical Chatbot] → Process with context
  ↓
[OpenRouter LLM] → Detect booking intent
  ↓ (Function call)
[Function Extractor] → Extract: book_appointment(...)
  ↓
[Appointment Tool] → Validate parameters
  ↓
[Name Matcher] → Match "Sarah" → "Dr. Sarah Martinez"
  ↓
[Date Normalizer] → "Nov 20" → "2025-11-20"
  ↓
[Time Normalizer] → "10 AM" → "10:00"
  ↓
[Excel Manager] → Open doctor's sheet
  ↓
[Excel Manager] → Find matching date/time row
  ↓
[Excel Manager] → Check if slot is available
  ↓ (If available)
[Excel Manager] → Write patient name and phone
  ↓
[Excel Manager] → Apply green color to cells
  ↓
[Excel Manager] → Save file
  ↓
[Appointment Tool] → Return success message
  ↓
[Medical Chatbot] → Format confirmation
  ↓
[Flask] → JSON response
  ↓
[Web UI] → Display confirmation
```

---

## Sequence Diagrams

### Full Query Processing Sequence

```
User    WebUI    Flask    Chatbot    LLM    Tools    Database
 |        |        |         |        |       |         |
 |--msg-->|        |         |        |       |         |
 |        |--POST->|         |        |       |         |
 |        |        |--query->|        |       |         |
 |        |        |         |--ctx-->|       |         |
 |        |        |         |        |       |         |
 |        |        |         |<-resp--|       |         |
 |        |        |         |        |       |         |
 |        |        |         |--extract-fn    |         |
 |        |        |         |        |       |         |
 |        |        |         |--execute------>|         |
 |        |        |         |        |       |         |
 |        |        |         |        |       |--query->|
 |        |        |         |        |       |<-data---|
 |        |        |         |<-result--------|         |
 |        |        |         |        |       |         |
 |        |        |         |--format-resp-->|         |
 |        |        |         |<-formatted-----|         |
 |        |        |         |        |       |         |
 |        |        |<-json---|        |       |         |
 |        |<-200---|         |        |       |         |
 |<-show--|        |         |        |       |         |
```

---

## Database Design

### Vector Database (Qdrant)

**Collection Structure**:
```
Collection: medical_center_knowledge
├── Configuration:
│   ├── vector_size: 768
│   ├── distance: Cosine
│   └── index: HNSW
│
└── Documents:
    ├── Point ID: UUID
    ├── Vector: [768 floats]
    └── Payload:
        ├── text: "document chunk text"
        └── metadata:
            ├── filename: "Doctor_Information_Guide.pdf"
            ├── source_type: "pdf"
            ├── chunk_index: 0
            └── total_chunks: 45
```

### Excel Database

**File Structure**:
```
Simple_Clinic_Database.xlsx
├── Sheet: "Dr. Sarah Martinez"
│   ├── Headers: [Date, Time, Patient_Name, Phone, Status]
│   ├── Data:
│   │   ├── Row 2: [2025-11-20, 09:00 AM, John Doe, 555-1234, Booked] (GREEN)
│   │   ├── Row 3: [2025-11-20, 09:30 AM, , , Available] (WHITE)
│   │   └── ...
│   └── Formatting:
│       ├── Booked = Green cells
│       └── Available = White cells
│
├── Sheet: "Dr. James Wilson"
│   └── ...
│
└── Sheet: "Dr. Emily Roberts"
    └── ...
```

---

## Deployment Architecture

### Single Server Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                      Production Server                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Nginx (Port 80/443)                 │ │
│  │  • SSL/TLS termination                                 │ │
│  │  • Static file serving                                 │ │
│  │  • Reverse proxy                                       │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────┴─────────────────────────────────┐ │
│  │            Gunicorn (Port 5000)                        │ │
│  │  • 4 worker processes                                  │ │
│  │  • Flask application                                   │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────┴─────────────────────────────────┐ │
│  │            Ollama Service (Port 11434)                 │ │
│  │  • Local embedding generation                          │ │
│  │  • nomic-embed-text model                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  File System                           │ │
│  │  • Excel database                                      │ │
│  │  • PDF documents                                       │ │
│  │  • Application logs                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ↓
            ┌────────────────────────┐
            │   External Services    │
            ├────────────────────────┤
            │  OpenRouter API        │
            │  Qdrant Cloud          │
            └────────────────────────┘
```

### High Availability Deployment

```
┌──────────────────────────────────────────────────────────────┐
│                     Load Balancer (HAProxy)                   │
│  • Health checks                                              │
│  • SSL termination                                            │
│  • Round-robin distribution                                   │
└────────┬────────────────────────────────────────────┬────────┘
         │                                            │
┌────────┴────────┐                          ┌────────┴────────┐
│  App Server 1   │                          │  App Server 2   │
│  ┌───────────┐  │                          │  ┌───────────┐  │
│  │  Nginx    │  │                          │  │  Nginx    │  │
│  └─────┬─────┘  │                          │  └─────┬─────┘  │
│  ┌─────┴─────┐  │                          │  ┌─────┴─────┐  │
│  │ Gunicorn  │  │                          │  │ Gunicorn  │  │
│  └─────┬─────┘  │                          │  └─────┬─────┘  │
│  ┌─────┴─────┐  │                          │  ┌─────┴─────┐  │
│  │  Ollama   │  │                          │  │  Ollama   │  │
│  └───────────┘  │                          │  └───────────┘  │
└────────┬────────┘                          └────────┬────────┘
         │                                            │
         └────────────────┬──────────────────────────┘
                          │
         ┌────────────────┴────────────────┐
         │    Shared File System (NFS)     │
         │  • Excel database               │
         │  • PDF documents                │
         └─────────────────────────────────┘
```

---

## Scalability Considerations

### Vertical Scaling (Single Server)

**Current Limits**:
- 50-100 concurrent users
- 1000 requests/hour
- 2-5 second response time

**Optimization Strategies**:
1. Increase worker processes: `gunicorn -w 8`
2. Add Redis for session storage
3. Implement response caching
4. Use connection pooling

### Horizontal Scaling (Multiple Servers)

**Requirements**:
1. **Shared Session Store**
   ```python
   # Use Redis instead of in-memory
   from flask_session import Session
   app.config['SESSION_TYPE'] = 'redis'
   app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
   ```

2. **Shared File System**
   - Mount NFS for Excel database
   - Or migrate to PostgreSQL/MySQL

3. **Database Connection Pooling**
   ```python
   # For SQL databases
   from sqlalchemy import create_engine
   engine = create_engine('postgresql://...', pool_size=20)
   ```

### Caching Strategy

```python
from functools import lru_cache
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=300)
def search_knowledge(query: str):
    # Cache search results for 5 minutes
    return vector_manager.search(query)

@lru_cache(maxsize=100)
def get_doctor_info(doctor_name: str):
    # In-memory cache for frequently accessed data
    return excel_manager.get_doctor(doctor_name)
```

---

## Security Architecture

### Defense Layers

```
┌────────────────────────────────────────────────────────┐
│              Layer 1: Network Security                  │
│  • Firewall rules                                      │
│  • DDoS protection                                     │
│  • IP whitelisting (optional)                          │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│         Layer 2: Transport Security (TLS)              │
│  • HTTPS enforcement                                   │
│  • Certificate validation                              │
│  • Strong cipher suites                                │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│           Layer 3: Application Security                │
│  • Input validation                                    │
│  • Output sanitization                                 │
│  • CSRF protection                                     │
│  • Rate limiting                                       │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│            Layer 4: Data Security                      │
│  • Encryption at rest                                  │
│  • Encrypted backups                                   │
│  • Access logging                                      │
└────────────────────────────────────────────────────────┘
```

### API Security

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour", "10 per minute"]
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("20 per minute")
def chat():
    # Rate-limited endpoint
    pass
```

---

## Monitoring & Observability

### Logging Architecture

```python
import logging
from logging.handlers import RotatingFileHandler

# Application logs
app_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10_000_000,
    backupCount=10
)
app_handler.setLevel(logging.INFO)

# Error logs
error_handler = RotatingFileHandler(
    'logs/error.log',
    maxBytes=10_000_000,
    backupCount=10
)
error_handler.setLevel(logging.ERROR)

# Add handlers
app.logger.addHandler(app_handler)
app.logger.addHandler(error_handler)
```

### Metrics Collection

**Key Metrics**:
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (%)
- Active sessions
- Database query time
- LLM API latency
- Ollama embedding generation time

**Example Implementation**:
```python
import time
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    REQUEST_COUNT.inc()
    latency = time.time() - request.start_time
    REQUEST_LATENCY.observe(latency)
    return response
```

---

## Future Architecture Enhancements

### Microservices Migration

```
Current Monolith:
┌─────────────────┐
│  Flask App      │
│  • UI           │
│  • API          │
│  • AI Logic     │
│  • Data Access  │
└─────────────────┘

Future Microservices:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  API Gateway │→ │  Chat Service│  │  DB Service  │
└──────────────┘  └──────┬───────┘  └──────────────┘
                         │
                  ┌──────┴───────┐
                  │  AI Service  │
                  └──────────────┘
```

### Event-Driven Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Flask API  │────>│  Message     │────>│  Workers    │
│             │     │  Queue       │     │  • AI       │
└─────────────┘     │  (RabbitMQ)  │     │  • DB Ops   │
                    └──────────────┘     │  • Search   │
                                         └─────────────┘
```

---

**Document Version**: 1.0.0  
**Last Updated**: November 19, 2025  
**Maintained By**: Development Team
