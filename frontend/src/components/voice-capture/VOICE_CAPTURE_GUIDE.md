# Voice Input Capture for Interview Answers

## Overview for Students

This guide explains how to capture a user's voice through their microphone in a web browser, record their interview answers, and send the audio to your backend for processing.

---

## How It Works (Simple Flow)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VOICE CAPTURE FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    USER                     BROWSER                    BACKEND
      │                         │                          │
      │  1. Click "Start"       │                          │
      │────────────────────────▶│                          │
      │                         │                          │
      │  2. "Allow microphone?" │                          │
      │◀────────────────────────│                          │
      │                         │                          │
      │  3. Grant Permission    │                          │
      │────────────────────────▶│                          │
      │                         │                          │
      │  4. 🎤 Recording...     │                          │
      │  ══════════════════════ │                          │
      │  (User speaks answer)   │                          │
      │                         │                          │
      │  5. Click "Stop"        │                          │
      │────────────────────────▶│                          │
      │                         │                          │
      │                         │  6. Send Audio File      │
      │                         │─────────────────────────▶│
      │                         │                          │
      │                         │  7. Processing Complete  │
      │                         │◀─────────────────────────│
      │  8. Show Feedback       │                          │
      │◀────────────────────────│                          │
      │                         │                          │
```

---

## Key Concepts for Students

### What APIs Do We Use?

| API | Purpose | Browser Support |
|-----|---------|-----------------|
| `navigator.mediaDevices.getUserMedia()` | Access microphone | All modern browsers |
| `MediaRecorder` | Record audio stream | All modern browsers |
| `Blob` | Store audio data | All browsers |
| `FormData` | Send file to server | All browsers |

### The Recording Process

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Request    │     │   Capture    │     │   Record     │     │    Save      │
│  Microphone  │────▶│   Audio      │────▶│   Chunks     │────▶│   as Blob    │
│  Permission  │     │   Stream     │     │   (pieces)   │     │   (file)     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## Step-by-Step Implementation

### Step 1: HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Voice Recorder</title>
    <style>
        .recorder-container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
            font-family: Arial, sans-serif;
        }
        
        .question-box {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .record-btn {
            padding: 15px 40px;
            font-size: 18px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
        }
        
        .start-btn {
            background: #4CAF50;
            color: white;
        }
        
        .stop-btn {
            background: #f44336;
            color: white;
        }
        
        .record-btn:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }
        
        .recording-indicator {
            display: none;
            color: #f44336;
            font-weight: bold;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .audio-preview {
            margin-top: 20px;
        }
        
        .status-message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 5px;
        }
        
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #cce5ff; color: #004085; }
    </style>
</head>
<body>
    <div class="recorder-container">
        <div class="question-box">
            <h2>Interview Question:</h2>
            <p id="question-text">Tell me about yourself and your experience.</p>
        </div>
        
        <div class="recording-indicator" id="recording-indicator">
            🔴 Recording... <span id="timer">00:00</span>
        </div>
        
        <div class="controls">
            <button class="record-btn start-btn" id="start-btn">
                🎤 Start Recording
            </button>
            <button class="record-btn stop-btn" id="stop-btn" disabled>
                ⏹️ Stop Recording
            </button>
        </div>
        
        <div class="audio-preview" id="audio-preview">
            <!-- Audio player will appear here after recording -->
        </div>
        
        <div id="status-message"></div>
        
        <button class="record-btn" id="submit-btn" style="background: #2196F3; color: white; display: none;">
            📤 Submit Answer
        </button>
    </div>

    <script src="voice-recorder.js"></script>
</body>
</html>
```

### Step 2: JavaScript - Voice Recorder Class

