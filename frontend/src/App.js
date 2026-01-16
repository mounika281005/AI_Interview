/**
 * AI Mock Interview System - Main Application
 * React Router setup with protected routes
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useApiHooks';

// Import pages (we'll create these)
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import InterviewPage from './pages/InterviewPage';
import InterviewSessionPage from './pages/InterviewSessionPage';
import FeedbackPage from './pages/FeedbackPage';
import HistoryPage from './pages/HistoryPage';
import ProfilePage from './pages/ProfilePage';
import LandingPage from './pages/LandingPage';
import SkillInterviewPage from './pages/SkillInterviewPage';
import SkillInterviewResultsPage from './pages/SkillInterviewResultsPage';

// Import styles
import './styles/App.css';

// ============================================
// Protected Route Component
// ============================================
function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();
    
    if (loading) {
        return (
            <div className="loading-screen">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }
    
    if (!user) {
        return <Navigate to="/login" replace />;
    }
    
    return children;
}

// ============================================
// Public Route (redirect if already logged in)
// ============================================
function PublicRoute({ children }) {
    const { user, loading } = useAuth();
    
    if (loading) {
        return (
            <div className="loading-screen">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }
    
    if (user) {
        return <Navigate to="/dashboard" replace />;
    }
    
    return children;
}

// ============================================
// Navigation Bar Component
// ============================================
function Navbar() {
    const { user, logout } = useAuth();
    
    const handleLogout = async () => {
        await logout();
    };
    
    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-brand">
                    <span className="brand-icon">🎯</span>
                    <span className="brand-text">AI Interview</span>
                </Link>
                
                <div className="navbar-menu">
                    {user ? (
                        <>
                            <Link to="/dashboard" className="nav-link">Dashboard</Link>
                            <Link to="/skill-interview" className="nav-link">Skill Interview</Link>
                            <Link to="/interview" className="nav-link">Practice</Link>
                            <Link to="/history" className="nav-link">History</Link>
                            <Link to="/profile" className="nav-link">
                                <span className="user-avatar">
                                    {user.full_name?.charAt(0).toUpperCase() || 'U'}
                                </span>
                                {user.full_name?.split(' ')[0] || 'Profile'}
                            </Link>
                            <button onClick={handleLogout} className="nav-button logout-btn">
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-link">Login</Link>
                            <Link to="/register" className="nav-button primary-btn">
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}

// ============================================
// Footer Component
// ============================================
function Footer() {
    return (
        <footer className="footer">
            <div className="footer-container">
                <div className="footer-content">
                    <div className="footer-section">
                        <h4>AI Mock Interview</h4>
                        <p>Practice interviews with AI-powered feedback</p>
                    </div>
                    <div className="footer-section">
                        <h4>Quick Links</h4>
                        <Link to="/interview">Start Practice</Link>
                        <Link to="/dashboard">Dashboard</Link>
                        <Link to="/history">History</Link>
                    </div>
                    <div className="footer-section">
                        <h4>Resources</h4>
                        <a href="#tips">Interview Tips</a>
                        <a href="#faq">FAQ</a>
                        <a href="#contact">Contact</a>
                    </div>
                </div>
                <div className="footer-bottom">
                    <p>&copy; 2026 AI Mock Interview System. Final Year Project.</p>
                </div>
            </div>
        </footer>
    );
}

// ============================================
// Layout Component
// ============================================
function Layout({ children, showFooter = true }) {
    return (
        <div className="app-layout">
            <Navbar />
            <main className="main-content">
                {children}
            </main>
            {showFooter && <Footer />}
        </div>
    );
}

// ============================================
// Main App Component
// ============================================
function AppContent() {
    return (
        <Routes>
            {/* Public Routes */}
            <Route 
                path="/" 
                element={
                    <Layout>
                        <LandingPage />
                    </Layout>
                } 
            />
            
            <Route 
                path="/login" 
                element={
                    <PublicRoute>
                        <Layout showFooter={false}>
                            <LoginPage />
                        </Layout>
                    </PublicRoute>
                } 
            />
            
            <Route 
                path="/register" 
                element={
                    <PublicRoute>
                        <Layout showFooter={false}>
                            <RegisterPage />
                        </Layout>
                    </PublicRoute>
                } 
            />
            
            {/* Protected Routes */}
            <Route 
                path="/dashboard" 
                element={
                    <ProtectedRoute>
                        <Layout>
                            <DashboardPage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            <Route 
                path="/interview" 
                element={
                    <ProtectedRoute>
                        <Layout>
                            <InterviewPage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            <Route 
                path="/interview/:sessionId" 
                element={
                    <ProtectedRoute>
                        <Layout showFooter={false}>
                            <InterviewSessionPage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            <Route 
                path="/feedback/:sessionId" 
                element={
                    <ProtectedRoute>
                        <Layout>
                            <FeedbackPage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            <Route 
                path="/history" 
                element={
                    <ProtectedRoute>
                        <Layout>
                            <HistoryPage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            <Route 
                path="/skill-interview" 
                element={
                    <ProtectedRoute>
                        <Layout showFooter={false}>
                            <SkillInterviewPage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            <Route 
                path="/skill-interview/results/:sessionId" 
                element={
                    <ProtectedRoute>
                        <Layout showFooter={false}>
                            <SkillInterviewResultsPage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            <Route 
                path="/profile" 
                element={
                    <ProtectedRoute>
                        <Layout>
                            <ProfilePage />
                        </Layout>
                    </ProtectedRoute>
                } 
            />
            
            {/* 404 Route */}
            <Route 
                path="*" 
                element={
                    <Layout>
                        <div className="not-found-page">
                            <h1>404</h1>
                            <p>Page not found</p>
                            <Link to="/" className="btn btn-primary">Go Home</Link>
                        </div>
                    </Layout>
                } 
            />
        </Routes>
    );
}

// ============================================
// Root App with Providers
// ============================================
function App() {
    return (
        <Router>
            <AuthProvider>
                <AppContent />
            </AuthProvider>
        </Router>
    );
}

export default App;
