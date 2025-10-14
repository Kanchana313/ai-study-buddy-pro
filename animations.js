// Animation JavaScript for AI Study Buddy Pro

// Function to animate elements on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementPosition < windowHeight - 100) {
            element.classList.add('animated');
        }
    });
}

// Add scroll event listener
window.addEventListener('scroll', animateOnScroll);

// Initial call to animate elements already in view
document.addEventListener('DOMContentLoaded', animateOnScroll);

// Function to add pulse animation to buttons
function addPulseAnimation(element) {
    element.classList.add('btn-pulse');
    setTimeout(() => {
        element.classList.remove('btn-pulse');
    }, 2000);
}

// Function to add bounce animation to icons
function addBounceAnimation(element) {
    element.classList.add('icon-bounce');
    setTimeout(() => {
        element.classList.remove('icon-bounce');
    }, 2000);
}

// Function to add glow animation
function addGlowAnimation(element) {
    element.classList.add('glow');
    setTimeout(() => {
        element.classList.remove('glow');
    }, 2000);
}

// Function to add shake animation for errors
function addShakeAnimation(element) {
    element.classList.add('shake');
    setTimeout(() => {
        element.classList.remove('shake');
    }, 500);
}

// Function to add loading animation
function showLoading(element) {
    element.innerHTML = '<div class="loading"></div>';
}

// Function to add typing animation to text
function typeText(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Function to animate a number counting up
function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Function to create a floating animation
function createFloatAnimation(element) {
    element.classList.add('float');
}

// Function to create a slide-in animation
function createSlideInAnimation(element, direction = 'left') {
    if (direction === 'left') {
        element.classList.add('slide-in-left');
    } else {
        element.classList.add('slide-in-right');
    }
}

// Function to create a flip animation
function createFlipAnimation(element) {
    element.classList.add('flip');
}

// Function to animate progress bars
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width || bar.getAttribute('style').match(/width:\s*(\d+%)/)[1];
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Animate progress bars
    animateProgressBars();
    
    // Add hover animations to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', () => {
            if (!button.classList.contains('btn-pulse')) {
                button.style.transform = 'scale(1.05)';
                button.style.transition = 'transform 0.2s ease';
            }
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
    });
    
    // Add click animations to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', () => {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 100);
        });
    });
    
    // Add animations to feature cards
    document.querySelectorAll('.feature-card').forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('animated');
        }, index * 100);
    });
    
    // Add animations to timeline items
    document.querySelectorAll('.timeline-item').forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('animated');
        }, index * 200);
    });
});