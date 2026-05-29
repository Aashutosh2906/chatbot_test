# GLM Chatbot

A simple Python chatbot that uses the GLM API for intelligent conversations.

## Features

- 🤖 Multi-turn conversation with context history
- 🔐 Secure API key management using environment variables
- 💬 Interactive CLI interface
- 📝 Conversation history tracking
- 🔄 Reset conversation anytime

## Prerequisites

- Python 3.7+
- GLM API key (from [Zhipu AI](https://open.bigmodel.cn/))

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aashutosh2906/chatbot_test.git
   cd chatbot_test
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your GLM API key:
   ```
   GLM_API_KEY=your_actual_api_key_here
   ```

## Usage

### Interactive Mode

Run the chatbot in interactive mode:

```bash
python chatbot.py
```

Then simply type your messages:
```
You: Hello, how are you?
Chatbot: I'm doing well, thank you for asking! How can I help you today?

You: Tell me about Python
Chatbot: Python is a versatile programming language known for...
```

### Special Commands

- `quit` - Exit the chatbot
- `clear` - Clear conversation history
- `history` - View the entire conversation history

### Programmatic Usage

You can also use the chatbot in your own Python code:

```python
from chatbot import GLMChatbot

# Initialize chatbot
chatbot = GLMChatbot()

# Send a message
response = chatbot.send_message("Hello, what's the weather like?")
print(response)

# View conversation history
chatbot.show_history()

# Reset for new conversation
chatbot.reset_conversation()
```

## How It Works

1. The chatbot sends your message to the GLM API along with the conversation history
2. The API processes your message and generates a response based on the context
3. The response is displayed and added to the conversation history
4. Subsequent messages maintain the context of the conversation

## File Structure

```
chatbot_test/
├── chatbot.py          # Main chatbot implementation
├── requirements.txt    # Python dependencies
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Getting a GLM API Key

1. Visit [Zhipu AI](https://open.bigmodel.cn/)
2. Sign up or log in to your account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

## Troubleshooting

### "GLM_API_KEY not found" Error
- Make sure you've created the `.env` file
- Verify the API key is correctly set in the `.env` file
- Check that the `.env` file is in the same directory as `chatbot.py`

### API Connection Errors
- Verify your API key is valid
- Check your internet connection
- Ensure the GLM API service is accessible

### Response Parsing Errors
- The API response format might have changed
- Try updating the API endpoint or check GLM's documentation

## Contributing

Feel free to fork this repository and submit pull requests for any improvements!

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please open an issue on GitHub.

---

Made with ❤️ by [Aashutosh2906](https://github.com/Aashutosh2906)
