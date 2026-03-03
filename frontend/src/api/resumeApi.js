/**
 * ==============================================================================
 * AI Mock Interview System - Resume API Service
 * ==============================================================================
 *
 * API calls for resume upload, parsing, and management.
 *
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import apiClient, { parseError } from './client';
import { ENDPOINTS } from './config';

// =============================================================================
// RESUME UPLOAD
// =============================================================================

/**
 * Upload and parse a resume file
 *
 * @param {File} file - Resume file (PDF, TXT, or DOCX)
 * @returns {Promise<Object>} - Parsed resume data
 */
export const uploadResume = async (file) => {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await apiClient.post(
            ENDPOINTS.USERS.UPLOAD_RESUME,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
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

/**
 * Get parsed resume data
 *
 * @returns {Promise<Object>} - Resume data
 */
export const getResumeData = async () => {
    try {
        const response = await apiClient.get(ENDPOINTS.USERS.GET_RESUME);
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
 * Delete resume
 *
 * @returns {Promise<Object>} - Confirmation
 */
export const deleteResume = async () => {
    try {
        const response = await apiClient.delete(ENDPOINTS.USERS.DELETE_RESUME);
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

const resumeApi = {
    uploadResume,
    getResumeData,
    deleteResume,
};

export default resumeApi;
