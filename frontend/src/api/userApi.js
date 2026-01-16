/**
 * ==============================================================================
 * AI Mock Interview System - User API Service
 * ==============================================================================
 * 
 * API calls for user authentication and profile management.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import apiClient, { setToken, removeToken, parseError } from './client';
import { ENDPOINTS } from './config';

// =============================================================================
// AUTHENTICATION
// =============================================================================

/**
 * Register a new user
 * 
 * @param {Object} userData - User registration data
 * @param {string} userData.email - User email
 * @param {string} userData.password - User password
 * @param {string} userData.full_name - User full name
 * @returns {Promise<Object>} - User data with token
 * 
 * @example
 * const response = await userApi.register({
 *     email: 'user@example.com',
 *     password: 'SecurePass123!',
 *     full_name: 'John Doe'
 * });
 */
export const register = async (userData) => {
    try {
        // Split full_name into first_name and last_name for backend compatibility
        const nameParts = (userData.full_name || '').trim().split(/\s+/);
        const first_name = nameParts[0] || '';
        const last_name = nameParts.slice(1).join(' ') || first_name; // Use first_name if no last name provided
        
        const payload = {
            email: userData.email,
            password: userData.password,
            first_name,
            last_name,
        };
        
        const response = await apiClient.post(ENDPOINTS.USERS.REGISTER, payload);
        
        // Store token if returned
        if (response.data.data?.token) {
            setToken(response.data.data.token);
        }
        
        return {
            success: true,
            data: response.data.data,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Login user
 * 
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} - User data with token
 * 
 * @example
 * const response = await userApi.login('user@example.com', 'password123');
 * if (response.success) {
 *     console.log('Logged in:', response.data.user);
 * }
 */
export const login = async (email, password) => {
    try {
        // Send JSON body with email and password
        const response = await apiClient.post(ENDPOINTS.USERS.LOGIN, {
            email,
            password,
        });
        
        // Store token
        if (response.data.access_token) {
            setToken(response.data.access_token);
        }
        
        return {
            success: true,
            data: {
                token: response.data.access_token,
                token_type: response.data.token_type,
            },
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

/**
 * Logout user
 */
export const logout = () => {
    removeToken();
    window.location.href = '/login';
};

// =============================================================================
// PROFILE MANAGEMENT
// =============================================================================

/**
 * Get current user profile
 * 
 * @returns {Promise<Object>} - User profile data
 * 
 * @example
 * const response = await userApi.getProfile();
 * if (response.success) {
 *     setUser(response.data);
 * }
 */
export const getProfile = async () => {
    try {
        const response = await apiClient.get(ENDPOINTS.USERS.PROFILE);
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
 * Update user profile
 * 
 * @param {Object} profileData - Updated profile data
 * @returns {Promise<Object>} - Updated user profile
 * 
 * @example
 * const response = await userApi.updateProfile({
 *     full_name: 'John Smith',
 *     target_role: 'Senior Developer',
 *     experience_years: 5
 * });
 */
export const updateProfile = async (profileData) => {
    try {
        const response = await apiClient.put(ENDPOINTS.USERS.UPDATE_PROFILE, profileData);
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
 * Update user skills
 * 
 * @param {string} userId - User ID
 * @param {string[]} skills - Array of skills
 * @returns {Promise<Object>} - Updated user profile
 * 
 * @example
 * await userApi.updateSkills(userId, ['Python', 'JavaScript', 'React']);
 */
export const updateSkills = async (userId, skills) => {
    try {
        const response = await apiClient.put(
            ENDPOINTS.USERS.UPDATE_SKILLS(userId),
            { skills }
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
// EXPORT
// =============================================================================

const userApi = {
    register,
    login,
    logout,
    getProfile,
    updateProfile,
    updateSkills,
};

export default userApi;
