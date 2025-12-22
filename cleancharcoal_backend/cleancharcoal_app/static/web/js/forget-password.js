// forgot-password.js - Password Reset Functionality

// Global variables
let verificationCode = '';
let countdownInterval = null;
let resendCountdownInterval = null;
let currentStep = 1;
let userEmail = '';
let totalSeconds = 300; // 5 minutes
let resendSeconds = 60; // 1 minute

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 Forgot Password Page Loaded');
    
    // Initialize forms
    initEmailForm();
    initCodeForm();
    initPasswordForm();
    initPasswordRequirements();
    
    // Initialize password toggles
    initPasswordToggles();
    
    // Initialize toast
    initToast();
});

// ===== TOAST NOTIFICATION =====
function initToast() {
    window.showToast = function(title, message, type = 'info') {
        const toastEl = document.getElementById('toast');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        
        if (!toastEl || !toastTitle || !toastMessage) return;
        
        // Set content
        toastTitle.textContent = title;
        toastMessage.textContent = message;
        
        // Set color based on type
        const toastHeader = toastEl.querySelector('.toast-header');
        toastHeader.className = 'toast-header';
        if (type === 'success') {
            toastHeader.classList.add('bg-success', 'text-white');
        } else if (type === 'error') {
            toastHeader.classList.add('bg-danger', 'text-white');
        } else if (type === 'warning') {
            toastHeader.classList.add('bg-warning', 'text-dark');
        } else {
            toastHeader.classList.add('bg-info', 'text-white');
        }
        
        // Show toast
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    };
}

