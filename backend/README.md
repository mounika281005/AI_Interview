# Backend APIs

## Purpose
The central API server that handles all business logic, authentication, and coordinates between the frontend and AI modules.

## Structure
```
backend/
├── src/
│   ├── api/
│   │   ├── routes/            # API route definitions
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── interview.py   # Interview session endpoints
│   │   │   ├── questions.py   # Question management
│   │   │   ├── feedback.py    # Feedback retrieval
│   │   │   └── user.py        # User management
│   │   ├── middleware/        # Request middleware
│   │   │   ├── auth.py        # JWT validation
│   │   │   ├── logging.py     # Request logging
│   │   │   └── cors.py        # CORS handling
│   │   └── validators/        # Request validation schemas
│   ├── services/              # Business logic layer
│   │   ├── interview_service.py
│   │   ├── user_service.py
│   │   └── analytics_service.py
│   ├── config/                # Configuration management
│   ├── utils/                 # Helper utilities
│   └── main.py               # Application entry point
├── requirements.txt
└── Dockerfile
```

## Key Responsibilities
- User authentication & authorization
- Interview session management
- Coordinating AI module calls
- Data persistence
- WebSocket connections for real-time features
