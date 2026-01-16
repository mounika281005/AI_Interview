/**
 * Feedback Page - Display interview results and feedback
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { feedbackApi, interviewApi } from '../api';

function FeedbackPage() {
    const { sessionId } = useParams();
    
    const [session, setSession] = useState(null);
    const [feedback, setFeedback] = useState(null);
    const [scores, setScores] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');
    
    useEffect(() => {
        const loadFeedback = async () => {
            setLoading(true);
            setError(null);
            
            try {
                // Load session details
                const sessionResult = await interviewApi.getSession(sessionId);
                if (sessionResult.success) {
                    setSession(sessionResult.data);
                }
                
                // Load feedback
                const feedbackResult = await feedbackApi.getSessionFeedback(sessionId);
                if (feedbackResult.success) {
                    setFeedback(feedbackResult.data);
                }
                
                // Load scores
                const scoresResult = await feedbackApi.getSessionScores(sessionId);
                if (scoresResult.success) {
                    setScores(scoresResult.data);
                }
                
            } catch (err) {
                setError('Failed to load feedback');
            }
            
            setLoading(false);
        };
        
        loadFeedback();
    }, [sessionId]);
    
    if (loading) {
        return (
            <div className="feedback-page">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading your feedback...</p>
                </div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="feedback-page">
                <div className="error-container">
                    <h2>Oops!</h2>
                    <p>{error}</p>
                    <Link to="/dashboard" className="btn btn-primary">
                        Back to Dashboard
                    </Link>
                </div>
            </div>
        );
    }
    
    return (
        <div className="feedback-page">
            {/* Header */}
            <header className="feedback-header">
                <div className="header-content">
                    <Link to="/dashboard" className="back-link">
                        ← Back to Dashboard
                    </Link>
                    <h1>{session?.title || 'Interview Feedback'}</h1>
                    <p className="session-meta">
                        {session?.target_role} • {session?.questions?.length || 0} questions • 
                        {new Date(session?.created_at).toLocaleDateString()}
                    </p>
                </div>
            </header>
            
            {/* Overall Score Card */}
            <section className="score-overview">
                <div className="main-score-card">
                    <div className="score-circle">
                        <svg viewBox="0 0 100 100">
                            <circle 
                                className="score-bg" 
                                cx="50" cy="50" r="45"
                            />
                            <circle 
                                className="score-progress"
                                cx="50" cy="50" r="45"
                                style={{
                                    strokeDasharray: `${(feedback?.readiness_score || 0) * 2.83} 283`
                                }}
                            />
                        </svg>
                        <div className="score-value">
                            <span className="score-number">{feedback?.readiness_score || 0}</span>
                            <span className="score-max">/100</span>
                        </div>
                    </div>
                    <div className="score-info">
                        <h2 className={`rating ${getRatingClass(feedback?.overall_rating)}`}>
                            {feedback?.overall_rating || 'Not Rated'}
                        </h2>
                        <p className="readiness-level">
                            Readiness: {feedback?.readiness_level || 'Unknown'}
                        </p>
                    </div>
                </div>
                
                {/* Category Scores */}
                <div className="category-scores">
                    {scores?.category_scores && Object.entries(scores.category_scores).map(([category, score]) => (
                        <div key={category} className="category-score-card">
                            <div className="category-header">
                                <span className="category-name">{formatCategory(category)}</span>
                                <span className="category-value">{Math.round(score)}%</span>
                            </div>
                            <div className="category-bar">
                                <div 
                                    className="category-fill"
                                    style={{ width: `${score}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </section>
            
            {/* Tabs */}
            <div className="feedback-tabs">
                <button 
                    className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    Overview
                </button>
                <button 
                    className={`tab ${activeTab === 'strengths' ? 'active' : ''}`}
                    onClick={() => setActiveTab('strengths')}
                >
                    Strengths & Weaknesses
                </button>
                <button 
                    className={`tab ${activeTab === 'questions' ? 'active' : ''}`}
                    onClick={() => setActiveTab('questions')}
                >
                    Question Details
                </button>
                <button 
                    className={`tab ${activeTab === 'next-steps' ? 'active' : ''}`}
                    onClick={() => setActiveTab('next-steps')}
                >
                    Next Steps
                </button>
            </div>
            
            {/* Tab Content */}
            <div className="tab-content">
                {activeTab === 'overview' && (
                    <div className="overview-tab">
                        <div className="summary-card">
                            <h3>Summary</h3>
                            <p>{feedback?.summary || 'No summary available.'}</p>
                        </div>
                        
                        {feedback?.suggestions && feedback.suggestions.length > 0 && (
                            <div className="suggestions-card">
                                <h3>Key Suggestions</h3>
                                <ul>
                                    {feedback.suggestions.map((suggestion, index) => (
                                        <li key={index}>
                                            <span className="suggestion-icon">💡</span>
                                            {suggestion.message || suggestion}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
                
                {activeTab === 'strengths' && (
                    <div className="strengths-tab">
                        <div className="strengths-section">
                            <h3>💪 Strengths</h3>
                            {feedback?.strengths && feedback.strengths.length > 0 ? (
                                <div className="feedback-list">
                                    {feedback.strengths.map((item, index) => (
                                        <div key={index} className="feedback-item strength">
                                            <span className="item-category">{item.category}</span>
                                            <p>{item.message}</p>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="empty-message">No specific strengths identified.</p>
                            )}
                        </div>
                        
                        <div className="weaknesses-section">
                            <h3>🎯 Areas to Improve</h3>
                            {feedback?.weaknesses && feedback.weaknesses.length > 0 ? (
                                <div className="feedback-list">
                                    {feedback.weaknesses.map((item, index) => (
                                        <div key={index} className="feedback-item weakness">
                                            <span className="item-category">{item.category}</span>
                                            <p>{item.message}</p>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="empty-message">No specific weaknesses identified.</p>
                            )}
                        </div>
                    </div>
                )}
                
                {activeTab === 'questions' && (
                    <div className="questions-tab">
                        <h3>Question-by-Question Breakdown</h3>
                        <div className="questions-list">
                            {session?.questions?.map((question, index) => (
                                <div key={question.id} className="question-feedback-card">
                                    <div className="question-header">
                                        <span className="question-number">Q{index + 1}</span>
                                        <span className={`category-badge ${question.category}`}>
                                            {question.category}
                                        </span>
                                    </div>
                                    <p className="question-text">{question.question_text}</p>
                                    
                                    {question.evaluation && (
                                        <div className="question-scores">
                                            <div className="score-item">
                                                <span>Relevance</span>
                                                <span>{Math.round(question.evaluation.relevance_score * 100)}%</span>
                                            </div>
                                            <div className="score-item">
                                                <span>Completeness</span>
                                                <span>{Math.round(question.evaluation.completeness_score * 100)}%</span>
                                            </div>
                                            <div className="score-item">
                                                <span>Grammar</span>
                                                <span>{Math.round(question.evaluation.grammar_score * 100)}%</span>
                                            </div>
                                        </div>
                                    )}
                                    
                                    {question.transcription && (
                                        <div className="transcription">
                                            <strong>Your Answer:</strong>
                                            <p>"{question.transcription}"</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                
                {activeTab === 'next-steps' && (
                    <div className="next-steps-tab">
                        <h3>Recommended Next Steps</h3>
                        {feedback?.next_steps && feedback.next_steps.length > 0 ? (
                            <div className="steps-list">
                                {feedback.next_steps.map((step, index) => (
                                    <div key={index} className="step-item">
                                        <span className="step-number">{index + 1}</span>
                                        <p>{step}</p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="empty-message">No specific next steps recommended.</p>
                        )}
                        
                        <div className="action-buttons">
                            <Link to="/interview" className="btn btn-primary">
                                Practice Again
                            </Link>
                            <Link to="/history" className="btn btn-outline">
                                View History
                            </Link>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function getRatingClass(rating) {
    const ratingLower = (rating || '').toLowerCase();
    if (ratingLower.includes('excellent')) return 'excellent';
    if (ratingLower.includes('good')) return 'good';
    if (ratingLower.includes('average')) return 'average';
    return 'needs-work';
}

function formatCategory(category) {
    return category
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
}

export default FeedbackPage;
