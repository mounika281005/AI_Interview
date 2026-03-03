/**
 * ==============================================================================
 * AI Mock Interview System - Example React Components
 * ==============================================================================
 * 
 * Sample components demonstrating how to use the API integration.
 * Copy and customize these for your actual implementation.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import React, { useState, useEffect } from 'react';
import { 
    useAuth, 
    useInterviewSessions, 
    useQuestions, 
    useAudioRecording,
    useFeedback,
    useDashboard 
} from '../hooks/useApiHooks';
import interviewApi from '../api/interviewApi';

// =============================================================================
// LOGIN COMPONENT
// =============================================================================

/**
 * Login Form Component
 * 
 * Handles user authentication
 */
export function LoginForm({ onSuccess }) {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        const result = await login(email, password);
        
        setLoading(false);
        
        if (result.success) {
            onSuccess?.();
        } else {
            setError(result.error?.message || 'Login failed');
        }
    };
    
    return (
        <form onSubmit={handleSubmit} className="login-form">
            <h2>Login</h2>
            
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
            </div>
            
            <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
            </div>
            
            <button type="submit" disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
            </button>
        </form>
    );
}

// =============================================================================
// INTERVIEW SESSION COMPONENT
// =============================================================================

/**
 * Interview Session Component
 * 
 * Main component for conducting an interview
 */
export function InterviewSession({ sessionId }) {
    const { 
        questions, 
        currentQuestion, 
        currentIndex,
        totalQuestions,
        loading: questionsLoading,
        generateQuestions,
        nextQuestion,
        isLastQuestion 
    } = useQuestions(sessionId);
    
    const { 
        isRecording, 
        audioBlob, 
        duration,
        startRecording, 
        stopRecording,
        resetRecording 
    } = useAudioRecording();
    
    const [transcript, setTranscript] = useState('');
    const [evaluation, setEvaluation] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [step, setStep] = useState('question'); // question | recording | processing | evaluation
    
    // Generate questions on mount
    useEffect(() => {
        if (sessionId && questions.length === 0) {
            generateQuestions({
                num_questions: 5,
                categories: ['behavioral', 'technical'],
                skills: ['JavaScript', 'React']
            });
        }
    }, [sessionId, questions.length, generateQuestions]);
    
    // Process audio after recording
    const processResponse = async () => {
        if (!audioBlob || !currentQuestion) return;
        
        setProcessing(true);
        setStep('processing');
        
        try {
            // Step 1: Upload audio
            const uploadResult = await interviewApi.uploadAudio(
                sessionId,
                currentQuestion.id,
                audioBlob,
                duration
            );
            
            if (!uploadResult.success) {
                throw new Error('Failed to upload audio');
            }
            
            // Step 2: Transcribe
            const transcriptResult = await interviewApi.transcribeAudio(
                sessionId,
                currentQuestion.id,
                'en'
            );
            
            if (transcriptResult.success) {
                setTranscript(transcriptResult.data.transcript);
            }
            
            // Step 3: Evaluate
            const evalResult = await interviewApi.evaluateResponse(
                sessionId,
                currentQuestion.id,
                currentQuestion.expected_topics || []
            );
            
            if (evalResult.success) {
                setEvaluation(evalResult.data);
            }
            
            setStep('evaluation');
            
        } catch (error) {
            console.error('Processing error:', error);
            alert('Failed to process response');
            setStep('question');
        } finally {
            setProcessing(false);
        }
    };
    
    // Move to next question
    const handleNext = () => {
        setTranscript('');
        setEvaluation(null);
        resetRecording();
        setStep('question');
        nextQuestion();
    };
    
    if (questionsLoading) {
        return <div className="loading">Generating questions...</div>;
    }
    
    if (!currentQuestion) {
        return <div className="no-questions">No questions available</div>;
    }
    
    return (
        <div className="interview-session">
            {/* Progress indicator */}
            <div className="progress">
                Question {currentIndex + 1} of {totalQuestions}
            </div>
            
            {/* Question display */}
            <div className="question-card">
                <span className="category">{currentQuestion.category}</span>
                <h2>{currentQuestion.question_text}</h2>
                <p className="time-limit">
                    Time limit: {currentQuestion.time_limit} seconds
                </p>
            </div>
            
            {/* Recording controls */}
            {step === 'question' && (
                <div className="recording-controls">
                    {!isRecording ? (
                        <button onClick={startRecording} className="btn-record">
                            🎤 Start Recording
                        </button>
                    ) : (
                        <button onClick={stopRecording} className="btn-stop">
                            ⏹ Stop Recording ({duration}s)
                        </button>
                    )}
                    
                    {audioBlob && !isRecording && (
                        <div className="audio-preview">
                            <audio controls src={URL.createObjectURL(audioBlob)} />
                            <button onClick={processResponse} className="btn-submit">
                                Submit Response
                            </button>
                            <button onClick={resetRecording} className="btn-retry">
                                Re-record
                            </button>
                        </div>
                    )}
                </div>
            )}
            
            {/* Processing indicator */}
            {step === 'processing' && (
                <div className="processing">
                    <div className="spinner" />
                    <p>Processing your response...</p>
                </div>
            )}
            
            {/* Evaluation results */}
            {step === 'evaluation' && evaluation && (
                <div className="evaluation-results">
                    <h3>Evaluation Results</h3>
                    
                    <div className="scores">
                        <div className="score-item">
                            <span>Relevance</span>
                            <span>{evaluation.relevance_score}%</span>
                        </div>
                        <div className="score-item">
                            <span>Grammar</span>
                            <span>{evaluation.grammar_score}%</span>
                        </div>
                        <div className="score-item">
                            <span>Fluency</span>
                            <span>{evaluation.fluency_score}%</span>
                        </div>
                        <div className="score-item">
                            <span>Keywords</span>
                            <span>{evaluation.keyword_score}%</span>
                        </div>
                        <div className="score-item overall">
                            <span>Overall</span>
                            <span>{evaluation.overall_score}%</span>
                        </div>
                    </div>
                    
                    <div className="transcript">
                        <h4>Your Response:</h4>
                        <p>{transcript}</p>
                    </div>
                    
                    <div className="summary">
                        <h4>Summary:</h4>
                        <p>{evaluation.summary}</p>
                    </div>
                    
                    <button onClick={handleNext} className="btn-next">
                        {isLastQuestion ? 'Complete Interview' : 'Next Question →'}
                    </button>
                </div>
            )}
        </div>
    );
}

