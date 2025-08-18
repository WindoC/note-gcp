import os
import base64
import hashlib
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from ..config import settings


def get_aes_key() -> bytes:
    """
    Derive AES key from environment variable using SHA-256.
    
    Returns:
        32-byte AES key derived from user input
        
    Raises:
        EncryptionError: If AES_KEY environment variable is not set
    """
    raw_key = settings.aes_key
    if not raw_key:
        raise EncryptionError("AES_KEY environment variable is not set")
    
    # Use SHA-256 to derive 32-byte key from user input
    return hashlib.sha256(raw_key.encode('utf-8')).digest()


class EncryptionError(Exception):
    """Custom exception for encryption/decryption errors"""
    pass


def encrypt_data(plaintext: Union[str, bytes]) -> str:
    """
    Encrypt data using AES-GCM with hard-coded key.
    
    Args:
        plaintext: String or bytes to encrypt
        
    Returns:
        Base64-encoded string containing nonce + ciphertext
        
    Raises:
        EncryptionError: If encryption fails
    """
    try:
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Create AESGCM cipher
        aes_key = get_aes_key()
        aesgcm = AESGCM(aes_key)
        
        # Generate random 12-byte nonce for GCM
        nonce = os.urandom(12)
        
        # Encrypt data
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Combine nonce + ciphertext and encode as base64
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode('ascii')
        
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {str(e)}")


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt base64-encoded AES-GCM encrypted data.
    
    Args:
        encrypted_data: Base64-encoded string containing nonce + ciphertext
        
    Returns:
        Decrypted string
        
    Raises:
        EncryptionError: If decryption fails or data is invalid
    """
    try:
        # Decode base64
        combined_data = base64.b64decode(encrypted_data.encode('ascii'))
        
        if len(combined_data) < 12:
            raise EncryptionError("Invalid encrypted data: too short")
        
        # Extract nonce (first 12 bytes) and ciphertext (remainder)
        nonce = combined_data[:12]
        ciphertext = combined_data[12:]
        
        # Create AESGCM cipher
        aes_key = get_aes_key()
        aesgcm = AESGCM(aes_key)
        
        # Decrypt data
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode('utf-8')
        
    except InvalidTag:
        raise EncryptionError("Decryption failed: invalid authentication tag")
    except ValueError as e:
        raise EncryptionError(f"Decryption failed: invalid data format - {str(e)}")
    except Exception as e:
        raise EncryptionError(f"Decryption failed: {str(e)}")


def encrypt_json_field(data: dict, field: str) -> dict:
    """
    Encrypt a specific field in a dictionary.
    
    Args:
        data: Dictionary containing the field to encrypt
        field: Name of the field to encrypt
        
    Returns:
        Dictionary with the field encrypted
    """
    if field in data and data[field] is not None:
        data[field] = encrypt_data(str(data[field]))
    return data


def decrypt_json_field(data: dict, field: str) -> dict:
    """
    Decrypt a specific field in a dictionary.
    
    Args:
        data: Dictionary containing the encrypted field
        field: Name of the field to decrypt
        
    Returns:
        Dictionary with the field decrypted
    """
    if field in data and data[field] is not None:
        data[field] = decrypt_data(str(data[field]))
    return data