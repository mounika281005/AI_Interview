# AI Mock Interview System - Deployment Guide

## Overview

This guide explains how to deploy the FastAPI-based AI Mock Interview System backend for both **local development** and **production** environments.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Virtual Environment Setup](#virtual-environment-setup)
3. [Dependency Installation](#dependency-installation)
4. [Running the FastAPI Server](#running-the-fastapi-server)
5. [Environment Variables](#environment-variables)
6. [Production Deployment](#production-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Cloud Deployment](#cloud-deployment)
9. [Troubleshooting](#troubleshooting)

---

## 1. Local Development Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

```bash
# 1. Clone or navigate to the project
cd f:\Interview\backend

# 2. Check Python version
python --version
# Should output: Python 3.9.x or higher
```

---

## 2. Virtual Environment Setup

A virtual environment isolates project dependencies from your system Python.

### Windows (PowerShell)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# You should see (venv) in your prompt
# (venv) PS F:\Interview\backend>
```

### Windows (Command Prompt)

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat
```

### Linux/macOS

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Deactivating Virtual Environment

```bash
# When done working
deactivate
```

---

## 3. Dependency Installation

### Install All Dependencies

```bash
# Make sure virtual environment is activated
# (venv) should appear in your prompt

# Install dependencies
pip install -r requirements.txt
```

### Install Dependencies Individually (if requirements.txt fails)

```bash
# Core Framework
pip install fastapi==0.109.0
pip install uvicorn[standard]==0.27.0

# Database
pip install sqlalchemy==2.0.25
pip install aiosqlite==0.19.0

# For PostgreSQL (production)
# pip install asyncpg==0.29.0

# Authentication
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4

# Validation
pip install pydantic==2.5.3
pip install pydantic-settings==2.1.0

# NLP (optional - for evaluation)
pip install nltk==3.8.1
pip install sentence-transformers==2.2.2

# Speech-to-Text (optional)
pip install openai-whisper==20231117
# OR for API only:
pip install openai==1.9.0
```

### Verify Installation

```bash
# Check installed packages
pip list

# Check FastAPI version
python -c "import fastapi; print(fastapi.__version__)"
```

---

## 4. Running the FastAPI Server

### Development Mode (with auto-reload)

```bash
# Navigate to backend directory
cd f:\Interview\backend

# Activate virtual environment
.\venv\Scripts\Activate

# Run with uvicorn (recommended for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# OR run using Python
python -m app.main
```

### What You Should See

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     🚀 Starting AI Mock Interview System...
INFO:     📦 Initializing database...
INFO:     ✅ Database initialized successfully
INFO:     ✅ Application started successfully!
INFO:     Application startup complete.
```

### Accessing the Application

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Root endpoint |
| http://localhost:8000/docs | Swagger UI (API documentation) |
| http://localhost:8000/redoc | ReDoc (alternative docs) |
| http://localhost:8000/health | Health check endpoint |

---

## 5. Environment Variables

### Create Environment File

```bash
# Copy the example file
copy .env.example .env

# Edit the .env file with your settings
notepad .env
```

### Essential Environment Variables

```env
# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_NAME="AI Mock Interview System"
APP_VERSION="1.0.0"
APP_ENV=development

# =============================================================================
# SERVER SETTINGS
# =============================================================================
HOST=0.0.0.0
PORT=8000

# =============================================================================
# DATABASE (SQLite for development)
# =============================================================================
DATABASE_URL=sqlite+aiosqlite:///./interview.db

# For PostgreSQL (production):
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/interview_db

# =============================================================================
# SECURITY
# =============================================================================
# Generate a secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# =============================================================================
# AI CONFIGURATION (Optional)
# =============================================================================
# OpenAI API Key for question generation
OPENAI_API_KEY=sk-your-openai-api-key

# AI Provider: openai or google
AI_PROVIDER=openai

# =============================================================================
# SPEECH-TO-TEXT (Optional)
# =============================================================================
WHISPER_USE_API=true
WHISPER_MODEL=base

# =============================================================================
# FILE STORAGE
# =============================================================================
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800

# =============================================================================
# CORS SETTINGS
# =============================================================================
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Generate Secret Key

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 6. Production Deployment

### Production Checklist

- [ ] Change `APP_ENV` to `production`
- [ ] Set a strong `SECRET_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS
- [ ] Configure logging
- [ ] Set up monitoring

### Running in Production Mode

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn + Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/interview.conf`:

```ini
[program:interview-api]
command=/path/to/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/path/to/Interview/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/interview-api.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start interview-api
```

---

## 7. Docker Deployment

### Dockerfile

Create `Dockerfile` in the backend directory:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/interview_db
      - SECRET_KEY=${SECRET_KEY}
      - APP_ENV=production
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=interview_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Running with Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

---

## 8. Cloud Deployment

### AWS (Elastic Beanstalk)

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p python-3.11 interview-api

# Create environment
eb create interview-api-env

# Deploy
eb deploy
```

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create ai-interview-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set APP_ENV=production

# Deploy
git push heroku main
```

### Railway / Render

1. Connect your GitHub repository
2. Set the build command: `pip install -r requirements.txt`
3. Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in the dashboard

---

## 9. Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual PID)
taskkill /PID <PID> /F
```

#### Module Not Found Error

```bash
# Make sure virtual environment is activated
.\venv\Scripts\Activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Database Connection Error

```bash
# For SQLite, check file permissions
# For PostgreSQL, verify connection string and credentials

# Test database connection
python -c "from app.database import engine; print('Connected!')"
```

#### CORS Errors

Update `.env`:
```env
CORS_ORIGINS=["http://localhost:3000","http://your-frontend-domain.com"]
```

#### Whisper Model Download

```bash
# Download Whisper model manually
python -c "import whisper; whisper.load_model('base')"
```

### Checking Logs

```bash
# View application logs (development)
# Logs appear in terminal

# View logs in production (if using supervisor)
tail -f /var/log/interview-api.log

# Docker logs
docker-compose logs -f api
```

### Health Check

```bash
# Check if API is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0","environment":"development"}
```

---

## Quick Start Summary

```bash
# 1. Navigate to project
cd f:\Interview\backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
copy .env.example .env
# Edit .env with your settings

# 6. Run server
uvicorn app.main:app --reload

# 7. Open browser
# http://localhost:8000/docs
```

---

*For academic demonstration, the local development setup is sufficient. Production deployment is optional but recommended for showcasing the complete system.*

---

*Last Updated: January 2024*
