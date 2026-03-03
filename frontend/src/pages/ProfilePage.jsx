/**
 * Profile Page - User profile and settings
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useApiHooks';
import { userApi, resumeApi } from '../api';

function ProfilePage() {
    const { user, refreshUser, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const redirectToResumeInterview = location.state?.redirectToResumeInterview || false;
    
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

    // Resume state
    const [resumeData, setResumeData] = useState(null);
    const [resumeUploading, setResumeUploading] = useState(false);
    const [resumeFile, setResumeFile] = useState(null);

    useEffect(() => {
        if (user) {
            setFormData({
                full_name: user.full_name || '',
                target_role: user.target_role || '',
                experience_level: user.experience_level || 'mid'
            });
            setSkills(user.skills || []);
            loadResumeData();
        }
    }, [user]);

    const loadResumeData = async () => {
        const result = await resumeApi.getResumeData();
        if (result.success) {
            setResumeData(result.data);
        }
    };
    
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

    const handleResumeFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setResumeFile(file);
        }
    };

    const handleResumeUpload = async () => {
        if (!resumeFile) {
            setError('Please select a file first');
            return;
        }

        setResumeUploading(true);
        setError(null);
        setSuccess(null);

        const result = await resumeApi.uploadResume(resumeFile);

        setResumeUploading(false);

        if (result.success) {
            setSuccess(`Resume uploaded! Extracted ${result.data.skills_extracted} skills and ${result.data.experience_found} years of experience.`);
            setResumeData(result.data.parsed_data);
            setResumeFile(null);

            // Refresh user to get updated skills
            if (refreshUser) {
                refreshUser();
            }

            // Redirect to resume interview if user came from Dashboard resume card
            if (redirectToResumeInterview) {
                setTimeout(() => navigate('/skill-interview?type=resume'), 1500);
                return;
            }

            setTimeout(() => setSuccess(null), 5000);
        } else {
            setError(result.error?.message || 'Failed to upload resume');
        }
    };

    const handleResumeDelete = async () => {
        if (!window.confirm('Are you sure you want to delete your resume?')) {
            return;
        }

        setResumeUploading(true);
        setError(null);

        const result = await resumeApi.deleteResume();

        setResumeUploading(false);

        if (result.success) {
            setSuccess('Resume deleted successfully');
            setResumeData(null);
            setResumeFile(null);
            setTimeout(() => setSuccess(null), 3000);
        } else {
            setError(result.error?.message || 'Failed to delete resume');
        }
    };

    const handleExportData = async () => {
        setError(null);
        setSuccess(null);
        setLoading(true);

        const result = await userApi.exportData();

        setLoading(false);

        if (result.success) {
            setSuccess('Data exported successfully!');
            setTimeout(() => setSuccess(null), 3000);
        } else {
            setError(result.error?.message || 'Failed to export data');
        }
    };

    const handleDeleteAccount = async () => {
        if (!window.confirm('Are you sure you want to delete your account? This action is irreversible and will delete all your data including interview sessions and scores.')) {
            return;
        }

        setError(null);
        setLoading(true);

        const result = await userApi.deleteAccount();

        setLoading(false);

        if (result.success) {
            if (logout) {
                logout();
            }
            navigate('/login');
        } else {
            setError(result.error?.message || 'Failed to delete account');
        }
    };

    return (
        <div className="profile-page">
            <header className="profile-header">
                <h1>Your Profile</h1>
                <p>Manage your account settings and preferences</p>
            </header>
            
            {redirectToResumeInterview && !resumeData && (
                <div className="alert alert-info">
                    <span className="alert-icon">📄</span>
                    Upload your resume below to start the Resume Interview. You'll be redirected automatically after upload.
                </div>
            )}

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

                {/* Resume Upload Section */}
                <section className="resume-card">
                    <h3>📄 Resume / CV</h3>
                    <p className="section-description">
                        Upload your resume to get personalized interview questions based on your experience
                    </p>

                    {resumeData ? (
                        <div className="resume-uploaded">
                            <div className="resume-info">
                                <div className="resume-header">
                                    <span className="resume-icon">✅</span>
                                    <div>
                                        <strong>{resumeData.file_name}</strong>
                                        <p className="resume-date">
                                            Uploaded {new Date(resumeData.parsed_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>

                                <div className="resume-stats">
                                    <div className="resume-stat">
                                        <strong>{resumeData.extracted_skills?.length || 0}</strong>
                                        <span>Skills Extracted</span>
                                    </div>
                                    <div className="resume-stat">
                                        <strong>{resumeData.work_experience?.length || 0}</strong>
                                        <span>Work Experiences</span>
                                    </div>
                                    <div className="resume-stat">
                                        <strong>{resumeData.projects?.length || 0}</strong>
                                        <span>Projects</span>
                                    </div>
                                    <div className="resume-stat">
                                        <strong>{resumeData.total_years_experience || 0}</strong>
                                        <span>Years Experience</span>
                                    </div>
                                </div>

                                {resumeData.extracted_skills && resumeData.extracted_skills.length > 0 && (
                                    <div className="resume-skills">
                                        <strong>Extracted Skills:</strong>
                                        <div className="skills-tags">
                                            {resumeData.extracted_skills.slice(0, 10).map((skill, idx) => (
                                                <span key={idx} className="skill-tag">{skill}</span>
                                            ))}
                                            {resumeData.extracted_skills.length > 10 && (
                                                <span className="skill-tag">+{resumeData.extracted_skills.length - 10} more</span>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="resume-actions">
                                <button
                                    className="btn btn-danger btn-sm"
                                    onClick={handleResumeDelete}
                                    disabled={resumeUploading}
                                >
                                    {resumeUploading ? 'Deleting...' : 'Delete Resume'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="resume-upload">
                            <div className="upload-area">
                                <input
                                    type="file"
                                    id="resume-file"
                                    accept=".pdf,.txt,.doc,.docx"
                                    onChange={handleResumeFileChange}
                                    style={{ display: 'none' }}
                                />
                                <label htmlFor="resume-file" className="upload-label">
                                    <div className="upload-icon">📎</div>
                                    <p>
                                        {resumeFile ? resumeFile.name : 'Click to select resume file'}
                                    </p>
                                    <span className="upload-hint">PDF, TXT, or DOCX (max 10MB)</span>
                                </label>
                            </div>

                            {resumeFile && (
                                <button
                                    className="btn btn-primary"
                                    onClick={handleResumeUpload}
                                    disabled={resumeUploading}
                                >
                                    {resumeUploading ? (
                                        <>
                                            <span className="spinner-small"></span>
                                            Uploading & Parsing...
                                        </>
                                    ) : (
                                        'Upload Resume'
                                    )}
                                </button>
                            )}
                        </div>
                    )}
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
                        <button
                            className="btn btn-outline"
                            onClick={handleExportData}
                            disabled={loading}
                        >
                            {loading ? 'Exporting...' : 'Export Data'}
                        </button>
                        <button
                            className="btn btn-danger"
                            onClick={handleDeleteAccount}
                            disabled={loading}
                        >
                            {loading ? 'Deleting...' : 'Delete Account'}
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
