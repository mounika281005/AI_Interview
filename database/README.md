# Database Models

## Purpose
Defines all database schemas, models, and handles data persistence. Contains migrations, seeds, and repository patterns for data access.

## Structure
```
database/
├── models/
│   ├── user.py                  # User account model
│   ├── interview_session.py     # Interview session model
│   ├── question.py              # Question bank model
│   ├── answer.py                # Candidate answers model
│   ├── feedback.py              # Feedback & scores model
│   ├── job_role.py              # Job roles & categories
│   └── base.py                  # Base model class
├── migrations/
│   ├── versions/                # Migration version files
│   └── alembic.ini              # Alembic configuration
├── repositories/
│   ├── user_repository.py       # User data access
│   ├── interview_repository.py  # Interview data access
│   ├── question_repository.py   # Question data access
│   └── base_repository.py       # Base repository pattern
├── seeds/
│   ├── questions_seed.py        # Default questions
│   ├── job_roles_seed.py        # Job role categories
│   └── run_seeds.py             # Seed runner
├── schemas/                     # Pydantic schemas for validation
│   ├── user_schema.py
│   ├── interview_schema.py
│   └── question_schema.py
└── config/
    └── database.py              # DB connection config
```

## Database Schema Overview

### Users
- id, email, password_hash, name, created_at

### Interview Sessions
- id, user_id, job_role_id, status, started_at, completed_at

### Questions
- id, content, type, difficulty, job_role_id, category

### Answers
- id, session_id, question_id, transcription, audio_url

### Feedback
- id, answer_id, scores (JSON), suggestions, strengths

## Technologies
- PostgreSQL (primary database)
- Redis (caching & sessions)
- SQLAlchemy (ORM)
- Alembic (migrations)
