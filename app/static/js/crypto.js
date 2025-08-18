/**
 * Client-side AES-GCM encryption utilities for note application
 * 
 * WARNING: This implementation uses a hard-coded symmetric key visible in JavaScript source.
 * This is insecure by design but accepted as a tradeoff for simplicity per requirements.
 */

// AES key management - key derived from user input and stored in localStorage
let AES_KEY_BYTES = null;

let cryptoKey = null;

/**
 * Derive AES key from user input using SHA-256
 */
async function deriveKeyFromPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return new Uint8Array(hash);
}

/**
 * Get AES key from localStorage or prompt user
 */
async function getAESKey() {
    // Only prompt on /notes* pages
    if (!window.location.pathname.startsWith('/notes')) {
        throw new Error('AES key not available on this page');
    }
    
    let keyHash = localStorage.getItem('aes_key_hash');
    
    if (!keyHash) {
        const userKey = await promptForAESKey();
        if (!userKey) {
            throw new Error('AES key is required for encryption');
        }
        
        const keyBytes = await deriveKeyFromPassword(userKey);
        keyHash = Array.from(keyBytes).map(b => b.toString(16).padStart(2, '0')).join('');
        localStorage.setItem('aes_key_hash', keyHash);
    }
    
    // Convert hex string back to Uint8Array
    const keyBytes = new Uint8Array(keyHash.match(/.{2}/g).map(byte => parseInt(byte, 16)));
    return keyBytes;
}

/**
 * Prompt user for AES key input using modal
 */
async function promptForAESKey(isRetry = false) {
    return new Promise((resolve, reject) => {
        const modal = document.getElementById('aes-key-modal');
        const titleElement = document.getElementById('aes-key-modal-title');
        const messageElement = document.getElementById('aes-key-modal-message');
        const inputElement = document.getElementById('aes-key-input');
        const okButton = document.getElementById('aes-key-ok');
        const cancelButton = document.getElementById('aes-key-cancel');
        
        if (!modal) {
            // Fallback to browser prompt if modal not available
            const message = isRetry 
                ? 'Decryption failed. Please enter the correct AES key:'
                : 'Please enter your AES key to encrypt/decrypt notes:';
            return resolve(prompt(message));
        }
        
        // Set modal content
        titleElement.textContent = isRetry ? 'AES Key Required' : 'Enter AES Key';
        messageElement.textContent = isRetry 
            ? 'Decryption failed. Please enter the correct AES key:'
            : 'Please enter your AES key to encrypt/decrypt notes:';
        
        inputElement.value = '';
        inputElement.focus();
        
        // Show modal
        modal.style.display = 'flex';
        
        const handleOk = () => {
            const value = inputElement.value.trim();
            cleanup();
            resolve(value || null);
        };
        
        const handleCancel = () => {
            cleanup();
            resolve(null);
        };
        
        const handleKeyPress = (e) => {
            if (e.key === 'Enter') {
                handleOk();
            } else if (e.key === 'Escape') {
                handleCancel();
            }
        };
        
        const cleanup = () => {
            modal.style.display = 'none';
            okButton.removeEventListener('click', handleOk);
            cancelButton.removeEventListener('click', handleCancel);
            inputElement.removeEventListener('keydown', handleKeyPress);
        };
        
        okButton.addEventListener('click', handleOk);
        cancelButton.addEventListener('click', handleCancel);
        inputElement.addEventListener('keydown', handleKeyPress);
    });
}

/**
 * Initialize the crypto key - must be called before encrypt/decrypt operations
 */
async function initializeCrypto() {
    if (!cryptoKey || !AES_KEY_BYTES) {
        try {
            AES_KEY_BYTES = await getAESKey();
            cryptoKey = await window.crypto.subtle.importKey(
                'raw',
                AES_KEY_BYTES,
                { name: 'AES-GCM' },
                false, // not extractable
                ['encrypt', 'decrypt']
            );
        } catch (error) {
            throw new Error('Failed to initialize crypto key: ' + error.message);
        }
    }
}

/**
 * Generate a random 12-byte nonce for AES-GCM
 */
function generateNonce() {
    return window.crypto.getRandomValues(new Uint8Array(12));
}

/**
 * Convert string to UTF-8 bytes
 */
function stringToBytes(str) {
    return new TextEncoder().encode(str);
}

/**
 * Convert UTF-8 bytes to string
 */
function bytesToString(bytes) {
    return new TextDecoder().decode(bytes);
}

/**
 * Convert bytes to base64 string
 */
function bytesToBase64(bytes) {
    const binary = String.fromCharCode(...bytes);
    return btoa(binary);
}

/**
 * Convert base64 string to bytes
 */
function base64ToBytes(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
}

/**
 * Encrypt plaintext string using AES-GCM
 * 
 * @param {string} plaintext - Text to encrypt
 * @returns {Promise<string>} Base64-encoded nonce + ciphertext
 * @throws {Error} If encryption fails
 */
async function encryptData(plaintext) {
    if (!plaintext) {
        return '';
    }
    
    try {
        await initializeCrypto();
        
        const nonce = generateNonce();
        const plaintextBytes = stringToBytes(plaintext);
        
        const ciphertext = await window.crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: nonce },
            cryptoKey,
            plaintextBytes
        );
        
        // Combine nonce + ciphertext
        const combined = new Uint8Array(nonce.length + ciphertext.byteLength);
        combined.set(nonce);
        combined.set(new Uint8Array(ciphertext), nonce.length);
        
        return bytesToBase64(combined);
        
    } catch (error) {
        throw new Error('Encryption failed: ' + error.message);
    }
}

