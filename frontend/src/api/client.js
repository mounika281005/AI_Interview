/**
 * ==============================================================================
 * AI Mock Interview System - API Client
 * ==============================================================================
 * 
 * Axios-based HTTP client with interceptors for authentication and error handling.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import axios from 'axios';
import { API_BASE_URL, REQUEST_TIMEOUT } from './config';

// =============================================================================
// AXIOS INSTANCE
// =============================================================================

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: REQUEST_TIMEOUT,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false, // Important: must be false when using CORS with "*"
});

// =============================================================================
// TOKEN MANAGEMENT
// =============================================================================

/**
 * Get authentication token from local storage
 */
export const getToken = () => {
    return localStorage.getItem('auth_token');
};

/**
 * Set authentication token in local storage
 */
export const setToken = (token) => {
    localStorage.setItem('auth_token', token);
};

/**
 * Remove authentication token from local storage
 */
export const removeToken = () => {
    localStorage.removeItem('auth_token');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
    return !!getToken();
};

// =============================================================================
// REQUEST INTERCEPTOR
// =============================================================================

apiClient.interceptors.request.use(
    (config) => {
        // Add auth token to headers if available
        const token = getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Log request in development
        if (process.env.NODE_ENV === 'development') {
            console.log(`📤 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        }
        
        return config;
    },
    (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// =============================================================================
// RESPONSE INTERCEPTOR
// =============================================================================

apiClient.interceptors.response.use(
    (response) => {
        // Log response in development
        if (process.env.NODE_ENV === 'development') {
            console.log(`📥 API Response: ${response.status} ${response.config.url}`);
            console.log(`📥 Response data:`, response.data);
        }
        
        return response;
    },
    (error) => {
        // Enhanced error logging with full details
        console.error('=== API ERROR DETAILS ===');
        console.error('[API ERROR] URL:', error.config?.baseURL + error.config?.url);
        console.error('[API ERROR] Method:', error.config?.method?.toUpperCase());
        console.error('[API ERROR] Headers:', error.config?.headers);
        
        if (error.response) {
            console.error('[API ERROR] Status:', error.response.status, error.response.statusText);
            console.error('[API ERROR] Response Data:', error.response.data);
            console.error('[API ERROR] Response Headers:', error.response.headers);
        } else if (error.request) {
            console.error('[API ERROR] No response received - possible causes:');
            console.error('  1. Backend server not running (check terminal)');
            console.error('  2. CORS blocking the request');
            console.error('  3. Network connectivity issue');
            console.error('  4. Wrong API URL:', error.config?.baseURL);
            console.error('[API ERROR] Request was:', error.request);
        } else {
            console.error('[API ERROR] Request setup error:', error.message);
        }
        console.error('[API ERROR] Full error:', error);
        console.error('=========================');
        
        // Handle different error scenarios
        if (error.response) {
            const { status, data } = error.response;
            
            switch (status) {
                case 401:
                    // Unauthorized - clear token and redirect to login
                    console.error('Authentication failed - redirecting to login');
                    removeToken();
                    window.location.href = '/login';
                    break;
                    
                case 403:
                    console.error('Access forbidden');
                    break;
                    
                case 404:
                    console.error('Resource not found');
                    break;
                    
                case 422:
                    // Validation error
                    console.error('Validation error:', data);
                    break;
                    
                case 500:
                    console.error('Server error');
                    break;
                    
                default:
                    console.error(`API Error: ${status}`, data);
            }
        } else if (error.request) {
            // Network error
            console.error('Network error - no response received');
        } else {
            console.error('Request configuration error:', error.message);
        }
        
        return Promise.reject(error);
    }
);

// =============================================================================
// HELPER METHODS
// =============================================================================

/**
 * Parse API error response
 */
export const parseError = (error) => {
    if (error.response?.data?.error) {
        return {
            code: error.response.data.error.code || error.response.status,
            message: error.response.data.error.message || 'An error occurred',
            details: error.response.data.error.details || [],
        };
    }
    
    if (error.response?.data?.detail) {
        // FastAPI validation error format
        return {
            code: error.response.status,
            message: typeof error.response.data.detail === 'string' 
                ? error.response.data.detail 
                : 'Validation error',
            details: Array.isArray(error.response.data.detail) 
                ? error.response.data.detail 
                : [],
        };
    }
    
    return {
        code: error.response?.status || 500,
        message: error.message || 'An unexpected error occurred',
        details: [],
    };
};

/**
 * Create FormData for file uploads
 */
export const createFormData = (file, additionalData = {}, fieldName = 'file') => {
    const formData = new FormData();
    formData.append(fieldName, file);
    
    Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
    });
    
    return formData;
};

export default apiClient;
