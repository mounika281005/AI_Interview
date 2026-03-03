/**
 * ==============================================================================
 * AI Mock Interview System - Complete Interview Flow Example
 * ==============================================================================
 * 
 * This file demonstrates the complete API call flow from start to finish.
 * Use this as a reference for implementing the interview flow in your React app.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import userApi from './userApi';
import interviewApi from './interviewApi';
import feedbackApi from './feedbackApi';

/**
 * ==============================================================================
 * API CALL FLOW ORDER
 * ==============================================================================
 * 
 * 1. User Registration/Login
 *    └─> POST /users/register OR POST /users/login
 * 
 * 2. Create Interview Session
 *    └─> POST /interviews/sessions
 * 
 * 3. Generate Questions
 *    └─> POST /interviews/sessions/{id}/questions/generate
 * 
 * 4. For Each Question:
 *    a. Display Question
 *    b. Record Audio Response
 *       └─> POST /interviews/sessions/{id}/questions/{qid}/audio
 *    c. Transcribe Audio
 *       └─> POST /interviews/sessions/{id}/questions/{qid}/transcribe
 *    d. Evaluate Response
 *       └─> POST /interviews/sessions/{id}/questions/{qid}/evaluate
 * 
 * 5. Complete Session
 *    └─> POST /interviews/sessions/{id}/complete
 * 
 * 6. Calculate Final Scores
 *    └─> POST /feedback/sessions/{id}/scores
 * 
 * 7. Generate Feedback
 *    └─> POST /feedback/sessions/{id}/feedback
 * 
 * 8. Display Results & Dashboard
 *    └─> GET /feedback/dashboard
 *    └─> GET /feedback/history
 * 
 * ==============================================================================
 */

// =============================================================================
// EXAMPLE REQUEST/RESPONSE JSON
// =============================================================================

/*
1. USER REGISTRATION
--------------------
Request:
{
    "email": "student@university.edu",
    "password": "SecurePass123!",
    "full_name": "John Doe"
}

Response:
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "student@university.edu",
        "full_name": "John Doe",
        "created_at": "2024-01-15T10:30:00Z",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}

2. CREATE SESSION
-----------------
Request:
{
    "title": "Software Engineer Practice",
    "target_role": "Software Engineer",
    "target_company": "Google",
    "difficulty": "medium"
}

Response:
{
    "success": true,
    "data": {
        "id": "session-uuid-123",
        "title": "Software Engineer Practice",
        "status": "created",
        "created_at": "2024-01-15T10:35:00Z"
    }
}

3. GENERATE QUESTIONS
---------------------
Request:
{
    "num_questions": 5,
    "categories": ["behavioral", "technical", "situational"],
    "skills": ["Python", "React", "SQL"]
}

Response:
{
    "success": true,
    "data": {
        "questions": [
            {
                "id": "q-uuid-1",
                "question_text": "Tell me about a time when you faced a tight deadline.",
                "category": "behavioral",
                "difficulty": "medium",
                "time_limit": 120,
                "expected_topics": ["deadline", "prioritization", "outcome"]
            },
            {
                "id": "q-uuid-2",
                "question_text": "Explain how you would design a REST API for a social media app.",
                "category": "technical",
                "difficulty": "medium",
                "time_limit": 180,
                "expected_topics": ["endpoints", "authentication", "scalability"]
            }
        ]
    }
}

4. UPLOAD AUDIO
---------------
Request: FormData with audio file

Response:
{
    "success": true,
    "data": {
        "audio_id": "audio-uuid",
        "file_path": "/uploads/sessions/123/q-1.mp3",
        "duration": 95,
        "format": "mp3",
        "size_bytes": 1523456
    }
}

5. TRANSCRIBE AUDIO
-------------------
Request:
{
    "language": "en"
}

Response:
{
    "success": true,
    "data": {
        "transcript": "In my previous role, I faced a situation where we had only two weeks to deliver a critical feature...",
        "confidence": 0.94,
        "language": "en",
        "word_count": 156
    }
}

6. EVALUATE RESPONSE
--------------------
Request:
{
    "expected_keywords": ["deadline", "prioritization", "teamwork", "outcome"]
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
        "summary": "Good response with clear structure and relevant examples."
    }
}

7. CALCULATE SCORES
-------------------
Response:
{
    "success": true,
    "data": {
        "total_score": 78.5,
        "letter_grade": "B+",
        "breakdown": {
            "relevance": { "raw": 82, "weighted": 28.7 },
            "grammar": { "raw": 75, "weighted": 15.0 },
            "fluency": { "raw": 80, "weighted": 20.0 },
            "keywords": { "raw": 77, "weighted": 15.4 }
        }
    }
}

8. GENERATE FEEDBACK
--------------------
Response:
{
    "success": true,
    "data": {
        "overall_rating": "Good",
        "summary": "Your performance was rated Good with a score of 78.5/100.",
        "strengths": [
            { "category": "Relevance", "message": "Strong connection to question" },
            { "category": "Keywords", "message": "Good use of technical terms" }
        ],
        "weaknesses": [
            { "category": "Grammar", "message": "Some grammatical errors" }
        ],
        "suggestions": [
            { "message": "Practice with the STAR method" },
            { "message": "Review grammar rules" }
        ],
        "readiness_score": 72,
        "readiness_level": "Almost Ready",
        "next_steps": [
            "Complete 2-3 more mock sessions",
            "Focus on grammar improvement"
        ]
    }
}

9. DASHBOARD
------------
Response:
{
    "success": true,
    "data": {
        "total_interviews": 12,
        "total_questions": 48,
        "average_score": 76.3,
        "best_score": 89.2,
        "improvement_rate": 8.5,
        "current_streak": 3,
        "skills_breakdown": {
            "relevance": 80.2,
            "grammar": 72.5,
            "fluency": 78.0,
            "keywords": 74.8
        }
    }
}
*/

