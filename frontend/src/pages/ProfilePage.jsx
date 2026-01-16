/**
 * Profile Page - User profile and settings
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useApiHooks';
import { userApi } from '../api';

function ProfilePage() {
    const { user, refreshUser } = useAuth();
    
    const [editing, setEditing] = useState(false);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(null);
    const [error, setError] = useState(null);
    
    const [formData, setFormData] = useState({
        full_name: '',
        target_role: '',
        experience_level: 'mid'
    });
    
    const [skills, setSkills] = useState([]);
    const [newSkill, setNewSkill] = useState('');
    
    useEffect(() => {
        if (user) {
            setFormData({
                full_name: user.full_name || '',
                target_role: user.target_role || '',
                experience_level: user.experience_level || 'mid'
            });
            setSkills(user.skills || []);
        }
    }, [user]);
    
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };
    
    const handleAddSkill = () => {
        if (newSkill.trim() && !skills.includes(newSkill.trim())) {
            setSkills(prev => [...prev, newSkill.trim()]);
            setNewSkill('');
        }
    };
    
    const handleRemoveSkill = (skill) => {
        setSkills(prev => prev.filter(s => s !== skill));
    };
    
    const handleSave = async () => {
        setLoading(true);
        setError(null);
        setSuccess(null);
        
        // Update profile
        const profileResult = await userApi.updateProfile(formData);
        
        if (!profileResult.success) {
            setError(profileResult.error?.message || 'Failed to update profile');
            setLoading(false);
            return;
        }
        
        // Update skills
        const skillsResult = await userApi.updateSkills(skills);
        
        if (!skillsResult.success) {
            setError(skillsResult.error?.message || 'Failed to update skills');
            setLoading(false);
            return;
        }
        
        setLoading(false);
        setSuccess('Profile updated successfully!');
        setEditing(false);
        
        // Refresh user data
        if (refreshUser) {
            refreshUser();
        }
        
        setTimeout(() => setSuccess(null), 3000);
    };
    
    const handleCancel = () => {
        setEditing(false);
        setFormData({
            full_name: user?.full_name || '',
            target_role: user?.target_role || '',
            experience_level: user?.experience_level || 'mid'
        });
        setSkills(user?.skills || []);
        setError(null);
    };
    
    return (
        <div className="profile-page">
            <header className="profile-header">
                <h1>Your Profile</h1>
                <p>Manage your account settings and preferences</p>
            </header>
            
            {success && (
                <div className="alert alert-success">
                    <span className="alert-icon">✅</span>
                    {success}
                </div>
            )}
            
            {error && (
                <div className="alert alert-error">
                    <span className="alert-icon">⚠️</span>
                    {error}
                </div>
            )}
            
            <div className="profile-content">
                {/* Profile Card */}
                <section className="profile-card">
                    <div className="profile-avatar">
                        <div className="avatar-circle">
                            {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                        </div>
                    </div>
                    
                    <div className="profile-info">
                        {editing ? (
                            <div className="edit-form">
                                <div className="form-group">
                                    <label>Full Name</label>
                                    <input
                                        type="text"
                                        name="full_name"
                                        value={formData.full_name}
                                        onChange={handleChange}
                                        placeholder="Your full name"
                                    />
                                </div>
                                
                                <div className="form-group">
                                    <label>Email</label>
                                    <input
                                        type="email"
                                        value={user?.email || ''}
                                        disabled
                                        className="disabled"
                                    />
                                    <span className="input-hint">Email cannot be changed</span>
                                </div>
                                
                                <div className="form-group">
                                    <label>Target Role</label>
                                    <input
                                        type="text"
                                        name="target_role"
                                        value={formData.target_role}
                                        onChange={handleChange}
                                        placeholder="e.g., Software Engineer"
                                    />
                                </div>
                                
                                <div className="form-group">
                                    <label>Experience Level</label>
                                    <select
                                        name="experience_level"
                                        value={formData.experience_level}
                                        onChange={handleChange}
                                    >
                                        <option value="entry">Entry Level (0-2 years)</option>
                                        <option value="mid">Mid Level (2-5 years)</option>
                                        <option value="senior">Senior (5+ years)</option>
                                        <option value="lead">Lead/Manager</option>
                                    </select>
                                </div>
                            </div>
                        ) : (
                            <div className="view-info">
                                <h2>{user?.full_name || 'User'}</h2>
                                <p className="email">{user?.email}</p>
                                {user?.target_role && (
                                    <p className="role">🎯 {user.target_role}</p>
                                )}
                                <p className="experience">
                                    📊 {formatExperience(user?.experience_level)}
                                </p>
                            </div>
                        )}
                    </div>
                    
                    <div className="profile-actions">
                        {editing ? (
                            <>
                                <button 
                                    className="btn btn-outline"
                                    onClick={handleCancel}
                                    disabled={loading}
                                >
                                    Cancel
                                </button>
                                <button 
                                    className="btn btn-primary"
                                    onClick={handleSave}
                                    disabled={loading}
                                >
                                    {loading ? 'Saving...' : 'Save Changes'}
                                </button>
                            </>
                        ) : (
                            <button 
                                className="btn btn-outline"
                                onClick={() => setEditing(true)}
                            >
                                Edit Profile
                            </button>
                        )}
                    </div>
                </section>
                
                {/* Skills Section */}
                <section className="skills-card">
                    <h3>Your Skills</h3>
                    <p className="section-desc">
                        Add skills to receive more relevant interview questions
                    </p>
                    
                    {editing && (
                        <div className="skills-input">
                            <input
                                type="text"
                                value={newSkill}
                                onChange={(e) => setNewSkill(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                                placeholder="Add a skill (e.g., React, Python)"
                            />
                            <button 
                                className="btn btn-outline"
                                onClick={handleAddSkill}
                            >
                                Add
                            </button>
                        </div>
                    )}
                    
                    <div className="skills-list">
                        {skills.length > 0 ? (
                            skills.map(skill => (
                                <span key={skill} className="skill-tag">
                                    {skill}
                                    {editing && (
                                        <button onClick={() => handleRemoveSkill(skill)}>×</button>
                                    )}
                                </span>
                            ))
                        ) : (
                            <p className="empty-skills">No skills added yet</p>
                        )}
                    </div>
                </section>
                
                {/* Stats Section */}
                <section className="stats-card">
                    <h3>Your Statistics</h3>
                    <div className="stats-grid">
                        <div className="stat-item">
                            <span className="stat-value">{user?.total_sessions || 0}</span>
                            <span className="stat-label">Total Sessions</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{user?.total_questions || 0}</span>
                            <span className="stat-label">Questions Answered</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{user?.average_score || 0}%</span>
                            <span className="stat-label">Average Score</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">
                                {user?.created_at 
                                    ? new Date(user.created_at).toLocaleDateString() 
                                    : 'N/A'}
                            </span>
                            <span className="stat-label">Member Since</span>
                        </div>
                    </div>
                </section>
                
                {/* Account Actions */}
                <section className="account-actions">
                    <h3>Account</h3>
                    <div className="action-buttons">
                        <button className="btn btn-outline">
                            Change Password
                        </button>
                        <button className="btn btn-outline">
                            Export Data
                        </button>
                        <button className="btn btn-danger">
                            Delete Account
                        </button>
                    </div>
                </section>
            </div>
        </div>
    );
}

function formatExperience(level) {
    const levels = {
        entry: 'Entry Level (0-2 years)',
        mid: 'Mid Level (2-5 years)',
        senior: 'Senior (5+ years)',
        lead: 'Lead/Manager'
    };
    return levels[level] || 'Not specified';
}

export default ProfilePage;
