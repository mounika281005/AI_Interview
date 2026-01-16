/**
 * ==============================================================================
 * AI Mock Interview System - Interview Results Page
 * ==============================================================================
 * 
 * View detailed results for a specific interview from history.
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import skillInterviewApi from '../api/skillInterviewApi';
import '../styles/SkillInterview.css';

function SkillInterviewResultsPage() {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedQuestion, setExpandedQuestion] = useState(null);
    
    useEffect(() => {
        const loadResults = async () => {
            setLoading(true);
            const result = await skillInterviewApi.getResults(sessionId);
            
            if (result.success) {
                setResults(result.data);
            } else {
                setError(result.error?.message || 'Failed to load results');
            }
            setLoading(false);
        };
        
        loadResults();
    }, [sessionId]);
    
    const getScoreColor = (score, max = 5) => {
        const percentage = (score / max) * 100;
        if (percentage >= 80) return 'excellent';
        if (percentage >= 60) return 'good';
        if (percentage >= 40) return 'average';
        return 'poor';
    };
    
    const renderScoreBar = (score, max, label) => (
        <div className="score-bar-container">
            <div className="score-label">{label}</div>
            <div className="score-bar">
                <div 
                    className={`score-fill ${getScoreColor(score, max)}`}
                    style={{ width: `${(score / max) * 100}%` }}
                />
            </div>
            <div className="score-value">{score.toFixed(1)}/{max}</div>
        </div>
    );
    
    if (loading) {
        return (
            <div className="skill-interview-page">
                <div className="loading-container">
                    <div className="spinner large"></div>
                    <p>Loading results...</p>
                </div>
            </div>
        );
    }
    
    if (error || !results) {
        return (
            <div className="skill-interview-page">
                <div className="error-container">
                    <h2>❌ Error</h2>
                    <p>{error || 'Results not found'}</p>
                    <Link to="/history" className="new-interview-btn">
                        ← Back to History
                    </Link>
                </div>
            </div>
        );
    }
    
    return (
        <div className="skill-interview-page">
            <div className="interview-results">
                {/* Header */}
                <div className="results-header">
                    <div className="results-title">
                        <Link to="/history" className="back-link">← Back to History</Link>
                        <h1>📊 Interview Results</h1>
                        <p>{results.technology} - {results.difficulty}</p>
                    </div>
                    
                    <div className={`grade-circle ${getScoreColor(results.percentage_score, 100)}`}>
                        <span className="grade">{results.grade}</span>
                        <span className="percentage">{results.percentage_score.toFixed(0)}%</span>
                    </div>
                </div>
                
                {/* Total Score */}
                <div className="total-score-section">
                    <h2>📊 Overall Score</h2>
                    <div className="total-score">
                        <span className="score">{results.total_score.toFixed(1)}</span>
                        <span className="max">/ {results.max_possible_score.toFixed(1)}</span>
                    </div>
                    <p className="performance-summary">{results.performance_summary}</p>
                </div>
                
                {/* Category Scores */}
                <div className="category-scores">
                    <h3>Score Breakdown</h3>
                    {renderScoreBar(results.total_grammar_score, results.question_scores.length * 5, '📝 Grammar')}
                    {renderScoreBar(results.total_fluency_score, results.question_scores.length * 5, '🗣️ Fluency')}
                    {renderScoreBar(results.total_structure_score, results.question_scores.length * 5, '🏗️ Structure')}
                    {renderScoreBar(results.total_similarity_score, results.question_scores.length * 5, '🎯 Accuracy')}
                </div>
                
                {/* Overall Feedback */}
                <div className="overall-feedback">
                    <div className="strengths-section">
                        <h3>💪 Strengths</h3>
                        <ul>
                            {results.overall_strengths.map((strength, i) => (
                                <li key={i}>{strength}</li>
                            ))}
                        </ul>
                    </div>
                    
                    <div className="improvements-section">
                        <h3>📈 Areas for Improvement</h3>
                        <ul>
                            {results.overall_improvements.map((improvement, i) => (
                                <li key={i}>{improvement}</li>
                            ))}
                        </ul>
                    </div>
                </div>
                
                {/* Question-wise Results */}
                <div className="question-results">
                    <h2>📋 Question-wise Results</h2>
                    
                    {results.question_scores.map((qs, index) => (
                        <div 
                            key={qs.question_id}
                            className={`question-result-card ${expandedQuestion === qs.question_id ? 'expanded' : ''}`}
                        >
                            <div 
                                className="question-result-header"
                                onClick={() => setExpandedQuestion(
                                    expandedQuestion === qs.question_id ? null : qs.question_id
                                )}
                            >
                                <div className="question-info">
                                    <span className="q-number">Q{qs.question_number}</span>
                                    <span className="q-text">{qs.question_text}</span>
                                </div>
                                <div className={`q-score ${getScoreColor(qs.overall_score)}`}>
                                    {qs.overall_score.toFixed(1)}/5
                                </div>
                            </div>
                            
                            {expandedQuestion === qs.question_id && (
                                <div className="question-result-details">
                                    {/* Your Answer */}
                                    <div className="answer-section">
                                        <h4>Your Answer:</h4>
                                        <p className="transcript">{qs.transcript || '[No transcript available]'}</p>
                                    </div>
                                    
                                    {/* Score Breakdown */}
                                    <div className="score-breakdown">
                                        <h4>Score Breakdown:</h4>
                                        <div className="mini-scores">
                                            <div className="mini-score">
                                                <span>Grammar</span>
                                                <span className={getScoreColor(qs.grammar_score)}>{qs.grammar_score.toFixed(1)}/5</span>
                                            </div>
                                            <div className="mini-score">
                                                <span>Fluency</span>
                                                <span className={getScoreColor(qs.fluency_score)}>{qs.fluency_score.toFixed(1)}/5</span>
                                            </div>
                                            <div className="mini-score">
                                                <span>Structure</span>
                                                <span className={getScoreColor(qs.structure_score)}>{qs.structure_score.toFixed(1)}/5</span>
                                            </div>
                                            <div className="mini-score">
                                                <span>Accuracy</span>
                                                <span className={getScoreColor(qs.similarity_score)}>{qs.similarity_score.toFixed(1)}/5</span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {/* Feedback */}
                                    <div className="feedback-section">
                                        {qs.strengths && qs.strengths.length > 0 && (
                                            <div className="q-strengths">
                                                <h4>✅ Strengths:</h4>
                                                <ul>
                                                    {qs.strengths.map((s, i) => <li key={i}>{s}</li>)}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        {qs.improvements && qs.improvements.length > 0 && (
                                            <div className="q-improvements">
                                                <h4>💡 Improvements:</h4>
                                                <ul>
                                                    {qs.improvements.map((imp, idx) => <li key={idx}>{imp}</li>)}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {/* Ideal Answer */}
                                    {qs.ideal_answer && (
                                        <div className="ideal-answer-section">
                                            <h4>📖 Ideal Answer:</h4>
                                            <p className="ideal-answer">{qs.ideal_answer}</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
                
                {/* Actions */}
                <div className="results-actions">
                    <button 
                        className="new-interview-btn" 
                        onClick={() => navigate('/skill-interview')}
                    >
                        🔄 Start New Interview
                    </button>
                    <button 
                        className="history-btn" 
                        onClick={() => navigate('/history')}
                    >
                        📚 View History
                    </button>
                </div>
            </div>
        </div>
    );
}

export default SkillInterviewResultsPage;