// =============================================================================
// DASHBOARD COMPONENT
// =============================================================================

/**
 * Dashboard Component
 * 
 * Displays user statistics and performance trends
 */
export function Dashboard() {
    const { stats, history, charts, loading, refresh } = useDashboard();
    
    if (loading) {
        return <div className="loading">Loading dashboard...</div>;
    }
    
    if (!stats) {
        return (
            <div className="empty-state">
                <h2>No data yet</h2>
                <p>Complete your first mock interview to see your progress!</p>
            </div>
        );
    }
    
    return (
        <div className="dashboard">
            <h1>Your Dashboard</h1>
            
            <button onClick={refresh} className="btn-refresh">
                🔄 Refresh
            </button>
            
            {/* Stats cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>{stats.total_interviews}</h3>
                    <p>Total Interviews</p>
                </div>
                <div className="stat-card">
                    <h3>{stats.average_score?.toFixed(1) || 0}%</h3>
                    <p>Average Score</p>
                </div>
                <div className="stat-card">
                    <h3>{stats.best_score?.toFixed(1) || 0}%</h3>
                    <p>Best Score</p>
                </div>
                <div className="stat-card">
                    <h3>{stats.improvement_rate?.toFixed(1) || 0}%</h3>
                    <p>Improvement</p>
                </div>
                <div className="stat-card">
                    <h3>{stats.current_streak}</h3>
                    <p>Current Streak</p>
                </div>
                <div className="stat-card">
                    <h3>{stats.total_practice_time} min</h3>
                    <p>Practice Time</p>
                </div>
            </div>
            
            {/* Skills breakdown */}
            {stats.skills_breakdown && (
                <div className="skills-section">
                    <h2>Skills Breakdown</h2>
                    <div className="skills-bars">
                        {Object.entries(stats.skills_breakdown).map(([skill, score]) => (
                            <div key={skill} className="skill-bar">
                                <div className="skill-label">
                                    <span>{skill}</span>
                                    <span>{score.toFixed(1)}%</span>
                                </div>
                                <div className="bar-bg">
                                    <div 
                                        className="bar-fill" 
                                        style={{ width: `${score}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            
            {/* Recent interviews */}
            <div className="history-section">
                <h2>Recent Interviews</h2>
                <div className="history-list">
                    {history.map((interview) => (
                        <div key={interview.id} className="history-item">
                            <div className="interview-info">
                                <h4>{interview.title}</h4>
                                <p>{new Date(interview.created_at).toLocaleDateString()}</p>
                            </div>
                            <div className="interview-score">
                                <span className="score">{interview.overall_score?.toFixed(1) || 'N/A'}%</span>
                                <span className="grade">{interview.letter_grade || '-'}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

// =============================================================================
// FEEDBACK COMPONENT
// =============================================================================

/**
 * Feedback Component
 * 
 * Displays comprehensive feedback for a completed session
 */
export function FeedbackDisplay({ sessionId }) {
    const { scores, feedback, loading, calculateScores, generateFeedback, loadFeedback } = useFeedback(sessionId);
    const [feedbackGenerated, setFeedbackGenerated] = useState(false);
    
    // Generate feedback on mount
    useEffect(() => {
        const generateAll = async () => {
            await calculateScores();
            await generateFeedback();
            setFeedbackGenerated(true);
        };
        
        if (sessionId && !feedbackGenerated) {
            generateAll();
        }
    }, [sessionId, feedbackGenerated, calculateScores, generateFeedback]);
    
    if (loading) {
        return <div className="loading">Generating feedback...</div>;
    }
    
    if (!feedback) {
        return <div className="no-feedback">No feedback available</div>;
    }
    
    return (
        <div className="feedback-display">
            <h1>Interview Feedback</h1>
            
            {/* Overall score */}
            {scores && (
                <div className="overall-score">
                    <div className="score-circle">
                        <span className="score">{scores.total_score?.toFixed(1)}</span>
                        <span className="max">/100</span>
                    </div>
                    <span className="grade">{scores.letter_grade}</span>
                </div>
            )}
            
            {/* Summary */}
            <div className="summary-section">
                <h2>{feedback.overall_rating}</h2>
                <p>{feedback.summary}</p>
            </div>
            
            {/* Readiness */}
            <div className="readiness-section">
                <h3>Interview Readiness</h3>
                <div className="readiness-meter">
                    <div 
                        className="readiness-fill" 
                        style={{ width: `${feedback.readiness_score}%` }}
                    />
                </div>
                <span>{feedback.readiness_level} ({feedback.readiness_score}%)</span>
            </div>
            
            {/* Strengths */}
            <div className="strengths-section">
                <h3>✅ Strengths</h3>
                <ul>
                    {feedback.strengths?.map((item, index) => (
                        <li key={index}>
                            <strong>{item.category}:</strong> {item.message}
                        </li>
                    ))}
                </ul>
            </div>
            
            {/* Weaknesses */}
            <div className="weaknesses-section">
                <h3>⚠️ Areas for Improvement</h3>
                <ul>
                    {feedback.weaknesses?.map((item, index) => (
                        <li key={index}>
                            <strong>{item.category}:</strong> {item.message}
                        </li>
                    ))}
                </ul>
            </div>
            
            {/* Suggestions */}
            <div className="suggestions-section">
                <h3>💡 Suggestions</h3>
                <ul>
                    {feedback.suggestions?.map((item, index) => (
                        <li key={index}>{item.message}</li>
                    ))}
                </ul>
            </div>
            
            {/* Next steps */}
            <div className="next-steps-section">
                <h3>📋 Next Steps</h3>
                <ol>
                    {feedback.next_steps?.map((step, index) => (
                        <li key={index}>{step}</li>
                    ))}
                </ol>
            </div>
            
            {/* Resources */}
            {feedback.resources?.length > 0 && (
                <div className="resources-section">
                    <h3>📚 Recommended Resources</h3>
                    <ul>
                        {feedback.resources.map((resource, index) => (
                            <li key={index}>
                                <a href={resource.url} target="_blank" rel="noopener noreferrer">
                                    {resource.title}
                                </a>
                                <span className="resource-type">({resource.type})</span>
                                <p>{resource.description}</p>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// =============================================================================
// EXPORTS
// =============================================================================

export default {
    LoginForm,
    InterviewSession,
    Dashboard,
    FeedbackDisplay,
};
