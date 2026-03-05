/**
 * ==============================================================================
 * AI Mock Interview System - Skill Interview Page
 * ==============================================================================
 * 
 * Complete skill-based interview flow:
 * 1. Technology dropdown selection
 * 2. Question generation
 * 3. Voice recording for each question
 * 4. Submit and get results
 * 
 * @author AI Mock Interview System
 * @version 1.0.0
 * ==============================================================================
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import skillInterviewApi from '../api/skillInterviewApi';
import '../styles/SkillInterview.css';

// =============================================================================
// DEBUG HELPER
// =============================================================================
const DEBUG = process.env.NODE_ENV === 'development';
const debug = (component, action, data = null) => {
    if (!DEBUG) return;
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
    const prefix = `[${timestamp}] [${component}]`;
    if (data !== null) {
        console.log(`${prefix} ${action}:`, data);
    } else {
        console.log(`${prefix} ${action}`);
    }
};

// =============================================================================
// CONSTANTS
// =============================================================================

const STEPS = {
    SELECT_SKILL: 'select_skill',
    ANSWER_QUESTIONS: 'answer_questions',
    SUBMITTING: 'submitting',
    RESULTS: 'results',
};

// =============================================================================
// VOICE RECORDER HOOK
// =============================================================================

function useVoiceRecorder() {
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [audioUrl, setAudioUrl] = useState(null);
    const [duration, setDuration] = useState(0);
    const [error, setError] = useState(null);

    const mediaRecorderRef = useRef(null);
    const streamRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);
    const startTimeRef = useRef(null);

    // Helper: immediately stop mic stream and clear timer
    const killStream = useCallback(() => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
    }, []);

    const startRecording = useCallback(async () => {
        try {
            setError(null);
            // Clean up any previous session
            killStream();
            audioChunksRef.current = [];

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100,
                }
            });
            streamRef.current = stream;

            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: MediaRecorder.isTypeSupported('audio/webm')
                    ? 'audio/webm'
                    : 'audio/mp4',
            });

            mediaRecorderRef.current = mediaRecorder;

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(audioChunksRef.current, {
                    type: mediaRecorder.mimeType
                });
                setAudioBlob(blob);
                setAudioUrl(URL.createObjectURL(blob));
                // Always kill stream when recording stops
                killStream();
            };

            mediaRecorder.start(1000);
            startTimeRef.current = Date.now();
            setIsRecording(true);

            // Duration timer
            timerRef.current = setInterval(() => {
                setDuration(Math.floor((Date.now() - startTimeRef.current) / 1000));
            }, 1000);

        } catch (err) {
            console.error('Failed to start recording:', err);
            killStream();
            setError('Microphone access denied. Please allow microphone access.');
        }
    }, [killStream]);

    const stopRecording = useCallback(() => {
        const recorder = mediaRecorderRef.current;
        if (recorder && recorder.state !== 'inactive') {
            recorder.stop(); // triggers onstop -> killStream
            setIsRecording(false);
        } else {
            // Recorder already inactive — still kill stream & timer
            killStream();
            setIsRecording(false);
        }
    }, [killStream]);

    const resetRecording = useCallback(() => {
        // Stop any active recording and kill mic stream
        const recorder = mediaRecorderRef.current;
        if (recorder && recorder.state !== 'inactive') {
            recorder.stop();
        }
        killStream();
        mediaRecorderRef.current = null;
        audioChunksRef.current = [];
        if (audioUrl) {
            URL.revokeObjectURL(audioUrl);
        }
        setAudioBlob(null);
        setAudioUrl(null);
        setDuration(0);
        setError(null);
        setIsRecording(false);
    }, [killStream, audioUrl]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            const recorder = mediaRecorderRef.current;
            if (recorder && recorder.state !== 'inactive') {
                recorder.stop();
            }
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, []);

    return {
        isRecording,
        audioBlob,
        audioUrl,
        duration,
        error,
        startRecording,
        stopRecording,
        resetRecording,
    };
}

// =============================================================================
// SKILL SELECTION COMPONENT
// =============================================================================

function SkillSelection({ technologies, onSelect, loading }) {
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [selectedTech, setSelectedTech] = useState(null);
    const [difficulty, setDifficulty] = useState('medium');
    const [numQuestions, setNumQuestions] = useState(5);
    const [searchQuery, setSearchQuery] = useState('');

    // Get unique categories
    const categories = ['All', ...new Set(technologies.map(t => t.category))];

    // Filter technologies
    const filteredTechnologies = technologies.filter(tech => {
        const matchesCategory = selectedCategory === 'All' || tech.category === selectedCategory;
        const matchesSearch = tech.name.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    const handleStart = () => {
        if (selectedTech) {
            onSelect(selectedTech, difficulty, numQuestions);
        }
    };
    
    return (
        <div className="skill-selection">
            <div className="selection-header">
                <h1>🎯 Start Your Interview</h1>
                <p>Select a technology and difficulty level to begin</p>
            </div>
            
            {/* Search */}
            <div className="search-box">
                <input
                    type="text"
                    placeholder="🔍 Search technologies..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                />
            </div>
            
            {/* Category Filter */}
            <div className="category-tabs">
                {categories.map(category => (
                    <button
                        key={category}
                        className={`category-tab ${selectedCategory === category ? 'active' : ''}`}
                        onClick={() => setSelectedCategory(category)}
                    >
                        {category}
                    </button>
                ))}
            </div>
            
            {/* Technology Grid */}
            <div className="tech-grid">
                {filteredTechnologies.map(tech => (
                    <div
                        key={tech.id}
                        className={`tech-card ${selectedTech?.id === tech.id ? 'selected' : ''}`}
                        onClick={() => setSelectedTech(tech)}
                    >
                        <span className="tech-icon">{tech.icon || '💻'}</span>
                        <span className="tech-name">{tech.name}</span>
                        <span className="tech-category">{tech.category}</span>
                    </div>
                ))}
            </div>
            
            {/* Difficulty Selection */}
            {selectedTech && (
                <div className="difficulty-selection">
                    <h3>Select Difficulty</h3>
                    <div className="difficulty-options">
                        {['easy', 'medium', 'hard'].map(level => (
                            <button
                                key={level}
                                className={`difficulty-btn ${difficulty === level ? 'active' : ''} ${level}`}
                                onClick={() => setDifficulty(level)}
                            >
                                {level === 'easy' && '🟢 Easy'}
                                {level === 'medium' && '🟡 Medium'}
                                {level === 'hard' && '🔴 Hard'}
                            </button>
                        ))}
                    </div>
                </div>
            )}
            
            {/* Number of Questions */}
            {selectedTech && (
                <div className="question-count-selection">
                    <h3>Number of Questions: <span className="count-value">{numQuestions}</span></h3>
                    <div className="question-count-slider">
                        <span className="slider-label">3</span>
                        <input
                            type="range"
                            min="3"
                            max="10"
                            value={numQuestions}
                            onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                            className="count-slider"
                        />
                        <span className="slider-label">10</span>
                    </div>
                </div>
            )}

            {/* Start Button */}
            <div className="start-section">
                <button
                    className="start-btn"
                    onClick={handleStart}
                    disabled={!selectedTech || loading}
                >
                    {loading ? (
                        <>
                            <span className="spinner"></span>
                            Generating Questions...
                        </>
                    ) : (
                        <>
                            🚀 Start Interview ({selectedTech?.name || 'Select a skill'}) - {numQuestions} Questions
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

// =============================================================================
// QUESTION RECORDING COMPONENT
// =============================================================================

function QuestionRecording({
    question,
    questionNumber,
    totalQuestions,
    onRecordingComplete,
    recordedAnswer
}) {
    const {
        isRecording,
        audioBlob,
        audioUrl,
        duration,
        error,
        startRecording,
        stopRecording,
        resetRecording,
    } = useVoiceRecorder();

    const [saved, setSaved] = useState(!!recordedAnswer);
    const [answerMode, setAnswerMode] = useState('voice'); // 'voice' or 'text'
    const [textAnswer, setTextAnswer] = useState(recordedAnswer?.textAnswer || '');

    useEffect(() => {
        if (recordedAnswer) {
            setSaved(true);
            if (recordedAnswer.textAnswer) {
                setTextAnswer(recordedAnswer.textAnswer);
                setAnswerMode('text');
            }
        }
    }, [recordedAnswer]);

    const handleSave = () => {
        if (answerMode === 'text' && textAnswer.trim()) {
            onRecordingComplete(question.id, null, 0, textAnswer.trim());
            setSaved(true);
        } else if (audioBlob) {
            onRecordingComplete(question.id, audioBlob, duration, null);
            setSaved(true);
        }
    };

    const handleReRecord = () => {
        resetRecording();
        setTextAnswer('');
        setSaved(false);
    };

    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const canSave = answerMode === 'text' ? textAnswer.trim().length > 0 : !!audioBlob;

    return (
        <div className={`question-card ${saved ? 'completed' : ''}`}>
            <div className="question-header">
                <span className="question-number">Question {questionNumber}/{totalQuestions}</span>
                {saved && <span className="saved-badge">✓ {recordedAnswer?.textAnswer ? 'Typed' : 'Recorded'}</span>}
            </div>

            <div className="question-text">
                <h3>{question.question_text}</h3>
            </div>

            <div className="question-meta">
                <span className="difficulty-badge">{question.difficulty}</span>
                <span className="time-limit">⏱️ {question.time_limit_seconds}s</span>
            </div>

            {error && (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            )}

            {/* Answer Mode Toggle */}
            {!saved && (
                <div className="answer-mode-toggle">
                    <button
                        className={`mode-btn ${answerMode === 'voice' ? 'active' : ''}`}
                        onClick={() => setAnswerMode('voice')}
                        disabled={isRecording}
                    >
                        🎤 Voice
                    </button>
                    <button
                        className={`mode-btn ${answerMode === 'text' ? 'active' : ''}`}
                        onClick={() => setAnswerMode('text')}
                        disabled={isRecording}
                    >
                        ✍️ Type
                    </button>
                </div>
            )}

            <div className="recording-section">
                {answerMode === 'text' && !saved ? (
                    /* Text Answer Input */
                    <div className="text-answer-section">
                        <textarea
                            className="text-answer-input"
                            value={textAnswer}
                            onChange={(e) => setTextAnswer(e.target.value)}
                            placeholder="Type your answer here..."
                            rows={5}
                        />
                        <div className="text-answer-info">
                            <span>{textAnswer.trim().split(/\s+/).filter(Boolean).length} words</span>
                        </div>
                        {canSave && (
                            <div className="save-controls">
                                <button className="save-btn" onClick={handleSave}>
                                    ✓ Save Answer
                                </button>
                            </div>
                        )}
                    </div>
                ) : answerMode === 'voice' && !saved ? (
                    /* Voice Recording */
                    <>
                        {!audioBlob && !recordedAnswer ? (
                            <div className="record-controls">
                                {isRecording ? (
                                    <>
                                        <div className="recording-indicator">
                                            <span className="recording-dot"></span>
                                            Recording... {formatDuration(duration)}
                                        </div>
                                        <button
                                            className="stop-btn"
                                            onClick={stopRecording}
                                        >
                                            ⏹️ Stop Recording
                                        </button>
                                    </>
                                ) : (
                                    <button
                                        className="record-btn"
                                        onClick={startRecording}
                                    >
                                        🎤 Start Recording
                                    </button>
                                )}
                            </div>
                        ) : (
                            <div className="playback-controls">
                                {audioUrl && (
                                    <audio controls src={audioUrl} className="audio-player" />
                                )}
                                <div className="duration-info">
                                    Duration: {formatDuration(duration || recordedAnswer?.duration || 0)}
                                </div>
                                {canSave && (
                                    <div className="save-controls">
                                        <button className="save-btn" onClick={handleSave}>
                                            ✓ Save Answer
                                        </button>
                                        <button className="rerecord-btn" onClick={handleReRecord}>
                                            🔄 Re-record
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                ) : saved ? (
                    /* Saved answer display */
                    <div className="playback-controls">
                        {recordedAnswer?.textAnswer ? (
                            <div className="saved-text-answer">
                                <p>{recordedAnswer.textAnswer}</p>
                            </div>
                        ) : audioUrl ? (
                            <audio controls src={audioUrl} className="audio-player" />
                        ) : null}
                        <button className="rerecord-btn" onClick={handleReRecord}>
                            🔄 Re-answer
                        </button>
                    </div>
                ) : null}
            </div>
        </div>
    );
}

// =============================================================================
// INTERVIEW SESSION COMPONENT
// =============================================================================

function InterviewSession({ 
    session, 
    onSubmit, 
    submitting,
    onGenerateAdaptiveFollowup
}) {
    const [recordings, setRecordings] = useState({});
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [viewMode, setViewMode] = useState('single'); // 'single' or 'all'
    const [followupGeneratedFor, setFollowupGeneratedFor] = useState({});

    const questions = session.questions || [];
    const answeredCount = Object.keys(recordings).length;
    const allAnswered = answeredCount === questions.length;

    const handleRecordingComplete = (questionId, audioBlob, duration, textAnswer) => {
        setRecordings(prev => ({
            ...prev,
            [questionId]: { audioBlob, duration, textAnswer }
        }));
    };
    
    const handleSubmit = () => {
        onSubmit(recordings);
    };
    
    const goToNext = async () => {
        const currentQuestion = questions[currentQuestionIndex];
        const currentAnswer = currentQuestion ? recordings[currentQuestion.id] : null;
        const isResumeInterview = session.technology === 'Resume-Based';

        if (
            isResumeInterview &&
            currentQuestion &&
            currentAnswer &&
            !followupGeneratedFor[currentQuestion.id] &&
            onGenerateAdaptiveFollowup
        ) {
            const followupResult = await onGenerateAdaptiveFollowup(
                currentQuestion.id,
                currentAnswer.textAnswer || null
            );

            if (followupResult?.success) {
                setFollowupGeneratedFor(prev => ({ ...prev, [currentQuestion.id]: true }));
            }
        }

        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
        }
    };
    
    const goToPrev = () => {
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(prev => prev - 1);
        }
    };
    
    return (
        <div className="interview-session">
            {/* Header */}
            <div className="session-header">
                <div className="session-info">
                    <h2>{session.technology} Interview</h2>
                    <span className="session-difficulty">{session.difficulty}</span>
                </div>
                
                <div className="progress-info">
                    <div className="progress-bar">
                        <div 
                            className="progress-fill"
                            style={{ width: `${(answeredCount / questions.length) * 100}%` }}
                        />
                    </div>
                    <span className="progress-text">
                        {answeredCount}/{questions.length} answered
                    </span>
                </div>
                
                <div className="view-toggle">
                    <button 
                        className={viewMode === 'single' ? 'active' : ''}
                        onClick={() => setViewMode('single')}
                    >
                        Single View
                    </button>
                    <button 
                        className={viewMode === 'all' ? 'active' : ''}
                        onClick={() => setViewMode('all')}
                    >
                        All Questions
                    </button>
                </div>
            </div>
            
            {/* Questions */}
            {viewMode === 'single' ? (
                <div className="single-question-view">
                    <QuestionRecording
                        question={questions[currentQuestionIndex]}
                        questionNumber={currentQuestionIndex + 1}
                        totalQuestions={questions.length}
                        onRecordingComplete={handleRecordingComplete}
                        recordedAnswer={recordings[questions[currentQuestionIndex]?.id]}
                    />
                    
                    <div className="navigation-controls">
                        <button 
                            className="nav-btn prev"
                            onClick={goToPrev}
                            disabled={currentQuestionIndex === 0}
                        >
                            ← Previous
                        </button>
                        
                        <div className="question-dots">
                            {questions.map((q, i) => (
                                <button
                                    key={q.id}
                                    className={`dot ${i === currentQuestionIndex ? 'active' : ''} ${recordings[q.id] ? 'answered' : ''}`}
                                    onClick={() => setCurrentQuestionIndex(i)}
                                />
                            ))}
                        </div>
                        
                        <button 
                            className="nav-btn next"
                            onClick={goToNext}
                            disabled={currentQuestionIndex === questions.length - 1}
                        >
                            Next →
                        </button>
                    </div>
                </div>
            ) : (
                <div className="all-questions-view">
                    {questions.map((question, index) => (
                        <QuestionRecording
                            key={question.id}
                            question={question}
                            questionNumber={index + 1}
                            totalQuestions={questions.length}
                            onRecordingComplete={handleRecordingComplete}
                            recordedAnswer={recordings[question.id]}
                        />
                    ))}
                </div>
            )}
            
            {/* Submit Button */}
            <div className="submit-section">
                <button
                    className="submit-btn"
                    onClick={handleSubmit}
                    disabled={answeredCount === 0 || submitting}
                >
                    {submitting ? (
                        <>
                            <span className="spinner"></span>
                            Evaluating Answers...
                        </>
                    ) : allAnswered ? (
                        '📤 Submit Interview'
                    ) : answeredCount > 0 ? (
                        `📤 Submit (${answeredCount}/${questions.length} answered)`
                    ) : (
                        'Record at least one answer to submit'
                    )}
                </button>

                {!allAnswered && answeredCount > 0 && (
                    <p className="submit-hint">
                        Unanswered questions will receive a score of 0. Record all {questions.length} questions for best results.
                    </p>
                )}
                {answeredCount === 0 && (
                    <p className="submit-hint">
                        Please record answers for at least one question to submit
                    </p>
                )}
            </div>
        </div>
    );
}

// =============================================================================
// RESULTS COMPONENT
// =============================================================================

function InterviewResults({ results, onNewInterview }) {
    const navigate = useNavigate();
    const [expandedQuestion, setExpandedQuestion] = useState(null);
    
    const getScoreColor = (score, max = 5) => {
        const percentage = (score / max) * 100;
        if (percentage >= 80) return 'excellent';
        if (percentage >= 60) return 'good';
        if (percentage >= 40) return 'average';
        return 'poor';
    };
    
    const renderScoreBar = (score, max = 5, label) => (
        <div className="score-bar-container">
            <div className="score-label">{label}</div>
            <div className="score-bar">
                <div 
                    className={`score-fill ${getScoreColor(score, max)}`}
                    style={{ width: `${(score / max) * 100}%` }}
                />
            </div>
            <div className="score-value">{score.toFixed(1)}/{max}</div>
        </div>
    );
    
    return (
        <div className="interview-results">
            {/* Summary Header */}
            <div className="results-header">
                <div className="results-title">
                    <h1>🎉 Interview Complete!</h1>
                    <p>{results.technology} - {results.difficulty}</p>
                </div>
                
                <div className={`grade-circle ${getScoreColor(results.percentage_score, 100)}`}>
                    <span className="grade">{results.grade}</span>
                    <span className="percentage">{results.percentage_score.toFixed(0)}%</span>
                </div>
            </div>
            
            {/* Total Score */}
            <div className="total-score-section">
                <h2>📊 Overall Score</h2>
                <div className="total-score">
                    <span className="score">{results.total_score.toFixed(1)}</span>
                    <span className="max">/ {results.max_possible_score.toFixed(1)}</span>
                </div>
                <p className="performance-summary">{results.performance_summary}</p>
            </div>
            
            {/* Category Scores */}
            <div className="category-scores">
                <h3>Score Breakdown</h3>
                {renderScoreBar(results.total_grammar_score, results.question_scores.length * 5, '📝 Grammar')}
                {renderScoreBar(results.total_fluency_score, results.question_scores.length * 5, '🗣️ Fluency')}
                {renderScoreBar(results.total_structure_score, results.question_scores.length * 5, '🏗️ Structure')}
                {renderScoreBar(results.total_similarity_score, results.question_scores.length * 5, '🎯 Accuracy')}
            </div>
            
            {/* Overall Feedback */}
            <div className="overall-feedback">
                <div className="strengths-section">
                    <h3>💪 Strengths</h3>
                    <ul>
                        {results.overall_strengths.map((strength, i) => (
                            <li key={i}>{strength}</li>
                        ))}
                    </ul>
                </div>
                
                <div className="improvements-section">
                    <h3>📈 Areas for Improvement</h3>
                    <ul>
                        {results.overall_improvements.map((improvement, i) => (
                            <li key={i}>{improvement}</li>
                        ))}
                    </ul>
                </div>
            </div>
            
            {/* Question-wise Results */}
            <div className="question-results">
                <h2>📋 Question-wise Results</h2>
                
                {results.question_scores.map((qs, index) => (
                    <div 
                        key={qs.question_id}
                        className={`question-result-card ${expandedQuestion === qs.question_id ? 'expanded' : ''}`}
                    >
                        <div 
                            className="question-result-header"
                            onClick={() => setExpandedQuestion(
                                expandedQuestion === qs.question_id ? null : qs.question_id
                            )}
                        >
                            <div className="question-info">
                                <span className="q-number">Q{qs.question_number}</span>
                                <span className="q-text">{qs.question_text}</span>
                            </div>
                            <div className={`q-score ${getScoreColor(qs.overall_score)}`}>
                                {qs.overall_score.toFixed(1)}/5
                            </div>
                        </div>
                        
                        {expandedQuestion === qs.question_id && (
                            <div className="question-result-details">
                                {/* Your Answer */}
                                <div className="answer-section">
                                    <h4>Your Answer:</h4>
                                    {qs.transcript && qs.transcript.trim() ? (
                                        <p className="transcript">{qs.transcript}</p>
                                    ) : (
                                        <p className="transcript no-answer">
                                            No answer recorded or speech was not detected.
                                        </p>
                                    )}
                                </div>
                                
                                {/* Score Breakdown */}
                                <div className="score-breakdown">
                                    <h4>Score Breakdown:</h4>
                                    <div className="mini-scores">
                                        <div className="mini-score">
                                            <span>Grammar</span>
                                            <span className={getScoreColor(qs.grammar_score)}>{qs.grammar_score.toFixed(1)}/5</span>
                                        </div>
                                        <div className="mini-score">
                                            <span>Fluency</span>
                                            <span className={getScoreColor(qs.fluency_score)}>{qs.fluency_score.toFixed(1)}/5</span>
                                        </div>
                                        <div className="mini-score">
                                            <span>Structure</span>
                                            <span className={getScoreColor(qs.structure_score)}>{qs.structure_score.toFixed(1)}/5</span>
                                        </div>
                                        <div className="mini-score">
                                            <span>Accuracy</span>
                                            <span className={getScoreColor(qs.similarity_score)}>{qs.similarity_score.toFixed(1)}/5</span>
                                        </div>
                                    </div>
                                </div>
                                
                                {/* Feedback */}
                                <div className="feedback-section">
                                    {qs.strengths.length > 0 && (
                                        <div className="q-strengths">
                                            <h4>✅ Strengths:</h4>
                                            <ul>
                                                {qs.strengths.map((s, i) => <li key={i}>{s}</li>)}
                                            </ul>
                                        </div>
                                    )}
                                    
                                    {qs.improvements.length > 0 && (
                                        <div className="q-improvements">
                                            <h4>💡 Improvements:</h4>
                                            <ul>
                                                {qs.improvements.map((i, idx) => <li key={idx}>{i}</li>)}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                                
                                {/* Ideal Answer */}
                                {qs.ideal_answer && (
                                    <div className="ideal-answer-section">
                                        <h4>📖 Ideal Answer:</h4>
                                        <p className="ideal-answer">{qs.ideal_answer}</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
            
            {/* Actions */}
            <div className="results-actions">
                <button className="new-interview-btn" onClick={onNewInterview}>
                    🔄 Start New Interview
                </button>
                <button className="history-btn" onClick={() => navigate('/history')}>
                    📚 View History
                </button>
            </div>
        </div>
    );
}

// =============================================================================
// RESUME INTERVIEW SETUP COMPONENT
// =============================================================================

function ResumeInterviewSetup({ onStart, loading }) {
    const [difficulty, setDifficulty] = useState('medium');
    const [numQuestions, setNumQuestions] = useState(5);

    const handleStart = () => {
        onStart(difficulty, numQuestions);
    };

    return (
        <div className="skill-selection resume-interview-setup">
            <div className="selection-header">
                <h1>📄 Resume-Based Interview</h1>
                <p>Questions will be generated based on your resume - projects, skills, and experience</p>
            </div>

            {/* Difficulty Selection */}
            <div className="difficulty-selection">
                <h3>Select Difficulty</h3>
                <div className="difficulty-options">
                    {['easy', 'medium', 'hard'].map(level => (
                        <button
                            key={level}
                            className={`difficulty-btn ${difficulty === level ? 'active' : ''} ${level}`}
                            onClick={() => setDifficulty(level)}
                        >
                            {level === 'easy' && '🟢 Easy'}
                            {level === 'medium' && '🟡 Medium'}
                            {level === 'hard' && '🔴 Hard'}
                        </button>
                    ))}
                </div>
            </div>

            {/* Number of Questions */}
            <div className="question-count-selection">
                <h3>Number of Questions: <span className="count-value">{numQuestions}</span></h3>
                <div className="question-count-slider">
                    <span className="slider-label">3</span>
                    <input
                        type="range"
                        min="3"
                        max="10"
                        value={numQuestions}
                        onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                        className="count-slider"
                    />
                    <span className="slider-label">10</span>
                </div>
            </div>

            {/* Start Button */}
            <div className="start-section">
                <button
                    className="start-btn"
                    onClick={handleStart}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <span className="spinner"></span>
                            Generating Questions from Resume...
                        </>
                    ) : (
                        <>
                            🚀 Start Resume Interview - {numQuestions} Questions
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

// =============================================================================
// MAIN PAGE COMPONENT
// =============================================================================

function SkillInterviewPage() {
    const [searchParams] = useSearchParams();
    const interviewType = searchParams.get('type'); // 'resume' or null

    const [step, setStep] = useState(STEPS.SELECT_SKILL);
    const [technologies, setTechnologies] = useState([]);
    const [session, setSession] = useState(null);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);

    debug('SkillInterviewPage', 'Component mounted', { interviewType });

    // Check backend health and load technologies on mount
    useEffect(() => {
        const initPage = async () => {
            debug('SkillInterviewPage', '=== PAGE INIT ===');

            // First check backend health
            debug('SkillInterviewPage', 'Checking backend health...');
            const healthCheck = await skillInterviewApi.checkBackendHealth();
            debug('SkillInterviewPage', 'Backend health result', healthCheck);

            if (!healthCheck.isUp) {
                console.error('[PAGE] Backend is not reachable!');
                console.error('[PAGE] Make sure backend is running at http://localhost:8000');
                setError('Backend server is not reachable. Please start the backend server.');
                return;
            }

            // If resume interview, show setup page (don't auto-start)
            if (interviewType === 'resume') {
                debug('SkillInterviewPage', 'Resume interview mode - showing setup');
                return;
            }

            debug('SkillInterviewPage', 'Loading technologies...');
            setLoading(true);
            const result = await skillInterviewApi.getTechnologies();
            debug('SkillInterviewPage', 'Technologies result', result);

            if (result.success) {
                debug('SkillInterviewPage', 'Technologies loaded', result.data.technologies?.length);
                setTechnologies(result.data.technologies || []);
            } else {
                debug('SkillInterviewPage', 'Technologies load FAILED', result.error);
                setError('Failed to load technologies: ' + (result.error?.message || 'Unknown error'));
            }
            setLoading(false);
        };

        initPage();
    }, [interviewType]);
    
    // Handle skill selection and start interview
    const handleSkillSelect = async (technology, difficulty, numQuestions) => {
        debug('SkillInterviewPage', 'Starting interview', { technology: technology.name, difficulty, numQuestions });
        setLoading(true);
        setError(null);

        // Re-check backend before starting
        const healthCheck = await skillInterviewApi.checkBackendHealth();
        if (!healthCheck.isUp) {
            setError('Backend server disconnected. Please restart the backend.');
            setLoading(false);
            return;
        }

        const result = await skillInterviewApi.startInterview({
            technology: technology.name,
            num_questions: numQuestions,
            difficulty: difficulty,
        });

        debug('SkillInterviewPage', 'Start interview result', result);

        if (result.success) {
            debug('SkillInterviewPage', 'Interview started successfully', result.data);
            setSession(result.data);
            setStep(STEPS.ANSWER_QUESTIONS);
        } else {
            debug('SkillInterviewPage', 'Interview start FAILED', result.error);
            setError(result.error?.message || 'Failed to start interview');
        }

        setLoading(false);
    };

    // Handle resume interview start
    const handleResumeStart = async (difficulty, numQuestions) => {
        debug('SkillInterviewPage', 'Starting resume interview', { difficulty, numQuestions });
        setLoading(true);
        setError(null);

        const result = await skillInterviewApi.startResumeInterview({
            num_questions: numQuestions,
            difficulty: difficulty,
        });

        debug('SkillInterviewPage', 'Resume interview result', result);

        if (result.success) {
            setSession(result.data);
            setStep(STEPS.ANSWER_QUESTIONS);
        } else {
            setError(result.error?.message || 'Failed to start resume interview. Please upload your resume first.');
        }

        setLoading(false);
    };
    
    // Handle interview submission
    const handleSubmit = async (recordings) => {
        debug('SkillInterviewPage', 'Submitting interview', { questionCount: Object.keys(recordings).length });
        setSubmitting(true);
        setError(null);

        try {
            // Upload all answers (audio or text)
            for (const [questionId, { audioBlob, duration, textAnswer }] of Object.entries(recordings)) {
                if (textAnswer) {
                    // Text answer - submit via text endpoint
                    debug('SkillInterviewPage', 'Submitting text answer', { questionId, length: textAnswer.length });
                    const textResult = await skillInterviewApi.submitTextAnswer(
                        session.session_id,
                        questionId,
                        textAnswer
                    );
                    if (!textResult.success) {
                        throw new Error(`Failed to submit text answer for question ${questionId}`);
                    }
                } else if (audioBlob) {
                    // Audio answer - upload audio file
                    debug('SkillInterviewPage', 'Uploading audio', { questionId, blobSize: audioBlob?.size, duration });
                    const uploadResult = await skillInterviewApi.uploadAudio(
                        session.session_id,
                        questionId,
                        audioBlob,
                        duration
                    );
                    if (!uploadResult.success) {
                        throw new Error(`Failed to upload answer for question ${questionId}`);
                    }
                }
            }

            // Submit for evaluation
            const submitResult = await skillInterviewApi.submitInterview(session.session_id);

            if (submitResult.success) {
                setResults(submitResult.data);
                setStep(STEPS.RESULTS);
            } else {
                throw new Error(submitResult.error?.message || 'Failed to evaluate interview');
            }

        } catch (err) {
            setError(err.message);
        }

        setSubmitting(false);
    };
    
    // Handle new interview
    const handleNewInterview = () => {
        setSession(null);
        setResults(null);
        setStep(STEPS.SELECT_SKILL);
    };
    
    // Render based on step
    return (
        <div className="skill-interview-page">
            {error && (
                <div className="error-banner">
                    ⚠️ {error}
                    <button onClick={() => setError(null)}>✕</button>
                </div>
            )}
            
            {step === STEPS.SELECT_SKILL && (
                interviewType === 'resume' ? (
                    <ResumeInterviewSetup
                        onStart={handleResumeStart}
                        loading={loading}
                    />
                ) : (
                    <SkillSelection
                        technologies={technologies}
                        onSelect={handleSkillSelect}
                        loading={loading}
                    />
                )
            )}
            
            {step === STEPS.ANSWER_QUESTIONS && session && (
                <InterviewSession
                    session={session}
                    onSubmit={handleSubmit}
                    submitting={submitting}
                />
            )}
            
            {step === STEPS.RESULTS && results && (
                <InterviewResults
                    results={results}
                    onNewInterview={handleNewInterview}
                />
            )}
        </div>
    );
}

export default SkillInterviewPage;