// =============================================================================
// COMPLETE INTERVIEW FLOW IMPLEMENTATION
// =============================================================================

/**
 * Complete interview flow from start to finish
 * 
 * This function demonstrates how to orchestrate all API calls
 * for a complete interview session.
 */
export async function runCompleteInterviewFlow(userCredentials, interviewConfig, questions) {
    const results = {
        user: null,
        session: null,
        questions: [],
        responses: [],
        scores: null,
        feedback: null,
        errors: [],
    };
    
    try {
        // =====================================================================
        // STEP 1: User Login/Registration
        // =====================================================================
        console.log('Step 1: Authenticating user...');
        
        let authResult;
        if (userCredentials.isNewUser) {
            authResult = await userApi.register({
                email: userCredentials.email,
                password: userCredentials.password,
                full_name: userCredentials.fullName,
            });
        } else {
            authResult = await userApi.login(
                userCredentials.email,
                userCredentials.password
            );
        }
        
        if (!authResult.success) {
            throw new Error(`Authentication failed: ${authResult.error.message}`);
        }
        
        // Get user profile
        const profileResult = await userApi.getProfile();
        if (profileResult.success) {
            results.user = profileResult.data;
        }
        
        console.log('✅ User authenticated');
        
        // =====================================================================
        // STEP 2: Create Interview Session
        // =====================================================================
        console.log('Step 2: Creating interview session...');
        
        const sessionResult = await interviewApi.createSession({
            title: interviewConfig.title,
            target_role: interviewConfig.targetRole,
            target_company: interviewConfig.targetCompany,
            difficulty: interviewConfig.difficulty || 'medium',
        });
        
        if (!sessionResult.success) {
            throw new Error(`Failed to create session: ${sessionResult.error.message}`);
        }
        
        results.session = sessionResult.data;
        const sessionId = sessionResult.data.id;
        
        console.log('✅ Session created:', sessionId);
        
        // =====================================================================
        // STEP 3: Generate Questions
        // =====================================================================
        console.log('Step 3: Generating questions...');
        
        const questionsResult = await interviewApi.generateQuestions(sessionId, {
            num_questions: interviewConfig.numQuestions || 5,
            categories: interviewConfig.categories || ['behavioral', 'technical'],
            skills: interviewConfig.skills || [],
        });
        
        if (!questionsResult.success) {
            throw new Error(`Failed to generate questions: ${questionsResult.error.message}`);
        }
        
        results.questions = questionsResult.data.questions;
        
        console.log(`✅ Generated ${results.questions.length} questions`);
        
        // =====================================================================
        // STEP 4: Process Each Question (Audio → Transcribe → Evaluate)
        // =====================================================================
        console.log('Step 4: Processing responses...');
        
        for (let i = 0; i < results.questions.length; i++) {
            const question = results.questions[i];
            const questionId = question.id;
            
            console.log(`  Processing question ${i + 1}/${results.questions.length}...`);
            
            // Skip if no audio provided for this question
            if (!questions[i]?.audioFile) {
                console.log(`  ⚠️ No audio for question ${i + 1}, skipping...`);
                continue;
            }
            
            // 4a. Upload Audio
            const audioResult = await interviewApi.uploadAudio(
                sessionId,
                questionId,
                questions[i].audioFile,
                questions[i].duration || 0
            );
            
            if (!audioResult.success) {
                results.errors.push({
                    question: i + 1,
                    step: 'upload',
                    error: audioResult.error,
                });
                continue;
            }
            
            // 4b. Transcribe Audio
            const transcriptResult = await interviewApi.transcribeAudio(
                sessionId,
                questionId,
                'en'
            );
            
            if (!transcriptResult.success) {
                results.errors.push({
                    question: i + 1,
                    step: 'transcribe',
                    error: transcriptResult.error,
                });
                continue;
            }
            
            // 4c. Evaluate Response
            const evalResult = await interviewApi.evaluateResponse(
                sessionId,
                questionId,
                question.expected_topics || []
            );
            
            if (!evalResult.success) {
                results.errors.push({
                    question: i + 1,
                    step: 'evaluate',
                    error: evalResult.error,
                });
                continue;
            }
            
            results.responses.push({
                questionId,
                transcript: transcriptResult.data.transcript,
                evaluation: evalResult.data,
            });
            
            console.log(`  ✅ Question ${i + 1} processed`);
        }
        
        // =====================================================================
        // STEP 5: Complete Session
        // =====================================================================
        console.log('Step 5: Completing session...');
        
        await interviewApi.completeSession(sessionId);
        
        console.log('✅ Session completed');
        
        // =====================================================================
        // STEP 6: Calculate Final Scores
        // =====================================================================
        console.log('Step 6: Calculating scores...');
        
        const scoresResult = await feedbackApi.calculateScores(sessionId);
        
        if (scoresResult.success) {
            results.scores = scoresResult.data;
            console.log(`✅ Final score: ${results.scores.total_score}`);
        }
        
        // =====================================================================
        // STEP 7: Generate Feedback
        // =====================================================================
        console.log('Step 7: Generating feedback...');
        
        const feedbackResult = await feedbackApi.generateFeedback(sessionId);
        
        if (feedbackResult.success) {
            results.feedback = feedbackResult.data;
            console.log(`✅ Feedback generated: ${results.feedback.overall_rating}`);
        }
        
        // =====================================================================
        // COMPLETE
        // =====================================================================
        console.log('\n🎉 Interview flow completed successfully!');
        console.log(`Total Score: ${results.scores?.total_score || 'N/A'}`);
        console.log(`Grade: ${results.scores?.letter_grade || 'N/A'}`);
        console.log(`Readiness: ${results.feedback?.readiness_level || 'N/A'}`);
        
        return {
            success: true,
            data: results,
        };
        
    } catch (error) {
        console.error('❌ Interview flow failed:', error.message);
        return {
            success: false,
            error: error.message,
            partialResults: results,
        };
    }
}

