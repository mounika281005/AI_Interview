# System Architecture - AI Mock Interview Platform

## Overview

This document describes the complete system architecture for the AI-based mock interview platform, including user flows, API design, AI service integration, and data management.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │ Mobile App  │  │   Admin     │  │  Analytics  │        │
│  │  (React)    │  │  (Future)   │  │  Dashboard  │  │  Dashboard  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Nginx / AWS API Gateway                                             │   │
│  │  • Load Balancing    • Rate Limiting    • SSL Termination           │   │
│  │  • Request Routing   • Authentication   • CORS Handling             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND SERVICES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Auth        │  │  Interview   │  │  User        │  │  Analytics   │    │
│  │  Service     │  │  Service     │  │  Service     │  │  Service     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Question    │  │  Feedback    │  │  Notification│  │  File        │    │
│  │  Service     │  │  Service     │  │  Service     │  │  Service     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AI SERVICES LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Speech-to-  │  │  NLP         │  │  Question    │  │  Scoring &   │    │
│  │  Text        │  │  Evaluation  │  │  Generation  │  │  Feedback    │    │
│  │  (Whisper)   │  │  (BERT)      │  │  (GPT/LLaMA) │  │  Engine      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  PostgreSQL  │  │  Redis       │  │  S3/Blob     │  │  Vector DB   │    │
│  │  (Primary)   │  │  (Cache)     │  │  (Files)     │  │  (Embeddings)│    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. User Interaction Flow

### 2.1 Complete Interview Journey

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER INTERVIEW JOURNEY                               │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
    │  Sign   │────▶│  Setup  │────▶│Interview│────▶│  AI     │────▶│ Results │
    │  Up     │     │ Profile │     │ Session │     │Analysis │     │ Review  │
    └─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
         │               │               │               │               │
         ▼               ▼               ▼               ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
    │• Email  │     │• Job    │     │• Video  │     │• Speech │     │• Scores │
    │• OAuth  │     │  Role   │     │  Record │     │  to Text│     │• Graphs │
    │• Profile│     │• Skills │     │• Audio  │     │• NLP    │     │• Tips   │
    │  Create │     │• Level  │     │  Capture│     │• Scoring│     │• Export │
    └─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### 2.2 Detailed Interview Session Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      INTERVIEW SESSION FLOW                               │
└──────────────────────────────────────────────────────────────────────────┘

     USER                    FRONTEND                   BACKEND
       │                        │                          │
       │   1. Start Interview   │                          │
       │───────────────────────▶│                          │
       │                        │   2. Create Session      │
       │                        │─────────────────────────▶│
       │                        │                          │
       │                        │   3. Get First Question  │
       │                        │◀─────────────────────────│
       │   4. Display Question  │                          │
       │◀───────────────────────│                          │
       │                        │                          │
       │   5. Record Answer     │                          │
       │───────────────────────▶│                          │
       │                        │   6. Upload Audio        │
       │                        │─────────────────────────▶│
       │                        │                          │
       │                        │         ┌────────────────┴────────────────┐
       │                        │         │     AI PROCESSING PIPELINE      │
       │                        │         │  7. Speech-to-Text (Whisper)    │
       │                        │         │  8. NLP Evaluation (BERT)       │
       │                        │         │  9. Generate Score              │
       │                        │         │  10. Create Follow-up Question  │
       │                        │         └────────────────┬────────────────┘
       │                        │                          │
       │                        │   11. Next Question      │
       │                        │◀─────────────────────────│
       │   12. Display Question │                          │
       │◀───────────────────────│                          │
       │                        │                          │
       │        ... (Repeat for all questions) ...         │
       │                        │                          │
       │                        │   13. End Session        │
       │                        │─────────────────────────▶│
       │                        │                          │
       │                        │   14. Final Results      │
       │                        │◀─────────────────────────│
       │   15. Show Dashboard   │                          │
       │◀───────────────────────│                          │
       │                        │                          │
