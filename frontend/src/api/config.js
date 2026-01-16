/**
 * ==============================================================================
 * AI Mock Interview System - API Configuration
 * ==============================================================================
 * 
 * Central configuration for all API calls.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

// Base API URL - Change this for production
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// API Endpoints
export const ENDPOINTS = {
    // User endpoints
    USERS: {
        REGISTER: '/users/register',
        LOGIN: '/users/login',
        PROFILE: '/users/me',
        UPDATE_PROFILE: '/users/me',
        UPDATE_SKILLS: (userId) => `/users/${userId}/skills`,
    },
    
    // Interview session endpoints
    INTERVIEWS: {
        SESSIONS: '/interviews/',
        SESSION_BY_ID: (id) => `/interviews/${id}`,
        COMPLETE_SESSION: (id) => `/interviews/${id}/complete`,
        
        // Question endpoints
        GENERATE_QUESTIONS: (sessionId) => `/interviews/${sessionId}/questions/generate`,
        GET_QUESTIONS: (sessionId) => `/interviews/${sessionId}/questions`,
        GET_QUESTION: (sessionId, questionId) => `/interviews/${sessionId}/questions/${questionId}`,
        
        // Audio endpoints
        UPLOAD_AUDIO: (sessionId, questionId) => `/interviews/${sessionId}/questions/${questionId}/audio`,
        GET_AUDIO: (sessionId, questionId) => `/interviews/${sessionId}/questions/${questionId}/audio`,
        
        // Transcription endpoints
        TRANSCRIBE: (sessionId, questionId) => `/interviews/${sessionId}/questions/${questionId}/transcribe`,
        GET_TRANSCRIPT: (sessionId, questionId) => `/interviews/${sessionId}/questions/${questionId}/transcript`,
        
        // Evaluation endpoints
        EVALUATE: (sessionId, questionId) => `/interviews/${sessionId}/questions/${questionId}/evaluate`,
        GET_EVALUATION: (sessionId) => `/interviews/${sessionId}/evaluation`,
    },
    
    // Feedback & Analytics endpoints
    FEEDBACK: {
        CALCULATE_SCORES: (sessionId) => `/feedback/sessions/${sessionId}/scores`,
        GET_SCORES: (sessionId) => `/feedback/sessions/${sessionId}/scores`,
        GENERATE_FEEDBACK: (sessionId) => `/feedback/sessions/${sessionId}/feedback`,
        GET_FEEDBACK: (sessionId) => `/feedback/sessions/${sessionId}/feedback`,
        HISTORY: '/feedback/history',
        DASHBOARD: '/feedback/dashboard',
        CHART_DATA: (chartType) => `/feedback/charts/${chartType}`,
    },
};

// Request timeout (in milliseconds)
export const REQUEST_TIMEOUT = 30000;

// File upload limits
export const UPLOAD_LIMITS = {
    MAX_AUDIO_SIZE: 50 * 1024 * 1024, // 50MB
    ALLOWED_AUDIO_TYPES: ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/webm', 'audio/m4a'],
};

export default {
    API_BASE_URL,
    ENDPOINTS,
    REQUEST_TIMEOUT,
    UPLOAD_LIMITS,
};