/**
 * Decrypt base64-encoded AES-GCM encrypted data
 * 
 * @param {string} encryptedData - Base64-encoded nonce + ciphertext
 * @returns {Promise<string>} Decrypted plaintext
 * @throws {Error} If decryption fails
 */
async function decryptData(encryptedData) {
    if (!encryptedData) {
        return '';
    }
    
    try {
        await initializeCrypto();
        
        const combined = base64ToBytes(encryptedData);
        
        if (combined.length < 12) {
            throw new Error('Invalid encrypted data: too short');
        }
        
        // Extract nonce (first 12 bytes) and ciphertext (remainder)
        const nonce = combined.slice(0, 12);
        const ciphertext = combined.slice(12);
        
        const decrypted = await window.crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: nonce },
            cryptoKey,
            ciphertext
        );
        
        return bytesToString(new Uint8Array(decrypted));
        
    } catch (error) {
        // Handle authentication tag failures - likely wrong key
        if (error.name === 'OperationError') {
            // Clear stored key and prompt for new one
            localStorage.removeItem('aes_key_hash');
            cryptoKey = null;
            AES_KEY_BYTES = null;
            
            // Retry with new key if on notes pages
            if (window.location.pathname.startsWith('/notes')) {
                try {
                    const userKey = await promptForAESKey(true);
                    if (userKey) {
                        AES_KEY_BYTES = await deriveKeyFromPassword(userKey);
                        const keyHash = Array.from(AES_KEY_BYTES).map(b => b.toString(16).padStart(2, '0')).join('');
                        localStorage.setItem('aes_key_hash', keyHash);
                        
                        cryptoKey = await window.crypto.subtle.importKey(
                            'raw',
                            AES_KEY_BYTES,
                            { name: 'AES-GCM' },
                            false,
                            ['encrypt', 'decrypt']
                        );
                        
                        // Retry decryption
                        const combined = base64ToBytes(encryptedData);
                        const nonce = combined.slice(0, 12);
                        const ciphertext = combined.slice(12);
                        const decrypted = await window.crypto.subtle.decrypt(
                            { name: 'AES-GCM', iv: nonce },
                            cryptoKey,
                            ciphertext
                        );
                        return bytesToString(new Uint8Array(decrypted));
                    }
                } catch (retryError) {
                    throw new Error('Decryption failed: invalid authentication tag');
                }
            }
            throw new Error('Decryption failed: invalid authentication tag');
        }
        throw new Error('Decryption failed: ' + error.message);
    }
}

/**
 * Encrypt file content for upload
 * 
 * @param {File} file - File object to encrypt
 * @returns {Promise<{encryptedContent: string, filename: string}>} Encrypted file data
 * @throws {Error} If encryption or file reading fails
 */
async function encryptFile(file) {
    if (!file) {
        throw new Error('No file provided');
    }
    
    try {
        // Read file as text
        const fileContent = await readFileAsText(file);
        
        // Encrypt the content
        const encryptedContent = await encryptData(fileContent);
        
        return {
            encryptedContent: encryptedContent,
            filename: file.name
        };
        
    } catch (error) {
        throw new Error('File encryption failed: ' + error.message);
    }
}

/**
 * Read file as text using FileReader
 * 
 * @param {File} file - File to read
 * @returns {Promise<string>} File content as string
 */
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            resolve(e.target.result);
        };
        
        reader.onerror = function() {
            reject(new Error('Failed to read file'));
        };
        
        reader.readAsText(file, 'UTF-8');
    });
}

/**
 * Validate file type and size
 * 
 * @param {File} file - File to validate
 * @param {Array<string>} allowedTypes - Array of allowed file extensions
 * @param {number} maxSize - Maximum file size in bytes
 * @returns {boolean} True if valid, throws error if invalid
 */
function validateFile(file, allowedTypes = ['.txt', '.md'], maxSize = 1024 * 1024) {
    if (!file) {
        throw new Error('No file selected');
    }
    
    // Check file size
    if (file.size > maxSize) {
        throw new Error(`File size (${Math.round(file.size / 1024)}KB) exceeds ${Math.round(maxSize / 1024)}KB limit`);
    }
    
    // Check file type
    const fileName = file.name.toLowerCase();
    const hasValidExtension = allowedTypes.some(type => fileName.endsWith(type.toLowerCase()));
    
    if (!hasValidExtension) {
        throw new Error(`File type not supported. Allowed types: ${allowedTypes.join(', ')}`);
    }
    
    return true;
}

/**
 * Check if Web Crypto API is supported
 */
function isCryptoSupported() {
    return !!(window.crypto && window.crypto.subtle);
}

/**
 * Show error message to user
 */
function showCryptoError(message) {
    console.error('Crypto Error:', message);
    // You can customize this to show user-friendly error messages
    alert('Encryption error: ' + message);
}

// Export functions for use in other scripts
window.NoteCrypto = {
    encryptData,
    decryptData,
    encryptFile,
    readFileAsText,
    validateFile,
    isCryptoSupported,
    showCryptoError
};