```

### 2.3 User States & Transitions

```
                                    ┌─────────────┐
                                    │   GUEST     │
                                    └──────┬──────┘
                                           │ Register/Login
                                           ▼
                                    ┌─────────────┐
                                    │ REGISTERED  │
                                    └──────┬──────┘
                                           │ Complete Profile
                                           ▼
                                    ┌─────────────┐
                         ┌─────────│   ACTIVE    │─────────┐
                         │         └─────────────┘         │
                         │                                 │
              Start Interview                      View History
                         │                                 │
                         ▼                                 ▼
                  ┌─────────────┐                   ┌─────────────┐
                  │ IN_INTERVIEW│                   │  REVIEWING  │
                  └──────┬──────┘                   └─────────────┘
                         │ Complete
                         ▼
                  ┌─────────────┐
                  │  COMPLETED  │──────▶ Return to ACTIVE
                  └─────────────┘
```

---

## 3. Backend API Responsibilities

### 3.1 Service Breakdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND SERVICE ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  AUTH SERVICE                                                                │
│  ─────────────                                                               │
│  Responsibilities:                                                           │
│  • User registration & login                                                 │
│  • JWT token generation & validation                                         │
│  • OAuth integration (Google, GitHub)                                        │
│  • Password reset & email verification                                       │
│  • Session management                                                        │
│                                                                              │
│  Endpoints:                                                                  │
│  POST /api/auth/register          POST /api/auth/login                      │
│  POST /api/auth/refresh           POST /api/auth/logout                     │
│  POST /api/auth/forgot-password   POST /api/auth/reset-password             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  INTERVIEW SERVICE                                                           │
│  ─────────────────                                                           │
│  Responsibilities:                                                           │
│  • Create & manage interview sessions                                        │
│  • Coordinate question delivery                                              │
│  • Handle answer submissions                                                 │
│  • Trigger AI processing pipeline                                            │
│  • Manage interview state & progress                                         │
│                                                                              │
│  Endpoints:                                                                  │
│  POST   /api/interviews              GET    /api/interviews/{id}            │
│  POST   /api/interviews/{id}/start   POST   /api/interviews/{id}/answer     │
│  POST   /api/interviews/{id}/end     GET    /api/interviews/{id}/progress   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  QUESTION SERVICE                                                            │
│  ────────────────                                                            │
│  Responsibilities:                                                           │
│  • Manage question bank                                                      │
│  • Fetch questions by role/difficulty                                        │
│  • Request AI-generated questions                                            │
│  • Handle follow-up question logic                                           │
│                                                                              │
│  Endpoints:                                                                  │
│  GET    /api/questions                GET    /api/questions/{id}            │
│  POST   /api/questions/generate       GET    /api/questions/by-role         │
│  POST   /api/questions/follow-up                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  FEEDBACK SERVICE                                                            │
│  ────────────────                                                            │
│  Responsibilities:                                                           │
│  • Aggregate scores from AI modules                                          │
│  • Generate comprehensive feedback                                           │
│  • Create performance reports                                                │
│  • Track improvement over time                                               │
│                                                                              │
│  Endpoints:                                                                  │
│  GET    /api/feedback/{session_id}    GET    /api/feedback/history          │
│  GET    /api/feedback/report/{id}     POST   /api/feedback/export           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  USER SERVICE                                                                │
│  ────────────                                                                │
│  Responsibilities:                                                           │
│  • Manage user profiles                                                      │
│  • Track user preferences                                                    │
│  • Handle subscription/plan management                                       │
│  • User settings & notifications                                             │
│                                                                              │
│  Endpoints:                                                                  │
│  GET    /api/users/me                 PUT    /api/users/me                  │
│  GET    /api/users/me/stats           PUT    /api/users/me/preferences      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 API Request/Response Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API REQUEST LIFECYCLE                                │
└─────────────────────────────────────────────────────────────────────────────┘

  Client Request
        │
        ▼
┌───────────────┐
│  API Gateway  │──── Rate Limiting Check
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Auth         │──── JWT Validation
│  Middleware   │──── User Context Extraction
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Validation   │──── Request Schema Validation
│  Middleware   │──── Data Sanitization
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Route        │──── Business Logic Execution
│  Handler      │──── Service Layer Calls
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Response     │──── Format Response
│  Builder      │──── Error Handling
└───────┬───────┘
        │
        ▼
  Client Response
```

