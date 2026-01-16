# AI Mock Interview System - Database Schema

## Overview

This document describes the complete database schema for the AI Mock Interview System.
The schema is designed for **FastAPI + SQLAlchemy** with support for both **SQLite** (development) and **PostgreSQL** (production).

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                                      │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐         ┌─────────────────────┐         ┌────────────────┐
    │   USERS     │────────▶│  INTERVIEW_SESSIONS │────────▶│INTERVIEW_QUES- │
    │             │  1:N    │                     │   1:N   │    TIONS       │
    └─────────────┘         └─────────────────────┘         └────────────────┘
                                      │
                                      │ 1:1
                                      ▼
                            ┌─────────────────────┐
                            │ INTERVIEW_FEEDBACK  │
                            └─────────────────────┘
```

---

## Tables/Collections

### 1. USERS Table

**Purpose**: Stores user account information, profile data, and interview preferences.

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `full_name` | VARCHAR(100) | NOT NULL | User's display name |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Email verification status |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation time |
| `updated_at` | TIMESTAMP | ON UPDATE NOW() | Last update time |
| `last_login` | TIMESTAMP | NULLABLE | Last login timestamp |
| `profile_picture` | VARCHAR(500) | NULLABLE | Avatar URL |
| `phone_number` | VARCHAR(20) | NULLABLE | Contact number |
| `target_role` | VARCHAR(100) | NULLABLE | Desired job role |
| `target_company` | VARCHAR(100) | NULLABLE | Target company |
| `experience_years` | INTEGER | DEFAULT 0 | Years of experience |
| `education_level` | VARCHAR(50) | NULLABLE | Highest education |
| `skills` | JSON/TEXT | NULLABLE | Array of skills |
| `total_interviews` | INTEGER | DEFAULT 0 | Interview count |
| `average_score` | FLOAT | DEFAULT 0.0 | Average performance |
| `best_score` | FLOAT | DEFAULT 0.0 | Highest score achieved |
| `preferred_language` | VARCHAR(10) | DEFAULT 'en' | UI language |
| `notification_email` | BOOLEAN | DEFAULT TRUE | Email notifications |
| `notification_push` | BOOLEAN | DEFAULT TRUE | Push notifications |

**Indexes**:
- `idx_users_email` on `email`
- `idx_users_created_at` on `created_at`

**SQL Definition**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    profile_picture VARCHAR(500),
    phone_number VARCHAR(20),
    target_role VARCHAR(100),
    target_company VARCHAR(100),
    experience_years INTEGER DEFAULT 0,
    education_level VARCHAR(50),
    skills JSON,
    total_interviews INTEGER DEFAULT 0,
    average_score FLOAT DEFAULT 0.0,
    best_score FLOAT DEFAULT 0.0,
    preferred_language VARCHAR(10) DEFAULT 'en',
    notification_email BOOLEAN DEFAULT TRUE,
    notification_push BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

---

### 2. INTERVIEW_SESSIONS Table

**Purpose**: Tracks interview practice sessions including configuration, status, and scores.

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique session identifier |
| `user_id` | UUID | FOREIGN KEY → users.id | Session owner |
| `title` | VARCHAR(200) | NOT NULL | Session title |
| `description` | TEXT | NULLABLE | Session description |
| `status` | ENUM | NOT NULL | created/in_progress/completed/cancelled |
| `target_role` | VARCHAR(100) | NULLABLE | Target job role |
| `target_company` | VARCHAR(100) | NULLABLE | Target company |
| `difficulty` | VARCHAR(20) | DEFAULT 'medium' | easy/medium/hard |
| `interview_type` | VARCHAR(50) | DEFAULT 'mixed' | behavioral/technical/mixed |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Session creation time |
| `started_at` | TIMESTAMP | NULLABLE | When user started |
| `completed_at` | TIMESTAMP | NULLABLE | When completed |
| `total_duration` | INTEGER | NULLABLE | Total time in seconds |
| `num_questions` | INTEGER | DEFAULT 5 | Number of questions |
| `questions_answered` | INTEGER | DEFAULT 0 | Completed questions |
| `overall_score` | FLOAT | NULLABLE | Final score (0-100) |
| `relevance_avg` | FLOAT | NULLABLE | Average relevance score |
| `grammar_avg` | FLOAT | NULLABLE | Average grammar score |
| `fluency_avg` | FLOAT | NULLABLE | Average fluency score |
| `keyword_avg` | FLOAT | NULLABLE | Average keyword score |
| `notes` | TEXT | NULLABLE | User/system notes |
| `metadata` | JSON | NULLABLE | Additional data |

**Indexes**:
- `idx_sessions_user_id` on `user_id`
- `idx_sessions_status` on `status`
- `idx_sessions_created_at` on `created_at`

**SQL Definition**:
```sql
CREATE TYPE interview_status AS ENUM ('created', 'in_progress', 'completed', 'cancelled');

CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status interview_status NOT NULL DEFAULT 'created',
    target_role VARCHAR(100),
    target_company VARCHAR(100),
    difficulty VARCHAR(20) DEFAULT 'medium',
    interview_type VARCHAR(50) DEFAULT 'mixed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_duration INTEGER,
    num_questions INTEGER DEFAULT 5,
    questions_answered INTEGER DEFAULT 0,
    overall_score FLOAT,
    relevance_avg FLOAT,
    grammar_avg FLOAT,
    fluency_avg FLOAT,
    keyword_avg FLOAT,
    notes TEXT,
    metadata JSON
);

CREATE INDEX idx_sessions_user_id ON interview_sessions(user_id);
CREATE INDEX idx_sessions_status ON interview_sessions(status);
CREATE INDEX idx_sessions_created_at ON interview_sessions(created_at);
```

---

### 3. INTERVIEW_QUESTIONS Table

**Purpose**: Stores individual questions, audio responses, transcripts, and NLP scores.

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique question identifier |
| `session_id` | UUID | FOREIGN KEY → interview_sessions.id | Parent session |
| `question_number` | INTEGER | NOT NULL | Order in session (1, 2, 3...) |
| `question_text` | TEXT | NOT NULL | The interview question |
| `category` | VARCHAR(50) | DEFAULT 'general' | behavioral/technical/situational |
| `difficulty` | VARCHAR(20) | DEFAULT 'medium' | easy/medium/hard |
| `expected_topics` | JSON | NULLABLE | Keywords to cover |
| `time_limit` | INTEGER | DEFAULT 120 | Allowed time in seconds |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Question creation time |
| `answered_at` | TIMESTAMP | NULLABLE | When answered |
| `audio_file_path` | VARCHAR(500) | NULLABLE | Path to audio file |
| `audio_duration` | INTEGER | NULLABLE | Audio length in seconds |
| `audio_format` | VARCHAR(20) | NULLABLE | mp3/wav/webm |
| `audio_size_bytes` | INTEGER | NULLABLE | File size |
| `transcript` | TEXT | NULLABLE | Speech-to-text result |
| `transcript_confidence` | FLOAT | NULLABLE | STT confidence (0-1) |
| `transcript_language` | VARCHAR(10) | DEFAULT 'en' | Detected language |
| `word_count` | INTEGER | NULLABLE | Words in response |
| `relevance_score` | FLOAT | NULLABLE | NLP: Relevance (0-100) |
| `grammar_score` | FLOAT | NULLABLE | NLP: Grammar (0-100) |
| `fluency_score` | FLOAT | NULLABLE | NLP: Fluency (0-100) |
| `keyword_score` | FLOAT | NULLABLE | NLP: Keywords (0-100) |
| `overall_score` | FLOAT | NULLABLE | Weighted average (0-100) |
| `evaluation_summary` | TEXT | NULLABLE | Brief feedback text |
| `suggestions` | JSON | NULLABLE | Improvement suggestions |
| `is_evaluated` | BOOLEAN | DEFAULT FALSE | Evaluation complete flag |
| `follow_up_questions` | JSON | NULLABLE | Suggested follow-ups |

**Indexes**:
- `idx_questions_session_id` on `session_id`
- `idx_questions_category` on `category`

**SQL Definition**:
```sql
CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    difficulty VARCHAR(20) DEFAULT 'medium',
    expected_topics JSON,
    time_limit INTEGER DEFAULT 120,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP,
    audio_file_path VARCHAR(500),
    audio_duration INTEGER,
    audio_format VARCHAR(20),
    audio_size_bytes INTEGER,
    transcript TEXT,
    transcript_confidence FLOAT,
    transcript_language VARCHAR(10) DEFAULT 'en',
    word_count INTEGER,
    relevance_score FLOAT,
    grammar_score FLOAT,
    fluency_score FLOAT,
    keyword_score FLOAT,
    overall_score FLOAT,
    evaluation_summary TEXT,
    suggestions JSON,
    is_evaluated BOOLEAN DEFAULT FALSE,
    follow_up_questions JSON,
    
    UNIQUE(session_id, question_number)
);

