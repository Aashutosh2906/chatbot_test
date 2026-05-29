import os
import json
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

class GLMChatbot:
    """
    A simple chatbot that uses the GLM API for conversation.
    Supports multi-turn conversation with context history.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chatbot with API key.
        
        Args:
            api_key: GLM API key. If not provided, reads from .env file
        """
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GLM_API_KEY not found. Please set it in .env file or pass it as argument."
            )
        
        # GLM API endpoint
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
    
    def send_message(self, user_message: str) -> str:
        """
        Send a message to the chatbot and get a response.
        
        Args:
            user_message: The user's message
            
        Returns:
            The chatbot's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "glm-4",
                "messages": self.conversation_history,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Send request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API Error: {str(e)}"
            print(error_msg)
            return error_msg
        except (KeyError, json.JSONDecodeError) as e:
            error_msg = f"Response parsing error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        print("Conversation history cleared.")
    
    def show_history(self):
        """Display conversation history."""
        if not self.conversation_history:
            print("No conversation history.")
            return
        
        print("\n" + "="*50)
        print("CONVERSATION HISTORY")
        print("="*50)
        for msg in self.conversation_history:
            role = msg["role"].upper()
            content = msg["content"]
            print(f"\n[{role}]:\n{content}")
        print("\n" + "="*50 + "\n")


def main():
    """Main function to run the chatbot in interactive mode."""
    print("="*50)
    print("GLM Chatbot")
    print("="*50)
    print("Commands:")
    print("  'quit' - Exit the chatbot")
    print("  'clear' - Clear conversation history")
    print("  'history' - Show conversation history")
    print("="*50 + "\n")
    
    try:
        chatbot = GLMChatbot()
        print("Chatbot initialized. Type your message (or 'quit' to exit):\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                break
            
            if user_input.lower() == "clear":
                chatbot.reset_conversation()
                continue
            
            if user_input.lower() == "history":
                chatbot.show_history()
                continue
            
            print("\nChatbot: ", end="", flush=True)
            response = chatbot.send_message(user_input)
            print(response + "\n")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set up your GLM_API_KEY in the .env file.")


if __name__ == "__main__":
    main()
