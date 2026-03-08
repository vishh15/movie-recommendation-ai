/**
 * Premium JavaScript UX for Movie Recommender
 * AI Product Interface
 */

// ===== SMOOTH SCROLL =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== DARK MODE TOGGLE =====
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark');
        const newTheme = isDark ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        
        // Smooth theme transition
        document.body.style.transition = 'background-color 0.3s ease';
    });
}

function updateThemeIcon(theme) {
    const icon = theme === 'dark' ? '🌙' : '☀️';
    if (themeToggle) {
        themeToggle.querySelector('span').textContent = icon;
    }
}

// ===== INTERSECTION OBSERVER FOR ANIMATIONS =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe sections
document.querySelectorAll('section, .feature-card, .movie-card').forEach(el => {
    observer.observe(el);
});

// ===== SESSION INFO HELPER =====
async function getSessionInfo() {
    try {
        const response = await fetch('/api/session-info');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching session info:', error);
        return null;
    }
}

// ===== CLEAR SESSION HELPER =====
async function clearSession() {
    try {
        const response = await fetch('/api/clear-session', {
            method: 'POST'
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error clearing session:', error);
        return null;
    }
}

// ===== TOAST NOTIFICATION SYSTEM =====
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-6 right-6 px-6 py-4 rounded-xl shadow-2xl z-50 transition-all transform backdrop-blur-md border`;
    
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    const colors = {
        success: 'bg-green-600/90 border-green-500/50 text-white',
        error: 'bg-red-600/90 border-red-500/50 text-white',
        warning: 'bg-yellow-600/90 border-yellow-500/50 text-white',
        info: 'bg-blue-600/90 border-blue-500/50 text-white'
    };
    
    // Split classes and add them individually (classList.add doesn't accept spaces)
    (colors[type] || colors.info).split(' ').forEach(cls => toast.classList.add(cls));
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <span class="text-2xl">${icons[type] || icons.info}</span>
            <span class="font-medium">${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);
    
    // Auto-remove
    setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ===== LOADING SPINNER HELPER =====
function showLoadingSpinner(container, message = 'Loading...') {
    const spinner = document.createElement('div');
    spinner.className = 'loading-container text-center py-12';
    spinner.innerHTML = `
        <div class="spinner mx-auto mb-4"></div>
        <p class="text-gray-400 font-accent">${message}</p>
    `;
    container.innerHTML = '';
    container.appendChild(spinner);
}

// ===== LAZY LOAD IMAGES =====
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img.lazy').forEach(img => {
        imageObserver.observe(img);
    });
}

// ===== QUIZ OPTION CARD SELECTION =====
document.querySelectorAll('.quiz-option-card').forEach(card => {
    card.addEventListener('click', function() {
        const radio = this.querySelector('input[type="radio"]');
        if (radio) {
            // Deselect other options in the same question
            const questionContainer = this.closest('.question-container');
            if (questionContainer) {
                questionContainer.querySelectorAll('.quiz-option-card').forEach(c => {
                    c.classList.remove('selected');
                });
            }
            
            // Select this option
            radio.checked = true;
            this.classList.add('selected');
        }
    });
});

// ===== NAVBAR SCROLL EFFECT =====
let lastScroll = 0;
const nav = document.querySelector('nav');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 50) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
});

// ===== CONSOLE BRANDING =====
console.log('%c🎬 MOVREC AI', 'font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #ef4444, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;');
console.log('%cEmotion-Powered Movie Discovery', 'font-size: 14px; color: #8b5cf6; font-weight: 600;');
console.log('%cBuilt with PyTorch • Flask • TailwindCSS • TMDB API', 'font-size: 11px; color: #6b7280;');

// ===== GLOBAL ERROR HANDLER =====
window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred', 'error');
});

// Export utilities for use in other scripts
window.movieRecUtils = {
    showToast,
    showLoadingSpinner,
    getSessionInfo,
    clearSession
};
