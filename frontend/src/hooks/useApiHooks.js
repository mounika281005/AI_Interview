/**
 * ==============================================================================
 * AI Mock Interview System - Custom React Hooks for API Integration
 * ==============================================================================
 * 
 * Reusable hooks for managing API state in React components.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import { useState, useCallback, useEffect, useContext, createContext } from 'react';
import userApi from '../api/userApi';
import interviewApi from '../api/interviewApi';
import feedbackApi from '../api/feedbackApi';
import { isAuthenticated, removeToken } from '../api/client';

// =============================================================================
// AUTH CONTEXT
// =============================================================================

const AuthContext = createContext(null);

/**
 * Auth Provider Component
 * Wrap your app with this to provide auth state
 * 
 * @example
 * <AuthProvider>
 *   <App />
 * </AuthProvider>
 */
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    // Load user on mount if authenticated
    useEffect(() => {
        const loadUser = async () => {
            if (isAuthenticated()) {
                const result = await userApi.getProfile();
                if (result.success) {
                    setUser(result.data);
                }
            }
            setLoading(false);
        };
        loadUser();
    }, []);
    
    const login = async (email, password) => {
        const result = await userApi.login(email, password);
        if (result.success) {
            const profileResult = await userApi.getProfile();
            if (profileResult.success) {
                setUser(profileResult.data);
            }
        }
        return result;
    };
    
    const register = async (userData) => {
        const result = await userApi.register(userData);
        if (result.success) {
            setUser(result.data);
        }
        return result;
    };
    
    const logout = () => {
        removeToken();
        setUser(null);
    };
    
    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
            {children}
        </AuthContext.Provider>
    );
}

/**
 * Hook to access auth context
 * 
 * @example
 * const { user, login, logout } = useAuth();
 */
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

// =============================================================================
// API STATE HOOK
// =============================================================================

/**
 * Generic hook for API calls with loading and error state
 * 
 * @param {Function} apiFunction - The API function to call
 * @returns {Object} - { data, loading, error, execute, reset }
 * 
 * @example
 * const { data, loading, error, execute } = useApi(interviewApi.getSessions);
 * 
 * useEffect(() => {
 *   execute();
 * }, []);
 */
export function useApi(apiFunction) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const execute = useCallback(async (...args) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await apiFunction(...args);
            
            if (result.success) {
                setData(result.data);
                return { success: true, data: result.data };
            } else {
                setError(result.error);
                return { success: false, error: result.error };
            }
        } catch (err) {
            const error = { message: err.message };
            setError(error);
            return { success: false, error };
        } finally {
            setLoading(false);
        }
    }, [apiFunction]);
    
    const reset = useCallback(() => {
        setData(null);
        setError(null);
        setLoading(false);
    }, []);
    
    return { data, loading, error, execute, reset };
}

// =============================================================================
// INTERVIEW SESSION HOOK
// =============================================================================

/**
 * Hook for managing interview sessions
 * 
 * @example
 * const { 
 *   sessions, 
 *   currentSession, 
 *   loading, 
 *   createSession, 
 *   loadSessions 
 * } = useInterviewSessions();
 */
export function useInterviewSessions() {
    const [sessions, setSessions] = useState([]);
    const [currentSession, setCurrentSession] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const loadSessions = useCallback(async (params = {}) => {
        setLoading(true);
        const result = await interviewApi.getSessions(params);
        setLoading(false);
        
        if (result.success) {
            setSessions(result.data);
        } else {
            setError(result.error);
        }
        return result;
    }, []);
    
    const loadSession = useCallback(async (sessionId) => {
        setLoading(true);
        const result = await interviewApi.getSession(sessionId);
        setLoading(false);
        
        if (result.success) {
            setCurrentSession(result.data);
        } else {
            setError(result.error);
        }
        return result;
    }, []);
    
    const createSession = useCallback(async (sessionData) => {
        setLoading(true);
        const result = await interviewApi.createSession(sessionData);
        setLoading(false);
        
        if (result.success) {
            setCurrentSession(result.data);
            setSessions(prev => [result.data, ...prev]);
        } else {
            setError(result.error);
        }
        return result;
    }, []);
    
    const completeSession = useCallback(async (sessionId) => {
        setLoading(true);
        const result = await interviewApi.completeSession(sessionId);
        setLoading(false);
        
        if (result.success) {
            setCurrentSession(result.data);
            setSessions(prev => 
                prev.map(s => s.id === sessionId ? result.data : s)
            );
        }
        return result;
    }, []);
    
    return {
        sessions,
        currentSession,
        loading,
        error,
        loadSessions,
        loadSession,
        createSession,
        completeSession,
        setCurrentSession,
    };
}

