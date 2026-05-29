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
CONVERSATIONS_FILE = 'conversations.json'

def load_conversations():
    """Load all conversations from JSON file"""
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_conversations(conversations):
    """Save conversations to JSON file"""
    try:
        with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving conversations: {e}")

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
        
        if not data.get('conversation_id'):
            return jsonify({"error": "Conversation ID is required"}), 400
        
        user_message = data['message'].strip()
        conversation_id = data['conversation_id']
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        chatbot, error = get_chatbot()
        if error:
            return jsonify({"error": error}), 500
        
        response = chatbot.send_message(user_message)
        
        # Save message to conversation
        conversations = load_conversations()
        if conversation_id not in conversations:
            conversations[conversation_id] = {
                "id": conversation_id,
                "title": user_message[:50] + "..." if len(user_message) > 50 else user_message,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
        
        conversations[conversation_id]["messages"].append({
            "role": "user",
            "content": user_message
        })
        conversations[conversation_id]["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        save_conversations(conversations)
        
        return jsonify({
            "success": True,
            "message": user_message,
            "response": response
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    try:
        conversations = load_conversations()
        # Return sorted by created_at (newest first)
        sorted_convs = sorted(
            conversations.values(),
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )
        return jsonify({
            "success": True,
            "conversations": sorted_convs
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation"""
    try:
        conversations = load_conversations()
        if conversation_id in conversations:
            return jsonify({
                "success": True,
                "conversation": conversations[conversation_id]
            }), 200
        else:
            return jsonify({
                "error": "Conversation not found"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        conversations = load_conversations()
        if conversation_id in conversations:
            del conversations[conversation_id]
            save_conversations(conversations)
            return jsonify({
                "success": True,
                "message": "Conversation deleted"
            }), 200
        else:
            return jsonify({
                "error": "Conversation not found"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/conversation/<conversation_id>/clear', methods=['POST'])
def clear_conversation(conversation_id):
    """Clear messages in a conversation"""
    try:
        conversations = load_conversations()
        if conversation_id in conversations:
            conversations[conversation_id]["messages"] = []
            save_conversations(conversations)
            return jsonify({
                "success": True,
                "message": "Conversation cleared"
            }), 200
        else:
            return jsonify({
                "error": "Conversation not found"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