// =============================================================================
// ERROR HANDLING PATTERNS
// =============================================================================

/**
 * Generic error handler for API calls
 * Use this in your React components
 */
export function handleApiError(error, setError, setLoading) {
    console.error('API Error:', error);
    
    // Set loading state to false
    if (setLoading) {
        setLoading(false);
    }
    
    // Handle different error types
    if (error.code === 401) {
        // Unauthorized - redirect to login
        window.location.href = '/login';
        return;
    }
    
    if (error.code === 422) {
        // Validation error - show field-specific errors
        const fieldErrors = error.details.reduce((acc, detail) => {
            acc[detail.loc[detail.loc.length - 1]] = detail.msg;
            return acc;
        }, {});
        setError({ type: 'validation', fields: fieldErrors });
        return;
    }
    
    if (error.code === 404) {
        setError({ type: 'not_found', message: 'Resource not found' });
        return;
    }
    
    if (error.code >= 500) {
        setError({ type: 'server', message: 'Server error. Please try again later.' });
        return;
    }
    
    // Generic error
    setError({ type: 'generic', message: error.message || 'An error occurred' });
}

/**
 * Retry logic for failed API calls
 */
export async function withRetry(apiCall, maxRetries = 3, delay = 1000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        const result = await apiCall();
        
        if (result.success) {
            return result;
        }
        
        // Don't retry on client errors (4xx)
        if (result.error?.code >= 400 && result.error?.code < 500) {
            return result;
        }
        
        // Wait before retrying
        if (attempt < maxRetries) {
            console.log(`Retry attempt ${attempt}/${maxRetries} in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
            delay *= 2; // Exponential backoff
        }
    }
    
    return { success: false, error: { message: 'Max retries exceeded' } };
}

export default runCompleteInterviewFlow;
