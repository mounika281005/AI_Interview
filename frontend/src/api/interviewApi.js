/**
 * ==============================================================================
 * AI Mock Interview System - Interview API Service
 * ==============================================================================
 * 
 * API calls for interview sessions, questions, audio, and transcription.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import apiClient, { parseError, createFormData } from './client';
import { ENDPOINTS, UPLOAD_LIMITS } from './config';

// =============================================================================
// SESSION MANAGEMENT
// =============================================================================

/**
 * Create a new interview session
 * 
 * @param {Object} sessionData - Session configuration
 * @param {string} sessionData.title - Session title (optional, for display)
 * @param {string} sessionData.target_role - Target job role
 * @param {string} sessionData.target_company - Target company (optional)
 * @param {string} sessionData.difficulty - Difficulty level
 * @param {string} sessionData.interview_type - Interview type (technical, behavioral, mixed)
 * @param {Array} sessionData.skills_tested - Skills to test
 * @param {string} sessionData.experience_level - Experience level
 * @param {number} sessionData.total_questions - Number of questions
 * @param {number} sessionData.time_limit_per_question - Seconds per question
 * @returns {Promise<Object>} - Created session
 * 
 * @example
 * const response = await interviewApi.createSession({
 *     target_role: 'Senior Frontend Developer',
 *     difficulty: 'medium',
 *     interview_type: 'technical',
 *     skills_tested: ['React', 'JavaScript']
 * });
 */
