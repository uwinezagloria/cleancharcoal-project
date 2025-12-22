// auth.js - Authentication Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 Auth Page Loaded');
    
    // Initialize toast system first
    initToast();
    
    // Check which page we're on
    const path = window.location.pathname;
    
    if (path.includes('login.html')) {
        initLoginPage();
    } else if (path.includes('signup.html')) {
        initSignupPage();
    }
    
    // Common initialization
    initCommonAuthFeatures();
    ensureDemoUser(); // Create demo user if not exists
    initForgotPasswordLink(); // Initialize forgot password link
});

// ===== SIMPLE FORGOT PASSWORD LINK FIX =====
function initForgotPasswordLink() {
    // Find the "Forgot password?" link
    const forgotPasswordLink = document.querySelector('a[href*="forgot-password"], a[href*="forgotpassword"]');
    
    if (!forgotPasswordLink) {
        console.log('❌ Forgot password link not found');
        return;
    }
    
    console.log('✅ Found forgot password link:', forgotPasswordLink);
    
    // Remove any existing event listeners first
    const newLink = forgotPasswordLink.cloneNode(true);
    forgotPasswordLink.parentNode.replaceChild(newLink, forgotPasswordLink);
    
    // Add new event listener
    newLink.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent default link behavior
        
        // Get email from login form if available
        const emailInput = document.getElementById('email');
        if (emailInput && emailInput.value.trim()) {
            const email = emailInput.value.trim();
            
            // Save email for pre-filling on reset page
            sessionStorage.setItem('forgotPasswordEmail', email);
            console.log('📧 Saved email for password reset:', email);
        }
        
        // Show notification
        showToast('Redirecting...', 'Taking you to password reset page', 'info');
        
        // Redirect to forgot password page
        setTimeout(() => {
            window.location.href = 'forgot-password.html';
        }, 500);
    });
    
    console.log('✅ Forgot password link event listener added');
}

