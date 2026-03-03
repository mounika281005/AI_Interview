# AI Mock Interview System

A comprehensive AI-powered mock interview platform that helps candidates practice and improve their interview skills through voice-based interviews with NLP-powered evaluation and feedback.

## 🎯 Key Features

### Skill-Based Interview Flow
1. **Skill Dropdown** - Select from 40+ technologies (Python, JavaScript, React, AWS, etc.)
2. **Question Generation** - AI generates 5 interview questions based on selected technology
3. **Voice Answer Recording** - Record voice answers for all 5 questions using microphone
4. **Submit Interview** - Submit all recordings for evaluation
5. **Speech-to-Text** - Convert recorded audio to text using Whisper
6. **NLP-Based Scoring** - Score each answer (0-5) based on:
   - Grammar
   - Fluency
   - Answer Structure
   - Similarity with Ideal Answer
7. **Feedback & Improvements** - For each question:
   - Strengths
   - Areas for Improvement
   - Ideal/Expected Answer
8. **Final Results** - Question-wise scores + Total score + Grade
9. **Store Results** - Save all data in database for history

## 🚀 Quick Start

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

### Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
Interview/
├── frontend/                    # React web application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── SkillInterviewPage.jsx    # Main interview flow
│   │   │   └── SkillInterviewResultsPage.jsx
│   │   ├── api/
│   │   │   └── skillInterviewApi.js      # API client
│   │   └── styles/
│   │       └── SkillInterview.css        # Styles
├── backend/                     # FastAPI server
│   ├── app/
│   │   ├── main.py              # App entry point
│   │   ├── routers/
│   │   │   └── skill_interview.py        # Interview endpoints
│   │   ├── schemas/
│   │   │   └── skill_interview.py        # Request/Response schemas
│   │   ├── services/
│   │   │   ├── stt_service.py            # Speech-to-Text
│   │   │   ├── evaluation_service.py     # NLP Evaluation
│   │   │   └── question_service.py       # Question Generation
│   │   └── models/              # Database models
├── ai-modules/                  # AI/ML components
│   ├── speech-to-text/         # Whisper transcription
│   ├── nlp-evaluation/         # Answer analysis
│   ├── question-generation/    # Dynamic questions
│   └── scoring-feedback/       # Performance scoring
├── database/                    # Database config
├── shared/                      # Shared utilities
├── tests/                       # Test suites
├── docker/                      # Container configs
└── docs/                        # Documentation
```

## 🔌 API Endpoints

### Skill Interview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/skill-interview/technologies` | Get available technologies |
| POST | `/api/v1/skill-interview/start` | Start interview & generate questions |
| POST | `/api/v1/skill-interview/{session_id}/upload-audio/{question_id}` | Upload voice recording |
| POST | `/api/v1/skill-interview/{session_id}/submit` | Submit for evaluation |
| GET | `/api/v1/skill-interview/{session_id}/results` | Get interview results |
| GET | `/api/v1/skill-interview/history` | Get interview history |

## 🛠️ Tech Stack

- **Frontend**: React, React Router, CSS3
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic
- **AI/ML**: OpenAI Whisper (STT), Sentence Transformers, NLTK
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Infrastructure**: Docker, Uvicorn

## 📊 Scoring System

Each question is scored on 4 criteria (0-5 scale each):

| Criteria | Description |
|----------|-------------|
| **Grammar** | Grammatical correctness of the answer |
| **Fluency** | Natural language flow and coherence |
| **Structure** | Logical organization of the response |
| **Similarity** | Relevance to ideal answer / keywords |

**Total Score**: Sum of all question scores  
**Grade**: A+ (90%+), A (80%+), B+ (70%+), B (60%+), C (50%+), D (40%+), F (<40%)

## 🔐 Environment Variables

Create a `.env` file in the backend folder:

```env
# App
SECRET_KEY=your-secret-key-min-32-chars
ENVIRONMENT=development

# AI
OPENAI_API_KEY=sk-your-openai-key  # For Whisper API & GPT
GOOGLE_API_KEY=your-google-key     # Optional: For Gemini

# Database
DATABASE_URL=sqlite+aiosqlite:///./interview_system.db
```

## 👥 Authors

Final Year Project - AI Mock Interview System