export const createSession = async (sessionData) => {
    try {
        // Transform frontend field names to backend schema
        const payload = {
            job_role: sessionData.target_role || sessionData.job_role,
            interview_type: sessionData.interview_type || 'technical',
            skills_tested: sessionData.skills_tested || sessionData.skills || [],
            experience_level: sessionData.experience_level || 'mid',
            difficulty: sessionData.difficulty || 'medium',
            total_questions: sessionData.total_questions || 5,
            time_limit_per_question: sessionData.time_limit_per_question || 180,
        };
        
        const response = await apiClient.post(ENDPOINTS.INTERVIEWS.SESSIONS, payload);
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get all interview sessions for current user
 * 
 * @param {Object} params - Query parameters
 * @param {number} params.skip - Number of items to skip
 * @param {number} params.limit - Number of items to return
 * @param {string} params.status - Filter by status
 * @returns {Promise<Object>} - List of sessions
 */
export const getSessions = async (params = {}) => {
    try {
        const response = await apiClient.get(ENDPOINTS.INTERVIEWS.SESSIONS, { params });
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get session by ID
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - Session details
 */
export const getSession = async (sessionId) => {
    try {
        const response = await apiClient.get(ENDPOINTS.INTERVIEWS.SESSION_BY_ID(sessionId));
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Mark session as complete
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - Updated session
 */
export const completeSession = async (sessionId) => {
    try {
        const response = await apiClient.post(ENDPOINTS.INTERVIEWS.COMPLETE_SESSION(sessionId));
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// =============================================================================
// QUESTION GENERATION
// =============================================================================

/**
 * Generate interview questions using AI
 * 
 * @param {string} sessionId - Session ID
 * @param {Object} config - Generation configuration
 * @param {number} config.num_questions - Number of questions
 * @param {string[]} config.categories - Question categories
 * @param {string[]} config.skills - Technical skills to focus on
 * @returns {Promise<Object>} - Generated questions
 * 
 * @example
 * const response = await interviewApi.generateQuestions(sessionId, {
 *     num_questions: 5,
 *     categories: ['behavioral', 'technical'],
 *     skills: ['React', 'JavaScript', 'Node.js']
 * });
 */
export const generateQuestions = async (sessionId, config) => {
    try {
        const response = await apiClient.post(
            ENDPOINTS.INTERVIEWS.GENERATE_QUESTIONS(sessionId),
            config
        );
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get all questions for a session
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - List of questions
 */
export const getQuestions = async (sessionId) => {
    try {
        const response = await apiClient.get(ENDPOINTS.INTERVIEWS.GET_QUESTIONS(sessionId));
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get specific question
 * 
 * @param {string} sessionId - Session ID
 * @param {string} questionId - Question ID
 * @returns {Promise<Object>} - Question details
 */
export const getQuestion = async (sessionId, questionId) => {
    try {
        const response = await apiClient.get(
            ENDPOINTS.INTERVIEWS.GET_QUESTION(sessionId, questionId)
        );
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// =============================================================================
// AUDIO UPLOAD
// =============================================================================

/**
 * Upload audio response for a question
 * 
 * @param {string} sessionId - Session ID
 * @param {string} questionId - Question ID
 * @param {File} audioFile - Audio file to upload
 * @param {number} duration - Recording duration in seconds
 * @returns {Promise<Object>} - Upload result
 * 
 * @example
 * const response = await interviewApi.uploadAudio(
 *     sessionId,
 *     questionId,
 *     audioBlob,
 *     recordingDuration
 * );
 */
export const uploadAudio = async (sessionId, questionId, audioFile, duration) => {
    // Validate file size
    if (audioFile.size > UPLOAD_LIMITS.MAX_AUDIO_SIZE) {
        return {
            success: false,
            error: {
                code: 400,
                message: `File size exceeds limit of ${UPLOAD_LIMITS.MAX_AUDIO_SIZE / 1024 / 1024}MB`,
            },
        };
    }
    
    try {
        const formData = createFormData(audioFile, { duration: duration.toString() }, 'audio');
        
        const response = await apiClient.post(
            ENDPOINTS.INTERVIEWS.UPLOAD_AUDIO(sessionId, questionId),
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                // Track upload progress
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    console.log(`Upload progress: ${percentCompleted}%`);
                },
            }
        );
        
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// =============================================================================
// SPEECH-TO-TEXT
// =============================================================================

/**
 * Transcribe audio to text
 * 
 * @param {string} sessionId - Session ID
 * @param {string} questionId - Question ID
 * @param {string} language - Language code (default: 'en')
 * @returns {Promise<Object>} - Transcription result
 * 
 * @example
 * const response = await interviewApi.transcribeAudio(sessionId, questionId, 'en');
 * if (response.success) {
 *     console.log('Transcript:', response.data.transcript);
 * }
 */
export const transcribeAudio = async (sessionId, questionId, language = 'en') => {
    try {
        const response = await apiClient.post(
            ENDPOINTS.INTERVIEWS.TRANSCRIBE(sessionId, questionId),
            { language }
        );
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get transcript for a question
 * 
 * @param {string} sessionId - Session ID
 * @param {string} questionId - Question ID
 * @returns {Promise<Object>} - Transcript data
 */
export const getTranscript = async (sessionId, questionId) => {
    try {
        const response = await apiClient.get(
            ENDPOINTS.INTERVIEWS.GET_TRANSCRIPT(sessionId, questionId)
        );
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// =============================================================================
// NLP EVALUATION
// =============================================================================

/**
 * Evaluate response using NLP
 * 
 * @param {string} sessionId - Session ID
 * @param {string} questionId - Question ID
 * @param {string[]} expectedKeywords - Expected keywords (optional)
 * @returns {Promise<Object>} - Evaluation scores
 * 
 * @example
 * const response = await interviewApi.evaluateResponse(sessionId, questionId, [
 *     'teamwork', 'problem-solving', 'leadership'
 * ]);
 * console.log('Scores:', response.data);
 */
export const evaluateResponse = async (sessionId, questionId, expectedKeywords = []) => {
    try {
        const response = await apiClient.post(
            ENDPOINTS.INTERVIEWS.EVALUATE(sessionId, questionId),
            { expected_keywords: expectedKeywords }
        );
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get full session evaluation
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - Session evaluation data
 */
export const getSessionEvaluation = async (sessionId) => {
    try {
        const response = await apiClient.get(ENDPOINTS.INTERVIEWS.GET_EVALUATION(sessionId));
        return {
            success: true,
            data: response.data.data || response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// =============================================================================
// EXPORT
// =============================================================================

const interviewApi = {
    // Sessions
    createSession,
    getSessions,
    getSession,
    completeSession,
    
    // Questions
    generateQuestions,
    getQuestions,
    getQuestion,
    
    // Audio
    uploadAudio,
    
    // Transcription
    transcribeAudio,
    getTranscript,
    
    // Evaluation
    evaluateResponse,
    getSessionEvaluation,
};

export default interviewApi;
