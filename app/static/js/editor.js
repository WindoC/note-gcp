// Basic editor functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Real-time preview functionality (will be enhanced later)
    const markdownEditor = document.querySelector('#markdown-content');
    const previewPane = document.querySelector('#preview-content');
    
    if (markdownEditor && previewPane) {
        markdownEditor.addEventListener('input', debounce(updatePreview, 300));
    }
    
    function updatePreview() {
        const content = markdownEditor.value;
        // For now, just show raw content. Will implement markdown parsing later
        previewPane.innerHTML = '<pre>' + escapeHtml(content) + '</pre>';
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});