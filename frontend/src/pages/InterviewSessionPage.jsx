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
    const [answerMode, setAnswerMode] = useState('text'); // 'text' or 'voice'
    const [textAnswer, setTextAnswer] = useState('');
    
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
                const sessionData = result.data;

                // If session is already completed/evaluated, redirect to feedback
                if (['completed', 'evaluated'].includes(sessionData.status)) {
                    navigate(`/feedback/${sessionId}`, { replace: true });
                    return;
                }

                setSession(sessionData);
                const sessionQuestions = sessionData.questions || [];
                setQuestions(sessionQuestions);

                // Resume from first unanswered question
                const firstUnanswered = sessionQuestions.findIndex(q => !q.has_response);
                if (firstUnanswered > 0) {
                    setCurrentIndex(firstUnanswered);
                }
            } else {
                setError('Failed to load interview session');
            }
            
            setLoading(false);
        };
        
        loadSession();
    }, [sessionId, navigate]);
    
    // Submit answer for current question
    const handleSubmitAnswer = async () => {
        // Determine which mode based on actual input available
        const hasText = textAnswer && textAnswer.trim().length > 0;
        const hasAudio = !!audioBlob;
        const useTextMode = hasText && (answerMode === 'text' || !hasAudio);

        if (!hasText && !hasAudio) {
            setError('Please type your answer or record audio first');
            return;
        }

        setSubmitting(true);
        setError(null);

        try {
            if (useTextMode) {
                // Text mode: Submit text answer directly
                const textResult = await interviewApi.submitTextAnswer(
                    sessionId,
                    currentQuestion.id,
                    textAnswer.trim()
                );
                if (!textResult.success) {
                    throw new Error('Failed to submit text answer: ' + JSON.stringify(textResult.error));
                }
            } else if (hasAudio) {
                // Voice mode: Upload audio -> Transcribe -> Evaluate
                const uploadResult = await interviewApi.uploadAudio(
                    sessionId,
                    currentQuestion.id,
                    audioBlob,
                    duration
                );

                if (!uploadResult.success) {
                    throw new Error('Failed to upload audio');
                }

                const transcribeResult = await interviewApi.transcribeAudio(
                    sessionId,
                    currentQuestion.id
                );

                if (!transcribeResult.success) {
                    throw new Error('Failed to transcribe audio');
                }
            }

            // Evaluate the response (works for both modes since transcript is set)
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
                setTextAnswer('');
            }

        } catch (err) {
            setError(err.message);
        }

        setSubmitting(false);
    };
    
    // Finish the interview
    const handleFinishInterview = async () => {
        setSubmitting(true);
        setError(null);

        try {
            // Complete session
            const completeResult = await interviewApi.completeSession(sessionId);
            if (!completeResult.success) {
                console.error('[handleFinishInterview] completeSession failed:', completeResult.error);
            }

            // Calculate scores
            const scoresResult = await feedbackApi.calculateScores(sessionId);
            if (!scoresResult.success) {
                console.error('[handleFinishInterview] calculateScores failed:', scoresResult.error);
                setError('Failed to calculate scores: ' + (scoresResult.error?.message || 'Unknown error'));
                setSubmitting(false);
                return;
            }

            // Generate feedback
            const feedbackResult = await feedbackApi.generateFeedback(sessionId);
            if (!feedbackResult.success) {
                console.error('[handleFinishInterview] generateFeedback failed:', feedbackResult.error);
                // Still navigate - scores exist even if feedback generation failed
            }

            // Navigate to feedback page
            navigate(`/feedback/${sessionId}`);

        } catch (err) {
            console.error('[handleFinishInterview] Exception:', err);
            setError('Failed to complete interview: ' + err.message);
            setSubmitting(false);
        }
    };
    
    // Skip current question — stop any active recording first
    const handleSkip = () => {
        if (!isLastQuestion) {
            // Stop active recording before moving to next question
            if (isRecording) {
                stopRecording();
            }
            // Reset recorder state (kills stream, clears buffers)
            resetRecording();
            setTextAnswer('');
            setCurrentIndex(prev => prev + 1);
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
    
    if (!session) {
        return (
            <div className="interview-session-page">
                <div className="error-container">
                    <h2>Session Not Found</h2>
                    <p>This interview session doesn't exist.</p>
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

    if (questions.length === 0) {
        return (
            <div className="interview-session-page">
                <div className="error-container">
                    <h2>No Questions Yet</h2>
                    <p>This session hasn't generated questions yet. Please start a new interview.</p>
                    <button
                        className="btn btn-primary"
                        onClick={() => navigate('/interview')}
                    >
                        Start New Interview
                    </button>
                    <button
                        className="btn btn-outline"
                        onClick={() => navigate('/history')}
                        style={{ marginLeft: '10px' }}
                    >
                        Back to History
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
                    <h2>{session.job_role || session.interview_type || 'Interview'} Interview</h2>
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
                    
                    {currentQuestion.expected_keywords && currentQuestion.expected_keywords.length > 0 && (
                        <div className="expected-topics">
                            <span>Topics to cover: </span>
                            {currentQuestion.expected_keywords.map(topic => (
                                <span key={topic} className="topic-tag">{topic}</span>
                            ))}
                        </div>
                    )}
                </div>
                
                {/* Answer Mode Toggle */}
                <div className="answer-mode-toggle">
                    <button
                        className={`btn btn-mode ${answerMode === 'text' ? 'active' : ''}`}
                        onClick={() => setAnswerMode('text')}
                        disabled={submitting || isRecording}
                    >
                        ✍️ Type Answer
                    </button>
                    <button
                        className={`btn btn-mode ${answerMode === 'voice' ? 'active' : ''}`}
                        onClick={() => setAnswerMode('voice')}
                        disabled={submitting || isRecording}
                    >
                        🎤 Voice Answer
                    </button>
                </div>

                {/* Text Answer Input */}
                {answerMode === 'text' && (
                    <div className="text-answer-section">
                        <textarea
                            className="text-answer-input"
                            value={textAnswer}
                            onChange={(e) => setTextAnswer(e.target.value)}
                            placeholder="Type your answer here..."
                            rows={6}
                            disabled={submitting}
                        />
                        <div className="text-answer-info">
                            <span>{textAnswer.trim().split(/\s+/).filter(Boolean).length} words</span>
                        </div>
                    </div>
                )}

                {/* Recording Controls (Voice Mode) */}
                {answerMode === 'voice' && (
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
                )}
                
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
                        disabled={(!audioBlob && (!textAnswer || !textAnswer.trim())) || submitting}
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
