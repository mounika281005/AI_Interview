/**
 * AudioUploadService.js
 * 
 * Service for uploading recorded audio to the backend.
 * Handles FormData creation, upload progress, and error handling.
 */

class AudioUploadService {
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
        this.defaultHeaders = {
            // Note: Don't set Content-Type for FormData
            // Browser sets it automatically with boundary
        };
    }

    /**
     * Upload audio file to the server
     * 
     * @param {Blob} audioBlob - The recorded audio
     * @param {Object} metadata - Additional data to send
     * @param {Object} options - Upload options
     * @returns {Promise<Object>} Server response
     */
    async upload(audioBlob, metadata = {}, options = {}) {
        const {
            endpoint = '/api/interviews/answer',
            onProgress = null,
            timeout = 60000,
        } = options;

        // Validate input
        if (!audioBlob || !(audioBlob instanceof Blob)) {
            throw new Error('Invalid audio blob');
        }

        // Create FormData
        const formData = this._createFormData(audioBlob, metadata);

        // Upload with progress tracking
        if (onProgress) {
            return this._uploadWithProgress(endpoint, formData, onProgress, timeout);
        }

        // Simple upload with fetch
        return this._uploadWithFetch(endpoint, formData, timeout);
    }

    /**
     * Create FormData with audio and metadata
     * @private
     */
    _createFormData(audioBlob, metadata) {
        const formData = new FormData();

        // Determine file extension from MIME type
        const extension = this._getExtension(audioBlob.type);
        const filename = `answer_${Date.now()}.${extension}`;

        // Add audio file
        formData.append('audio', audioBlob, filename);

        // Add metadata
        Object.entries(metadata).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                formData.append(key, typeof value === 'object' ? JSON.stringify(value) : value);
            }
        });

        // Add timestamp
        formData.append('uploaded_at', new Date().toISOString());

        return formData;
    }

    /**
     * Upload using fetch API
     * @private
     */
    async _uploadWithFetch(endpoint, formData, timeout) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                body: formData,
                signal: controller.signal,
                credentials: 'include', // Include cookies for auth
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Upload failed: ${response.status}`);
            }

            return await response.json();

        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                throw new Error('Upload timeout');
            }

            throw error;
        }
    }

    /**
     * Upload with progress tracking using XMLHttpRequest
     * @private
     */
    _uploadWithProgress(endpoint, formData, onProgress, timeout) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // Set timeout
            xhr.timeout = timeout;

            // Track upload progress
            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const progress = {
                        loaded: event.loaded,
                        total: event.total,
                        percentage: Math.round((event.loaded / event.total) * 100),
                    };
                    onProgress(progress);
                }
            };

            // Handle completion
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        resolve({ success: true, raw: xhr.responseText });
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.status}`));
                }
            };

            // Handle errors
            xhr.onerror = () => reject(new Error('Network error during upload'));
            xhr.ontimeout = () => reject(new Error('Upload timeout'));

            // Send request
            xhr.open('POST', `${this.baseURL}${endpoint}`);
            xhr.withCredentials = true; // Include cookies
            xhr.send(formData);
        });
    }

    /**
     * Get file extension from MIME type
     * @private
     */
    _getExtension(mimeType) {
        const map = {
            'audio/webm': 'webm',
            'audio/webm;codecs=opus': 'webm',
            'audio/mp4': 'm4a',
            'audio/ogg': 'ogg',
            'audio/ogg;codecs=opus': 'ogg',
            'audio/wav': 'wav',
            'audio/mpeg': 'mp3',
        };

        return map[mimeType] || 'webm';
    }

    /**
     * Check if a file is within size limits
     * @param {Blob} blob - The file to check
     * @param {number} maxSizeMB - Maximum size in megabytes
     * @returns {boolean}
     */
    static isWithinSizeLimit(blob, maxSizeMB = 50) {
        const maxBytes = maxSizeMB * 1024 * 1024;
        return blob.size <= maxBytes;
    }

    /**
     * Get human-readable file size
     * @param {number} bytes - Size in bytes
     * @returns {string}
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioUploadService;
}
