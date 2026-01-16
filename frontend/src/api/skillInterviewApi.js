/**
 * ==============================================================================
 * AI Mock Interview System - Skill Interview API Service
 * ==============================================================================
 * 
 * API calls for the streamlined skill-based interview flow.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import apiClient, { parseError, createFormData } from './client';
import { API_BASE_URL } from './config';

// Debug logging only in development
const debug = (action, data = null) => {
    if (process.env.NODE_ENV !== 'development') return;
    const timestamp = new Date().toISOString();
    if (data) {
        console.log(`[SKILL-API ${timestamp}] ${action}:`, data);
    } else {
        console.log(`[SKILL-API ${timestamp}] ${action}`);
    }
};

// Get base URL without /api/v1 suffix for health check
const getBaseUrl = () => {
    const url = API_BASE_URL.replace('/api/v1', '');
    return url;
};

const ENDPOINTS = {
    TECHNOLOGIES: '/skill-interview/technologies',
    START: '/skill-interview/start',
    UPLOAD_AUDIO: (sessionId, questionId) => `/skill-interview/${sessionId}/upload-audio/${questionId}`,
    SUBMIT: (sessionId) => `/skill-interview/${sessionId}/submit`,
    RESULTS: (sessionId) => `/skill-interview/${sessionId}/results`,
    HISTORY: '/skill-interview/history',
    HEALTH: '/health',
};

// =============================================================================
// HEALTH CHECK
// =============================================================================

/**
 * Check if backend is reachable
 */
export const checkBackendHealth = async () => {
    debug('checkBackendHealth: Testing backend connectivity...');
    try {
        // Health endpoint is at root, not under /api/v1
        const baseUrl = getBaseUrl();
        const response = await fetch(`${baseUrl}/health`);
        const data = await response.json();
        debug('checkBackendHealth: Backend is UP', data);
        return { isUp: true, data: data };
    } catch (error) {
        debug('checkBackendHealth: Backend is DOWN or unreachable', error.message);
        if (process.env.NODE_ENV === 'development') {
            console.error('[HEALTH CHECK FAILED]', {
                message: error.message,
                isNetworkError: true,
            });
        }
        return { isUp: false, error: error.message };
    }
};

// =============================================================================
// TECHNOLOGY SELECTION
// =============================================================================

/**
 * Get all available technologies for interview
 * 
 * @returns {Promise<Object>} - List of technologies with categories
 */
export const getTechnologies = async () => {
    debug('getTechnologies: Fetching technologies...');
    try {
        const response = await apiClient.get(ENDPOINTS.TECHNOLOGIES);
        debug('getTechnologies: Success', response.data);
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        debug('getTechnologies: Error', error);
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// =============================================================================
// INTERVIEW SESSION
// =============================================================================

/**
 * Start a new skill-based interview
 * 
 * @param {Object} params - Interview parameters
 * @param {string} params.technology - Selected technology/skill
 * @param {number} params.num_questions - Number of questions (default: 5)
 * @param {string} params.difficulty - Difficulty level (easy, medium, hard)
 * @returns {Promise<Object>} - Session with generated questions
 */
export const startInterview = async (params) => {
    debug('startInterview: Starting interview...', params);
    try {
        const requestBody = {
            technology: params.technology,
            num_questions: params.num_questions || 5,
            difficulty: params.difficulty || 'medium',
        };
        debug('startInterview: Request body', requestBody);
        
        const response = await apiClient.post(ENDPOINTS.START, requestBody);
        debug('startInterview: Success', response.data);
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        debug('startInterview: Error', { 
            message: error.message, 
            response: error.response?.data,
            status: error.response?.status 
        });
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Upload audio answer for a question
 * 
 * @param {string} sessionId - Interview session ID
 * @param {string} questionId - Question ID
 * @param {Blob} audioBlob - Recorded audio blob
 * @param {number} durationSeconds - Audio duration in seconds
 * @returns {Promise<Object>} - Upload result
 */
export const uploadAudio = async (sessionId, questionId, audioBlob, durationSeconds = 0) => {
    try {
        const formData = new FormData();
        
        // Convert blob to file with proper extension
        const extension = audioBlob.type.includes('webm') ? 'webm' : 
                         audioBlob.type.includes('mp3') ? 'mp3' : 
                         audioBlob.type.includes('wav') ? 'wav' : 'webm';
        
        const audioFile = new File([audioBlob], `answer.${extension}`, {
            type: audioBlob.type || 'audio/webm',
        });
        
        formData.append('audio', audioFile);
        formData.append('duration_seconds', durationSeconds.toString());
        
        const response = await apiClient.post(
            ENDPOINTS.UPLOAD_AUDIO(sessionId, questionId),
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );
        
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Submit interview for evaluation
 * 
 * @param {string} sessionId - Interview session ID
 * @returns {Promise<Object>} - Complete evaluation results
 */
export const submitInterview = async (sessionId) => {
    try {
        const response = await apiClient.post(ENDPOINTS.SUBMIT(sessionId));
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get interview results
 * 
 * @param {string} sessionId - Interview session ID
 * @returns {Promise<Object>} - Interview results
 */
export const getResults = async (sessionId) => {
    try {
        const response = await apiClient.get(ENDPOINTS.RESULTS(sessionId));
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Get interview history
 * 
 * @param {Object} params - Query parameters
 * @param {number} params.limit - Number of items to return
 * @param {number} params.offset - Number of items to skip
 * @returns {Promise<Object>} - Interview history
 */
export const getHistory = async (params = {}) => {
    try {
        const response = await apiClient.get(ENDPOINTS.HISTORY, { params });
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// Default export
const skillInterviewApi = {
    checkBackendHealth,
    getTechnologies,
    startInterview,
    uploadAudio,
    submitInterview,
    getResults,
    getHistory,
};

export default skillInterviewApi;
