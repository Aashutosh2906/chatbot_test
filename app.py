from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from chatbot import GLMChatbot
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Global chatbot instance
chatbot_instance = None
CONVERSATIONS_FILE = 'conversations.json'

def load_conversations():
    """Load all conversations from JSON file"""
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            return {}
    return {}

def save_conversations(conversations):
    """Save conversations to JSON file"""
    try:
        with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving conversations: {e}")

def get_chatbot():
    global chatbot_instance
    if chatbot_instance is None:
        try:
            logger.info("Initializing GLM Chatbot...")
            chatbot_instance = GLMChatbot()
            logger.info("Chatbot initialized successfully")
        except ValueError as e:
            logger.error(f"Error initializing chatbot: {e}")
            return None, str(e)
    return chatbot_instance, None

# Read the HTML file
def get_html_content():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error("index.html not found")
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
    logger.info("Serving home page")
    return render_template_string(get_html_content())

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Handle chat messages"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        logger.info("Received chat request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'message' not in data:
            logger.error("Message field missing")
            return jsonify({"error": "Message field is required"}), 400
        
        if not data.get('conversation_id'):
            logger.error("Conversation ID missing")
            return jsonify({"error": "Conversation ID is required"}), 400
        
        user_message = data['message'].strip()
        conversation_id = data['conversation_id']
        
        if not user_message:
            logger.error("Empty message")
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"Processing message from conversation {conversation_id}: {user_message[:50]}")
        
        chatbot, error = get_chatbot()
        if error:
            logger.error(f"Chatbot error: {error}")
            return jsonify({"error": error}), 500
        
        logger.info("Sending message to GLM API...")
        response = chatbot.send_message(user_message)
        logger.info(f"Got response: {response[:100]}")
        
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
        logger.info("Conversation saved")
        
        return jsonify({
            "success": True,
            "message": user_message,
            "response": response
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/conversations', methods=['GET', 'OPTIONS'])
def get_conversations():
    """Get all conversations"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        logger.info("Fetching conversations")
        conversations = load_conversations()
        # Return sorted by created_at (newest first)
        sorted_convs = sorted(
            conversations.values(),
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )
        logger.info(f"Returning {len(sorted_convs)} conversations")
        return jsonify({
            "success": True,
            "conversations": sorted_convs
        }), 200
    except Exception as e:
        logger.error(f"Exception in get_conversations: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/conversation/<conversation_id>', methods=['GET', 'DELETE', 'OPTIONS'])
def manage_conversation(conversation_id):
    """Get or delete a specific conversation"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        conversations = load_conversations()
        
        if request.method == 'GET':
            logger.info(f"Fetching conversation {conversation_id}")
            if conversation_id in conversations:
                return jsonify({
                    "success": True,
                    "conversation": conversations[conversation_id]
                }), 200
            else:
                logger.warning(f"Conversation {conversation_id} not found")
                return jsonify({
                    "error": "Conversation not found"
                }), 404
        
        elif request.method == 'DELETE':
            logger.info(f"Deleting conversation {conversation_id}")
            if conversation_id in conversations:
                del conversations[conversation_id]
                save_conversations(conversations)
                return jsonify({
                    "success": True,
                    "message": "Conversation deleted"
                }), 200
            else:
                logger.warning(f"Conversation {conversation_id} not found for deletion")
                return jsonify({
                    "error": "Conversation not found"
                }), 404
    except Exception as e:
        logger.error(f"Exception in manage_conversation: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/conversation/<conversation_id>/clear', methods=['POST', 'OPTIONS'])
def clear_conversation(conversation_id):
    """Clear messages in a conversation"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        logger.info(f"Clearing conversation {conversation_id}")
        conversations = load_conversations()
        if conversation_id in conversations:
            conversations[conversation_id]["messages"] = []
            save_conversations(conversations)
            return jsonify({
                "success": True,
                "message": "Conversation cleared"
            }), 200
        else:
            logger.warning(f"Conversation {conversation_id} not found for clearing")
            return jsonify({
                "error": "Conversation not found"
            }), 404
    except Exception as e:
        logger.error(f"Exception in clear_conversation: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({
        "status": "ok",
        "message": "GLM Chatbot API is running"
    }), 200

@app.errorhandler(404)
def not_found(error):
    logger.error(f"404 error: {error}")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=False, host='0.0.0.0', port=5000)
