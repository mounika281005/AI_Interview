/**
 * VoiceRecorder.js
 * 
 * A reusable voice recording component for capturing interview answers.
 * Uses the Web Audio API and MediaRecorder.
 * 
 * @example
 * const recorder = new VoiceRecorder();
 * await recorder.startRecording();
 * // ... user speaks ...
 * recorder.stopRecording();
 * const audioBlob = recorder.getAudioBlob();
 */

class VoiceRecorder {
    constructor(options = {}) {
        // Configuration with defaults
        this.config = {
            mimeType: options.mimeType || 'audio/webm',
            audioBitsPerSecond: options.audioBitsPerSecond || 128000,
            chunkInterval: options.chunkInterval || 1000, // Save chunk every 1 second
            maxDuration: options.maxDuration || 300, // Max 5 minutes
            onChunkReceived: options.onChunkReceived || null,
            onRecordingComplete: options.onRecordingComplete || null,
            onError: options.onError || null,
            onPermissionDenied: options.onPermissionDenied || null,
        };

        // Internal state
        this.mediaStream = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioBlob = null;
        this.audioURL = null;
        this.isRecording = false;
        this.isPaused = false;
        this.recordingStartTime = null;
        this.recordingDuration = 0;
        this.maxDurationTimer = null;

        // Audio visualization (optional)
        this.audioContext = null;
        this.analyser = null;
    }

    // ========================================
    // PUBLIC METHODS
    // ========================================

    /**
     * Check if browser supports audio recording
     * @returns {boolean}
     */
    static isSupported() {
        return !!(
            navigator.mediaDevices &&
            navigator.mediaDevices.getUserMedia &&
            window.MediaRecorder
        );
    }

