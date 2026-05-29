from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
from dotenv import load_dotenv
from chatbot import GLMChatbot

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global chatbot instance
chatbot_instance = None

def get_chatbot():
    global chatbot_instance
    if chatbot_instance is None:
        try:
            chatbot_instance = GLMChatbot()
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
        chatbot, error = get_chatbot()
        if error:
            return jsonify({"error": error}), 500
        
        return jsonify({
            "success": True,
            "history": chatbot.conversation_history
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    try:
        chatbot, error = get_chatbot()
        if error:
            return jsonify({"error": error}), 500
        
        chatbot.reset_conversation()
        
        return jsonify({
            "success": True,
            "message": "Conversation history cleared"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/reset', methods=['POST'])
def reset_chatbot():
    """Reset chatbot instance"""
    global chatbot_instance
    try:
        chatbot_instance = None
        return jsonify({
            "success": True,
            "message": "Chatbot reset successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
