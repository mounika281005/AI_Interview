import React, { useState, useRef, useCallback, useEffect } from 'react';

/**
 * useVoiceRecorder Hook
 * 
 * A React hook for voice recording functionality.
 * Provides state and methods for recording interview answers.
 * 
 * @example
 * const { isRecording, startRecording, stopRecording, audioBlob } = useVoiceRecorder();
 */

export const useVoiceRecorder = (options = {}) => {
    const {
        maxDuration = 300, // 5 minutes default
        onRecordingComplete = null,
        onError = null,
    } = options;

    // State
    const [isRecording, setIsRecording] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [duration, setDuration] = useState(0);
    const [audioBlob, setAudioBlob] = useState(null);
    const [audioURL, setAudioURL] = useState(null);
    const [error, setError] = useState(null);
    const [permissionGranted, setPermissionGranted] = useState(false);

    // Refs
    const mediaStreamRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);
    const startTimeRef = useRef(null);

    // Get supported MIME type
    const getSupportedMimeType = useCallback(() => {
        const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'];
        return types.find(type => MediaRecorder.isTypeSupported(type)) || 'audio/webm';
    }, []);

    // Request microphone permission
    const requestPermission = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                }
            });
            mediaStreamRef.current = stream;
            setPermissionGranted(true);
            setError(null);
            return true;
        } catch (err) {
            setError(err.message);
            setPermissionGranted(false);
            if (onError) onError(err);
            return false;
        }
    }, [onError]);

    // Start recording
    const startRecording = useCallback(async () => {
        setError(null);

        // Request permission if not granted
        if (!mediaStreamRef.current) {
            const granted = await requestPermission();
            if (!granted) return;
        }

        // Reset state
        audioChunksRef.current = [];
        setAudioBlob(null);
        setAudioURL(null);
        setDuration(0);

        // Create recorder
        const mimeType = getSupportedMimeType();
        const recorder = new MediaRecorder(mediaStreamRef.current, { mimeType });

        recorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunksRef.current.push(event.data);
            }
        };

        recorder.onstop = () => {
            const blob = new Blob(audioChunksRef.current, { type: mimeType });
            const url = URL.createObjectURL(blob);
            setAudioBlob(blob);
            setAudioURL(url);
            setIsRecording(false);
            setIsPaused(false);

            if (onRecordingComplete) {
                onRecordingComplete({ blob, url, duration });
            }
        };

        mediaRecorderRef.current = recorder;
        recorder.start(1000); // Chunk every second
        startTimeRef.current = Date.now();
        setIsRecording(true);

        // Duration timer
        timerRef.current = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
            setDuration(elapsed);

            // Auto-stop at max duration
            if (elapsed >= maxDuration) {
                stopRecording();
            }
        }, 1000);

    }, [requestPermission, getSupportedMimeType, maxDuration, onRecordingComplete]);

    // Stop recording
    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        }
    }, [isRecording]);

    // Pause recording
    const pauseRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording && !isPaused) {
            mediaRecorderRef.current.pause();
            setIsPaused(true);
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        }
    }, [isRecording, isPaused]);

    // Resume recording
    const resumeRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording && isPaused) {
            mediaRecorderRef.current.resume();
            setIsPaused(false);
            startTimeRef.current = Date.now() - (duration * 1000);
            timerRef.current = setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
                setDuration(elapsed);
            }, 1000);
        }
    }, [isRecording, isPaused, duration]);

    // Reset recording
    const resetRecording = useCallback(() => {
        if (audioURL) {
            URL.revokeObjectURL(audioURL);
        }
        setAudioBlob(null);
        setAudioURL(null);
        setDuration(0);
        setError(null);
    }, [audioURL]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
            if (mediaStreamRef.current) {
                mediaStreamRef.current.getTracks().forEach(track => track.stop());
            }
            if (audioURL) {
                URL.revokeObjectURL(audioURL);
            }
        };
    }, [audioURL]);

    // Format duration as MM:SS
    const formattedDuration = `${Math.floor(duration / 60).toString().padStart(2, '0')}:${(duration % 60).toString().padStart(2, '0')}`;

    return {
        // State
        isRecording,
        isPaused,
        duration,
        formattedDuration,
        audioBlob,
        audioURL,
        error,
        permissionGranted,

        // Methods
        requestPermission,
        startRecording,
        stopRecording,
        pauseRecording,
        resumeRecording,
        resetRecording,
    };
};