    /**
     * Request microphone permission
     * @returns {Promise<boolean>}
     */
    async requestPermission() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100,
                    channelCount: 1, // Mono audio (smaller files)
                }
            });
            return true;
        } catch (error) {
            this._handleError('permission', error);
            return false;
        }
    }

    /**
     * Start recording audio
     * @returns {Promise<void>}
     */
    async startRecording() {
        // Check support
        if (!VoiceRecorder.isSupported()) {
            throw new Error('Audio recording not supported in this browser');
        }

        // Request permission if needed
        if (!this.mediaStream) {
            const granted = await this.requestPermission();
            if (!granted) {
                throw new Error('Microphone permission required');
            }
        }

        // Reset state
        this.audioChunks = [];
        this.audioBlob = null;
        this.audioURL = null;
        this.recordingDuration = 0;

        // Create MediaRecorder
        const mimeType = this._getSupportedMimeType();
        this.mediaRecorder = new MediaRecorder(this.mediaStream, {
            mimeType: mimeType,
            audioBitsPerSecond: this.config.audioBitsPerSecond,
        });

        // Set up event handlers
        this._setupRecorderEvents();

        // Start recording
        this.mediaRecorder.start(this.config.chunkInterval);
        this.isRecording = true;
        this.isPaused = false;
        this.recordingStartTime = Date.now();

        // Set max duration timer
        if (this.config.maxDuration > 0) {
            this.maxDurationTimer = setTimeout(() => {
                console.warn('Max recording duration reached');
                this.stopRecording();
            }, this.config.maxDuration * 1000);
        }

        console.log('Recording started');
    }

    /**
     * Pause recording
     */
    pauseRecording() {
        if (this.mediaRecorder && this.isRecording && !this.isPaused) {
            this.mediaRecorder.pause();
            this.isPaused = true;
            this.recordingDuration += Date.now() - this.recordingStartTime;
            console.log('Recording paused');
        }
    }

    /**
     * Resume recording
     */
    resumeRecording() {
        if (this.mediaRecorder && this.isRecording && this.isPaused) {
            this.mediaRecorder.resume();
            this.isPaused = false;
            this.recordingStartTime = Date.now();
            console.log('Recording resumed');
        }
    }

    /**
     * Stop recording
     * @returns {Promise<Blob>}
     */
    stopRecording() {
        return new Promise((resolve) => {
            if (!this.mediaRecorder || !this.isRecording) {
                resolve(this.audioBlob);
                return;
            }

            // Clear max duration timer
            if (this.maxDurationTimer) {
                clearTimeout(this.maxDurationTimer);
                this.maxDurationTimer = null;
            }

            // Calculate final duration
            if (!this.isPaused) {
                this.recordingDuration += Date.now() - this.recordingStartTime;
            }

            // Set up completion handler
            this.mediaRecorder.onstop = () => {
                this._processRecording();
                this.isRecording = false;
                this.isPaused = false;
                resolve(this.audioBlob);
            };

            // Stop recording
            this.mediaRecorder.stop();
            console.log('Recording stopped');
        });
    }

    /**
     * Get the recorded audio as a Blob
     * @returns {Blob|null}
     */
    getAudioBlob() {
        return this.audioBlob;
    }

    /**
     * Get a playable URL for the recorded audio
     * @returns {string|null}
     */
    getAudioURL() {
        if (!this.audioURL && this.audioBlob) {
            this.audioURL = URL.createObjectURL(this.audioBlob);
        }
        return this.audioURL;
    }

    /**
     * Get recording duration in seconds
     * @returns {number}
     */
    getDuration() {
        if (this.isRecording && !this.isPaused) {
            return (this.recordingDuration + (Date.now() - this.recordingStartTime)) / 1000;
        }
        return this.recordingDuration / 1000;
    }

    /**
     * Get current recording state
     * @returns {Object}
     */
    getState() {
        return {
            isRecording: this.isRecording,
            isPaused: this.isPaused,
            duration: this.getDuration(),
            hasRecording: !!this.audioBlob,
        };
    }

    /**
     * Clean up resources
     */
    cleanup() {
        // Stop recording if active
        if (this.isRecording) {
            this.stopRecording();
        }

        // Stop media tracks
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }

        // Revoke object URL
        if (this.audioURL) {
            URL.revokeObjectURL(this.audioURL);
            this.audioURL = null;
        }

        // Clear timers
        if (this.maxDurationTimer) {
            clearTimeout(this.maxDurationTimer);
        }

        // Close audio context
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }

        console.log('VoiceRecorder cleaned up');
    }

    // ========================================
    // AUDIO VISUALIZATION (Optional)
    // ========================================

    /**
     * Set up audio visualization
     * @returns {AnalyserNode}
     */
    setupVisualization() {
        if (!this.mediaStream) {
            throw new Error('No media stream available');
        }

        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = this.audioContext.createMediaStreamSource(this.mediaStream);
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        source.connect(this.analyser);

        return this.analyser;
    }

    /**
     * Get current audio level (0-1)
     * @returns {number}
     */
    getAudioLevel() {
        if (!this.analyser) return 0;

        const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(dataArray);

        const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        return average / 255;
    }

    // ========================================
    // PRIVATE METHODS
    // ========================================

    _setupRecorderEvents() {
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
                if (this.config.onChunkReceived) {
                    this.config.onChunkReceived(event.data);
                }
            }
        };

        this.mediaRecorder.onerror = (event) => {
            this._handleError('recording', event.error);
        };
    }

    _processRecording() {
        const mimeType = this._getSupportedMimeType();
        this.audioBlob = new Blob(this.audioChunks, { type: mimeType });

        console.log(`Recording complete: ${this.audioBlob.size} bytes, ${this.getDuration().toFixed(1)}s`);

        if (this.config.onRecordingComplete) {
            this.config.onRecordingComplete({
                blob: this.audioBlob,
                duration: this.getDuration(),
                mimeType: mimeType,
            });
        }
    }

    _getSupportedMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/ogg;codecs=opus',
            'audio/wav',
        ];

        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }

        return 'audio/webm';
    }

    _handleError(type, error) {
        console.error(`VoiceRecorder ${type} error:`, error);

        if (type === 'permission' && error.name === 'NotAllowedError') {
            if (this.config.onPermissionDenied) {
                this.config.onPermissionDenied();
            }
        }

        if (this.config.onError) {
            this.config.onError(type, error);
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceRecorder;
}