```javascript
/**
 * VoiceRecorder Class
 * 
 * A simple class to handle voice recording in the browser.
 * Perfect for interview answer capture.
 * 
 * HOW IT WORKS:
 * 1. getUserMedia() asks for microphone permission
 * 2. MediaRecorder captures the audio stream
 * 3. Audio is saved in chunks (small pieces)
 * 4. When stopped, chunks combine into a Blob (file)
 */

class VoiceRecorder {
    constructor() {
        // Store the audio stream from microphone
        this.mediaStream = null;
        
        // The recorder object that captures audio
        this.mediaRecorder = null;
        
        // Array to store audio pieces as they're recorded
        this.audioChunks = [];
        
        // The final audio file (Blob)
        this.audioBlob = null;
        
        // Recording state
        this.isRecording = false;
        
        // Timer for recording duration
        this.recordingStartTime = null;
        this.timerInterval = null;
    }

    /**
     * STEP 1: Request Microphone Access
     * 
     * This asks the user for permission to use their microphone.
     * The browser will show a popup asking "Allow microphone?"
     * 
     * Returns: Promise<boolean> - true if permission granted
     */
    async requestMicrophoneAccess() {
        try {
            console.log('Requesting microphone access...');
            
            // navigator.mediaDevices.getUserMedia() is the key API
            // { audio: true } means we only want audio, not video
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    // Audio settings for good quality
                    echoCancellation: true,  // Remove echo
                    noiseSuppression: true,  // Reduce background noise
                    sampleRate: 44100        // CD quality audio
                }
            });
            
            console.log('Microphone access granted!');
            return true;
            
        } catch (error) {
            // Handle different types of errors
            if (error.name === 'NotAllowedError') {
                console.error('User denied microphone permission');
                throw new Error('Microphone permission denied. Please allow access to record.');
            } else if (error.name === 'NotFoundError') {
                console.error('No microphone found');
                throw new Error('No microphone found. Please connect a microphone.');
            } else {
                console.error('Error accessing microphone:', error);
                throw new Error('Could not access microphone. Please try again.');
            }
        }
    }

    /**
     * STEP 2: Start Recording
     * 
     * Begins capturing audio from the microphone.
     * Audio is stored in chunks as it's recorded.
     */
    async startRecording() {
        // First, make sure we have microphone access
        if (!this.mediaStream) {
            await this.requestMicrophoneAccess();
        }
        
        // Clear any previous recording
        this.audioChunks = [];
        this.audioBlob = null;
        
        // Create MediaRecorder with the audio stream
        // MediaRecorder is what actually records the audio
        this.mediaRecorder = new MediaRecorder(this.mediaStream, {
            mimeType: this.getSupportedMimeType()  // Audio format
        });
        
        // EVENT: When audio data is available
        // This fires periodically with chunks of audio
        this.mediaRecorder.ondataavailable = (event) => {
            // Only save chunks that have data
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
                console.log(`Received audio chunk: ${event.data.size} bytes`);
            }
        };
        
        // EVENT: When recording stops
        this.mediaRecorder.onstop = () => {
            console.log('Recording stopped, processing audio...');
            this.processRecording();
        };
        
        // EVENT: If an error occurs
        this.mediaRecorder.onerror = (event) => {
            console.error('Recording error:', event.error);
        };
        
        // Start recording!
        // The parameter (1000) means save a chunk every 1 second
        this.mediaRecorder.start(1000);
        this.isRecording = true;
        this.recordingStartTime = Date.now();
        
        console.log('Recording started!');
    }

    /**
     * STEP 3: Stop Recording
     * 
     * Stops the recording and triggers processing.
     */
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            console.log('Recording stop requested...');
        }
    }

    /**
     * STEP 4: Process the Recording
     * 
     * Combines all audio chunks into a single Blob (file).
     * This is called automatically when recording stops.
     */
    processRecording() {
        // Combine all chunks into one Blob
        // A Blob is like a file in memory
        this.audioBlob = new Blob(this.audioChunks, {
            type: this.getSupportedMimeType()
        });
        
        console.log(`Recording complete! Size: ${this.audioBlob.size} bytes`);
        
        // Calculate duration
        const duration = (Date.now() - this.recordingStartTime) / 1000;
        console.log(`Duration: ${duration.toFixed(1)} seconds`);
        
        // Trigger custom event so UI can update
        const event = new CustomEvent('recordingComplete', {
            detail: {
                blob: this.audioBlob,
                duration: duration
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get the audio file (Blob)
     * 
     * Returns the recorded audio as a Blob that can be:
     * - Played back in an <audio> element
     * - Sent to the server
     * - Downloaded as a file
     */
    getAudioBlob() {
        return this.audioBlob;
    }

    /**
     * Create a playable URL for the audio
     * 
     * Creates a temporary URL that can be used in an <audio> element
     * to let the user preview their recording.
     */
    getAudioURL() {
        if (this.audioBlob) {
            return URL.createObjectURL(this.audioBlob);
        }
        return null;
    }

    /**
     * Helper: Get supported audio format
     * 
     * Different browsers support different audio formats.
     * This finds one that works.
     */
    getSupportedMimeType() {
        const types = [
            'audio/webm',           // Chrome, Firefox, Edge
            'audio/mp4',            // Safari
            'audio/ogg',            // Firefox
            'audio/wav'             // Fallback
        ];
        
        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        
        return 'audio/webm';  // Default
    }

    /**
     * Clean up resources
     * 
     * Important: Always stop the microphone when done!
     * Otherwise, the browser will show the recording indicator.
     */
    cleanup() {
        if (this.mediaStream) {
            // Stop all audio tracks
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
        this.mediaRecorder = null;
        this.audioChunks = [];
        console.log('Recorder cleaned up');
    }
}
```

