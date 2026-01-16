/**
 * History Page - List of all past interview sessions
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { feedbackApi } from '../api';

function HistoryPage() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [sortBy, setSortBy] = useState('date');
    
    useEffect(() => {
        const loadHistory = async () => {
            setLoading(true);
            const result = await feedbackApi.getHistory();
            
            if (result.success) {
                // API returns { interviews: [...] } or similar structures
                const data = result.data;
                const sessionsList = data.interviews || data.sessions || data.items || data || [];
                setSessions(Array.isArray(sessionsList) ? sessionsList : []);
            }
            
            setLoading(false);
        };
        
        loadHistory();
    }, []);
    
    // Filter sessions
    const filteredSessions = sessions.filter(session => {
        if (filter === 'all') return true;
        if (filter === 'completed') return session.status === 'completed';
        if (filter === 'in-progress') return session.status !== 'completed';
        return true;
    });
    
    // Sort sessions
    const sortedSessions = [...filteredSessions].sort((a, b) => {
        if (sortBy === 'date') {
            return new Date(b.created_at) - new Date(a.created_at);
        }
        if (sortBy === 'score') {
            return (b.overall_score || 0) - (a.overall_score || 0);
        }
        return 0;
    });
    
    if (loading) {
        return (
            <div className="history-page">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading your history...</p>
                </div>
            </div>
        );
    }
    
    return (
        <div className="history-page">
            <header className="history-header">
                <h1>Practice History</h1>
                <p>Review your past interview sessions and track your progress</p>
            </header>
            
            {/* Filters */}
            <div className="history-filters">
                <div className="filter-group">
                    <label>Filter:</label>
                    <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                        <option value="all">All Sessions</option>
                        <option value="completed">Completed</option>
                        <option value="in-progress">In Progress</option>
                    </select>
                </div>
                
                <div className="filter-group">
                    <label>Sort by:</label>
                    <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                        <option value="date">Most Recent</option>
                        <option value="score">Highest Score</option>
                    </select>
                </div>
                
                <div className="session-count">
                    {sortedSessions.length} session{sortedSessions.length !== 1 ? 's' : ''}
                </div>
            </div>
            
            {/* Sessions List */}
            {sortedSessions.length > 0 ? (
                <div className="sessions-grid">
                    {sortedSessions.map(session => (
                        <div key={session.id} className="history-card">
                            <div className="card-header">
                                <h3>{session.title}</h3>
                                <span className={`status-badge ${session.status}`}>
                                    {session.status}
                                </span>
                            </div>
                            
                            <div className="card-meta">
                                <span className="meta-item">
                                    🎯 {session.target_role}
                                </span>
                                <span className="meta-item">
                                    📝 {session.questions_count || 0} questions
                                </span>
                                <span className="meta-item">
                                    📅 {formatDate(session.created_at)}
                                </span>
                            </div>
                            
                            {session.status === 'completed' && (
                                <div className="card-score">
                                    <div className="score-bar">
                                        <div 
                                            className="score-fill"
                                            style={{ width: `${session.overall_score || 0}%` }}
                                        />
                                    </div>
                                    <span className={`score-value ${getScoreClass(session.overall_score)}`}>
                                        {session.overall_score || 0}%
                                    </span>
                                </div>
                            )}
                            
                            <div className="card-actions">
                                {session.status === 'completed' ? (
                                    <Link 
                                        to={`/feedback/${session.id}`}
                                        className="btn btn-primary"
                                    >
                                        View Feedback
                                    </Link>
                                ) : (
                                    <Link 
                                        to={`/interview/${session.id}`}
                                        className="btn btn-outline"
                                    >
                                        Continue
                                    </Link>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <div className="empty-icon">📋</div>
                    <h2>No sessions yet</h2>
                    <p>Start your first practice interview to see your history here.</p>
                    <Link to="/interview" className="btn btn-primary">
                        Start Practicing
                    </Link>
                </div>
            )}
        </div>
    );
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // Less than 24 hours
    if (diff < 86400000) {
        return 'Today';
    }
    // Less than 48 hours
    if (diff < 172800000) {
        return 'Yesterday';
    }
    // Less than 7 days
    if (diff < 604800000) {
        return `${Math.floor(diff / 86400000)} days ago`;
    }
    
    return date.toLocaleDateString();
}

function getScoreClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'needs-work';
}

export default HistoryPage;
