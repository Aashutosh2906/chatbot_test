# Deployment Guide - Web-Based GLM Chatbot

This guide will help you deploy the chatbot as a web application with a frontend UI and Flask backend API.

## Architecture

- **Backend**: Flask REST API (Python)
- **Frontend**: HTML/CSS/JavaScript single-page application
- **API Server**: RESTful endpoints for chat operations
- **Chat Engine**: GLM API integration via Zhipu AI

## Prerequisites

- Python 3.7+
- GLM API key from [Zhipu AI](https://open.bigmodel.cn/)
- pip (Python package manager)

## Local Development Setup

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

### 5. Run Locally

Start the Flask server:

```bash
python app.py
```

The server will start at `http://localhost:5000`

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

1. **Create Procfile**
```bash
echo "web: gunicorn app:app" > Procfile
```

2. **Create .slugignore** (optional, to reduce slug size)
```bash
echo "index.html" > .slugignore
```

3. **Initialize git repo (if not already done)**
```bash
git init
git add .
git commit -m "Initial commit"
```

4. **Login to Heroku and create app**
```bash
heroku login
heroku create your-app-name
```

5. **Set environment variables**
```bash
heroku config:set GLM_API_KEY=your_actual_api_key_here
```

6. **Deploy**
```bash
git push heroku main
# or
git push heroku master
```

7. **Access your app**
```
https://your-app-name.herokuapp.com
```

---

### Option 2: Railway (Fast & Modern)

#### Prerequisites
- Railway account
- Railway CLI (optional)

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
   - Add: `FLASK_ENV=production`

4. **Deploy**
   - Railway auto-deploys on push
   - Your app will be live at the assigned domain

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
   - `FLASK_ENV=production`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

---

### Option 4: AWS EC2 (Production-Grade)

#### Prerequisites
- AWS account
- EC2 instance (Ubuntu 20.04+)
- SSH key pair
- Domain name (optional)

#### Steps

1. **SSH into your instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

2. **Install dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. **Clone and setup app**
```bash
git clone https://github.com/Aashutosh2906/chatbot_test.git
cd chatbot_test
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Create .env file**
```bash
echo "GLM_API_KEY=your_actual_api_key_here" > .env
```

5. **Setup Nginx reverse proxy**

Create `/etc/nginx/sites-available/chatbot`:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6. **Enable site and test Nginx**
```bash
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Use systemd to run Flask app as service**

Create `/etc/systemd/system/chatbot.service`:
```ini
[Unit]
Description=GLM Chatbot Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/chatbot_test
Environment="PATH=/home/ubuntu/chatbot_test/venv/bin"
ExecStart=/home/ubuntu/chatbot_test/venv/bin/gunicorn -w 4 app:app

[Install]
WantedBy=multi-user.target
```

8. **Start the service**
```bash
sudo systemctl daemon-reload
sudo systemctl start chatbot
sudo systemctl enable chatbot
```

9. **Setup SSL with Let's Encrypt (Free)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

---

### Option 5: Docker (Containerized Deployment)

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'
services:
  chatbot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GLM_API_KEY=${GLM_API_KEY}
      - FLASK_ENV=production
    restart: unless-stopped
```

3. **Build and run**
```bash
docker-compose up -d
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

**Response:**
```json
{
  "success": true,
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ]
}
```

### `POST /api/clear`
Clear conversation history.

### `POST /api/reset`
Reset chatbot instance.

---

## Troubleshooting

### CORS Errors
- Ensure Flask-CORS is installed: `pip install flask-cors`
- The app already has CORS enabled for all origins

### API Key Not Found
- Verify `.env` file exists in the same directory as `app.py`
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

### Static Files Not Loading
- Ensure `index.html` is in the same directory as `app.py`
- Clear browser cache (Ctrl+Shift+Delete)

### API Connection Errors in Frontend
- Check that backend server is running
- Verify API_URL in `index.html` matches your server URL
- Check browser console (F12) for detailed errors

---

## Production Best Practices

1. **Security**
   - Use HTTPS (SSL/TLS)
   - Store API keys in environment variables (never in code)
   - Use strong passwords and key rotation
   - Enable firewall rules

2. **Performance**
   - Use CDN for static assets
   - Enable gzip compression
   - Set up caching headers
   - Monitor API response times

3. **Monitoring**
   - Set up error tracking (e.g., Sentry)
   - Monitor API quotas
   - Log important events
   - Set up uptime monitoring

4. **Scaling**
   - Use load balancers for multiple instances
   - Consider database for persistent history
   - Implement rate limiting
   - Cache responses when possible

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs: `heroku logs --tail` (for Heroku)
3. Open an issue on GitHub
4. Check GLM API documentation at [Zhipu AI](https://open.bigmodel.cn/)

---

Happy chatting! 🚀