// =============================================================================
// QUESTIONS HOOK
// =============================================================================

/**
 * Hook for managing interview questions
 * 
 * @param {string} sessionId - Current session ID
 * 
 * @example
 * const { 
 *   questions, 
 *   currentQuestion, 
 *   generateQuestions,
 *   nextQuestion 
 * } = useQuestions(sessionId);
 */
export function useQuestions(sessionId) {
    const [questions, setQuestions] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const currentQuestion = questions[currentIndex] || null;
    
    const generateQuestions = useCallback(async (config) => {
        if (!sessionId) return { success: false, error: { message: 'No session ID' } };
        
        setLoading(true);
        const result = await interviewApi.generateQuestions(sessionId, config);
        setLoading(false);
        
        if (result.success) {
            setQuestions(result.data.questions || result.data);
            setCurrentIndex(0);
        } else {
            setError(result.error);
        }
        return result;
    }, [sessionId]);
    
    const loadQuestions = useCallback(async () => {
        if (!sessionId) return;
        
        setLoading(true);
        const result = await interviewApi.getQuestions(sessionId);
        setLoading(false);
        
        if (result.success) {
            setQuestions(result.data);
        } else {
            setError(result.error);
        }
        return result;
    }, [sessionId]);
    
    const nextQuestion = useCallback(() => {
        if (currentIndex < questions.length - 1) {
            setCurrentIndex(prev => prev + 1);
            return true;
        }
        return false;
    }, [currentIndex, questions.length]);
    
    const previousQuestion = useCallback(() => {
        if (currentIndex > 0) {
            setCurrentIndex(prev => prev - 1);
            return true;
        }
        return false;
    }, [currentIndex]);
    
    const goToQuestion = useCallback((index) => {
        if (index >= 0 && index < questions.length) {
            setCurrentIndex(index);
        }
    }, [questions.length]);
    
    return {
        questions,
        currentQuestion,
        currentIndex,
        totalQuestions: questions.length,
        loading,
        error,
        generateQuestions,
        loadQuestions,
        nextQuestion,
        previousQuestion,
        goToQuestion,
        isFirstQuestion: currentIndex === 0,
        isLastQuestion: currentIndex === questions.length - 1,
    };
}

// =============================================================================
// AUDIO RECORDING HOOK
// =============================================================================

/**
 * Hook for audio recording
 * 
 * @example
 * const { 
 *   isRecording, 
 *   audioBlob, 
 *   duration,
 *   startRecording, 
 *   stopRecording 
 * } = useAudioRecording();
 */
export function useAudioRecording() {
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [duration, setDuration] = useState(0);
    const [mediaRecorder, setMediaRecorder] = useState(null);
    const [error, setError] = useState(null);
    
    const startRecording = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            const chunks = [];
            let startTime = Date.now();
            
            recorder.ondataavailable = (e) => {
                chunks.push(e.data);
            };
            
            recorder.onstop = () => {
                const blob = new Blob(chunks, { type: 'audio/webm' });
                setAudioBlob(blob);
                setDuration(Math.round((Date.now() - startTime) / 1000));
                stream.getTracks().forEach(track => track.stop());
            };
            
            setMediaRecorder(recorder);
            recorder.start();
            setIsRecording(true);
            setError(null);
            
            return { success: true };
        } catch (err) {
            setError({ message: 'Failed to access microphone' });
            return { success: false, error: err };
        }
    }, []);
    
    const stopRecording = useCallback(() => {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            setIsRecording(false);
        }
    }, [mediaRecorder, isRecording]);
    
    const resetRecording = useCallback(() => {
        setAudioBlob(null);
        setDuration(0);
        setError(null);
    }, []);
    
    return {
        isRecording,
        audioBlob,
        duration,
        error,
        startRecording,
        stopRecording,
        resetRecording,
    };
}

