/**
 * Login Page Component
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useApiHooks';

function LoginPage() {
    const navigate = useNavigate();
    const { login } = useAuth();
    
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setError(null);
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        
        const result = await login(formData.email, formData.password);
        
        setLoading(false);
        
        if (result.success) {
            navigate('/dashboard');
        } else {
            if (result.error?.code === 401) {
                setError('Invalid email or password');
            } else if (result.error?.code === 422) {
                setError('Please enter a valid email address');
            } else {
                setError(result.error?.message || 'Login failed. Please try again.');
            }
        }
    };
    
    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-card">
                    <div className="auth-header">
                        <div className="auth-icon">🔐</div>
                        <h1>Welcome Back</h1>
                        <p>Sign in to continue your interview practice</p>
                    </div>
                    
                    {error && (
                        <div className="alert alert-error">
                            <span className="alert-icon">⚠️</span>
                            {error}
                        </div>
                    )}
                    
                    <form onSubmit={handleSubmit} className="auth-form">
                        <div className="form-group">
                            <label htmlFor="email">Email Address</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="you@example.com"
                                required
                                autoComplete="email"
                                disabled={loading}
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="password">
                                Password
                                <Link to="/forgot-password" className="forgot-link">
                                    Forgot?
                                </Link>
                            </label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="••••••••"
                                required
                                autoComplete="current-password"
                                disabled={loading}
                            />
                        </div>
                        
                        <button 
                            type="submit" 
                            className="btn btn-primary btn-full"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner-small"></span>
                                    Signing in...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>
                    
                    <div className="auth-footer">
                        <p>
                            Don't have an account?{' '}
                            <Link to="/register">Create one</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