### Step 3: JavaScript - API Service for Sending Audio

```javascript
/**
 * AudioUploadService
 * 
 * Handles sending the recorded audio to the backend server.
 */

class AudioUploadService {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    /**
     * STEP 5: Send Audio to Backend
     * 
     * Uploads the audio file to the server for processing.
     * Uses FormData to send the file (like a form with file upload).
     * 
     * @param {Blob} audioBlob - The recorded audio
     * @param {string} sessionId - Interview session ID
     * @param {string} questionId - Current question ID
     * @returns {Promise<Object>} - Server response
     */
    async uploadAudio(audioBlob, sessionId, questionId) {
        // Create FormData - this is how we send files to servers
        const formData = new FormData();
        
        // Add the audio file
        // 'audio' is the field name the server expects
        // 'answer.webm' is the filename
        formData.append('audio', audioBlob, 'answer.webm');
        
        // Add metadata
        formData.append('session_id', sessionId);
        formData.append('question_id', questionId);
        formData.append('timestamp', new Date().toISOString());
        
        try {
            console.log('Uploading audio to server...');
            
            // Send to server using fetch API
            const response = await fetch(`${this.baseURL}/api/interviews/answer`, {
                method: 'POST',
                body: formData,
                // Note: Don't set Content-Type header!
                // Browser sets it automatically with boundary for FormData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Upload successful:', result);
            return result;
            
        } catch (error) {
            console.error('Upload failed:', error);
            throw error;
        }
    }

    /**
     * Alternative: Upload with Progress Tracking
     * 
     * For large audio files, you might want to show upload progress.
     * This uses XMLHttpRequest which supports progress events.
     */
    uploadWithProgress(audioBlob, sessionId, questionId, onProgress) {
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'answer.webm');
            formData.append('session_id', sessionId);
            formData.append('question_id', questionId);
            
            const xhr = new XMLHttpRequest();
            
            // Track upload progress
            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    console.log(`Upload progress: ${percentComplete.toFixed(1)}%`);
                    if (onProgress) {
                        onProgress(percentComplete);
                    }
                }
            };
            
            // Handle completion
            xhr.onload = () => {
                if (xhr.status === 200) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    reject(new Error(`Upload failed: ${xhr.status}`));
                }
            };
            
            // Handle errors
            xhr.onerror = () => reject(new Error('Network error'));
            
            // Send request
            xhr.open('POST', `${this.baseURL}/api/interviews/answer`);
            xhr.send(formData);
        });
    }
}
```

### Step 4: JavaScript - Main Application Logic

