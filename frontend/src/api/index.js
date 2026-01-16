/**
 * ==============================================================================
 * AI Mock Interview System - API Index
 * ==============================================================================
 * 
 * Central export for all API services.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

// API Client
export { default as apiClient } from './client';
export { getToken, setToken, removeToken, isAuthenticated, parseError } from './client';

// Configuration
export { API_BASE_URL, ENDPOINTS, REQUEST_TIMEOUT, UPLOAD_LIMITS } from './config';

// API Services
export { default as userApi } from './userApi';
export { default as interviewApi } from './interviewApi';
export { default as feedbackApi } from './feedbackApi';
export { default as skillInterviewApi } from './skillInterviewApi';

// Named exports for convenience (excluding skillInterviewApi to avoid conflicts)
export * from './userApi';
export * from './interviewApi';
export * from './feedbackApi';
// Note: skillInterviewApi has conflicting names (getHistory, uploadAudio), 
// use skillInterviewApi.methodName() instead
