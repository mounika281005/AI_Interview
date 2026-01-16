# AI Mock Interview System - Frontend API Integration

## Overview

This folder contains all the API integration code for connecting the React frontend to the FastAPI backend.

---

## 📁 File Structure

```
frontend/src/
├── api/
│   ├── config.js           # API configuration & endpoints
│   ├── client.js           # Axios client with interceptors
│   ├── userApi.js          # User authentication & profile APIs
│   ├── interviewApi.js     # Interview session & question APIs
│   ├── feedbackApi.js      # Scoring & feedback APIs
│   ├── interviewFlow.js    # Complete flow example & documentation
│   └── index.js            # Central exports
├── hooks/
│   └── useApiHooks.js      # Custom React hooks for API state
└── components/
    └── ExampleComponents.jsx  # Sample component implementations
```

---

## 🔄 API Call Flow Order

```
1. User Registration/Login
   POST /users/register OR POST /users/login
                    │
                    ▼
2. Create Interview Session
   POST /interviews/sessions
                    │
                    ▼
3. Generate Questions
   POST /interviews/sessions/{id}/questions/generate
                    │
                    ▼
4. For Each Question:
   ├─▶ Display Question
   ├─▶ Record Audio
   │   POST /interviews/sessions/{id}/questions/{qid}/audio
   ├─▶ Transcribe Audio
   │   POST /interviews/sessions/{id}/questions/{qid}/transcribe
   └─▶ Evaluate Response
       POST /interviews/sessions/{id}/questions/{qid}/evaluate
                    │
                    ▼
5. Complete Session
   POST /interviews/sessions/{id}/complete
                    │
                    ▼
6. Calculate Scores
   POST /feedback/sessions/{id}/scores
                    │
                    ▼
7. Generate Feedback
   POST /feedback/sessions/{id}/feedback
                    │
                    ▼
8. Display Dashboard
   GET /feedback/dashboard
   GET /feedback/history
```

---

## 📦 Installation

```bash
# Install axios (HTTP client)
npm install axios

# If using React Router
npm install react-router-dom
```

---

## 🚀 Quick Start

### 1. Setup API Client

```javascript
// In your main App.js or index.js
import { API_BASE_URL } from './api/config';

console.log('API URL:', API_BASE_URL);
// Default: http://localhost:8000/api/v1
```

### 2. Wrap App with AuthProvider

```jsx
import { AuthProvider } from './hooks/useApiHooks';

function App() {
    return (
        <AuthProvider>
            <Router>
                {/* Your routes */}
            </Router>
        </AuthProvider>
    );
}
```

### 3. Use API in Components

```jsx
import { useAuth, useInterviewSessions } from './hooks/useApiHooks';

function InterviewPage() {
    const { user } = useAuth();
    const { sessions, createSession, loading } = useInterviewSessions();
    
    const handleStart = async () => {
        const result = await createSession({
            title: 'My Interview',
            target_role: 'Software Engineer',
            difficulty: 'medium'
        });
        
        if (result.success) {
            // Navigate to interview
        }
    };
    
    return (
        <div>
            <h1>Welcome, {user?.full_name}</h1>
            <button onClick={handleStart} disabled={loading}>
                Start Interview
            </button>
        </div>
    );
}
```

---

## 📋 Example Request/Response

### Login

**Request:**
```javascript
const result = await userApi.login('user@email.com', 'password123');
```

**Response:**
```json
{
    "success": true,
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer"
    }
}
```

### Create Session

