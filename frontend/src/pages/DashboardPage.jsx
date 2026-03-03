/**
 * Dashboard Page Component
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth, useDashboard } from '../hooks/useApiHooks';

function DashboardPage() {
    const { user } = useAuth();
    const { stats, history, charts, loading, error, refresh } = useDashboard();
    
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
                    {(user?.resume_url || user?.resume_data) ? (
                        <Link to="/skill-interview?type=resume" className="action-card featured">
                            <span className="action-icon">📄</span>
                            <span className="action-title">Resume Interview</span>
                            <span className="action-desc">Personalized questions</span>
                            <span className="featured-badge">✨ New</span>
                        </Link>
                    ) : (
                        <Link to="/profile" state={{ redirectToResumeInterview: true }} className="action-card featured">
                            <span className="action-icon">📄</span>
                            <span className="action-title">Resume Interview</span>
                            <span className="action-desc">Upload resume to start</span>
                            <span className="featured-badge">✨ New</span>
                        </Link>
                    )}
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
                        {history.slice(0, 5).map(session => {
                            const sessionId = session.id || session.session_id;
                            const score = session.overall_score || session.total_score || 0;
                            const role = session.target_role || session.job_role || 'Interview';
                            return (
                                <div key={sessionId} className="session-item">
                                    <div className="session-info">
                                        <h4>{session.title || `${role} Interview`}</h4>
                                        <p>
                                            {role} • {session.questions_count || 0} questions
                                        </p>
                                        <span className="session-date">
                                            {new Date(session.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="session-score">
                                        <span className={`score ${getScoreClass(score)}`}>
                                            {Math.round(score)}%
                                        </span>
                                    </div>
                                    <Link
                                        to={`/feedback/${sessionId}`}
                                        className="btn btn-small btn-outline"
                                    >
                                        View Feedback
                                    </Link>
                                </div>
                            );
                        })}
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
            
            {/* Progress Chart - Real Data */}
            <section className="progress-section">
                <div className="section-header">
                    <h2>Your Progress</h2>
                    {stats?.performance_trend && (
                        <span className={`trend-badge trend-${stats.performance_trend}`}>
                            {stats.performance_trend === 'improving' ? '📈 Improving' :
                             stats.performance_trend === 'declining' ? '📉 Declining' :
                             '➡️ Stable'}
                            {stats.improvement_percentage ? ` (${stats.improvement_percentage > 0 ? '+' : ''}${Math.round(stats.improvement_percentage)}%)` : ''}
                        </span>
                    )}
                </div>
                {(() => {
                    const chartData = charts?.score_trend?.datasets?.[0]?.data || [];
                    const chartLabels = charts?.score_trend?.labels || [];

                    if (chartData.length === 0) {
                        return (
                            <div className="empty-state">
                                <p>No progress data yet. Complete some interview sessions to see your scores here!</p>
                                <Link to="/interview" className="btn btn-primary">
                                    Start Practicing
                                </Link>
                            </div>
                        );
                    }

                    return (
                        <div className="chart-placeholder">
                            <div className="chart-bars">
                                {chartData.map((value, index) => (
                                    <div
                                        key={index}
                                        className={`chart-bar ${getScoreClass(value)}`}
                                        style={{ height: `${Math.max(value, 5)}%` }}
                                        title={`${chartLabels[index] || ''}: ${Math.round(value)}%`}
                                    >
                                        <span className="bar-value">{Math.round(value)}%</span>
                                    </div>
                                ))}
                            </div>
                            <div className="chart-labels">
                                {chartLabels.map((label, index) => (
                                    <span key={index}>{label}</span>
                                ))}
                            </div>
                        </div>
                    );
                })()}

                {/* Score Summary */}
                {stats && stats.average_score > 0 && (
                    <div className="score-summary">
                        <div className="summary-item">
                            <span className="summary-label">Best Score</span>
                            <span className={`summary-value ${getScoreClass(stats.best_score)}`}>
                                {Math.round(stats.best_score)}%
                            </span>
                        </div>
                        <div className="summary-item">
                            <span className="summary-label">Average</span>
                            <span className={`summary-value ${getScoreClass(stats.average_score)}`}>
                                {Math.round(stats.average_score)}%
                            </span>
                        </div>
                        <div className="summary-item">
                            <span className="summary-label">Target</span>
                            <span className="summary-value">{Math.round(stats.target_score || 85)}%</span>
                        </div>
                        <div className="summary-item">
                            <span className="summary-label">Progress to Target</span>
                            <span className="summary-value">
                                {Math.round(stats.progress_to_target || 0)}%
                            </span>
                        </div>
                    </div>
                )}

                {/* Category Breakdown */}
                {stats?.category_scores && Object.keys(stats.category_scores).length > 0 && (
                    <div className="category-breakdown">
                        <h3>Score by Category</h3>
                        <div className="category-bars">
                            {Object.entries(stats.category_scores).map(([category, score]) => (
                                <div key={category} className="category-bar-item">
                                    <div className="category-bar-header">
                                        <span className="category-name">{category}</span>
                                        <span className={`category-score ${getScoreClass(score)}`}>
                                            {Math.round(score)}%
                                        </span>
                                    </div>
                                    <div className="category-bar-track">
                                        <div
                                            className={`category-bar-fill ${getScoreClass(score)}`}
                                            style={{ width: `${score}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
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
