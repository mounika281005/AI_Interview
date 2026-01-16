/**
 * Dashboard Page Component
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth, useDashboard } from '../hooks/useApiHooks';

function DashboardPage() {
    const { user } = useAuth();
    const { stats, history, loading, error, refresh } = useDashboard();
    
    if (loading) {
        return (
            <div className="dashboard-page">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading your dashboard...</p>
                </div>
            </div>
        );
    }
    
    return (
        <div className="dashboard-page">
            {/* Welcome Section */}
            <section className="dashboard-header">
                <div className="welcome-message">
                    <h1>Welcome back, {user?.full_name?.split(' ')[0] || 'User'}! 👋</h1>
                    <p>Ready to practice your interview skills today?</p>
                </div>
                <Link to="/interview" className="btn btn-primary">
                    Start New Practice
                </Link>
            </section>
            
            {error && (
                <div className="alert alert-error">
                    <span>Failed to load dashboard data.</span>
                    <button onClick={refresh} className="btn btn-small">
                        Retry
                    </button>
                </div>
            )}
            
            {/* Stats Cards */}
            <section className="stats-cards">
                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats?.total_sessions || 0}</span>
                        <span className="stat-label">Total Sessions</span>
                    </div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-icon">⏱️</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats?.total_practice_minutes || 0}</span>
                        <span className="stat-label">Minutes Practiced</span>
                    </div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-icon">📈</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats?.average_score || 0}%</span>
                        <span className="stat-label">Average Score</span>
                    </div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-icon">🔥</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats?.current_streak || 0}</span>
                        <span className="stat-label">Day Streak</span>
                    </div>
                </div>
            </section>
            
            {/* Quick Actions */}
            <section className="quick-actions">
                <h2>Quick Actions</h2>
                <div className="actions-grid">
                    <Link to="/interview?type=behavioral" className="action-card">
                        <span className="action-icon">💭</span>
                        <span className="action-title">Behavioral</span>
                        <span className="action-desc">Practice STAR method</span>
                    </Link>
                    <Link to="/interview?type=technical" className="action-card">
                        <span className="action-icon">💻</span>
                        <span className="action-title">Technical</span>
                        <span className="action-desc">Coding & concepts</span>
                    </Link>
                    <Link to="/interview?type=situational" className="action-card">
                        <span className="action-icon">🎯</span>
                        <span className="action-title">Situational</span>
                        <span className="action-desc">Problem solving</span>
                    </Link>
                    <Link to="/interview?type=hr" className="action-card">
                        <span className="action-icon">🤝</span>
                        <span className="action-title">HR Round</span>
                        <span className="action-desc">Salary & culture</span>
                    </Link>
                </div>
            </section>
            
            {/* Recent Sessions */}
            <section className="recent-sessions">
                <div className="section-header">
                    <h2>Recent Sessions</h2>
                    <Link to="/history" className="view-all-link">View All →</Link>
                </div>
                
                {history && history.length > 0 ? (
                    <div className="sessions-list">
                        {history.slice(0, 5).map(session => (
                            <div key={session.id} className="session-item">
                                <div className="session-info">
                                    <h4>{session.title}</h4>
                                    <p>
                                        {session.target_role} • {session.questions_count} questions
                                    </p>
                                    <span className="session-date">
                                        {new Date(session.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <div className="session-score">
                                    <span className={`score ${getScoreClass(session.overall_score)}`}>
                                        {session.overall_score || 0}%
                                    </span>
                                </div>
                                <Link 
                                    to={`/feedback/${session.id}`} 
                                    className="btn btn-small btn-outline"
                                >
                                    View Feedback
                                </Link>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>No practice sessions yet. Start your first one!</p>
                        <Link to="/interview" className="btn btn-primary">
                            Start Practicing
                        </Link>
                    </div>
                )}
            </section>
            
            {/* Progress Chart Placeholder */}
            <section className="progress-section">
                <h2>Your Progress</h2>
                <div className="chart-placeholder">
                    <div className="chart-bars">
                        {[65, 72, 68, 75, 80, 78, 85].map((value, index) => (
                            <div 
                                key={index}
                                className="chart-bar"
                                style={{ height: `${value}%` }}
                            >
                                <span className="bar-value">{value}%</span>
                            </div>
                        ))}
                    </div>
                    <div className="chart-labels">
                        <span>Mon</span>
                        <span>Tue</span>
                        <span>Wed</span>
                        <span>Thu</span>
                        <span>Fri</span>
                        <span>Sat</span>
                        <span>Sun</span>
                    </div>
                </div>
            </section>
        </div>
    );
}

function getScoreClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'needs-work';
}

export default DashboardPage;
