// Main JavaScript for CleanCharcoal Rwanda Landing Page

// Back to Top Button
document.addEventListener('DOMContentLoaded', function() {
    const backToTopButton = document.getElementById('backToTop');
    
    if (backToTopButton) {
        // Show/hide back to top button on scroll
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        // Smooth scroll to top
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Service Details Modal/Function
function showServiceDetails(serviceType) {
    const messages = {
        'sensors': 'Our embedded sensors continuously monitor temperature, smoke levels, CO2, PM2.5, and humidity within the kiln. This real-time data helps ensure optimal burning conditions and early detection of any issues.',
        'alerts': 'When sensor readings indicate unsafe conditions or inefficiencies, the system immediately sends alerts to both the producer and community leaders. This proactive approach helps prevent accidents and reduces harmful emissions.',
        'dashboard': 'All sensor data is collected and displayed on our web dashboard. Community leaders can monitor multiple kilns, view historical data, generate reports, and make informed decisions about burning permissions.'
    };
    
    const message = messages[serviceType] || 'More information about this service coming soon.';
    alert(message);
    // You can replace this with a modal if preferred
}

// Newsletter Subscription
function subscribeNewsletter() {
    const emailInput = document.getElementById('newsletterEmail');
    if (!emailInput) return;
    
    const email = emailInput.value.trim();
    
    if (!email) {
        alert('Please enter your email address.');
        return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address.');
        return;
    }
    
    // TODO: Implement actual newsletter subscription API call
    alert('Thank you for subscribing! We\'ll keep you updated with our latest features and services.');
    emailInput.value = '';
}

// Privacy Policy
function showPrivacyPolicy() {
    alert('Privacy Policy\n\nWe respect your privacy and are committed to protecting your personal data. Our privacy policy outlines how we collect, use, and safeguard your information. Full privacy policy coming soon.');
    // TODO: Implement actual privacy policy page/modal
}

// Terms & Conditions
function showTermsConditions() {
    alert('Terms & Conditions\n\nBy using CleanCharcoal Rwanda, you agree to our terms and conditions. Full terms and conditions coming soon.');
    // TODO: Implement actual terms and conditions page/modal
}

