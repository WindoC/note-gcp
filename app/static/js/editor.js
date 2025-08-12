// Enhanced editor functionality with encryption support
document.addEventListener('DOMContentLoaded', function() {
    // Check if crypto is supported
    if (!window.NoteCrypto || !window.NoteCrypto.isCryptoSupported()) {
        alert('This browser does not support the required encryption features. Please use a modern browser.');
        return;
    }

    // Auto-resize textareas (for pages that don't have custom editor functionality)
    const textareas = document.querySelectorAll('textarea:not(#markdown-content)');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Handle note editor form submission with encryption
    const noteForm = document.querySelector('form[action*="/notes"]');
    if (noteForm) {
        noteForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const titleField = noteForm.querySelector('input[name="title"]');
            const contentField = noteForm.querySelector('textarea[name="content"]');
            const csrfField = noteForm.querySelector('input[name="csrf_token"]');
            
            if (!titleField || !contentField || !csrfField) {
                console.error('Required form fields not found');
                return;
            }
            
            const submitButton = noteForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Encrypting...';
            }
            
            try {
                // Encrypt form data
                const encryptedTitle = await window.NoteCrypto.encryptData(titleField.value);
                const encryptedContent = await window.NoteCrypto.encryptData(contentField.value);
                
                // Update form fields with encrypted data
                titleField.value = encryptedTitle;
                contentField.value = encryptedContent;
                
                // Submit the form
                noteForm.submit();
                
            } catch (error) {
                window.NoteCrypto.showCryptoError('Failed to encrypt note data: ' + error.message);
                
                // Re-enable submit button
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Save Note';
                }
            }
        });
    }

    // Decrypt note content for editing (if present)
    const noteData = window.noteData;
    if (noteData) {
        decryptNoteForEditing(noteData);
    }
});

/**
 * Decrypt note data for editing
 */
async function decryptNoteForEditing(noteData) {
    try {
        const titleField = document.querySelector('input[name="title"]');
        const contentField = document.querySelector('textarea[name="content"]');
        
        if (titleField && noteData.title) {
            const decryptedTitle = await window.NoteCrypto.decryptData(noteData.title);
            titleField.value = decryptedTitle;
        }
        
        if (contentField && noteData.content) {
            const decryptedContent = await window.NoteCrypto.decryptData(noteData.content);
            contentField.value = decryptedContent;
            
            // Trigger auto-resize
            contentField.style.height = 'auto';
            contentField.style.height = contentField.scrollHeight + 'px';
        }
        
    } catch (error) {
        window.NoteCrypto.showCryptoError('Failed to decrypt note data: ' + error.message);
    }
}