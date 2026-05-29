import os
import json
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional
import time

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
        
        # Timeout settings (increased from 30s to 120s to handle slow API)
        self.timeout = 120
        self.max_retries = 2
    
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
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                # Prepare request
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "glm-4.7-flash",
                    "messages": self.conversation_history,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
                
                print(f"[DEBUG] Sending request to GLM API (attempt {attempt + 1})...")
                
                # Send request with increased timeout
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                print(f"[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response text: {response.text[:500]}")
                
                response.raise_for_status()
                
                # Check if response has content
                if not response.text or response.text.strip() == '':
                    error_msg = f"API returned empty response (attempt {attempt + 1}/{self.max_retries})"
                    print(error_msg)
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        self.conversation_history.pop()
                        return "Sorry, the API returned an empty response. Please try again."
                
                # Parse response
                try:
                    data = response.json()
                    print(f"[DEBUG] Parsed JSON: {json.dumps(data)[:500]}")
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse JSON response: {str(e)} (attempt {attempt + 1}/{self.max_retries})"
                    print(error_msg)
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        self.conversation_history.pop()
                        return "Sorry, I couldn't parse the API response. Please try again."
                
                # Extract message from response
                if "choices" not in data or len(data["choices"]) == 0:
                    error_msg = f"Invalid response format - no choices (attempt {attempt + 1}/{self.max_retries})"
                    print(error_msg)
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        self.conversation_history.pop()
                        return f"API Error: Invalid response format. Response: {json.dumps(data)[:200]}"
                
                assistant_message = data["choices"][0].get("message", {}).get("content", "")
                
                if not assistant_message:
                    error_msg = f"Empty message in response (attempt {attempt + 1}/{self.max_retries})"
                    print(error_msg)
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        self.conversation_history.pop()
                        return "The API returned an empty message. Please try again."
                
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                print("[DEBUG] Successfully got response!")
                return assistant_message
                
            except requests.exceptions.Timeout:
                error_msg = f"API request timed out (attempt {attempt + 1}/{self.max_retries}). The server is taking longer than expected."
                print(error_msg)
                
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    self.conversation_history.pop()
                    return error_msg
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: Could not reach the API server. {str(e)}"
                print(error_msg)
                self.conversation_history.pop()
                return error_msg
                
            except requests.exceptions.HTTPError as e:
                try:
                    error_detail = response.json()
                    error_msg = f"API Error {response.status_code}: {json.dumps(error_detail)}"
                except:
                    error_msg = f"API Error: {response.status_code} - {str(e)}"
                
                print(error_msg)
                self.conversation_history.pop()
                return error_msg
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                print(error_msg)
                self.conversation_history.pop()
                return error_msg
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                print(error_msg)
                self.conversation_history.pop()
                return error_msg
        
        error_msg = "Failed to get response after multiple attempts. Please try again later."
        self.conversation_history.pop()
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
