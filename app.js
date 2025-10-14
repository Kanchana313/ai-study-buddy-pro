// Global JavaScript functions for AI Study Buddy Pro

// Function to show toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '11';
    
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    toast.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-body ${alertClass}">
                ${message}
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        document.body.removeChild(toast);
    }, 3000);
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        showToast('Failed to copy: ' + err, 'error');
    });
}

// Function to format date
function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options);
}

// Function to format time
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Function to save settings to localStorage
function saveSettings(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

// Function to load settings from localStorage
function loadSettings(key, defaultValue = null) {
    const value = localStorage.getItem(key);
    try {
        return value ? JSON.parse(value) : defaultValue;
    } catch (e) {
        return value || defaultValue;
    }
}

// Function to validate API key format
function validateApiKey(key) {
    // Google Gemini API keys typically start with 'AIza'
    return key.startsWith('AIza') && key.length > 20;
}

// Function to check if API key is set
function isApiKeySet() {
    const apiKey = loadSettings('gemini-api-key');
    return apiKey && validateApiKey(apiKey);
}

// Function to show API key warning
function showApiKeyWarning() {
    if (!isApiKeySet()) {
        showToast('Please set your Google Gemini API key in Settings to use all features', 'warning');
    }
}

// Initialize common functionality
document.addEventListener('DOMContentLoaded', () => {
    // Check API key on page load
    showApiKeyWarning();
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add hover effect to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
});