/**
 * Interview Setup Page - Create new interview session
 */

import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { interviewApi } from '../api';

const ROLES = [
    'Software Engineer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'Data Scientist',
    'Product Manager',
    'DevOps Engineer',
    'Mobile Developer',
    'QA Engineer',
    'UI/UX Designer'
];

const COMPANIES = [
    'Google',
    'Microsoft',
    'Amazon',
    'Meta',
    'Apple',
    'Netflix',
    'Startup',
    'Other'
];

const DIFFICULTIES = [
    { value: 'easy', label: 'Easy', desc: 'Entry-level questions' },
    { value: 'medium', label: 'Medium', desc: 'Standard interview difficulty' },
    { value: 'hard', label: 'Hard', desc: 'Senior-level challenges' }
];

const QUESTION_TYPES = [
    { value: 'behavioral', label: 'Behavioral', icon: '💭' },
    { value: 'technical', label: 'Technical', icon: '💻' },
    { value: 'situational', label: 'Situational', icon: '🎯' },
    { value: 'hr', label: 'HR Questions', icon: '🤝' }
];

function InterviewPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const preselectedType = searchParams.get('type');
    
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const [formData, setFormData] = useState({
        title: '',
        target_role: ROLES[0],
        target_company: '',
        difficulty: 'medium',
        question_types: preselectedType ? [preselectedType] : [],
        num_questions: 5,
        skills: []
    });
    
    const [skillInput, setSkillInput] = useState('');
    
    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        setError(null);
    };
    
    const handleTypeToggle = (type) => {
        setFormData(prev => ({
            ...prev,
            question_types: prev.question_types.includes(type)
                ? prev.question_types.filter(t => t !== type)
                : [...prev.question_types, type]
        }));
    };
    
    const handleAddSkill = () => {
        if (skillInput.trim() && !formData.skills.includes(skillInput.trim())) {
            setFormData(prev => ({
                ...prev,
                skills: [...prev.skills, skillInput.trim()]
            }));
            setSkillInput('');
        }
    };
    
    const handleRemoveSkill = (skill) => {
        setFormData(prev => ({
            ...prev,
            skills: prev.skills.filter(s => s !== skill)
        }));
    };
    
    const handleNext = () => {
        if (step === 1 && formData.question_types.length === 0) {
            setError('Please select at least one question type');
            return;
        }
        setStep(prev => prev + 1);
    };
    
    const handleBack = () => {
        setStep(prev => prev - 1);
    };
    
    const handleSubmit = async () => {
        setLoading(true);
        setError(null);
        
        // Generate title if empty
        const title = formData.title.trim() || 
            `${formData.target_role} Interview - ${new Date().toLocaleDateString()}`;
        
        // Create session
        const sessionResult = await interviewApi.createSession({
            title,
            target_role: formData.target_role,
            target_company: formData.target_company || undefined,
            difficulty: formData.difficulty
        });
        
        if (!sessionResult.success) {
            setLoading(false);
            setError(sessionResult.error?.message || 'Failed to create session');
            return;
        }
        
        const sessionId = sessionResult.data.id;
        
        // Generate questions
        const questionsResult = await interviewApi.generateQuestions(sessionId, {
            num_questions: formData.num_questions,
            categories: formData.question_types,
            skills: formData.skills
        });
        
        setLoading(false);
        
        if (!questionsResult.success) {
            setError(questionsResult.error?.message || 'Failed to generate questions');
            return;
        }
        
        // Navigate to interview session
        navigate(`/interview/${sessionId}`);
    };
    
    return (
        <div className="interview-setup-page">
            <div className="setup-container">
                {/* Progress Steps */}
                <div className="progress-steps">
                    <div className={`step ${step >= 1 ? 'active' : ''}`}>
                        <span className="step-number">1</span>
                        <span className="step-label">Type</span>
                    </div>
                    <div className="step-line"></div>
                    <div className={`step ${step >= 2 ? 'active' : ''}`}>
                        <span className="step-number">2</span>
                        <span className="step-label">Details</span>
                    </div>
                    <div className="step-line"></div>
                    <div className={`step ${step >= 3 ? 'active' : ''}`}>
                        <span className="step-number">3</span>
                        <span className="step-label">Skills</span>
                    </div>
                </div>
                
                {error && (
                    <div className="alert alert-error">
                        <span className="alert-icon">⚠️</span>
                        {error}
                    </div>
                )}
                
                {/* Step 1: Question Types */}
                {step === 1 && (
                    <div className="setup-step">
                        <h2>What type of interview do you want to practice?</h2>
                        <p>Select one or more question categories</p>
                        
                        <div className="type-grid">
                            {QUESTION_TYPES.map(type => (
                                <div
                                    key={type.value}
                                    className={`type-card ${formData.question_types.includes(type.value) ? 'selected' : ''}`}
                                    onClick={() => handleTypeToggle(type.value)}
                                >
                                    <span className="type-icon">{type.icon}</span>
                                    <span className="type-label">{type.label}</span>
                                </div>
                            ))}
                        </div>
                        
                        <div className="step-actions">
                            <button 
                                className="btn btn-primary"
                                onClick={handleNext}
                            >
                                Continue
                            </button>
                        </div>
                    </div>
                )}
                
                {/* Step 2: Role & Details */}
                {step === 2 && (
                    <div className="setup-step">
                        <h2>Tell us about the position</h2>
                        <p>This helps us generate relevant questions</p>
                        
                        <div className="form-grid">
                            <div className="form-group">
                                <label>Target Role</label>
                                <select
                                    value={formData.target_role}
                                    onChange={(e) => handleChange('target_role', e.target.value)}
                                >
                                    {ROLES.map(role => (
                                        <option key={role} value={role}>{role}</option>
                                    ))}
                                </select>
                            </div>
                            
                            <div className="form-group">
                                <label>Company Style (Optional)</label>
                                <select
                                    value={formData.target_company}
                                    onChange={(e) => handleChange('target_company', e.target.value)}
                                >
                                    <option value="">Select company type</option>
                                    {COMPANIES.map(company => (
                                        <option key={company} value={company}>{company}</option>
                                    ))}
                                </select>
                            </div>
                            
                            <div className="form-group">
                                <label>Difficulty Level</label>
                                <div className="difficulty-options">
                                    {DIFFICULTIES.map(diff => (
                                        <div
                                            key={diff.value}
                                            className={`difficulty-option ${formData.difficulty === diff.value ? 'selected' : ''}`}
                                            onClick={() => handleChange('difficulty', diff.value)}
                                        >
                                            <span className="diff-label">{diff.label}</span>
                                            <span className="diff-desc">{diff.desc}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            
                            <div className="form-group">
                                <label>Number of Questions: {formData.num_questions}</label>
                                <input
                                    type="range"
                                    min="3"
                                    max="10"
                                    value={formData.num_questions}
                                    onChange={(e) => handleChange('num_questions', parseInt(e.target.value))}
                                    className="range-slider"
                                />
                                <div className="range-labels">
                                    <span>3</span>
                                    <span>10</span>
                                </div>
                            </div>
                        </div>
                        
                        <div className="step-actions">
                            <button className="btn btn-outline" onClick={handleBack}>
                                Back
                            </button>
                            <button className="btn btn-primary" onClick={handleNext}>
                                Continue
                            </button>
                        </div>
                    </div>
                )}
                
                {/* Step 3: Skills */}
                {step === 3 && (
                    <div className="setup-step">
                        <h2>Add your skills (Optional)</h2>
                        <p>We'll tailor questions to your technical skills</p>
                        
                        <div className="skills-input">
                            <input
                                type="text"
                                value={skillInput}
                                onChange={(e) => setSkillInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                                placeholder="e.g., React, Python, AWS..."
                            />
                            <button 
                                className="btn btn-outline"
                                onClick={handleAddSkill}
                            >
                                Add
                            </button>
                        </div>
                        
                        <div className="skills-tags">
                            {formData.skills.map(skill => (
                                <span key={skill} className="skill-tag">
                                    {skill}
                                    <button onClick={() => handleRemoveSkill(skill)}>×</button>
                                </span>
                            ))}
                        </div>
                        
                        <div className="form-group">
                            <label>Session Title (Optional)</label>
                            <input
                                type="text"
                                value={formData.title}
                                onChange={(e) => handleChange('title', e.target.value)}
                                placeholder="My Practice Session"
                            />
                        </div>
                        
                        <div className="setup-summary">
                            <h3>Summary</h3>
                            <ul>
                                <li><strong>Type:</strong> {formData.question_types.join(', ')}</li>
                                <li><strong>Role:</strong> {formData.target_role}</li>
                                <li><strong>Difficulty:</strong> {formData.difficulty}</li>
                                <li><strong>Questions:</strong> {formData.num_questions}</li>
                            </ul>
                        </div>
                        
                        <div className="step-actions">
                            <button className="btn btn-outline" onClick={handleBack}>
                                Back
                            </button>
                            <button 
                                className="btn btn-primary"
                                onClick={handleSubmit}
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner-small"></span>
                                        Creating...
                                    </>
                                ) : (
                                    'Start Interview'
                                )}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default InterviewPage;
