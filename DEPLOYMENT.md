# Deployment Guide - Web-Based GLM Chatbot

This guide will help you deploy the chatbot as a web application with a frontend UI and Flask backend API.

## Quick Start (Local Development)

### 1. Clone and Setup

```bash
git clone https://github.com/Aashutosh2906/chatbot_test.git
cd chatbot_test
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your GLM API key:
```
GLM_API_KEY=your_actual_api_key_here
```

### 5. Run Flask Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

### 6. Open the Frontend

Open `index.html` in your browser or serve it with:

```bash
# Using Python's built-in server (in a new terminal)
python -m http.server 8000
```

Then visit `http://localhost:8000`

---

## Deployment Options

### Option 1: Heroku (Easy, Free Tier Available)

#### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed

#### Steps

1. **Initialize git repo (if not already done)**
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Login to Heroku and create app**
```bash
heroku login
heroku create your-app-name
```

3. **Set environment variables**
```bash
heroku config:set GLM_API_KEY=your_actual_api_key_here
```

4. **Deploy**
```bash
git push heroku main
# or
git push heroku master
```

5. **Access your app**
```
https://your-app-name.herokuapp.com
```

---

### Option 2: Railway (Fast & Modern)

#### Prerequisites
- Railway account
- GitHub repository

#### Steps

1. **Push to GitHub**
```bash
git push origin main
```

2. **Connect to Railway**
   - Visit [railway.app](https://railway.app)
   - Click "New Project"
   - Connect your GitHub repository
   - Select the chatbot_test repo

3. **Add Environment Variables**
   - In Railway dashboard, go to Variables
   - Add: `GLM_API_KEY=your_actual_api_key_here`

4. **Deploy**
   - Railway auto-deploys on push

---

### Option 3: Render (Free Tier with Web Services)

#### Prerequisites
- Render account
- GitHub repository

#### Steps

1. **Create Render Service**
   - Visit [render.com](https://render.com)
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repo

2. **Configure Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3.9

3. **Add Environment Variables**
   - `GLM_API_KEY=your_actual_api_key_here`

4. **Deploy**
   - Click "Create Web Service"

---

### Option 4: Docker (Local or Cloud)

#### Build and Run Locally

1. **Build Docker image**
```bash
docker build -t glm-chatbot .
```

2. **Run container**
```bash
docker run -p 5000:5000 -e GLM_API_KEY=your_api_key glm-chatbot
```

#### Using Docker Compose

1. **Create .env file**
```bash
echo "GLM_API_KEY=your_actual_api_key_here" > .env
```

2. **Start services**
```bash
docker-compose up -d
```

3. **Access the app**
```
http://localhost:5000
```

---

## API Endpoints

### `POST /api/chat`
Send a message and get a response.

**Request:**
```json
{
  "message": "Hello, how are you?"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Hello, how are you?",
  "response": "I'm doing well, thank you for asking!"
}
```

### `GET /api/history`
Get conversation history.

### `POST /api/clear`
Clear conversation history.

### `POST /api/reset`
Reset chatbot instance.

---

## Troubleshooting

### CORS Errors
- Ensure Flask-CORS is installed in requirements.txt
- The app already has CORS enabled

### API Key Not Found
- Verify `.env` file exists
- Check that `GLM_API_KEY` is correctly set
- Restart the server after changing `.env`

### Port Already in Use
```bash
# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux
lsof -i :5000
kill -9 <PID>
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Check GLM API documentation at [Zhipu AI](https://open.bigmodel.cn/)

Happy chatting! 🚀