CREATE INDEX idx_questions_session_id ON interview_questions(session_id);
CREATE INDEX idx_questions_category ON interview_questions(category);
```

---

### 4. INTERVIEW_FEEDBACK Table

**Purpose**: Stores comprehensive feedback for completed interview sessions.

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique feedback identifier |
| `session_id` | UUID | FOREIGN KEY, UNIQUE | One feedback per session |
| `overall_rating` | VARCHAR(50) | NOT NULL | Excellent/Good/Fair/Poor |
| `summary` | TEXT | NOT NULL | Overall performance summary |
| `strengths` | JSON | NOT NULL | Array of strength items |
| `weaknesses` | JSON | NOT NULL | Array of weakness items |
| `suggestions` | JSON | NOT NULL | Improvement suggestions |
| `resources` | JSON | NULLABLE | Learning resource links |
| `readiness_score` | INTEGER | NULLABLE | Interview readiness (0-100) |
| `readiness_level` | VARCHAR(50) | NULLABLE | Ready/Almost Ready/Needs Practice |
| `next_steps` | JSON | NULLABLE | Recommended actions |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Feedback generation time |
| `updated_at` | TIMESTAMP | ON UPDATE NOW() | Last update time |
| `question_feedback` | JSON | NULLABLE | Per-question feedback |
| `ai_insights` | TEXT | NULLABLE | AI-generated insights |
| `comparison_percentile` | INTEGER | NULLABLE | Percentile vs other users |

**SQL Definition**:
```sql
CREATE TABLE interview_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID UNIQUE NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    overall_rating VARCHAR(50) NOT NULL,
    summary TEXT NOT NULL,
    strengths JSON NOT NULL,
    weaknesses JSON NOT NULL,
    suggestions JSON NOT NULL,
    resources JSON,
    readiness_score INTEGER,
    readiness_level VARCHAR(50),
    next_steps JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    question_feedback JSON,
    ai_insights TEXT,
    comparison_percentile INTEGER
);

CREATE INDEX idx_feedback_session_id ON interview_feedback(session_id);
```

---

## Relationships Summary

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Sessions | 1:N | One user has many interview sessions |
| Session → Questions | 1:N | One session has many questions |
| Session → Feedback | 1:1 | One session has one feedback record |

---

## JSON Field Schemas

### skills (users.skills)
```json
["Python", "JavaScript", "React", "SQL", "Machine Learning"]
```

### expected_topics (interview_questions.expected_topics)
```json
["teamwork", "problem-solving", "leadership", "communication"]
```

### strengths/weaknesses (interview_feedback)
```json
[
    {
        "category": "Relevance",
        "type": "strength",
        "message": "Strong connection to question requirements",
        "priority": 1
    }
]
```

### suggestions (interview_feedback.suggestions)
```json
[
    {
        "category": "Practice",
        "message": "Use the STAR method for behavioral questions",
        "priority": 2
    }
]
```

### resources (interview_feedback.resources)
```json
[
    {
        "title": "STAR Method Guide",
        "type": "article",
        "url": "https://example.com/star-method",
        "skill_area": "Interview Structure"
    }
]
```

---

## SQLAlchemy Model Example

```python
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base

class InterviewStatus(str, enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    skills = Column(JSON, default=list)
    # ... other fields
    
    sessions = relationship("InterviewSession", back_populates="user")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.CREATED)
    overall_score = Column(Float, nullable=True)
    # ... other fields
    
    user = relationship("User", back_populates="sessions")
    questions = relationship("InterviewQuestion", back_populates="session")
    feedback = relationship("InterviewFeedback", back_populates="session", uselist=False)
```

---

## Migration Commands

Using Alembic for database migrations:

```bash
# Initialize Alembic
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Design Notes

1. **UUID Primary Keys**: Used for security (non-guessable IDs) and distributed systems compatibility.

2. **Soft Deletes**: Consider adding `deleted_at` column instead of hard deletes.

3. **JSON Fields**: Used for flexible arrays (skills, suggestions). In PostgreSQL, use JSONB for better performance.

4. **Indexes**: Added on frequently queried columns (email, user_id, status, created_at).

5. **Cascade Deletes**: When a user is deleted, all their sessions, questions, and feedback are also deleted.

6. **Timestamps**: All tables have `created_at`; mutable tables have `updated_at`.

---

*Last Updated: January 2024*