---

## 4. AI Service Integration

### 4.1 AI Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI PROCESSING PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────┘

   Audio Input                                                    Final Output
       │                                                               ▲
       ▼                                                               │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   STAGE 1    │    │   STAGE 2    │    │   STAGE 3    │    │   STAGE 4    │
│              │    │              │    │              │    │              │
│  Audio       │───▶│  Text        │───▶│  Semantic    │───▶│  Score &     │
│  Processing  │    │  Analysis    │    │  Evaluation  │    │  Feedback    │
│              │    │              │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│• Noise       │    │• Whisper     │    │• BERT        │    │• Score       │
│  Reduction   │    │  Transcribe  │    │  Embeddings  │    │  Aggregation │
│• Format      │    │• Punctuation │    │• Similarity  │    │• Feedback    │
│  Conversion  │    │  Restoration │    │  Matching    │    │  Generation  │
│• Chunking    │    │• Confidence  │    │• Sentiment   │    │• Improvement │
│              │    │  Scores      │    │  Analysis    │    │  Suggestions │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### 4.2 AI Service Communication

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI SERVICE COMMUNICATION FLOW                           │
└─────────────────────────────────────────────────────────────────────────────┘

    BACKEND                    MESSAGE QUEUE                   AI SERVICES
       │                           │                               │
       │   1. Submit Audio Job     │                               │
       │──────────────────────────▶│                               │
       │                           │   2. Process STT              │
       │                           │──────────────────────────────▶│
       │                           │                               │ Speech-to-Text
       │                           │   3. Return Transcript        │
       │                           │◀──────────────────────────────│
       │                           │                               │
       │                           │   4. Process NLP              │
       │                           │──────────────────────────────▶│
       │                           │                               │ NLP Evaluation
       │                           │   5. Return Analysis          │
       │                           │◀──────────────────────────────│
       │                           │                               │
       │                           │   6. Generate Score           │
       │                           │──────────────────────────────▶│
       │                           │                               │ Scoring Engine
       │                           │   7. Return Feedback          │
       │                           │◀──────────────────────────────│
       │                           │                               │
       │   8. Complete Results     │                               │
       │◀──────────────────────────│                               │
       │                           │                               │


┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI SERVICE INTERFACES                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Speech-to-Text Service:
─────────────────────────────────────────────────────────────────────────────
  Input:  { audio_url: string, language: string, format: string }
  Output: { transcript: string, confidence: float, timestamps: array }

NLP Evaluation Service:
─────────────────────────────────────────────────────────────────────────────
  Input:  { transcript: string, question: string, ideal_answer: string }
  Output: { 
            relevance_score: float, 
            sentiment: string,
            keywords: array,
            grammar_issues: array,
            embedding: vector 
          }

Question Generation Service:
─────────────────────────────────────────────────────────────────────────────
  Input:  { job_role: string, difficulty: string, previous_answers: array }
  Output: { question: string, type: string, expected_keywords: array }

Scoring & Feedback Service:
─────────────────────────────────────────────────────────────────────────────
  Input:  { nlp_result: object, question_context: object, user_history: array }
  Output: { 
            scores: { content: int, communication: int, technical: int },
            feedback: string,
            improvements: array,
            strengths: array 
          }
