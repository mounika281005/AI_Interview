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
                } else {
                    setError('Session not found');
                    setLoading(false);
                    return;
                }

                // Try loading existing scores, generate if not found
                let scoresResult = await feedbackApi.getScores(sessionId);
                if (!scoresResult.success) {
                    // Scores don't exist yet — try to calculate them
                    scoresResult = await feedbackApi.calculateScores(sessionId);
                }
                if (scoresResult.success) {
                    setScores(scoresResult.data);
                }

                // Try loading existing feedback, generate if not found
                let feedbackResult = await feedbackApi.getFeedback(sessionId);
                if (!feedbackResult.success && scoresResult.success) {
                    // Feedback doesn't exist yet — try to generate it
                    feedbackResult = await feedbackApi.generateFeedback(sessionId);
                }
                if (feedbackResult.success) {
                    setFeedback(feedbackResult.data);
                }

                // If neither scores nor feedback could be loaded or generated
                if (!scoresResult.success && !feedbackResult.success) {
                    setError('Feedback has not been generated for this session yet. Please complete and submit all answers first.');
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
                        {session?.job_role || session?.target_role} • {session?.questions?.length || 0} questions • 
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
                                    strokeDasharray: `${(feedback?.job_readiness_score || scores?.total_score || session?.overall_score || 0) * 2.83} 283`
                                }}
                            />
                        </svg>
                        <div className="score-value">
                            <span className="score-number">
                                {Math.round(feedback?.job_readiness_score || scores?.total_score || session?.overall_score || 0)}
                            </span>
                            <span className="score-max">/100</span>
                        </div>
                    </div>
                    <div className="score-info">
                        <h2 className={`rating ${getRatingClass(feedback?.performance_rating || scores?.grade)}`}>
                            {feedback?.performance_rating || scores?.grade || 'Not Rated'}
                        </h2>
                        <p className="readiness-level">
                            Readiness: {feedback?.readiness_level || 'Unknown'}
                        </p>
                    </div>
                </div>

                {/* Category Scores */}
                <div className="category-scores">
                    {scores?.section_scores && scores.section_scores.map((section) => (
                        <div key={section.section_name} className="category-score-card">
                            <div className="category-header">
                                <span className="category-name">{section.section_name}</span>
                                <span className="category-value">{Math.round(section.score)}%</span>
                            </div>
                            <div className="category-bar">
                                <div
                                    className="category-fill"
                                    style={{ width: `${section.score}%` }}
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
                            <p>{feedback?.executive_summary || 'No summary available.'}</p>
                        </div>

                        {feedback?.suggestions && feedback.suggestions.length > 0 && (
                            <div className="suggestions-card">
                                <h3>Key Suggestions</h3>
                                <ul>
                                    {feedback.suggestions.map((suggestion, index) => (
                                        <li key={index}>
                                            <span className="suggestion-icon">💡</span>
                                            {suggestion.suggestion || suggestion.message || suggestion}
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
                                            <span className="item-category">{item.area}</span>
                                            <p>{item.description}</p>
                                            {item.examples && item.examples.length > 0 && (
                                                <ul className="examples-list">
                                                    {item.examples.map((example, i) => (
                                                        <li key={i}>{example}</li>
                                                    ))}
                                                </ul>
                                            )}
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
                                            <span className="item-category">{item.area}</span>
                                            <p>{item.description}</p>
                                            {item.impact && (
                                                <span className={`impact-badge ${item.impact}`}>
                                                    Impact: {item.impact}
                                                </span>
                                            )}
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
                                    
                                    {question.is_evaluated && (
                                        <div className="question-scores">
                                            <div className="score-item">
                                                <span>Relevance</span>
                                                <span>{Math.round(question.relevance_score || 0)}%</span>
                                            </div>
                                            <div className="score-item">
                                                <span>Fluency</span>
                                                <span>{Math.round(question.fluency_score || 0)}%</span>
                                            </div>
                                            <div className="score-item">
                                                <span>Grammar</span>
                                                <span>{Math.round(question.grammar_score || 0)}%</span>
                                            </div>
                                            <div className="score-item">
                                                <span>Keywords</span>
                                                <span>{Math.round(question.keyword_score || 0)}%</span>
                                            </div>
                                            <div className="score-item overall">
                                                <span>Overall</span>
                                                <span>{Math.round(question.overall_score || 0)}%</span>
                                            </div>
                                        </div>
                                    )}

                                    <div className="transcription">
                                        <strong>Your Answer:</strong>
                                        {question.transcript ? (
                                            <p>"{question.transcript}"</p>
                                        ) : (
                                            <p className="no-response"><em>No response recorded</em></p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                
                {activeTab === 'next-steps' && (
                    <div className="next-steps-tab">
                        <h3>Recommended Next Steps</h3>

                        {feedback?.practice_topics && feedback.practice_topics.length > 0 && (
                            <div className="practice-topics-section">
                                <h4>Topics to Practice</h4>
                                <div className="topics-list">
                                    {feedback.practice_topics.map((topic, index) => (
                                        <div key={index} className="topic-item">
                                            <span className="topic-number">{index + 1}</span>
                                            <p>{topic}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {feedback?.recommended_resources && feedback.recommended_resources.length > 0 && (
                            <div className="resources-section">
                                <h4>Recommended Resources</h4>
                                <div className="resources-list">
                                    {feedback.recommended_resources.map((resource, index) => (
                                        <div key={index} className="resource-item">
                                            <strong>{resource.title || resource.name}</strong>
                                            {resource.description && <p>{resource.description}</p>}
                                            {resource.url && (
                                                <a href={resource.url} target="_blank" rel="noopener noreferrer">
                                                    Visit Resource →
                                                </a>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {(!feedback?.practice_topics || feedback.practice_topics.length === 0) &&
                         (!feedback?.recommended_resources || feedback.recommended_resources.length === 0) && (
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

export default FeedbackPage;