/**
 * VoiceRecorderComponent
 * 
 * A ready-to-use React component for voice recording.
 */
export const VoiceRecorderComponent = ({
    questionText = "Please answer the question",
    onRecordingComplete,
    onSubmit,
    maxDuration = 180,
}) => {
    const {
        isRecording,
        isPaused,
        formattedDuration,
        audioBlob,
        audioURL,
        error,
        startRecording,
        stopRecording,
        pauseRecording,
        resumeRecording,
        resetRecording,
    } = useVoiceRecorder({ maxDuration, onRecordingComplete });

    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async () => {
        if (!audioBlob || !onSubmit) return;

        setIsSubmitting(true);
        try {
            await onSubmit(audioBlob);
        } catch (err) {
            console.error('Submit error:', err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="voice-recorder">
            {/* Question Display */}
            <div className="question-box">
                <h3>Question:</h3>
                <p>{questionText}</p>
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            )}

            {/* Recording Indicator */}
            {isRecording && (
                <div className="recording-indicator">
                    <span className="recording-dot">🔴</span>
                    <span>{isPaused ? 'Paused' : 'Recording'}</span>
                    <span className="timer">{formattedDuration}</span>
                </div>
            )}

            {/* Controls */}
            <div className="controls">
                {!isRecording && !audioBlob && (
                    <button onClick={startRecording} className="btn btn-start">
                        🎤 Start Recording
                    </button>
                )}

                {isRecording && (
                    <>
                        {!isPaused ? (
                            <button onClick={pauseRecording} className="btn btn-pause">
                                ⏸️ Pause
                            </button>
                        ) : (
                            <button onClick={resumeRecording} className="btn btn-resume">
                                ▶️ Resume
                            </button>
                        )}
                        <button onClick={stopRecording} className="btn btn-stop">
                            ⏹️ Stop
                        </button>
                    </>
                )}
            </div>

            {/* Audio Preview */}
            {audioURL && (
                <div className="audio-preview">
                    <h4>Your Recording:</h4>
                    <audio controls src={audioURL} />
                    <div className="preview-controls">
                        <button onClick={resetRecording} className="btn btn-retry">
                            🔄 Record Again
                        </button>
                        <button
                            onClick={handleSubmit}
                            disabled={isSubmitting}
                            className="btn btn-submit"
                        >
                            {isSubmitting ? '⏳ Submitting...' : '📤 Submit Answer'}
                        </button>
                    </div>
                </div>
            )}

            <style jsx>{`
                .voice-recorder {
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                
                .question-box {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }
                
                .error-message {
                    background: #fee;
                    color: #c00;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                }
                
                .recording-indicator {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    padding: 15px;
                    background: #fff3f3;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }
                
                .recording-dot {
                    animation: pulse 1s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                
                .timer {
                    font-family: monospace;
                    font-size: 1.2em;
                    font-weight: bold;
                }
                
                .controls {
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    margin-bottom: 20px;
                }
                
                .btn {
                    padding: 12px 24px;
                    font-size: 16px;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    transition: transform 0.2s, opacity 0.2s;
                }
                
                .btn:hover {
                    transform: scale(1.05);
                }
                
                .btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .btn-start { background: #4CAF50; color: white; }
                .btn-pause { background: #ff9800; color: white; }
                .btn-resume { background: #2196F3; color: white; }
                .btn-stop { background: #f44336; color: white; }
                .btn-retry { background: #9e9e9e; color: white; }
                .btn-submit { background: #4CAF50; color: white; }
                
                .audio-preview {
                    text-align: center;
                    padding: 20px;
                    background: #f5f5f5;
                    border-radius: 10px;
                }
                
                .audio-preview audio {
                    width: 100%;
                    margin: 10px 0;
                }
                
                .preview-controls {
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    margin-top: 15px;
                }
            `}</style>
        </div>
    );
};

export default VoiceRecorderComponent;
