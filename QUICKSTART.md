# 🚀 Quick Start Guide

## Prerequisites Installation

### 1. Install Ollama

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### 2. Pull Required Models

```bash
# Start Ollama (if not already running)
ollama serve

# In a new terminal, pull the models
ollama pull deepseek-r1:14b
ollama pull nomic-embed-text
```

This will take some time as the models are several GB in size.

## Project Setup

### 1. Install Python Dependencies

```bash
cd medical-chatbot-agent
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file and add your Qdrant credentials:

```env
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

You can get free Qdrant cloud credentials at: https://cloud.qdrant.io

### 3. Verify Setup

```bash
python verify_setup.py
```

This will check:
- ✅ Python version
- ✅ Ollama service and models
- ✅ Python dependencies
- ✅ Data files
- ✅ Environment variables
- ✅ Qdrant connection

### 4. Index Documents

```bash
python index_documents.py
```

This will:
- Connect to Qdrant
- Process PDF and Excel files
- Generate embeddings
- Upload to vector database

Expected output:
```
✅ Connected to Qdrant
✅ Found: Doctor_Information_Guide.pdf
✅ Found: Physical_Therapy_Clinic_Guide.pdf
✅ Found: Simple_Clinic_Database.xlsx
🚀 Starting indexing process...
✅ Indexing completed successfully!
```

### 5. Start the Application

```bash
python app.py
```

Expected output:
```
╔══════════════════════════════════════════════════════════════╗
║   Medical Center AI Chatbot - Starting Flask Server...      ║
╚══════════════════════════════════════════════════════════════╝

🏥 Center: Medical Center
📞 Phone: (555) 200-1000
🌐 Server: http://0.0.0.0:5000
🤖 Model: deepseek-r1:14b
💾 Vector DB: medical_center_knowledge

 * Running on http://0.0.0.0:5000
```

### 6. Open the Chat Interface

Open your browser and go to:
```
http://localhost:5000
```

## Testing the Chatbot

### Test Information Queries

Try these questions:

1. **"Who is Dr. Emily Roberts?"**
   - Should provide specialty, education, experience, availability

2. **"What physical therapy services do you offer?"**
   - Should list PT services

3. **"What are your operating hours?"**
   - Should provide hours for weekdays, Saturday, Sunday

### Test Appointment Features

1. **Check Availability:**
   ```
   "Show me available slots for Dr. James Wilson"
   ```

2. **Book Appointment:**
   ```
   "Book an appointment with Dr. Maria Garcia on 2025-11-15 at 10:00 AM for John Smith, phone 555-123-4567"
   ```

3. **Search Appointments:**
   ```
   "Find appointments for John Smith"
   ```

4. **Cancel Appointment:**
   ```
   "Cancel John Smith's appointment with Dr. Maria Garcia"
   ```

## Common Issues

### Ollama Not Running

**Error:** Cannot connect to Ollama

**Solution:**
```bash
ollama serve
```

### Model Not Found

**Error:** Model not found

**Solution:**
```bash
ollama pull deepseek-r1:14b
ollama pull nomic-embed-text
```

### Qdrant Connection Failed

**Error:** Cannot connect to Qdrant

**Solutions:**
1. Check `.env` file has correct credentials
2. Verify internet connection
3. Check Qdrant cloud dashboard

### Port Already in Use

**Error:** Port 5000 is already in use

**Solution:**
Change port in `.env`:
```env
FLASK_PORT=5001
```

## Performance Tips

### For Faster Responses

1. **Use GPU acceleration** (if available):
   - Ollama automatically uses GPU if available
   - Check with: `ollama info`

2. **Reduce model size** (if acceptable):
   ```env
   LLM_MODEL=deepseek-r1:7b
   ```

3. **Lower temperature** (more focused):
   ```env
   LLM_TEMPERATURE=0.1
   ```

### For Better Quality

1. **Increase retrieval results**:
   ```env
   RAG_RETRIEVAL_K=10
   ```

2. **Enable verbose mode** (for debugging):
   ```env
   CREW_VERBOSE=True
   ```

## Project Structure Overview

```
medical-chatbot-agent/
├── src/                     # Source code
│   ├── agents/             # CrewAI agents
│   ├── tools/              # Agent tools
│   └── utils/              # Utilities
├── data/                   # Data files
├── templates/              # HTML templates
├── .env                    # Configuration
├── app.py                  # Flask app
├── index_documents.py      # Indexing script
└── verify_setup.py         # Setup checker
```

## Next Steps

1. **Customize** the chatbot responses in `src/agents/medical_agents.py`
2. **Add more doctors** to the Excel database
3. **Extend tools** in `src/tools/medical_tools.py`
4. **Improve UI** in `templates/index.html`
5. **Deploy** to production server

## Getting Help

- 📖 README.md - Comprehensive documentation
- 🐛 verify_setup.py - Diagnose issues
- 🔍 Check logs in terminal for errors
- 💬 Review agent prompts in src/agents/

## Security Reminder

- ✅ All LLM processing is local (via Ollama)
- ✅ No data sent to external AI APIs
- ⚠️  Back up Excel database regularly
- ⚠️  Use HTTPS in production
- ⚠️  Implement authentication for production

---

**Happy Chatting! 🤖💬**