// =============================================================================
// DASHBOARD HOOK
// =============================================================================

/**
 * Hook for dashboard data
 * 
 * @example
 * const { stats, history, charts, loading, refresh } = useDashboard();
 */
export function useDashboard() {
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [charts, setCharts] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const loadDashboard = useCallback(async () => {
        setLoading(true);
        
        try {
            // Load all dashboard data in parallel
            const [statsResult, historyResult] = await Promise.all([
                feedbackApi.getDashboard(),
                feedbackApi.getHistory({ limit: 10 }),
            ]);
            
            if (statsResult.success) {
                setStats(statsResult.data);
            }
            
            if (historyResult.success) {
                setHistory(historyResult.data);
            }
            
            // Load chart data
            const chartTypes = ['score_trend', 'category_radar', 'metrics_bar'];
            const chartResults = await Promise.all(
                chartTypes.map(type => feedbackApi.getChartData(type))
            );
            
            const chartsData = {};
            chartTypes.forEach((type, index) => {
                if (chartResults[index].success) {
                    chartsData[type] = chartResults[index].data;
                }
            });
            setCharts(chartsData);
            
        } catch (err) {
            setError({ message: err.message });
        } finally {
            setLoading(false);
        }
    }, []);
    
    const refresh = useCallback(() => {
        loadDashboard();
    }, [loadDashboard]);
    
    // Load on mount
    useEffect(() => {
        loadDashboard();
    }, [loadDashboard]);
    
    return {
        stats,
        history,
        charts,
        loading,
        error,
        refresh,
    };
}

// =============================================================================
// FEEDBACK HOOK
// =============================================================================

/**
 * Hook for session feedback
 * 
 * @param {string} sessionId - Session ID
 * 
 * @example
 * const { scores, feedback, loading, generateFeedback } = useFeedback(sessionId);
 */
export function useFeedback(sessionId) {
    const [scores, setScores] = useState(null);
    const [feedback, setFeedback] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const calculateScores = useCallback(async () => {
        if (!sessionId) return;
        
        setLoading(true);
        const result = await feedbackApi.calculateScores(sessionId);
        setLoading(false);
        
        if (result.success) {
            setScores(result.data);
        } else {
            setError(result.error);
        }
        return result;
    }, [sessionId]);
    
    const generateFeedback = useCallback(async () => {
        if (!sessionId) return;
        
        setLoading(true);
        const result = await feedbackApi.generateFeedback(sessionId);
        setLoading(false);
        
        if (result.success) {
            setFeedback(result.data);
        } else {
            setError(result.error);
        }
        return result;
    }, [sessionId]);
    
    const loadFeedback = useCallback(async () => {
        if (!sessionId) return;
        
        setLoading(true);
        const [scoresResult, feedbackResult] = await Promise.all([
            feedbackApi.getScores(sessionId),
            feedbackApi.getFeedback(sessionId),
        ]);
        setLoading(false);
        
        if (scoresResult.success) setScores(scoresResult.data);
        if (feedbackResult.success) setFeedback(feedbackResult.data);
    }, [sessionId]);
    
    return {
        scores,
        feedback,
        loading,
        error,
        calculateScores,
        generateFeedback,
        loadFeedback,
    };
}

export default {
    AuthProvider,
    useAuth,
    useApi,
    useInterviewSessions,
    useQuestions,
    useAudioRecording,
    useDashboard,
    useFeedback,
};