// ===== TOAST NOTIFICATION SYSTEM (SIMPLIFIED) =====
function initToast() {
    window.showToast = function(title, message, type = 'info') {
        console.log(`Toast: ${title} - ${message}`);
        
        // Create a simple alert for now
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.style.maxWidth = '300px';
        alertDiv.innerHTML = `
            <strong>${title}</strong><br>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    };
}

// ===== 1. LOGIN PAGE =====
function initLoginPage() {
    console.log('Initializing login page...');
    
    const loginForm = document.getElementById('loginForm');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    if (!loginForm) {
        console.log('❌ Login form not found');
        return;
    }
    
    // Toggle password visibility
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }
    
    // Real-time validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmailField(this);
        });
    }
    
    // Form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateLoginForm()) return;
        
        // Show loading state
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const btnText = document.getElementById('loginBtnText');
        const spinner = document.getElementById('loginSpinner');
        
        if (btnText && spinner) {
            btnText.textContent = 'Logging in...';
            spinner.classList.remove('d-none');
        }
        
        if (submitBtn) submitBtn.disabled = true;
        
        // Get form data
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;
        
        // Simulate API call
        setTimeout(() => {
            // Check credentials
            const users = JSON.parse(localStorage.getItem('ccrUsers') || '[]');
            const user = users.find(u => u.email === email && u.password === password);
            
            if (user || (email === 'demo@cleancharcoal.rw' && password === 'Demo@123')) {
                // Create user session
                const userSession = {
                    isLoggedIn: true,
                    userType: user ? user.userType : 'producer',
                    userName: user ? `${user.firstName} ${user.lastName}` : 'Demo User',
                    email: email,
                    remember: rememberMe,
                    lastLogin: new Date().toISOString()
                };
                
                // Save session
                if (rememberMe) {
                    localStorage.setItem('userSession', JSON.stringify(userSession));
                } else {
                    sessionStorage.setItem('userSession', JSON.stringify(userSession));
                }
                
                showToast('Success', 'Login successful!', 'success');
                
                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } else {
                showToast('Login Failed', 'Invalid email or password', 'error');
                
                // Reset button
                if (btnText && spinner) {
                    btnText.textContent = 'Login to Account';
                    spinner.classList.add('d-none');
                }
                if (submitBtn) submitBtn.disabled = false;
            }
        }, 1000);
    });
}

function validateLoginForm() {
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    
    let isValid = true;
    
    // Validate email
    if (!validateEmailField(email)) {
        isValid = false;
    }
    
    // Validate password
    if (!validateRequiredField(password, 'Password is required')) {
        isValid = false;
    }
    
    return isValid;
}

// ===== 2. SIGNUP PAGE =====
function initSignupPage() {
    const signupForm = document.getElementById('signupForm');
    
    if (!signupForm) return;
    
    // Password visibility toggles
    const toggleSignupPassword = document.getElementById('toggleSignupPassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const signupPassword = document.getElementById('signupPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    
    if (toggleSignupPassword && signupPassword) {
        toggleSignupPassword.addEventListener('click', function() {
            const type = signupPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            signupPassword.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }
    
    if (toggleConfirmPassword && confirmPassword) {
        toggleConfirmPassword.addEventListener('click', function() {
            const type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPassword.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    }
    
    // Form submission
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitBtn = signupForm.querySelector('button[type="submit"]');
        const btnText = document.getElementById('signupBtnText');
        const spinner = document.getElementById('signupSpinner');
        
        if (btnText && spinner) {
            btnText.textContent = 'Creating Account...';
            spinner.classList.remove('d-none');
        }
        
        if (submitBtn) submitBtn.disabled = true;
        
        // Collect form data
        const formData = {
            firstName: document.getElementById('firstName').value.trim(),
            lastName: document.getElementById('lastName').value.trim(),
            email: document.getElementById('signupEmail').value.trim(),
            password: document.getElementById('signupPassword').value,
            userType: document.getElementById('userType').value,
            createdAt: new Date().toISOString()
        };
        
        // Simulate API call
        setTimeout(() => {
            // Save to localStorage
            const users = JSON.parse(localStorage.getItem('ccrUsers') || '[]');
            users.push(formData);
            localStorage.setItem('ccrUsers', JSON.stringify(users));
            
            showToast('Success', 'Account created successfully!', 'success');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        }, 1000);
    });
}

// ===== 3. COMMON AUTH FUNCTIONS =====
function initCommonAuthFeatures() {
    // Add form validation styles
    const style = document.createElement('style');
    style.textContent = `
        .is-valid {
            border-color: #198754 !important;
        }
        
        .is-invalid {
            border-color: #dc3545 !important;
        }
        
        .invalid-feedback {
            display: block;
            color: #dc3545;
            font-size: 0.875em;
            margin-top: 0.25rem;
        }
    `;
    document.head.appendChild(style);
}

// ===== 4. VALIDATION FUNCTIONS =====
function validateEmailField(input) {
    const email = input.value.trim();
    
    if (!email) {
        showFieldError(input, 'Email is required');
        return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showFieldError(input, 'Please enter a valid email address');
        return false;
    }
    
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    removeFieldError(input);
    return true;
}

function validateRequiredField(input, message) {
    const value = input.value.trim();
    
    if (!value) {
        showFieldError(input, message);
        return false;
    }
    
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    removeFieldError(input);
    return true;
}

function showFieldError(input, message) {
    // Remove any existing error
    removeFieldError(input);
    
    // Add error class
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    
    // Find or create error message element
    let errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        input.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function removeFieldError(input) {
    input.classList.remove('is-invalid');
    
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

// ===== 5. UTILITY FUNCTIONS =====
function ensureDemoUser() {
    const users = JSON.parse(localStorage.getItem('ccrUsers') || '[]');
    const hasDemoUser = users.some(user => user.email === 'demo@cleancharcoal.rw');
    
    if (!hasDemoUser) {
        const demoUser = {
            firstName: 'Demo',
            lastName: 'User',
            email: 'demo@cleancharcoal.rw',
            password: 'Demo@123',
            userType: 'producer',
            createdAt: new Date().toISOString()
        };
        
        users.push(demoUser);
        localStorage.setItem('ccrUsers', JSON.stringify(users));
        console.log('✅ Demo user created');
    }
}