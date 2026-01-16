/**
 * Interview Session Page - Active interview with recording
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { interviewApi, feedbackApi } from '../api';
import { useAudioRecording } from '../hooks/useApiHooks';

function InterviewSessionPage() {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    
    const [session, setSession] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [evaluations, setEvaluations] = useState({});
    
    const {
        isRecording,
        audioBlob,
        duration,
        startRecording,
        stopRecording,
        resetRecording
    } = useAudioRecording();
    
    const currentQuestion = questions[currentIndex];
    const isLastQuestion = currentIndex === questions.length - 1;
    const progress = questions.length > 0 
        ? ((currentIndex + 1) / questions.length) * 100 
        : 0;
    
    // Load session and questions
    useEffect(() => {
        const loadSession = async () => {
            setLoading(true);
            setError(null);
            
            const result = await interviewApi.getSession(sessionId);
            
            if (result.success) {
                setSession(result.data);
                setQuestions(result.data.questions || []);
            } else {
                setError('Failed to load interview session');
            }
            
            setLoading(false);
        };
        
        loadSession();
    }, [sessionId]);
    
    // Submit answer for current question
    const handleSubmitAnswer = async () => {
        if (!audioBlob) {
            setError('Please record your answer first');
            return;
        }
        
        setSubmitting(true);
        setError(null);
        
        try {
            // 1. Upload audio
            const uploadResult = await interviewApi.uploadAudio(
                sessionId,
                currentQuestion.id,
                audioBlob,
                duration
            );
            
            if (!uploadResult.success) {
                throw new Error('Failed to upload audio');
            }
            
            // 2. Transcribe
            const transcribeResult = await interviewApi.transcribeAudio(
                sessionId,
                currentQuestion.id
            );
            
            if (!transcribeResult.success) {
                throw new Error('Failed to transcribe audio');
            }
            
            // 3. Evaluate
            const evaluateResult = await interviewApi.evaluateResponse(
                sessionId,
                currentQuestion.id
            );
            
            if (!evaluateResult.success) {
                throw new Error('Failed to evaluate response');
            }
            
            // Store evaluation
            setEvaluations(prev => ({
                ...prev,
                [currentQuestion.id]: evaluateResult.data
            }));
            
            // Move to next question or finish
            if (isLastQuestion) {
                await handleFinishInterview();
            } else {
                setCurrentIndex(prev => prev + 1);
                resetRecording();
            }
            
        } catch (err) {
            setError(err.message);
        }
        
        setSubmitting(false);
    };
    
    // Finish the interview
    const handleFinishInterview = async () => {
        setSubmitting(true);
        
        try {
            // Complete session
            await interviewApi.completeSession(sessionId);
            
            // Calculate scores
            await feedbackApi.calculateScores(sessionId);
            
            // Generate feedback
            await feedbackApi.generateFeedback(sessionId);
            
            // Navigate to feedback page
            navigate(`/feedback/${sessionId}`);
            
        } catch (err) {
            setError('Failed to complete interview');
            setSubmitting(false);
        }
    };
    
    // Skip current question
    const handleSkip = () => {
        if (!isLastQuestion) {
            setCurrentIndex(prev => prev + 1);
            resetRecording();
        }
    };
    
    if (loading) {
        return (
            <div className="interview-session-page">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading interview...</p>
                </div>
            </div>
        );
    }
    
    if (!session || questions.length === 0) {
        return (
            <div className="interview-session-page">
                <div className="error-container">
                    <h2>Session Not Found</h2>
                    <p>This interview session doesn't exist or has no questions.</p>
                    <button 
                        className="btn btn-primary"
                        onClick={() => navigate('/interview')}
                    >
                        Start New Interview
                    </button>
                </div>
            </div>
        );
    }
    
    return (
        <div className="interview-session-page">
            {/* Header with progress */}
            <header className="session-header">
                <div className="session-info">
                    <h2>{session.title}</h2>
                    <span className="question-counter">
                        Question {currentIndex + 1} of {questions.length}
                    </span>
                </div>
                <div className="progress-bar">
                    <div 
                        className="progress-fill"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>
            </header>
            
            {error && (
                <div className="alert alert-error">
                    <span className="alert-icon">⚠️</span>
                    {error}
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}
            
            {/* Question Card */}
            <main className="session-main">
                <div className="question-card">
                    <div className="question-meta">
                        <span className={`category-badge ${currentQuestion.category}`}>
                            {currentQuestion.category}
                        </span>
                        <span className={`difficulty-badge ${currentQuestion.difficulty}`}>
                            {currentQuestion.difficulty}
                        </span>
                        {currentQuestion.time_limit && (
                            <span className="time-limit">
                                ⏱️ {currentQuestion.time_limit}s recommended
                            </span>
                        )}
                    </div>
                    
                    <h3 className="question-text">
                        {currentQuestion.question_text}
                    </h3>
                    
                    {currentQuestion.expected_topics && (
                        <div className="expected-topics">
                            <span>Topics to cover: </span>
                            {currentQuestion.expected_topics.map(topic => (
                                <span key={topic} className="topic-tag">{topic}</span>
                            ))}
                        </div>
                    )}
                </div>
                
                {/* Recording Controls */}
                <div className="recording-section">
                    <div className="recording-status">
                        {isRecording ? (
                            <div className="recording-indicator">
                                <span className="pulse-dot"></span>
                                <span>Recording... {duration}s</span>
                            </div>
                        ) : audioBlob ? (
                            <div className="recording-complete">
                                <span>✅ Recording complete ({duration}s)</span>
                            </div>
                        ) : (
                            <div className="recording-prompt">
                                <span>🎤 Click to start recording your answer</span>
                            </div>
                        )}
                    </div>
                    
                    <div className="recording-controls">
                        {!isRecording && !audioBlob && (
                            <button 
                                className="btn btn-record"
                                onClick={startRecording}
                                disabled={submitting}
                            >
                                <span className="record-icon">🎙️</span>
                                Start Recording
                            </button>
                        )}
                        
                        {isRecording && (
                            <button 
                                className="btn btn-stop"
                                onClick={stopRecording}
                            >
                                <span className="stop-icon">⏹️</span>
                                Stop Recording
                            </button>
                        )}
                        
                        {audioBlob && !isRecording && (
                            <div className="playback-controls">
                                <audio 
                                    controls 
                                    src={URL.createObjectURL(audioBlob)}
                                    className="audio-player"
                                />
                                <button 
                                    className="btn btn-outline"
                                    onClick={resetRecording}
                                    disabled={submitting}
                                >
                                    🔄 Re-record
                                </button>
                            </div>
                        )}
                    </div>
                </div>
                
                {/* Action Buttons */}
                <div className="session-actions">
                    <button 
                        className="btn btn-outline"
                        onClick={handleSkip}
                        disabled={submitting || isLastQuestion}
                    >
                        Skip Question
                    </button>
                    
                    <button 
                        className="btn btn-primary"
                        onClick={handleSubmitAnswer}
                        disabled={!audioBlob || submitting}
                    >
                        {submitting ? (
                            <>
                                <span className="spinner-small"></span>
                                {isLastQuestion ? 'Finishing...' : 'Submitting...'}
                            </>
                        ) : (
                            isLastQuestion ? 'Finish Interview' : 'Submit & Next'
                        )}
                    </button>
                </div>
            </main>
            
            {/* Question Navigation */}
            <footer className="session-footer">
                <div className="question-nav">
                    {questions.map((q, index) => (
                        <div
                            key={q.id}
                            className={`nav-dot ${index === currentIndex ? 'current' : ''} ${evaluations[q.id] ? 'answered' : ''}`}
                            title={`Question ${index + 1}`}
                        />
                    ))}
                </div>
            </footer>
        </div>
    );
}

export default InterviewSessionPage;
