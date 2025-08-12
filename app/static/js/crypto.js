/**
 * Client-side AES-GCM encryption utilities for note application
 * 
 * WARNING: This implementation uses a hard-coded symmetric key visible in JavaScript source.
 * This is insecure by design but accepted as a tradeoff for simplicity per requirements.
 */

// Hard-coded 32-byte AES key (same as server) - WARNING: Visible in source!
const AES_KEY_BYTES = new Uint8Array([
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66,
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66
]);

let cryptoKey = null;

/**
 * Initialize the crypto key - must be called before encrypt/decrypt operations
 */
async function initializeCrypto() {
    if (!cryptoKey) {
        try {
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
        // Handle authentication tag failures
        if (error.name === 'OperationError') {
            throw new Error('Decryption failed: invalid authentication tag');
        }
        throw new Error('Decryption failed: ' + error.message);
    }
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
    isCryptoSupported,
    showCryptoError
};