```

### 4.3 Real-time Processing with WebSockets

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REAL-TIME INTERVIEW FLOW (WebSocket)                      │
└─────────────────────────────────────────────────────────────────────────────┘

    FRONTEND                    BACKEND                      AI SERVICES
        │                          │                              │
        │   WS: Connect            │                              │
        │─────────────────────────▶│                              │
        │                          │                              │
        │   WS: Start Interview    │                              │
        │─────────────────────────▶│                              │
        │                          │                              │
        │   WS: Question           │                              │
        │◀─────────────────────────│                              │
        │                          │                              │
        │   WS: Audio Stream       │                              │
        │─────────────────────────▶│                              │
        │                          │   Process Stream             │
        │                          │─────────────────────────────▶│
        │                          │                              │
        │   WS: Transcript Update  │◀─────────────────────────────│
        │◀─────────────────────────│   (Real-time)               │
        │                          │                              │
        │   WS: Analysis Progress  │                              │
        │◀─────────────────────────│                              │
        │                          │                              │
        │   WS: Score & Feedback   │                              │
        │◀─────────────────────────│                              │
        │                          │                              │
```

---

## 5. Data Storage and Retrieval

### 5.1 Database Schema Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE ENTITY RELATIONSHIP                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
│      USERS        │         │    JOB_ROLES      │         │    QUESTIONS      │
├───────────────────┤         ├───────────────────┤         ├───────────────────┤
│ id (PK)           │         │ id (PK)           │         │ id (PK)           │
│ email             │         │ title             │         │ content           │
│ password_hash     │         │ description       │         │ type              │
│ name              │         │ category          │         │ difficulty        │
│ avatar_url        │         │ skill_tags        │         │ job_role_id (FK)  │
│ created_at        │         │ created_at        │         │ category          │
│ updated_at        │         └─────────┬─────────┘         │ expected_keywords │
└─────────┬─────────┘                   │                   │ ideal_answer      │
          │                             │                   │ created_at        │
          │                             │                   └─────────┬─────────┘
          │         ┌───────────────────┴───────────────────┐         │
          │         │                                       │         │
          ▼         ▼                                       │         │
┌───────────────────────────────────┐                       │         │
│       INTERVIEW_SESSIONS          │                       │         │
├───────────────────────────────────┤                       │         │
│ id (PK)                           │◀──────────────────────┘         │
│ user_id (FK)                      │                                 │
│ job_role_id (FK)                  │                                 │
│ status (pending/active/completed) │                                 │
│ difficulty_level                  │                                 │
│ total_questions                   │                                 │
│ started_at                        │                                 │
│ completed_at                      │                                 │
│ overall_score                     │                                 │
│ created_at                        │                                 │
└─────────────────┬─────────────────┘                                 │
                  │                                                   │
                  ▼                                                   │
┌───────────────────────────────────┐         ┌───────────────────────┘
│           ANSWERS                 │         │
├───────────────────────────────────┤         │
│ id (PK)                           │         │
│ session_id (FK)                   │◀────────┘
│ question_id (FK)                  │
│ audio_url                         │
│ video_url                         │
│ transcription                     │
│ duration_seconds                  │
│ answered_at                       │
│ created_at                        │
└─────────────────┬─────────────────┘
                  │
                  ▼