**Request:**
```javascript
const result = await interviewApi.createSession({
    title: "Frontend Developer Interview",
    target_role: "Frontend Developer",
    target_company: "Google",
    difficulty: "medium"
});
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Frontend Developer Interview",
        "status": "created",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

### Generate Questions

**Request:**
```javascript
const result = await interviewApi.generateQuestions(sessionId, {
    num_questions: 5,
    categories: ["behavioral", "technical"],
    skills: ["React", "JavaScript", "CSS"]
});
```

**Response:**
```json
{
    "success": true,
    "data": {
        "questions": [
            {
                "id": "q-uuid-1",
                "question_text": "Tell me about a challenging React project.",
                "category": "technical",
                "difficulty": "medium",
                "time_limit": 120,
                "expected_topics": ["React", "challenges", "solution"]
            }
        ]
    }
}
```

### Upload Audio

**Request:**
```javascript
const result = await interviewApi.uploadAudio(
    sessionId,
    questionId,
    audioBlob,  // Blob from MediaRecorder
    95          // Duration in seconds
);
```

**Response:**
```json
{
    "success": true,
    "data": {
        "audio_id": "audio-uuid",
        "file_path": "/uploads/sessions/123/q-1.mp3",
        "duration": 95,
        "format": "webm"
    }
}
```

### Get Feedback

**Request:**
```javascript
const result = await feedbackApi.generateFeedback(sessionId);
```

**Response:**
```json
{
    "success": true,
    "data": {
        "overall_rating": "Good",
        "summary": "Your performance was rated Good...",
        "strengths": [
            { "category": "Relevance", "message": "Strong focus on questions" }
        ],
        "weaknesses": [
            { "category": "Grammar", "message": "Some errors detected" }
        ],
        "suggestions": [
            { "message": "Practice STAR method" }
        ],
        "readiness_score": 72,
        "readiness_level": "Almost Ready",
        "next_steps": [
            "Complete 2-3 more mock sessions"
        ]
    }
}
```

---

## ⚠️ Error Handling

All API functions return a consistent format:

```javascript
// Success
{
    success: true,
    data: { ... }
}

// Error
{
    success: false,
    error: {
        code: 400,
        message: "Error message",
        details: []
    }
}
```

### Error Handling Example

```jsx
const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    
    const result = await userApi.login(email, password);
    
    setLoading(false);
    
    if (result.success) {
        // Handle success
        navigate('/dashboard');
    } else {
        // Handle error
        if (result.error.code === 401) {
            setError('Invalid email or password');
        } else if (result.error.code === 422) {
            setError('Please check your input');
        } else {
            setError(result.error.message);
        }
    }
};
```

---

## 🎤 Audio Recording

Use the `useAudioRecording` hook for recording:

```jsx
import { useAudioRecording } from './hooks/useApiHooks';

function RecordingComponent() {
    const { 
        isRecording, 
        audioBlob, 
        duration,
        startRecording, 
        stopRecording,
        resetRecording 
    } = useAudioRecording();
    
    return (
        <div>
            {!isRecording ? (
                <button onClick={startRecording}>Start Recording</button>
            ) : (
                <button onClick={stopRecording}>Stop ({duration}s)</button>
            )}
            
            {audioBlob && (
                <>
                    <audio controls src={URL.createObjectURL(audioBlob)} />
                    <button onClick={resetRecording}>Re-record</button>
                </>
            )}
        </div>
    );
}
```

---

## 🔐 Authentication

The client automatically handles:

1. **Token Storage**: Tokens stored in localStorage
2. **Auto-attach**: Bearer token added to all requests
3. **Auto-redirect**: Redirects to login on 401 errors

```javascript
// Check if authenticated
import { isAuthenticated } from './api/client';

if (isAuthenticated()) {
    // User is logged in
}
```

---

## 📊 Dashboard Integration

```jsx
import { useDashboard } from './hooks/useApiHooks';

function DashboardPage() {
    const { stats, history, charts, loading, refresh } = useDashboard();
    
    if (loading) return <Loading />;
    
    return (
        <div>
            <h1>Your Progress</h1>
            <StatCards stats={stats} />
            <ScoreChart data={charts.score_trend} />
            <HistoryList items={history} />
        </div>
    );
}
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` in your React app root:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

For production:
```env
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
```

---

## 📚 Available Hooks

| Hook | Purpose |
|------|---------|
| `useAuth` | Authentication state & methods |
| `useApi` | Generic API call wrapper |
| `useInterviewSessions` | Session CRUD operations |
| `useQuestions` | Question management |
| `useAudioRecording` | Audio recording controls |
| `useFeedback` | Scores & feedback data |
| `useDashboard` | Dashboard statistics |

---

## 🧪 Testing

```javascript
// Test API connection
import { apiClient } from './api/client';

apiClient.get('/health')
    .then(res => console.log('API is healthy:', res.data))
    .catch(err => console.error('API connection failed:', err));
```

---

*For questions or issues, refer to the backend API documentation.*
