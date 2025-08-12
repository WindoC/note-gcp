// Basic editor functionality - minimal shared functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textareas (for pages that don't have custom editor functionality)
    const textareas = document.querySelectorAll('textarea:not(#markdown-content)');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});