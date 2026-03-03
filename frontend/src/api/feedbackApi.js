/**
 * ==============================================================================
 * AI Mock Interview System - Feedback API Service
 * ==============================================================================
 * 
 * API calls for scoring, feedback, and analytics.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import apiClient, { parseError } from './client';
import { ENDPOINTS } from './config';

// =============================================================================
// SCORING
// =============================================================================

/**
 * Calculate final scores for a session
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - Score breakdown
 * 
 * @example
 * const response = await feedbackApi.calculateScores(sessionId);
 * console.log('Total Score:', response.data.total_score);
 * console.log('Grade:', response.data.letter_grade);
 */
export const calculateScores = async (sessionId) => {
    try {
        const response = await apiClient.post(ENDPOINTS.FEEDBACK.CALCULATE_SCORES(sessionId));
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
 * Get calculated scores for a session
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - Score breakdown
 */
export const getScores = async (sessionId) => {
    try {
        const response = await apiClient.get(ENDPOINTS.FEEDBACK.GET_SCORES(sessionId));
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
// FEEDBACK
// =============================================================================

/**
 * Generate comprehensive feedback for a session
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - Feedback with strengths, weaknesses, suggestions
 * 
 * @example
 * const response = await feedbackApi.generateFeedback(sessionId);
 * console.log('Strengths:', response.data.strengths);
 * console.log('Areas to improve:', response.data.weaknesses);
 * console.log('Next steps:', response.data.next_steps);
 */
export const generateFeedback = async (sessionId) => {
    try {
        const response = await apiClient.post(ENDPOINTS.FEEDBACK.GENERATE_FEEDBACK(sessionId));
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
 * Get generated feedback for a session
 * 
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - Feedback data
 */
export const getFeedback = async (sessionId) => {
    try {
        const response = await apiClient.get(ENDPOINTS.FEEDBACK.GET_FEEDBACK(sessionId));
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
// HISTORY & ANALYTICS
// =============================================================================

/**
 * Get interview history
 * 
 * @param {Object} params - Query parameters
 * @param {number} params.skip - Number of items to skip
 * @param {number} params.limit - Number of items to return
 * @param {string} params.start_date - Start date filter (ISO format)
 * @param {string} params.end_date - End date filter (ISO format)
 * @returns {Promise<Object>} - Interview history list
 * 
 * @example
 * const response = await feedbackApi.getHistory({ limit: 10 });
 * response.data.forEach(interview => {
 *     console.log(`${interview.title}: ${interview.overall_score}`);
 * });
 */
export const getHistory = async (params = {}) => {
    try {
        const response = await apiClient.get(ENDPOINTS.FEEDBACK.HISTORY, { params });
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
 * Get dashboard statistics
 * 
 * @returns {Promise<Object>} - Dashboard data
 * 
 * @example
 * const response = await feedbackApi.getDashboard();
 * const { total_interviews, average_score, improvement_rate } = response.data;
 */
export const getDashboard = async () => {
    try {
        const response = await apiClient.get(ENDPOINTS.FEEDBACK.DASHBOARD);
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
 * Get chart data for visualizations
 * 
 * @param {string} chartType - Type of chart (score_trend, category_radar, metrics_bar, weekly_activity)
 * @returns {Promise<Object>} - Chart data with labels and datasets
 * 
 * @example
 * const response = await feedbackApi.getChartData('score_trend');
 * // Use with Chart.js or Recharts
 */
export const getChartData = async (chartType) => {
    try {
        const response = await apiClient.get(ENDPOINTS.FEEDBACK.CHART_DATA(chartType));
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

const feedbackApi = {
    // Scoring
    calculateScores,
    getScores,
    
    // Feedback
    generateFeedback,
    getFeedback,
    
    // History & Analytics
    getHistory,
    getDashboard,
    getChartData,
};

export default feedbackApi;
