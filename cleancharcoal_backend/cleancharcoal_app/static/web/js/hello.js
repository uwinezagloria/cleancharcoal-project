// main.js - Clean Charcoal Rwanda - Home Page Interactions

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Clean Charcoal Rwanda - Home Page Loaded');
    
    // Initialize features
    initNavbarScroll();
    initStatsAnimation();
    initServiceCards();
    initSmoothScrolling();
    initBackToTop();
    initTestimonialSlider();
    initNewsletter();
});

// ===== 1. NAVBAR SCROLL EFFECT =====
function initNavbarScroll() {
    const navbar = document.querySelector('.custom-nav');
    const backToTopBtn = document.getElementById('backToTop');
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
                if (backToTopBtn) backToTopBtn.classList.add('visible');
            } else {
                navbar.classList.remove('scrolled');
                if (backToTopBtn) backToTopBtn.classList.remove('visible');
            }
            
            // Update active nav link based on scroll position
            updateActiveNavLink();
        });
    }
}

function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link-lg');
    
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.clientHeight;
        
        if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// ===== 2. STATS COUNTER ANIMATION =====
function initStatsAnimation() {
    const statNumbers = document.querySelectorAll('.stat-number[data-count]');
    
    if (statNumbers.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const stat = entry.target;
                const target = parseInt(stat.getAttribute('data-count'));
                animateCounter(stat, target);
                observer.unobserve(stat);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(stat => observer.observe(stat));
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 100;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 20);
}

// ===== 3. SERVICE CARDS INTERACTIVITY =====
function initServiceCards() {
    const serviceCards = document.querySelectorAll('.service-card');
    const serviceBtns = document.querySelectorAll('.service-btn');
    
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 30px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
        });
    });
    
    serviceBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.textContent.includes('Request Permission')) {
                return; // Let link handle navigation
            }
            e.preventDefault();
            const service = this.getAttribute('data-service') || 
                           this.closest('.service-card')?.querySelector('.service-heading')?.textContent;
            if (service) showServiceDetails(service.toLowerCase());
        });
    });
}

function showServiceDetails(service) {
    const serviceData = {
        'sensors': {
            title: 'Sensor Monitoring System',
            description: 'Our advanced sensors provide real-time monitoring of charcoal kilns to ensure optimal burning conditions.',
            features: [
                'Real-time temperature monitoring (up to 600°C)',
                'Smoke level detection (0-1000 PPM)',
                'Humidity and oxygen level tracking',
                'Wireless data transmission every 5 minutes',
                'Weather-resistant and durable design'
            ],
            benefits: [
                'Increased production efficiency by 40%',
                'Reduced harmful emissions by 60%',
                'Prevents kiln overheating accidents',
                'Saves up to 30% on fuel costs'
            ]
        },
        'alerts': {
            title: 'Smart Alert System',
            description: 'Receive instant notifications and recommendations to optimize your charcoal production.',
            features: [
                'SMS & Mobile app notifications',
                'Email alerts for critical conditions',
                'Voice alerts for immediate attention',
                'Predictive analytics for maintenance',
                'Customizable alert thresholds'
            ],
            benefits: [
                'Prevent equipment failure',
                'Reduce smoke pollution',
                'Optimize burning schedules',
                'Improve charcoal quality'
            ]
        },
        'dashboard': {
            title: 'Centralized Dashboard',
            description: 'Monitor all your kilns from a single, intuitive dashboard with real-time data visualization.',
            features: [
                'Multi-kiln monitoring interface',
                'Historical data analysis',
                'Performance reports generation',
                'Export data to PDF/Excel',
                'Role-based access control'
            ],
            benefits: [
                'Complete production overview',
                'Data-driven decision making',
                'Easy compliance reporting',
                'Remote monitoring capability'
            ]
        }
    };
    
    const data = serviceData[service] || serviceData.sensors;
    
    // Create modal content
    const modalContent = `
        <div class="service-details">
            <h4 class="mb-3">${data.title}</h4>
            <p class="mb-4">${data.description}</p>
            
            <h5 class="mb-3">Key Features:</h5>
            <ul class="mb-4">
                ${data.features.map(feat => `<li><i class="fas fa-check text-success me-2"></i>${feat}</li>`).join('')}
            </ul>
            
            <h5 class="mb-3">Benefits:</h5>
            <ul class="mb-4">
                ${data.benefits.map(benefit => `<li><i class="fas fa-chart-line text-primary me-2"></i>${benefit}</li>`).join('')}
            </ul>
            
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Interested in this service? <a href="signup.html" class="alert-link">Sign up now</a> to get started!
            </div>
        </div>
    `;
    
    // Update modal
    document.getElementById('serviceModalTitle').textContent = data.title;
    document.getElementById('serviceModalBody').innerHTML = modalContent;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('serviceModal'));
    modal.show();
}

// ===== 4. SMOOTH SCROLLING =====
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // Update URL without page reload
                history.pushState(null, null, href);
            }
        });
    });
}

// ===== 5. BACK TO TOP =====
function initBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// ===== 6. TESTIMONIAL SLIDER =====
function initTestimonialSlider() {
    const testimonials = document.querySelector('.testimonials-container');
    if (!testimonials) return;
    
    const testimonialCards = Array.from(testimonials.children);
    let currentIndex = 0;
    
    // Auto rotate testimonials
    setInterval(() => {
        testimonialCards.forEach(card => card.style.opacity = '0.5');
        
        testimonialCards[currentIndex].style.opacity = '1';
        testimonialCards[currentIndex].style.transform = 'scale(1.05)';
        
        currentIndex = (currentIndex + 1) % testimonialCards.length;
    }, 4000);
}

// ===== 7. NEWSLETTER SUBSCRIPTION =====
function initNewsletter() {
    const subscribeBtn = document.querySelector('.footer-subscribe-btn');
    const emailInput = document.getElementById('newsletterEmail');
    
    if (subscribeBtn && emailInput) {
        subscribeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            subscribeNewsletter();
        });
        
        emailInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                subscribeNewsletter();
            }
        });
    }
}

function subscribeNewsletter() {
    const emailInput = document.getElementById('newsletterEmail');
    if (!emailInput) return;
    
    const email = emailInput.value.trim();
    
    if (!validateEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        emailInput.focus();
        return;
    }
    
    // Save to localStorage
    const subscribers = JSON.parse(localStorage.getItem('ccrNewsletter') || '[]');
    if (subscribers.includes(email)) {
        showNotification('You are already subscribed!', 'info');
        return;
    }
    
    subscribers.push(email);
    localStorage.setItem('ccrNewsletter', JSON.stringify(subscribers));
    
    // Show success
    showNotification('Successfully subscribed to newsletter!', 'success');
    emailInput.value = '';
    
    // Update button
    const subscribeBtn = document.querySelector('.footer-subscribe-btn');
    if (subscribeBtn) {
        const originalText = subscribeBtn.innerHTML;
        subscribeBtn.innerHTML = '<i class="fas fa-check"></i> Subscribed!';
        subscribeBtn.disabled = true;
        
        setTimeout(() => {
            subscribeBtn.innerHTML = originalText;
            subscribeBtn.disabled = false;
        }, 3000);
    }
}

// ===== 8. UTILITY FUNCTIONS =====
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    // Style
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
        color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Close button
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

function showPrivacyPolicy() {
    showNotification('Privacy policy page coming soon!', 'info');
}

function showTermsConditions() {
    showNotification('Terms & conditions page coming soon!', 'info');
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: inherit;
        opacity: 0.7;
        transition: opacity 0.3s;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(style);