// ===== STEP NAVIGATION =====
function goToStep(stepNumber) {
    // Hide all panels
    document.querySelectorAll('.step-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Remove active class from all steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    
    // Show target panel and mark step as active
    const panelId = `stepPanel${stepNumber}`;
    const stepId = `step${stepNumber}`;
    
    document.getElementById(panelId).classList.add('active');
    document.getElementById(stepId).classList.add('active');
    
    // Mark previous steps as completed
    for (let i = 1; i < stepNumber; i++) {
        document.getElementById(`step${i}`).classList.add('completed');
    }
    
    currentStep = stepNumber;
    
    // Start timer if we're on step 2
    if (stepNumber === 2) {
        // Update the email display for Step 2
        const emailDisplay = document.getElementById('userEmailDisplay');
        if (emailDisplay) {
            emailDisplay.textContent = userEmail;
        }

        startCountdown();
        startResendCountdown();
    }
    
    // Stop timers if leaving step 2
    if (stepNumber !== 2) {
        if (countdownInterval) clearInterval(countdownInterval);
        if (resendCountdownInterval) clearInterval(resendCountdownInterval);
    }
}

function showSuccessPanel() {
    // Hide all panels
    document.querySelectorAll('.step-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Mark all steps as completed
    document.querySelectorAll('.step').forEach(step => {
        step.classList.add('completed');
    });
    
    // Show success panel
    document.getElementById('successPanel').classList.add('active');
    
    // Clear intervals
    if (countdownInterval) clearInterval(countdownInterval);
    if (resendCountdownInterval) clearInterval(resendCountdownInterval);
}

// ===== TIMER FUNCTIONS =====
function startCountdown() {
    totalSeconds = 300; // Reset to 5 minutes
    updateCountdownDisplay();
    
    if (countdownInterval) clearInterval(countdownInterval);
    
    countdownInterval = setInterval(() => {
        totalSeconds--;
        updateCountdownDisplay();
        
        if (totalSeconds <= 0) {
            clearInterval(countdownInterval);
            document.getElementById('countdown').textContent = 'Expired!';
            document.getElementById('countdown').classList.add('expired');
            
            // Disable verification
            document.getElementById('verificationCode').disabled = true;
            document.getElementById('verifyBtnText').textContent = 'Code Expired';
            
            showToast('Code Expired', 'The verification code has expired. Please request a new one.', 'error');
        } else if (totalSeconds <= 60) {
            document.getElementById('countdown').classList.add('expiring');
        }
    }, 1000);
}

function updateCountdownDisplay() {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const countdownElement = document.getElementById('countdown');
    
    if (countdownElement) {
        countdownElement.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

function startResendCountdown() {
    resendSeconds = 60;
    updateResendCountdownDisplay();
    
    // Disable resend link
    const resendContainer = document.getElementById('resendContainer');
    const resendLink = document.getElementById('resendCode');
    
    if (resendContainer && resendLink) {
        resendContainer.classList.add('disabled');
        resendLink.style.pointerEvents = 'none';
    }
    
    if (resendCountdownInterval) clearInterval(resendCountdownInterval);
    
    resendCountdownInterval = setInterval(() => {
        resendSeconds--;
        updateResendCountdownDisplay();
        
        if (resendSeconds <= 0) {
            clearInterval(resendCountdownInterval);
            
            // Enable resend link
            if (resendContainer && resendLink) {
                resendContainer.classList.remove('disabled');
                resendLink.style.pointerEvents = 'auto';
                document.getElementById('resendCountdown').textContent = 'You can now resend the code';
            }
        }
    }, 1000);
}

function updateResendCountdownDisplay() {
    const resendCountdownElement = document.getElementById('resendCountdown');
    if (resendCountdownElement) {
        resendCountdownElement.textContent = `You can resend in ${resendSeconds} seconds`;
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===== EMAIL FORM =====
function initEmailForm() {
    const emailForm = document.getElementById('emailForm');
    if (!emailForm) return;
    
    emailForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateEmailForm()) return;
        
        // Get email
        userEmail = document.getElementById('resetEmail').value.trim().toLowerCase();
        
        // Show loading
        const submitBtn = emailForm.querySelector('button[type="submit"]');
        const btnText = document.getElementById('emailBtnText');
        const spinner = document.getElementById('emailSpinner');
        
        if (btnText && spinner) {
            btnText.textContent = 'Sending Code...';
            spinner.classList.remove('d-none');
        }
        if (submitBtn) submitBtn.disabled = true;
        
        try {
            // Call backend API to send OTP
            const csrftoken = getCookie('csrftoken');
            const response = await fetch('/api/password/forgot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken || ''
                },
                body: JSON.stringify({ email: userEmail }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Failed to send verification code');
            }
            
            // Show success
            showToast('Code Sent', `Verification code sent to ${userEmail}`, 'success');
            
            // Move to next step
            goToStep(2);
            
        } catch (error) {
            console.error('Error sending OTP:', error);
            let errorMessage = error.message || 'Failed to send verification code. Please try again.';
            
            // Check if it's a leader restriction error
            if (errorMessage.includes('Leaders cannot reset') || errorMessage.includes('leader')) {
                showToast('Access Restricted', 'Leaders cannot reset their password through this system. Please contact an administrator.', 'error');
            } else {
                showToast('Error', errorMessage, 'error');
            }
            
            showFieldError(document.getElementById('resetEmail'), errorMessage);
        } finally {
            // Reset button
            if (btnText && spinner) {
                btnText.textContent = 'Send Verification Code';
                spinner.classList.add('d-none');
            }
            if (submitBtn) submitBtn.disabled = false;
        }
    });
    
    // Real-time email validation
    const emailInput = document.getElementById('resetEmail');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmailField(this);
        });
        
        emailInput.addEventListener('input', function() {
            clearFieldError(this);
        });
    }
}

function validateEmailForm() {
    const emailInput = document.getElementById('resetEmail');
    
    // Validate email format only - backend will check if user exists
    return validateEmailField(emailInput);
}

