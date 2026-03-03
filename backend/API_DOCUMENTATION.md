# AI Mock Interview System - API Documentation

## 🚀 Complete API Flow

This document explains the complete flow of the AI Mock Interview System from user registration to performance analytics.

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [API Flow Overview](#api-flow-overview)
3. [Detailed API Endpoints](#detailed-api-endpoints)
4. [Complete Interview Flow](#complete-interview-flow)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Handling](#error-handling)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI MOCK INTERVIEW SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Frontend  │───▶│   FastAPI   │───▶│  Services   │───▶│  Database   │  │
│  │   Client    │    │   Backend   │    │   Layer     │    │  (SQLite/   │  │
│  │             │◀───│             │◀───│             │◀───│  PostgreSQL)│  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                            │                  │                             │
│                            ▼                  ▼                             │
│                     ┌─────────────┐    ┌─────────────┐                     │
│                     │   OpenAI/   │    │   Whisper   │                     │
│                     │   Google    │    │   STT       │                     │
│                     │   (AI Gen)  │    │   Engine    │                     │
│                     └─────────────┘    └─────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 API Flow Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE INTERVIEW FLOW                               │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐        ┌─────────┐        ┌─────────┐        ┌─────────┐
    │  USER   │        │QUESTION │        │  AUDIO  │        │   STT   │
    │REGISTER │───────▶│ GENERA- │───────▶│ UPLOAD  │───────▶│TRANSCRI-│
    │ /LOGIN  │        │  TION   │        │         │        │  PTION  │
    └─────────┘        └─────────┘        └─────────┘        └─────────┘
                                                                   │
    ┌─────────┐        ┌─────────┐        ┌─────────┐              │
    │DASHBOARD│◀───────│FEEDBACK │◀───────│SCORING  │◀─────────────┘
    │  STATS  │        │GENERATE │        │ & EVAL  │
    └─────────┘        └─────────┘        └─────────┘
```

---

## 📡 Detailed API Endpoints

### 1. User Management (`/api/v1/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Authenticate and get token |
| GET | `/me` | Get current user profile |
| PUT | `/me` | Update user profile |
| GET | `/{id}` | Get user by ID |
| DELETE | `/{id}` | Delete user account |
| PUT | `/{id}/skills` | Update user skills |

### 2. Interview Sessions (`/api/v1/interviews`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions` | Create new interview session |
| GET | `/sessions` | List user's sessions |
| GET | `/sessions/{id}` | Get session details |
| PUT | `/sessions/{id}` | Update session |
| DELETE | `/sessions/{id}` | Delete session |
| POST | `/sessions/{id}/complete` | Mark session complete |

### 3. Question Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions/{id}/questions/generate` | Generate AI questions |
| GET | `/sessions/{id}/questions` | List session questions |
| GET | `/sessions/{id}/questions/{q_id}` | Get question details |

### 4. Audio & Transcription

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions/{s_id}/questions/{q_id}/audio` | Upload audio response |
| GET | `/sessions/{s_id}/questions/{q_id}/audio` | Get audio file |
| POST | `/sessions/{s_id}/questions/{q_id}/transcribe` | Convert to text |
| GET | `/sessions/{s_id}/questions/{q_id}/transcript` | Get transcript |

### 5. Evaluation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions/{s_id}/questions/{q_id}/evaluate` | Evaluate response |
| GET | `/sessions/{s_id}/evaluation` | Get session evaluation |

### 6. Feedback & Analytics (`/api/v1/feedback`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions/{id}/scores` | Calculate final scores |
| GET | `/sessions/{id}/scores` | Get session scores |
| POST | `/sessions/{id}/feedback` | Generate feedback |
| GET | `/sessions/{id}/feedback` | Get session feedback |
| GET | `/history` | Get interview history |
| GET | `/dashboard` | Get dashboard stats |
| GET | `/charts/{type}` | Get chart data |

---

## 🎯 Complete Interview Flow

### Step 1: User Registration & Login

```
POST /api/v1/users/register
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
}

Response:
{
    "success": true,
    "data": {
        "id": "uuid-xxx",
        "email": "user@example.com",
        "full_name": "John Doe",
        "token": "eyJ..."
    }
}
```

### Step 2: Create Interview Session

```
POST /api/v1/interviews/sessions
Authorization: Bearer <token>
{
    "title": "Software Engineer Interview",
    "target_role": "Senior Software Engineer",
    "target_company": "Tech Corp",
    "difficulty": "medium"
}

Response:
{
    "success": true,
    "data": {
        "id": "session-uuid",
        "status": "created",
        "title": "Software Engineer Interview"
    }
}
```

### Step 3: Generate Questions

```
POST /api/v1/interviews/sessions/{session_id}/questions/generate
Authorization: Bearer <token>
{
    "num_questions": 5,
    "categories": ["behavioral", "technical", "situational"],
    "skills": ["Python", "FastAPI", "PostgreSQL"]
}

Response:
{
    "success": true,
    "data": {
        "questions": [
            {
                "id": "q-uuid-1",
                "question_text": "Tell me about a challenging project...",
                "category": "behavioral",
                "difficulty": "medium",
                "time_limit": 120
            },
            ...
        ]
    }
}
```

### Step 4: Upload Audio Response

```
POST /api/v1/interviews/sessions/{session_id}/questions/{question_id}/audio
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <audio_file.mp3>
duration: 95

Response:
{
    "success": true,
    "data": {
        "audio_id": "audio-uuid",
        "file_path": "/uploads/sessions/xxx/q-1.mp3",
        "duration": 95,
        "format": "mp3",
        "size_bytes": 1234567
    }
}
```

### Step 5: Transcribe Audio (Speech-to-Text)

```
POST /api/v1/interviews/sessions/{session_id}/questions/{question_id}/transcribe
Authorization: Bearer <token>
{
    "language": "en"
}

Response:
{
    "success": true,
    "data": {
        "transcript": "In my previous role at XYZ Company, I faced a challenging project where we needed to migrate our monolithic application to microservices. The main challenges were...",
        "language": "en",
        "duration": 95.5,
        "confidence": 0.94,
        "word_count": 156
    }
}
```

### Step 6: Evaluate Response (NLP Analysis)

```
POST /api/v1/interviews/sessions/{session_id}/questions/{question_id}/evaluate
Authorization: Bearer <token>
{
    "expected_keywords": ["challenge", "solution", "teamwork", "outcome", "learning"]
}

Response:
{
    "success": true,
    "data": {
        "relevance_score": 85.5,
        "grammar_score": 78.2,
        "fluency_score": 82.0,
        "keyword_score": 90.0,
        "overall_score": 83.8,
        "summary": "Good response with clear structure...",
        "suggestions": [
            "Consider adding more specific metrics",
            "Include the outcome more explicitly"
        ]
    }
}
```

### Step 7: Calculate Final Scores

```
POST /api/v1/feedback/sessions/{session_id}/scores
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "total_score": 78.5,
        "letter_grade": "B+",
        "breakdown": {
            "relevance": {"raw": 82, "weighted": 28.7},
            "grammar": {"raw": 75, "weighted": 15.0},
            "fluency": {"raw": 80, "weighted": 20.0},
            "keywords": {"raw": 77, "weighted": 15.4}
        },
        "question_scores": [...],
        "performance_summary": "Good performance with strong relevance..."
    }
}
```

### Step 8: Generate Comprehensive Feedback

```
POST /api/v1/feedback/sessions/{session_id}/feedback
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "overall_rating": "Good",
        "summary": "Your interview performance was rated as Good with an overall score of 78.5/100...",
        "strengths": [
            {
                "category": "Relevance",
                "message": "Strong connection between responses and question requirements"
            },
            {
                "category": "Keywords",
                "message": "Effective demonstration of technical knowledge"
            }
        ],
        "weaknesses": [
            {
                "category": "Grammar",
                "message": "Some grammatical errors affected clarity"
            }
        ],
        "suggestions": [
            {
                "category": "Grammar",
                "message": "Pay attention to sentence structure and tense consistency"
            },
            {
                "category": "Practice",
                "message": "Practice mock interviews regularly to build confidence"
            }
        ],
        "resources": [
            {
                "title": "Business English Communication",
                "type": "course",
                "url": "https://..."
            }
        ],
        "readiness_score": 72,
        "readiness_level": "Almost Ready",
        "next_steps": [
            "Complete 2-3 more mock interview sessions",
            "Focus on grammar improvement",
            "Start scheduling real interviews"
        ]
    }
}
```

### Step 9: Dashboard & Analytics

```
GET /api/v1/feedback/dashboard
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "total_interviews": 12,
        "total_questions": 48,
        "average_score": 76.3,
        "best_score": 89.2,
        "recent_score": 78.5,
        "total_practice_time": 240,
        "improvement_rate": 8.5,
        "current_streak": 3,
        "longest_streak": 7,
        "skills_breakdown": {
            "relevance": 80.2,
            "grammar": 72.5,
            "fluency": 78.0,
            "keywords": 74.8
        },
        "category_scores": {
            "behavioral": 82.0,
            "technical": 74.5,
            "situational": 77.8
        }
    }
}
```

---

## 📊 Request/Response Examples

### Standard API Response Format

All API responses follow this structure:

```json
{
    "success": true,
    "data": { ... },
    "error": null,
    "meta": {
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-uuid"
    }
}
```

### Error Response Format

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": 400,
        "message": "Validation error",
        "details": [
            {
                "field": "email",
                "message": "Invalid email format"
            }
        ]
    }
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Common Error Scenarios

1. **Invalid Token**: Returns 401 with "Token expired or invalid"
2. **Resource Not Found**: Returns 404 with specific resource info
3. **Validation Errors**: Returns 422 with field-level details
4. **Server Errors**: Returns 500 with generic message (details logged)

---

## 🔐 Authentication

All protected endpoints require a JWT bearer token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Token is obtained from `/api/v1/users/login` and valid for 30 minutes (configurable).

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── interview.py
│   │   ├── question.py
│   │   └── feedback.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── interview.py
│   │   ├── feedback.py
│   │   └── common.py
│   ├── routers/             # API routes
│   │   ├── users.py
│   │   ├── interviews.py
│   │   └── feedback.py
│   └── services/            # Business logic
│       ├── auth_service.py
│       ├── question_service.py
│       ├── stt_service.py
│       ├── evaluation_service.py
│       ├── scoring_service.py
│       ├── feedback_service.py
│       └── stats_service.py
├── requirements.txt
├── .env.example
└── API_DOCUMENTATION.md
```

---

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run the server**:
   ```bash
   python -m app.main
   # Or: uvicorn app.main:app --reload
   ```

4. **Access documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## 📝 Notes

- All timestamps are in UTC
- Audio files are stored in the `uploads/` directory
- Maximum audio file size: 50MB
- Supported audio formats: MP3, WAV, M4A, WebM
- Whisper STT supports multiple languages

---

*Last updated: January 2024*