```javascript
/**
 * Main Application
 * 
 * Connects everything together:
 * - UI elements
 * - Voice recorder
 * - Audio upload
 */

// Initialize components
const recorder = new VoiceRecorder();
const uploadService = new AudioUploadService('http://localhost:8000');

// Session data (would come from your app)
const sessionId = 'interview-123';
const questionId = 'question-456';

// Get UI elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const submitBtn = document.getElementById('submit-btn');
const recordingIndicator = document.getElementById('recording-indicator');
const timerDisplay = document.getElementById('timer');
const audioPreview = document.getElementById('audio-preview');
const statusMessage = document.getElementById('status-message');

// Timer variables
let timerInterval = null;
let seconds = 0;

// ============================================
// UI Helper Functions
// ============================================

function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
}

function updateTimer() {
    seconds++;
    const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    timerDisplay.textContent = `${mins}:${secs}`;
}

function resetTimer() {
    seconds = 0;
    timerDisplay.textContent = '00:00';
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// ============================================
// Recording Event Handlers
// ============================================

// START RECORDING
startBtn.addEventListener('click', async () => {
    try {
        showStatus('Requesting microphone access...', 'info');
        
        // Start recording
        await recorder.startRecording();
        
        // Update UI
        startBtn.disabled = true;
        stopBtn.disabled = false;
        submitBtn.style.display = 'none';
        recordingIndicator.style.display = 'block';
        audioPreview.innerHTML = '';
        
        // Start timer
        resetTimer();
        timerInterval = setInterval(updateTimer, 1000);
        
        showStatus('Recording... Speak your answer clearly.', 'info');
        
    } catch (error) {
        showStatus(error.message, 'error');
    }
});

// STOP RECORDING
stopBtn.addEventListener('click', () => {
    recorder.stopRecording();
    
    // Update UI
    stopBtn.disabled = true;
    recordingIndicator.style.display = 'none';
    
    // Stop timer
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    showStatus('Processing recording...', 'info');
});

// RECORDING COMPLETE - Show preview
document.addEventListener('recordingComplete', (event) => {
    const { blob, duration } = event.detail;
    
    // Create audio player for preview
    const audioURL = recorder.getAudioURL();
    audioPreview.innerHTML = `
        <h3>Your Recording:</h3>
        <audio controls src="${audioURL}"></audio>
        <p>Duration: ${duration.toFixed(1)} seconds</p>
        <button onclick="retryRecording()" class="record-btn" style="background: #ff9800; color: white;">
            🔄 Record Again
        </button>
    `;
    
    // Show submit button
    submitBtn.style.display = 'inline-block';
    startBtn.disabled = false;
    
    showStatus('Recording complete! Preview your answer or submit.', 'success');
});

// SUBMIT ANSWER
submitBtn.addEventListener('click', async () => {
    const audioBlob = recorder.getAudioBlob();
    
    if (!audioBlob) {
        showStatus('No recording to submit!', 'error');
        return;
    }
    
    try {
        submitBtn.disabled = true;
        showStatus('Uploading your answer...', 'info');
        
        // Upload to server
        const result = await uploadService.uploadAudio(
            audioBlob,
            sessionId,
            questionId
        );
        
        showStatus('Answer submitted successfully! Processing...', 'success');
        
        // Clean up
        recorder.cleanup();
        
        // In a real app, you would:
        // - Show next question
        // - Display feedback when ready
        console.log('Server response:', result);
        
    } catch (error) {
        showStatus('Failed to submit. Please try again.', 'error');
        submitBtn.disabled = false;
    }
});

// RETRY RECORDING
function retryRecording() {
    audioPreview.innerHTML = '';
    submitBtn.style.display = 'none';
    startBtn.disabled = false;
    showStatus('Click "Start Recording" to try again.', 'info');
}

// ============================================
// Cleanup when leaving page
// ============================================

window.addEventListener('beforeunload', () => {
    recorder.cleanup();
});
```

---

## Visual Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE VOICE CAPTURE FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  User clicks     │
│  "Start Record"  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│  getUserMedia()  │────▶│  Browser shows   │
│  Request mic     │     │  permission popup│
└──────────────────┘     └────────┬─────────┘
                                  │
                         User clicks "Allow"
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  MediaRecorder   │
                         │  starts capture  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              ┌─────────┐   ┌─────────┐   ┌─────────┐
              │ Chunk 1 │   │ Chunk 2 │   │ Chunk 3 │ ...
              └─────────┘   └─────────┘   └─────────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  User clicks     │
                         │  "Stop Record"   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Combine chunks  │
                         │  into Blob       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Preview audio   │
                         │  <audio> player  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  User clicks     │
                         │  "Submit"        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  FormData with   │
                         │  audio Blob      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  fetch() POST    │
                         │  to backend      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Backend returns │
                         │  success/next Q  │
                         └──────────────────┘
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Permission denied" | User must click "Allow" in browser popup |
| No audio recorded | Check if microphone is connected and selected |
| Poor audio quality | Enable `echoCancellation` and `noiseSuppression` |
| Large file size | Use `audio/webm` format (compressed) |
| Upload fails | Check CORS settings on backend |

---

## Key Takeaways for Students

1. **getUserMedia()** - The gateway to hardware access
2. **MediaRecorder** - Records the stream into chunks
3. **Blob** - Combines chunks into a file-like object
4. **FormData** - Packages the file for HTTP upload
5. **Always cleanup** - Stop microphone when done!