// ===== CODE FORM =====
function initCodeForm() {
    const codeForm = document.getElementById('codeForm');
    if (!codeForm) return;
    
    codeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateCodeForm()) return;
        
        // Show loading
        const submitBtn = codeForm.querySelector('button[type="submit"]');
        const btnText = document.getElementById('verifyBtnText');
        const spinner = document.getElementById('verifySpinner');
        
        if (btnText && spinner) {
            btnText.textContent = 'Verifying...';
            spinner.classList.remove('d-none');
        }
        if (submitBtn) submitBtn.disabled = true;
        
        try {
            const enteredCode = document.getElementById('verificationCode').value.trim();
            
            // Store OTP for password reset step (we'll verify it when resetting password)
            // The backend will verify OTP when we submit the new password
            verificationCode = enteredCode;
            
            // Code format is valid, move to password step
            // OTP will be verified when submitting new password
            showToast('Success', 'Code accepted. Please set your new password.', 'success');
            goToStep(3);
            
            // Clear intervals
            if (countdownInterval) clearInterval(countdownInterval);
            if (resendCountdownInterval) clearInterval(resendCountdownInterval);
            
        } catch (error) {
            console.error('Error verifying code:', error);
            showToast('Error', error.message || 'Failed to verify code. Please try again.', 'error');
            showFieldError(document.getElementById('verificationCode'), error.message || 'Verification failed');
        } finally {
            // Reset button
            if (btnText && spinner) {
                btnText.textContent = 'Verify Code';
                spinner.classList.add('d-none');
            }
            if (submitBtn) submitBtn.disabled = false;
        }
    });
    
    // Code input validation
    const codeInput = document.getElementById('verificationCode');
    if (codeInput) {
        codeInput.addEventListener('input', function() {
            // Auto-validate when 5 digits entered
            if (this.value.length === 5) {
                validateCodeField(this);
            }
            
            // Clear error on input
            clearFieldError(this);
        });
        
        codeInput.addEventListener('blur', function() {
            validateCodeField(this);
        });
    }
    
    // Resend code functionality
    const resendLink = document.getElementById('resendCode');
    if (resendLink) {
        resendLink.addEventListener('click', function(e) {
            e.preventDefault();
            resendVerificationCode();
        });
    }
}

function validateCodeForm() {
    const codeInput = document.getElementById('verificationCode');
    return validateCodeField(codeInput);
}

function validateCodeField(input) {
    const code = input.value.trim();
    
    if (!code) {
        showFieldError(input, 'Please enter the verification code');
        return false;
    }
    
    // Check for 5 digits (OTP from backend is 5 digits)
    if (!/^\d{5}$/.test(code)) {
        showFieldError(input, 'Please enter a valid 5-digit code');
        return false;
    }
    
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    removeFieldError(input);
    return true;
}

async function resendVerificationCode() {
    // Check if resend is allowed
    if (resendSeconds > 0) {
        showToast('Please Wait', `You can resend the code in ${resendSeconds} seconds`, 'warning');
        return;
    }
    
    try {
        // Call backend API to resend OTP
        const csrftoken = getCookie('csrftoken');
        const response = await fetch('/api/password/forgot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || ''
            },
            body: JSON.stringify({ email: userEmail }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Failed to resend verification code');
        }
        
        // Reset timers
        totalSeconds = 300;
        startCountdown();
        startResendCountdown();
        
        // Clear the code input
        document.getElementById('verificationCode').value = '';
        document.getElementById('verificationCode').classList.remove('is-valid');
        
        showToast('Code Resent', 'A new verification code has been sent to your email', 'success');
    } catch (error) {
        console.error('Error resending code:', error);
        showToast('Error', error.message || 'Failed to resend code. Please try again.', 'error');
    }
}

// ===== PASSWORD FORM =====
function initPasswordForm() {
    const passwordForm = document.getElementById('passwordForm');
    if (!passwordForm) return;
    
    passwordForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validatePasswordForm()) return;
        
        // Show loading
        const submitBtn = passwordForm.querySelector('button[type="submit"]');
        const btnText = document.getElementById('passwordBtnText');
        const spinner = document.getElementById('passwordSpinner');
        
        if (btnText && spinner) {
            btnText.textContent = 'Resetting Password...';
            spinner.classList.remove('d-none');
        }
        if (submitBtn) submitBtn.disabled = true;
        
        try {
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmNewPassword').value;
            const otp = verificationCode; // OTP entered in step 2
            
            // Call backend API to reset password with OTP verification
            const csrftoken = getCookie('csrftoken');
            const response = await fetch('/api/password/reset/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken || ''
                },
                body: JSON.stringify({
                    email: userEmail,
                    otp: otp,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                let errorMsg = data.error || data.detail || 'Failed to reset password';
                
                // Check if it's a leader restriction error
                if (errorMsg.includes('Leaders cannot reset') || errorMsg.includes('leader')) {
                    errorMsg = 'Leaders cannot reset their password through this system. Please contact an administrator.';
                }
                
                throw new Error(errorMsg);
            }
            
            // Show success
            showSuccessPanel();
            showToast('Success', 'Your password has been reset successfully!', 'success');
            
            console.log(`🔑 Password reset successful for ${userEmail}`);
            
        } catch (error) {
            console.error('Error resetting password:', error);
            let errorMessage = error.message || 'Failed to reset password. Please try again.';
            
            // Check if it's a leader restriction error
            if (errorMessage.includes('Leaders cannot reset') || errorMessage.includes('leader')) {
                showToast('Access Restricted', 'Leaders cannot reset their password through this system. Please contact an administrator.', 'error');
            } else {
                showToast('Error', errorMessage, 'error');
            }
            
            // Reset button
            if (btnText && spinner) {
                btnText.textContent = 'Reset Password';
                spinner.classList.add('d-none');
            }
            if (submitBtn) submitBtn.disabled = false;
        }
    });
    
    // Real-time password validation
    const newPasswordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmNewPassword');
    
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            validatePasswordMatch();
            checkPasswordRequirements(this.value);
        });
    }
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }
}

