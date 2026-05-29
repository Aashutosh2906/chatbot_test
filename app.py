from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from chatbot import GLMChatbot

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global chatbot instance
chatbot_instance = None
HISTORY_FILE = 'chat_history.json'

def load_history_from_file():
    """Load chat history from JSON file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history_to_file(history):
    """Save chat history to JSON file"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def get_chatbot():
    global chatbot_instance
    if chatbot_instance is None:
        try:
            chatbot_instance = GLMChatbot()
            # Load previous history into chatbot
            history = load_history_from_file()
            chatbot_instance.conversation_history = history
        except ValueError as e:
            return None, str(e)
    return chatbot_instance, None

# Read the HTML file
def get_html_content():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <h1>index.html not found</h1>
            <p>The frontend file could not be loaded.</p>
        </body>
        </html>
        """

@app.route('/')
def home():
    """Serve the home page (index.html)"""
    return render_template_string(get_html_content())

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message field is required"}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        chatbot, error = get_chatbot()
        if error:
            return jsonify({"error": error}), 500
        
        response = chatbot.send_message(user_message)
        
        # Save history after each message
        save_history_to_file(chatbot.conversation_history)
        
        return jsonify({
            "success": True,
            "message": user_message,
            "response": response
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        history = load_history_from_file()
        return jsonify({
            "success": True,
            "history": history
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    try:
        global chatbot_instance
        
        # Clear from file
        save_history_to_file([])
        
        # Clear from chatbot instance
        if chatbot_instance:
            chatbot_instance.reset_conversation()
        
        return jsonify({
            "success": True,
            "message": "Conversation history cleared"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/reset', methods=['POST'])
def reset_chatbot():
    """Reset chatbot instance and clear history"""
    global chatbot_instance
    try:
        # Clear history file
        save_history_to_file([])
        
        # Reset chatbot instance
        chatbot_instance = None
        
        return jsonify({
            "success": True,
            "message": "Chatbot reset successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
