"""
Flask Web Application for Medical Center AI Chatbot
Provides a web interface for interacting with the AI assistant
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import config
from src.agents import medical_crew


# Initialize Flask app
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
CORS(app)

# Store conversation history in memory
conversations = {}


@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        # Get user message
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create session ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        
        # Initialize conversation history for this session
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Add user message to history
        conversations[session_id].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process message with crew
        response = medical_crew.handle_query(user_message)
        
        # Add assistant response to history
        conversations[session_id].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Return response
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/history', methods=['GET'])
def history():
    """Get conversation history"""
    try:
        session_id = session.get('session_id')
        
        if not session_id or session_id not in conversations:
            return jsonify({'history': []})
        
        return jsonify({
            'history': conversations[session_id],
            'session_id': session_id
        })
    
    except Exception as e:
        print(f"Error in history endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear():
    """Clear conversation history"""
    try:
        session_id = session.get('session_id')
        
        if session_id and session_id in conversations:
            conversations[session_id] = []
        
        return jsonify({'message': 'Conversation cleared'})
    
    except Exception as e:
        print(f"Error in clear endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/info', methods=['GET'])
def info():
    """Get medical center information"""
    try:
        return jsonify({
            'center_name': config.CENTER_NAME,
            'phone': config.CENTER_PHONE,
            'pt_phone': config.PT_PHONE,
            'pt_email': config.PT_EMAIL,
            'location': config.CENTER_LOCATION,
            'hours': {
                'weekday': config.WEEKDAY_HOURS,
                'saturday': config.SATURDAY_HOURS,
                'sunday': config.SUNDAY_HOURS
            }
        })
    
    except Exception as e:
        print(f"Error in info endpoint: {e}")
        return jsonify({'error': str(e)}), 500


def run_app():
    """Run the Flask application"""
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║   Medical Center AI Chatbot - Starting Flask Server...      ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🏥 Center: {config.CENTER_NAME}
    📞 Phone: {config.CENTER_PHONE}
    🌐 Server: http://{config.FLASK_HOST}:{config.FLASK_PORT}
    🤖 Model: {config.LLM_MODEL}
    💾 Vector DB: {config.COLLECTION_NAME}
    
    """)
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == '__main__':
    run_app()