┌───────────────────────────────────┐
│          FEEDBACK                 │
├───────────────────────────────────┤
│ id (PK)                           │
│ answer_id (FK)                    │
│ content_score                     │
│ communication_score               │
│ technical_score                   │
│ relevance_score                   │
│ overall_score                     │
│ strengths (JSON)                  │
│ improvements (JSON)               │
│ detailed_feedback                 │
│ ai_confidence                     │
│ created_at                        │
└───────────────────────────────────┘
```

### 5.2 Data Storage Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MULTI-TIER STORAGE ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 1: HOT DATA (Redis)                                                    │
│  ─────────────────────────                                                   │
│  • Active session data              TTL: 2 hours                            │
│  • User authentication tokens       TTL: 24 hours                           │
│  • Real-time transcription cache    TTL: 30 minutes                         │
│  • Rate limiting counters           TTL: 1 minute                           │
│  • Question queue for session       TTL: 2 hours                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 2: WARM DATA (PostgreSQL)                                              │
│  ───────────────────────────────                                             │
│  • User profiles                    Indexed: email, id                      │
│  • Interview sessions               Indexed: user_id, status, created_at    │
│  • Questions & answers              Indexed: session_id, question_id        │
│  • Feedback & scores                Indexed: answer_id, created_at          │
│  • Job roles & categories           Indexed: category, title                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 3: COLD DATA (S3/Blob Storage)                                         │
│  ────────────────────────────────────                                        │
│  • Audio recordings                 Lifecycle: 90 days → Glacier            │
│  • Video recordings                 Lifecycle: 90 days → Glacier            │
│  • Generated PDF reports            Lifecycle: 1 year → Delete              │
│  • Model weights & checkpoints      Permanent storage                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 4: VECTOR DATA (Pinecone/Weaviate)                                     │
│  ────────────────────────────────────────                                    │
│  • Answer embeddings                For similarity search                   │
│  • Question embeddings              For semantic matching                   │
│  • User preference vectors          For personalization                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Data Access Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA ACCESS PATTERNS                                 │
└─────────────────────────────────────────────────────────────────────────────┘

READ PATTERNS:
─────────────────────────────────────────────────────────────────────────────

1. Get User Dashboard Data (High Frequency)
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   Check     │────▶│   If Miss   │────▶│   Cache     │
   │   Redis     │     │   Query DB  │     │   Result    │
   └─────────────┘     └─────────────┘     └─────────────┘

2. Load Interview History (Medium Frequency)
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   Query     │────▶│   Join      │────▶│   Paginate  │
   │   Sessions  │     │   Feedback  │     │   Results   │
   └─────────────┘     └─────────────┘     └─────────────┘

3. Get Question by Similarity (AI-Driven)
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   Vector    │────▶│   Semantic  │────▶│   Fetch     │
   │   Search    │     │   Match     │     │   Full Data │
   └─────────────┘     └─────────────┘     └─────────────┘


WRITE PATTERNS:
─────────────────────────────────────────────────────────────────────────────

1. Save Answer (Real-time)
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   Upload    │────▶│   Save      │────▶│   Trigger   │
   │   Audio/S3  │     │   Metadata  │     │   AI Queue  │
   └─────────────┘     └─────────────┘     └─────────────┘

2. Save Feedback (Async)
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   AI        │────▶│   Save      │────▶│   Update    │
   │   Results   │     │   Feedback  │     │   Session   │
   └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 6. API Flow Examples

### 6.1 Complete Interview API Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE INTERVIEW API SEQUENCE                           │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Create Interview Session
─────────────────────────────────────────────────────────────────────────────
POST /api/interviews
Request:  { "job_role_id": "uuid", "difficulty": "intermediate" }
Response: { "session_id": "uuid", "status": "pending", "total_questions": 10 }

Step 2: Start Interview
─────────────────────────────────────────────────────────────────────────────
POST /api/interviews/{session_id}/start
Response: { 
  "status": "active",
  "current_question": {
    "id": "uuid",
    "content": "Tell me about yourself",
    "type": "behavioral",
    "time_limit": 120
  }
}

Step 3: Submit Answer
─────────────────────────────────────────────────────────────────────────────
POST /api/interviews/{session_id}/answer
Request:  { 
  "question_id": "uuid", 
  "audio_url": "s3://bucket/audio.webm",
  "duration": 95 
}
Response: { 
  "answer_id": "uuid",
  "processing_status": "queued",
  "next_question": { ... }
}

Step 4: Get Real-time Updates (WebSocket)
─────────────────────────────────────────────────────────────────────────────
WS /api/interviews/{session_id}/live
Events:
  → { "type": "transcription", "text": "I am a software...", "partial": true }
  → { "type": "transcription", "text": "I am a software engineer...", "partial": false }
  → { "type": "analysis_complete", "answer_id": "uuid" }

Step 5: End Interview
─────────────────────────────────────────────────────────────────────────────
POST /api/interviews/{session_id}/end
Response: { "status": "completed", "redirect_to": "/results/{session_id}" }

Step 6: Get Results
─────────────────────────────────────────────────────────────────────────────
GET /api/feedback/{session_id}
Response: {
  "overall_score": 78,
  "scores": {
    "content": 82,
    "communication": 75,
    "technical": 80
  },
  "answers": [
    {
      "question": "Tell me about yourself",
      "score": 85,
      "strengths": ["Clear structure", "Relevant experience"],
      "improvements": ["Add specific metrics"]
    }
  ],
  "recommendations": ["Practice STAR method", "Prepare more examples"]
}
```

