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

        // Store token if returned (backend returns { access_token, ... })
        if (response.data.access_token) {
            setToken(response.data.access_token);
        }

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
                user: response.data.user || null,
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
        const userData = response.data.data || response.data;

        // Fetch stats separately for profile widgets (best-effort).
        let statsData = {};
        try {
            const statsResponse = await apiClient.get(ENDPOINTS.USERS.STATS);
            statsData = statsResponse.data.data || statsResponse.data || {};
        } catch (_) {
            // Keep profile usable even if stats endpoint fails.
            statsData = {};
        }

        // Transform backend field names to frontend field names
        const transformedData = {
            ...userData,
            full_name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim(),
            target_role: userData.job_role || '',
            // Aliases used by ProfilePage widgets
            total_sessions: statsData.total_interviews ?? userData.total_interviews ?? 0,
            total_questions:
                statsData.interview_history_summary?.total_questions_answered ??
                statsData.total_questions_answered ??
                0,
        };

        return {
            success: true,
            data: transformedData,
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
        // Transform frontend field names to backend field names
        const backendData = {};

        // Handle full_name -> first_name + last_name
        if (profileData.full_name) {
            const nameParts = profileData.full_name.trim().split(/\s+/);
            backendData.first_name = nameParts[0] || '';
            backendData.last_name = nameParts.slice(1).join(' ') || backendData.first_name;
        }

        // Map target_role -> job_role
        if (profileData.target_role !== undefined) {
            backendData.job_role = profileData.target_role;
        }

        // Pass through other fields
        if (profileData.experience_level !== undefined) {
            backendData.experience_level = profileData.experience_level;
        }
        if (profileData.experience_years !== undefined) {
            backendData.experience_years = profileData.experience_years;
        }

        const response = await apiClient.put(ENDPOINTS.USERS.UPDATE_PROFILE, backendData);

        // Transform response back to frontend format
        const userData = response.data.data || response.data;
        const transformedData = {
            ...userData,
            full_name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim(),
            target_role: userData.job_role || '',
        };

        return {
            success: true,
            data: transformedData,
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
 * @param {string[]} skills - Array of skills
 * @returns {Promise<Object>} - Updated user profile
 *
 * @example
 * await userApi.updateSkills(['Python', 'JavaScript', 'React']);
 */
export const updateSkills = async (skills) => {
    try {
        // Backend POST /users/me/skills expects List[str] directly as body
        const response = await apiClient.post(
            ENDPOINTS.USERS.SKILLS,
            skills  // Send array directly, not wrapped in object
        );

        // Transform response back to frontend format
        const userData = response.data.data || response.data;
        const transformedData = {
            ...userData,
            full_name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim(),
            target_role: userData.job_role || '',
        };

        return {
            success: true,
            data: transformedData,
        };
    } catch (error) {
        return {
            success: false,
            error: parseError(error),
        };
    }
};

// =============================================================================
// ACCOUNT ACTIONS
// =============================================================================

/**
 * Export all user data as a JSON download.
 *
 * Fetches the user profile and interview history, then triggers a
 * browser download of the combined data.
 *
 * @returns {Promise<Object>} - Success/error result
 */
export const exportData = async () => {
    try {
        // Gather profile data
        const profileRes = await apiClient.get(ENDPOINTS.USERS.PROFILE);
        const profile = profileRes.data.data || profileRes.data;

        // Gather interview history (best-effort)
        let history = [];
        try {
            const historyRes = await apiClient.get('/skill-interview/history');
            history = historyRes.data.interviews || historyRes.data || [];
        } catch (_) {
            // History fetch is optional – continue without it
        }

        const exportPayload = {
            exported_at: new Date().toISOString(),
            profile,
            interview_history: history,
        };

        // Trigger browser download
        const blob = new Blob([JSON.stringify(exportPayload, null, 2)], {
            type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `interview-data-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        return { success: true };
    } catch (error) {
        return { success: false, error: parseError(error) };
    }
};

/**
 * Permanently delete the current user's account.
 *
 * @returns {Promise<Object>} - Success/error result
 */
export const deleteAccount = async () => {
    try {
        await apiClient.delete(ENDPOINTS.USERS.DELETE_ACCOUNT);
        removeToken();
        return { success: true };
    } catch (error) {
        return { success: false, error: parseError(error) };
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
    exportData,
    deleteAccount,
};

export default userApi;
