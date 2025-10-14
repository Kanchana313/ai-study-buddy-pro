from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import os
import uuid
from config import Config
from chatbot import ChatBot
from test_simulator import TestSimulator
from knowledge_base import KnowledgeBase

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
chatbot = ChatBot()
test_simulator = TestSimulator()
knowledge_base = KnowledgeBase()

# --- NEW: Simple in-memory store for dashboard stats ---
# In a real app, you would use a database. This is just for demonstration.
app_data = {
    "chat_sessions": 0,
    "tests_completed": 0,
    "total_score": 0,
    "total_questions": 0,
    "study_time_minutes": 0
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/chat')
def chat():
    # Generate a unique session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('chat.html', session_id=session['session_id'])

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

# --- NEW: API endpoint to get dashboard stats ---
@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """Return real-time dashboard statistics"""
    avg_score = 0
    if app_data["total_questions"] > 0:
        avg_score = round((app_data["total_score"] / app_data["total_questions"]) * 100)
    
    study_time_hours = round(app_data["study_time_minutes"] / 60, 1)
    
    return jsonify({
        "chat_sessions": app_data["chat_sessions"],
        "tests_completed": app_data["tests_completed"],
        "average_score": avg_score,
        "study_time": f"{study_time_hours}h"
    })

# API Routes
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    # Get or create session ID
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # --- MODIFIED: Increment chat session count ---
    # We count each API call as a new chat session for simplicity
    app_data["chat_sessions"] += 1
    
    # Get response from chatbot
    response = chatbot.get_response(session_id, data['message'])
    
    return jsonify({
        "response": response["response"],
        "session_id": session_id
    })

@app.route('/api/test/create', methods=['POST'])
def api_test_create():
    """Create a new test"""
    data = request.get_json()
    
    if not data or 'topic' not in data:
        return jsonify({"error": "No topic provided"}), 400
    
    topic = data['topic']
    num_questions = data.get('num_questions', 10)
    difficulty = data.get('difficulty', 'medium')
    question_types = data.get('question_types', ['multiple choice', 'true/false'])
    duration = data.get('duration', 30)
    
    # Create test
    test = test_simulator.create_test(topic, num_questions, difficulty, question_types, duration)
    
    if "error" in test:
        return jsonify(test), 400
    
    return jsonify(test)

@app.route('/api/test/start', methods=['POST'])
def api_test_start():
    """Start a test"""
    data = request.get_json()
    
    if not data or 'test_id' not in data:
        return jsonify({"error": "No test ID provided"}), 400
    
    test_id = data['test_id']
    
    # Start test
    result = test_simulator.start_test(test_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/api/test/question', methods=['POST'])
def api_test_question():
    """Get the next question in a test"""
    data = request.get_json()
    
    if not data or 'test_id' not in data:
        return jsonify({"error": "No test ID provided"}), 400
    
    test_id = data['test_id']
    
    # Get next question
    result = test_simulator.get_next_question(test_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/api/test/answer', methods=['POST'])
def api_test_answer():
    """Submit an answer for a test question"""
    data = request.get_json()
    
    if not data or 'test_id' not in data or 'answer' not in data:
        return jsonify({"error": "Missing required data"}), 400
    
    test_id = data['test_id']
    answer = data['answer']
    
    # Submit answer
    result = test_simulator.submit_answer(test_id, answer)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/api/test/complete', methods=['POST'])
def api_test_complete():
    """Complete a test and get results"""
    data = request.get_json()
    
    if not data or 'test_id' not in data:
        return jsonify({"error": "No test ID provided"}), 400
    
    test_id = data['test_id']
    
    # Complete test
    result = test_simulator.complete_test(test_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    # --- MODIFIED: Update stats when a test is completed ---
    if "correct_answers" in result and "total_questions" in result:
        app_data["tests_completed"] += 1
        app_data["total_score"] += result["correct_answers"]
        app_data["total_questions"] += result["total_questions"]
        # Assuming time_taken is in seconds, convert to minutes
        if "time_taken" in result:
            app_data["study_time_minutes"] += round(result["time_taken"] / 60)
    
    return jsonify(result)

@app.route('/api/test/status', methods=['POST'])
def api_test_status():
    """Get the status of a test"""
    data = request.get_json()
    
    if not data or 'test_id' not in data:
        return jsonify({"error": "No test ID provided"}), 400
    
    test_id = data['test_id']
    
    # Get test status
    result = test_simulator.get_test_status(test_id)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/api/clear_chat', methods=['POST'])
def api_clear_chat():
    """Clear the chat history"""
    data = request.get_json()
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Clear conversation
    chatbot.clear_conversation(session_id)
    
    return jsonify({"status": "success", "session_id": session_id})

if __name__ == '__main__':
    app.run(debug=True)