/**
 * File upload functionality with drag-and-drop and encryption support
 */

document.addEventListener('DOMContentLoaded', function() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const fileSelectBtn = document.getElementById('file-select-btn');
    const uploadProgress = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const uploadStatus = document.getElementById('upload-status');
    const titleInput = document.getElementById('title');
    const contentTextarea = document.getElementById('markdown-content');

    if (!uploadZone || !fileInput || !fileSelectBtn) {
        console.warn('Upload elements not found');
        return;
    }

    // File select button click handler
    fileSelectBtn.addEventListener('click', function() {
        fileInput.click();
    });

    // File input change handler
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Drag and drop handlers
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    /**
     * Handle file upload process
     * @param {File} file - The file to upload
     */
    async function handleFile(file) {
        try {
            // Validate file
            window.NoteCrypto.validateFile(file, ['.txt', '.md'], 1024 * 1024);
            
            // Show progress
            showUploadProgress(true);
            updateProgress(10, 'Validating file...');

            // Check if crypto is supported
            if (!window.NoteCrypto.isCryptoSupported()) {
                throw new Error('Your browser does not support encryption features');
            }

            updateProgress(30, 'Reading file...');
            
            // Read and encrypt file content
            const fileContent = await window.NoteCrypto.readFileAsText(file);
            
            updateProgress(50, 'Encrypting content...');
            
            // Encrypt the content
            const encryptedContent = await window.NoteCrypto.encryptData(fileContent);
            
            updateProgress(70, 'Uploading...');
            
            // Upload encrypted file
            await uploadEncryptedFile(file, encryptedContent);
            
            updateProgress(100, 'Upload complete!');
            
            // Hide progress after delay
            setTimeout(() => {
                showUploadProgress(false);
            }, 2000);

        } catch (error) {
            console.error('Upload error:', error);
            showUploadError(error.message);
            
            // Hide progress after delay
            setTimeout(() => {
                showUploadProgress(false);
            }, 3000);
        }
    }

    /**
     * Upload encrypted file to server
     * @param {File} originalFile - Original file object
     * @param {string} encryptedContent - Encrypted file content
     */
    async function uploadEncryptedFile(originalFile, encryptedContent) {
        const formData = new FormData();
        
        // Create a new blob with encrypted content and append as file
        const encryptedBlob = new Blob([encryptedContent], { type: 'text/plain' });
        formData.append('file', encryptedBlob, originalFile.name);
        formData.append('csrf_token', getCsrfToken());

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorMessage = `Upload failed: ${response.status}`;
            try {
                const errorData = await response.json();
                console.error('Upload error details:', JSON.stringify(errorData, null, 2));
                
                if (errorData.detail && Array.isArray(errorData.detail)) {
                    // Handle FastAPI validation errors
                    errorMessage = errorData.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
                } else if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                } else {
                    errorMessage = JSON.stringify(errorData);
                }
            } catch (e) {
                // If we can't parse JSON, use the status text
                errorMessage = response.statusText || errorMessage;
                console.error('Failed to parse error response:', e);
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        
        if (result.success) {
            // Check if we have a custom success handler (upload page)
            if (typeof window.uploadSuccessHandler === 'function' && result.note_id) {
                showUploadSuccess(result.message);
                setTimeout(() => {
                    window.uploadSuccessHandler(result.note_id);
                }, 1500);
            }
            // Otherwise handle for editor page
            else if (result.note) {
                await populateFormFromNote(result.note);
                showUploadSuccess(result.message);
            } else {
                throw new Error('Upload failed: Invalid response');
            }
        } else {
            throw new Error('Upload failed: Invalid response');
        }
    }

    /**
     * Populate form with uploaded note data
     * @param {Object} encryptedNote - Note data with encrypted fields
     */
    async function populateFormFromNote(encryptedNote) {
        try {
            if (titleInput && encryptedNote.title) {
                const decryptedTitle = await window.NoteCrypto.decryptData(encryptedNote.title);
                titleInput.value = decryptedTitle;
            }

            if (contentTextarea && encryptedNote.content) {
                const decryptedContent = await window.NoteCrypto.decryptData(encryptedNote.content);
                contentTextarea.value = decryptedContent;
                
                // Auto-resize textarea
                contentTextarea.style.height = 'auto';
                contentTextarea.style.height = contentTextarea.scrollHeight + 'px';
            }

            // Update form state if available
            if (typeof window.clearUnsavedChanges === 'function') {
                window.clearUnsavedChanges();
            }

        } catch (error) {
            console.error('Error populating form:', error);
            throw new Error('Failed to load uploaded content');
        }
    }

    /**
     * Get CSRF token from form
     * @returns {string} CSRF token
     */
    function getCsrfToken() {
        // Try main form first (editor page), then csrf form (upload page)
        let csrfInput = document.querySelector('input[name="csrf_token"]');
        if (!csrfInput) {
            csrfInput = document.querySelector('#csrf-form input[name="csrf_token"]');
        }
        return csrfInput ? csrfInput.value : '';
    }

    /**
     * Show/hide upload progress
     * @param {boolean} show - Whether to show progress
     */
    function showUploadProgress(show) {
        if (uploadProgress) {
            uploadProgress.style.display = show ? 'block' : 'none';
        }
    }

    /**
     * Update progress bar and status
     * @param {number} percent - Progress percentage (0-100)
     * @param {string} status - Status message
     */
    function updateProgress(percent, status) {
        if (progressFill) {
            progressFill.style.width = percent + '%';
        }
        if (uploadStatus) {
            uploadStatus.textContent = status;
        }
    }

    /**
     * Show upload success message
     * @param {string} message - Success message
     */
    function showUploadSuccess(message) {
        // You can customize this to match your existing message display system
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        messageDiv.textContent = message || 'File uploaded successfully!';
        
        // Insert after upload section
        const uploadSection = document.querySelector('.upload-section');
        if (uploadSection && uploadSection.parentNode) {
            uploadSection.parentNode.insertBefore(messageDiv, uploadSection.nextSibling);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                messageDiv.remove();
            }, 5000);
        }
    }

    /**
     * Show upload error message
     * @param {string} message - Error message
     */
    function showUploadError(message) {
        updateProgress(0, 'Error: ' + message);
        
        if (uploadStatus) {
            uploadStatus.style.color = '#dc3545';
        }
        
        // Reset color after delay
        setTimeout(() => {
            if (uploadStatus) {
                uploadStatus.style.color = '';
            }
        }, 5000);
    }
});