### 6.2 Authentication API Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AUTHENTICATION API FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Register:
─────────────────────────────────────────────────────────────────────────────
POST /api/auth/register
Request:  { "email": "user@example.com", "password": "***", "name": "John" }
Response: { "user_id": "uuid", "message": "Verification email sent" }

Login:
─────────────────────────────────────────────────────────────────────────────
POST /api/auth/login
Request:  { "email": "user@example.com", "password": "***" }
Response: { 
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "user": { "id": "uuid", "name": "John", "email": "user@example.com" }
}

Token Refresh:
─────────────────────────────────────────────────────────────────────────────
POST /api/auth/refresh
Request:  { "refresh_token": "eyJ..." }
Response: { "access_token": "eyJ...", "expires_in": 3600 }
```

---

## 7. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PRODUCTION DEPLOYMENT                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   AWS CDN   │
                              │ CloudFront  │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │   Route 53  │
                              │     DNS     │
                              └──────┬──────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
             ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
             │  Frontend   │  │   Backend   │  │     AI      │
             │    S3 +     │  │    ECS      │  │   Lambda/   │
             │  CloudFront │  │   Fargate   │  │    ECS      │
             └─────────────┘  └──────┬──────┘  └──────┬──────┘
                                     │                │
                    ┌────────────────┴────────────────┘
                    │
         ┌──────────┼──────────┬──────────────────┐
         │          │          │                  │
  ┌──────▼──────┐ ┌─▼──────┐ ┌─▼──────────┐ ┌────▼─────┐
  │  PostgreSQL │ │ Redis  │ │     S3     │ │ SQS/SNS  │
  │    RDS      │ │ElastiC │ │   Bucket   │ │  Queue   │
  └─────────────┘ └────────┘ └────────────┘ └──────────┘
```

---

## 8. Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                                      │
└─────────────────────────────────────────────────────────────────────────────┘

Layer 1: Network Security
─────────────────────────────────────────────────────────────────────────────
  • VPC with private subnets for databases
  • WAF for DDoS protection
  • Security groups & NACLs

Layer 2: Application Security
─────────────────────────────────────────────────────────────────────────────
  • JWT authentication with short-lived tokens
  • HTTPS everywhere (TLS 1.3)
  • Input validation & sanitization
  • Rate limiting per user/IP

Layer 3: Data Security
─────────────────────────────────────────────────────────────────────────────
  • Encryption at rest (AES-256)
  • Encryption in transit (TLS)
  • PII data masking in logs
  • Regular security audits

Layer 4: Compliance
─────────────────────────────────────────────────────────────────────────────
  • GDPR compliance for EU users
  • Data retention policies
  • Right to deletion implementation
  • Audit logging
```

---

## Summary

This architecture provides:

1. **Scalability** - Microservices allow independent scaling
2. **Reliability** - Multi-tier storage with failover
3. **Performance** - Caching layers and async processing
4. **Security** - Multiple security layers
5. **Maintainability** - Clear separation of concerns
