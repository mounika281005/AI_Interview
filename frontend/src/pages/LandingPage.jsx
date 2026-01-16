/**
 * Landing Page - Welcome page for new visitors
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useApiHooks';

// Use public folder images via URL path (not import)
const bgimage = '/images/images.jpg';

function LandingPage() {
    const { user } = useAuth();
    
    return (
        <div className="landing-page">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        Master Your <span className="highlight">Interview Skills</span>
                        <br />with AI-Powered Practice
                    </h1>
                    <p className="hero-subtitle">
                        Practice mock interviews anytime, anywhere. Get instant AI feedback 
                        on your responses, improve your confidence, and land your dream job.
                    </p>
                    <div className="hero-actions">
                        {user ? (
                            <Link to="/interview" className="btn btn-primary btn-large">
                                Start Practicing
                            </Link>
                        ) : (
                            <>
                                <Link to="/register" className="btn btn-primary btn-large">
                                    Get Started Free
                                </Link>
                                <Link to="/login" className="btn btn-outline btn-large">
                                    Sign In
                                </Link>
                            </>
                        )}
                    </div>
                </div>
                <div className="hero-image">
                    <div className="hero-illustration">
                        <div className="illustration-circle"></div>
                        <img src={bgimage} alt="Interview illustration" className="illustration-icon" />
                    </div>
                </div>
            </section>
            
            {/* Features Section */}
            <section className="features-section">
                <h2 className="section-title">How It Works</h2>
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">📝</div>
                        <h3>Choose Your Interview</h3>
                        <p>Select your target role, company, and difficulty level for personalized questions.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">🎤</div>
                        <h3>Record Your Answers</h3>
                        <p>Speak your responses naturally. Our AI converts speech to text automatically.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">🤖</div>
                        <h3>Get AI Analysis</h3>
                        <p>Receive instant feedback on relevance, grammar, confidence, and more.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">📈</div>
                        <h3>Track Progress</h3>
                        <p>View your improvement over time with detailed analytics and insights.</p>
                    </div>
                </div>
            </section>
            
            {/* Stats Section */}
            <section className="stats-section">
                <div className="stats-grid">
                    <div className="stat-item">
                        <span className="stat-number">1000+</span>
                        <span className="stat-label">Practice Sessions</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">85%</span>
                        <span className="stat-label">Avg. Improvement</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">50+</span>
                        <span className="stat-label">Question Categories</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">4.8★</span>
                        <span className="stat-label">User Rating</span>
                    </div>
                </div>
            </section>
            
            {/* CTA Section */}
            <section className="cta-section">
                <h2>Ready to Ace Your Next Interview?</h2>
                <p>Join thousands of job seekers who improved their interview skills with our AI coach.</p>
                <Link to="/register" className="btn btn-primary btn-large">
                    Start Free Practice
                </Link>
            </section>
        </div>
    );
}

export default LandingPage;
