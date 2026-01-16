/**
 * Register Page Component
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { userApi } from '../api';

function RegisterPage() {
    const navigate = useNavigate();
    
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        full_name: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setError(null);
    };
    
    const validateForm = () => {
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return false;
        }
        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters');
            return false;
        }
        if (formData.full_name.trim().length < 2) {
            setError('Please enter your full name');
            return false;
        }
        return true;
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        setLoading(true);
        setError(null);
        
        const result = await userApi.register({
            email: formData.email,
            password: formData.password,
            full_name: formData.full_name
        });
        
        setLoading(false);
        
        if (result.success) {
            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } else {
            if (result.error?.code === 400) {
                setError('An account with this email already exists');
            } else if (result.error?.code === 422) {
                setError('Please check your input and try again');
            } else {
                setError(result.error?.message || 'Registration failed. Please try again.');
            }
        }
    };
    
    if (success) {
        return (
            <div className="auth-page">
                <div className="auth-container">
                    <div className="auth-card success-card">
                        <div className="success-icon">✅</div>
                        <h1>Account Created!</h1>
                        <p>Redirecting you to login...</p>
                    </div>
                </div>
            </div>
        );
    }
    
    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-card">
                    <div className="auth-header">
                        <div className="auth-icon">🚀</div>
                        <h1>Create Account</h1>
                        <p>Start your interview preparation journey</p>
                    </div>
                    
                    {error && (
                        <div className="alert alert-error">
                            <span className="alert-icon">⚠️</span>
                            {error}
                        </div>
                    )}
                    
                    <form onSubmit={handleSubmit} className="auth-form">
                        <div className="form-group">
                            <label htmlFor="full_name">Full Name</label>
                            <input
                                type="text"
                                id="full_name"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleChange}
                                placeholder="John Doe"
                                required
                                autoComplete="name"
                                disabled={loading}
                            />
                        </div>
                        
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
                            <label htmlFor="password">Password</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Minimum 8 characters"
                                required
                                autoComplete="new-password"
                                disabled={loading}
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="confirmPassword">Confirm Password</label>
                            <input
                                type="password"
                                id="confirmPassword"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Re-enter password"
                                required
                                autoComplete="new-password"
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
                                    Creating Account...
                                </>
                            ) : (
                                'Create Account'
                            )}
                        </button>
                    </form>
                    
                    <div className="auth-footer">
                        <p>
                            Already have an account?{' '}
                            <Link to="/login">Sign in</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;