function initPasswordToggles() {
    // Toggle new password visibility
    const toggleNewPassword = document.getElementById('toggleNewPassword');
    const newPasswordInput = document.getElementById('newPassword');
    
    if (toggleNewPassword && newPasswordInput) {
        toggleNewPassword.addEventListener('click', function() {
            togglePasswordVisibility(newPasswordInput, this);
        });
    }
    
    // Toggle confirm password visibility
    const toggleConfirmPassword = document.getElementById('toggleConfirmNewPassword');
    const confirmPasswordInput = document.getElementById('confirmNewPassword');
    
    if (toggleConfirmPassword && confirmPasswordInput) {
        toggleConfirmPassword.addEventListener('click', function() {
            togglePasswordVisibility(confirmPasswordInput, this);
        });
    }
}

function validatePasswordForm() {
    const newPassword = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmNewPassword');
    
    let isValid = true;
    
    // Validate new password (no length requirement)
    if (!validatePasswordField(newPassword)) {
        isValid = false;
    }
    
    // Validate password match
    if (!validatePasswordMatch()) {
        isValid = false;
    }
    
    return isValid;
}

function validatePasswordField(input) {
    const password = input.value.trim();
    
    if (!password) {
        showFieldError(input, 'Password is required');
        return false;
    }
    
    // No length or complexity requirements - any password is acceptable
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    removeFieldError(input);
    return true;
}

function validatePasswordMatch() {
    const password = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmNewPassword');
    const errorElement = document.getElementById('confirmPasswordError');
    
    if (!password || !confirmPassword) return true;
    
    if (password.value !== confirmPassword.value) {
        confirmPassword.classList.add('is-invalid');
        confirmPassword.classList.remove('is-valid');
        if (errorElement) {
            errorElement.style.display = 'block';
            errorElement.textContent = 'Passwords do not match';
        }
        return false;
    } else {
        confirmPassword.classList.remove('is-invalid');
        confirmPassword.classList.add('is-valid');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
        return true;
    }
}

// ===== PASSWORD REQUIREMENTS =====
function initPasswordRequirements() {
    const newPasswordInput = document.getElementById('newPassword');
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            checkPasswordRequirements(this.value);
        });
    }
}

function checkPasswordRequirements(password, showErrors = false) {
    // No password requirements - any password is acceptable
    // Hide all requirement elements
    ['Length', 'Uppercase', 'Lowercase', 'Number', 'Special'].forEach(req => {
        const element = document.getElementById(`req${req}`);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Always return true since there are no requirements
    return true;
}

// ===== VALIDATION HELPER FUNCTIONS =====
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
    
    // Focus the input
    input.focus();
}

function removeFieldError(input) {
    input.classList.remove('is-invalid');
    
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function clearFieldError(input) {
    input.classList.remove('is-invalid', 'is-valid');
    removeFieldError(input);
}

function togglePasswordVisibility(passwordInput, toggleButton) {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    toggleButton.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
}

// ===== ADDITIONAL FUNCTIONALITY =====

// Auto-focus next input for better UX
function initCodeInputs() {
    const codeInputs = document.querySelectorAll('.code-input');
    codeInputs.forEach((input, index) => {
        input.addEventListener('input', function(e) {
            // Move to next input if current is filled
            if (this.value.length === 1 && index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }
            
            // Auto-submit when all inputs are filled
            const allFilled = Array.from(codeInputs).every(input => input.value.length === 1);
            if (allFilled) {
                document.getElementById('codeForm').dispatchEvent(new Event('submit'));
            }
        });
        
        // Handle backspace
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && this.value.length === 0 && index > 0) {
                codeInputs[index - 1].focus();
            }
        });
    });
}
// No demo user needed - using real backend API
