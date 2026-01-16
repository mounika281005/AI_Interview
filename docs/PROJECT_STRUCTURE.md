# Project Structure Overview

## Complete Folder Structure

```
Interview/
│
├── 📁 frontend/                          # USER INTERFACE
│   ├── public/                           # Static assets (images, fonts)
│   └── src/
│       ├── components/                   # Reusable UI components
│       ├── pages/                        # Page routes
│       ├── services/                     # API calls
│       ├── hooks/                        # Custom React hooks
│       ├── store/                        # State management
│       ├── utils/                        # Helper functions
│       └── types/                        # TypeScript types
│
├── 📁 backend/                           # API SERVER
│   └── src/
│       ├── api/
│       │   ├── routes/                   # API endpoints
│       │   ├── middleware/               # Auth, logging, CORS
│       │   └── validators/               # Request validation
│       ├── services/                     # Business logic
│       ├── config/                       # App configuration
│       └── utils/                        # Utilities
│
├── 📁 ai-modules/                        # AI/ML COMPONENTS
│   │
│   ├── 📁 speech-to-text/               # AUDIO → TEXT
│   │   └── src/
│   │       ├── transcriber/              # Whisper, Google STT
│   │       ├── audio_processing/         # Noise reduction, splitting
│   │       ├── models/                   # Model weights
│   │       ├── api/                      # Service endpoint
│   │       └── utils/                    # Audio utilities
│   │
│   ├── 📁 nlp-evaluation/               # TEXT ANALYSIS
│   │   └── src/
│   │       ├── analyzers/                # Semantic, sentiment, grammar
│   │       ├── embeddings/               # Text vectorization
│   │       ├── models/                   # BERT, custom models
│   │       ├── api/                      # Service endpoint
│   │       └── utils/                    # Text preprocessing
│   │
│   ├── 📁 question-generation/          # DYNAMIC QUESTIONS
│   │   └── src/
│   │       ├── generators/               # LLM, template, adaptive
│   │       ├── templates/                # Question templates
│   │       │   ├── technical/
│   │       │   ├── behavioral/
│   │       │   ├── situational/
│   │       │   └── role_specific/
│   │       ├── question_bank/            # Question management
│   │       ├── api/                      # Service endpoint
│   │       └── utils/                    # Prompt building
│   │
│   └── 📁 scoring-feedback/             # SCORING & FEEDBACK
│       └── src/
│           ├── scorers/                  # Content, communication, tech
│           ├── feedback/                 # Feedback generation
│           ├── reports/                  # PDF reports, visualization
│           ├── benchmarks/               # Industry comparisons
│           ├── api/                      # Service endpoint
│           └── utils/                    # Score normalization
│
├── 📁 database/                          # DATA LAYER
│   ├── models/                           # SQLAlchemy models
│   ├── migrations/                       # Alembic migrations
│   ├── repositories/                     # Data access patterns
│   ├── seeds/                            # Initial data
│   ├── schemas/                          # Pydantic schemas
│   └── config/                           # DB configuration
│
├── 📁 shared/                            # SHARED CODE
│   ├── types/                            # Common type definitions
│   ├── constants/                        # Error codes, configs
│   ├── utils/                            # Logging, validators
│   └── exceptions/                       # Custom exceptions
│
├── 📁 tests/                             # TEST SUITES
│   ├── unit/                             # Unit tests
│   ├── integration/                      # Integration tests
│   ├── e2e/                              # End-to-end tests
│   └── fixtures/                         # Test data
│
├── 📁 docker/                            # CONTAINERS
│   ├── frontend/
│   ├── backend/
│   ├── ai-modules/
│   ├── database/
│   └── nginx/
│
└── 📁 docs/                              # DOCUMENTATION
    ├── architecture/                     # System design docs
    ├── api/                              # API documentation
    ├── guides/                           # Developer guides
    ├── ai-models/                        # AI model docs
    └── diagrams/                         # Visual diagrams
```

---

## Folder Purpose Summary

| Folder | Purpose |
|--------|---------|
| **frontend/** | User-facing web app where candidates take interviews |
| **backend/** | Central API server handling auth, sessions, coordination |
| **ai-modules/speech-to-text/** | Converts spoken audio to text using Whisper/Google |
| **ai-modules/nlp-evaluation/** | Analyzes answer quality, relevance, grammar using NLP |
| **ai-modules/question-generation/** | Creates dynamic interview questions using LLMs |
| **ai-modules/scoring-feedback/** | Generates scores, feedback, and improvement suggestions |
| **database/** | Data models, migrations, and persistence layer |
| **shared/** | Reusable code, types, and utilities across modules |
| **tests/** | All automated tests (unit, integration, e2e) |
| **docker/** | Container configurations for deployment |
| **docs/** | Project documentation and diagrams |

---

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────────┐
│  Frontend   │────▶│   Backend   │────▶│   Question Generator │
│  (React)    │     │   (FastAPI) │     │   (LLM-based)        │
└─────────────┘     └─────────────┘     └──────────────────────┘
       │                   │                        │
       │                   ▼                        │
       │           ┌─────────────┐                  │
       │           │  Database   │◀─────────────────┘
       │           │ (PostgreSQL)│
       │           └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌──────────────────────┐
│   Audio     │────▶│ Speech-to-  │────▶│   NLP Evaluation     │
│ Recording   │     │   Text      │     │   (BERT/Transformers)│
└─────────────┘     └─────────────┘     └──────────────────────┘
                                                   │
                                                   ▼
                                        ┌──────────────────────┐
                                        │  Scoring & Feedback  │
                                        │  Engine              │
                                        └──────────────────────┘
                                                   │
                                                   ▼
                                        ┌──────────────────────┐
                                        │  Results Dashboard   │
                                        │  (Frontend)          │
                                        └──────────────────────┘
```

---

## Getting Started

1. **Clone the repository**
2. **Set up environment variables** (copy `.env.example` to `.env`)
3. **Start with Docker**: `docker-compose up -d`
4. **Or run individually**:
   - Frontend: `cd frontend && npm install && npm run dev`
   - Backend: `cd backend && pip install -r requirements.txt && uvicorn src.main:app`
   - AI Modules: Each has its own startup script

---

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | React/Next.js, TailwindCSS, TypeScript |
| Backend | Python, FastAPI, WebSockets |
| Speech-to-Text | OpenAI Whisper, Google Speech API |
| NLP | HuggingFace Transformers, BERT, spaCy |
| Question Gen | OpenAI GPT / LLaMA, LangChain |
| Scoring | Custom ML models, scikit-learn |
| Database | PostgreSQL, Redis, SQLAlchemy |
| Infrastructure | Docker, Nginx, AWS/GCP |
