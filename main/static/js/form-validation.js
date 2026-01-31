// Form validation with enhanced security
class FormValidator {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindFormEvents();
        this.initRecaptcha();
    }
    
    bindFormEvents() {
        // Contact form validation
        const contactForm = document.getElementById('contactForm');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => this.validateContactForm(e));
        }
        
        // Subscribe form validation
        const subscribeForm = document.getElementById('footer-subscribe-form');
        if (subscribeForm) {
            subscribeForm.addEventListener('submit', (e) => this.validateSubscribeForm(e));
        }
        
        // Real-time validation
        this.initRealTimeValidation();
    }
    
    initRecaptcha() {
        // reCAPTCHA callback
        window.onRecaptchaSuccess = function() {
            document.getElementById('recaptcha-error').style.display = 'none';
        };
        
        window.onRecaptchaError = function() {
            document.getElementById('recaptcha-error').style.display = 'block';
        };
        
        window.onRecaptchaExpired = function() {
            document.getElementById('recaptcha-error').textContent = 'reCAPTCHA expired. Please verify again.';
            document.getElementById('recaptcha-error').style.display = 'block';
        };
    }
    
    validateContactForm(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const errors = [];
        
        // Validate name
        const name = formData.get('name');
        if (!name || name.trim().length < 2) {
            errors.push('Name must be at least 2 characters');
        }
        
        // Validate email
        const email = formData.get('email');
        if (!this.validateEmail(email)) {
            errors.push('Please enter a valid email address');
        }
        
        // Validate message
        const message = formData.get('message');
        if (!message || message.trim().length < 10) {
            errors.push('Message must be at least 10 characters');
        }
        
        // Check for spam keywords
        if (this.containsSpam(message)) {
            errors.push('Message contains suspicious content');
            this.logSecurityEvent('spam_attempt', {email: email});
        }
        
        // Validate reCAPTCHA
        const recaptchaResponse = grecaptcha.getResponse();
        if (!recaptchaResponse) {
            errors.push('Please complete the reCAPTCHA verification');
        }
        
        if (errors.length > 0) {
            this.showErrors(form, errors);
            return false;
        }
        
        // Submit form via AJAX
        this.submitFormViaAjax(form, 'contact');
        return false;
    }
    
    validateSubscribeForm(e) {
        e.preventDefault();
        
        const form = e.target;
        const email = form.querySelector('input[type="email"]').value;
        
        if (!this.validateEmail(email)) {
            this.showError(form, 'Please enter a valid email address');
            return false;
        }
        
        // Submit via AJAX
        this.submitFormViaAjax(form, 'subscribe');
        return false;
    }
    
    initRealTimeValidation() {
        // Email validation
        document.querySelectorAll('input[type="email"]').forEach(input => {
            input.addEventListener('blur', () => {
                if (input.value && !this.validateEmail(input.value)) {
                    this.showFieldError(input, 'Invalid email format');
                } else {
                    this.clearFieldError(input);
                }
            });
        });
        
        // Phone validation
        document.querySelectorAll('input[type="tel"]').forEach(input => {
            input.addEventListener('blur', () => {
                if (input.value && !this.validatePhone(input.value)) {
                    this.showFieldError(input, 'Invalid phone number');
                } else {
                    this.clearFieldError(input);
                }
            });
        });
        
        // Required fields
        document.querySelectorAll('[required]').forEach(input => {
            input.addEventListener('blur', () => {
                if (!input.value.trim()) {
                    this.showFieldError(input, 'This field is required');
                } else {
                    this.clearFieldError(input);
                }
            });
        });
    }
    
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    validatePhone(phone) {
        // Remove non-digit characters
        const digits = phone.replace(/\D/g, '');
        return digits.length >= 10;
    }
    
    containsSpam(text) {
        const spamPatterns = [
            /buy\s+now/i,
            /click\s+here/i,
            /http:\/\//i,
            /https:\/\//i,
            /www\./i,
            /\.com\s+free/i,
            /viagra/i,
            /casino/i,
            /loan/i,
            /insurance/i
        ];
        
        return spamPatterns.some(pattern => pattern.test(text));
    }
    
    showErrors(form, errors) {
        // Clear previous errors
        this.clearErrors(form);
        
        // Create error container
        const errorContainer = document.createElement('div');
        errorContainer.className = 'form-errors';
        errorContainer.innerHTML = `
            <div class="error-header">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Please fix the following errors:</strong>
            </div>
            <ul>
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;
        
        // Insert before form
        form.parentNode.insertBefore(errorContainer, form);
        
        // Scroll to errors
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    showError(form, message) {
        // Clear previous errors
        this.clearErrors(form);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-circle"></i> ${message}
        `;
        
        form.parentNode.insertBefore(errorDiv, form);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    showFieldError(input, message) {
        this.clearFieldError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
        input.classList.add('error');
    }
    
    clearFieldError(input) {
        const errorDiv = input.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
        input.classList.remove('error');
    }
    
    clearErrors(form) {
        const errors = form.parentNode.querySelectorAll('.form-errors, .alert-error');
        errors.forEach(error => error.remove());
    }
    
    async submitFormViaAjax(form, formType) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        submitBtn.disabled = true;
        
        try {
            const formData = new FormData(form);
            
            // Add form type
            formData.append('form_type', formType);
            
            // Add CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const response = await fetch(form.action || window.location.pathname, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Show success message
                this.showSuccess(form, data.message);
                
                // Reset form
                form.reset();
                
                // Reset reCAPTCHA
                if (typeof grecaptcha !== 'undefined') {
                    grecaptcha.reset();
                }
                
                // Log success
                this.logFormSubmission(formType, 'success');
                
            } else {
                // Show errors
                if (data.errors) {
                    const errors = Object.values(data.errors).flat();
                    this.showErrors(form, errors);
                } else {
                    this.showError(form, data.message || 'An error occurred');
                }
                
                // Log error
                this.logFormSubmission(formType, 'error', data.errors);
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.showError(form, 'Network error. Please try again.');
            this.logFormSubmission(formType, 'network_error');
            
        } finally {
            // Restore button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
    
    showSuccess(form, message) {
        this.clearErrors(form);
        
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success';
        successDiv.innerHTML = `
            <i class="fas fa-check-circle"></i> ${message}
        `;
        
        form.parentNode.insertBefore(successDiv, form);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.remove();
            }
        }, 5000);
    }
    
    logFormSubmission(type, status, data = null) {
        // Log to console (in production, send to analytics)
        console.log(`Form ${type}: ${status}`, data);
        
        // Send to security log
        if (status !== 'success') {
            fetch('/api/security/log/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    event: 'form_submission',
                    type: type,
                    status: status,
                    data: data,
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                })
            }).catch(() => {
                // Silently fail if logging fails
            });
        }
    }
    
    logSecurityEvent(event, data) {
        fetch('/api/security/log/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                event: event,
                data: data,
                url: window.location.href,
                timestamp: new Date().toISOString()
            })
        }).catch(() => {
            // Silently fail if logging fails
        });
    }
}

// Initialize form validator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.formValidator = new FormValidator();
    
    // Add CSS for error states
    const style = document.createElement('style');
    style.textContent = `
        .form-errors {
            background: #fee;
            border: 1px solid #f99;
            border-radius: var(--border-radius);
            padding: 15px;
            margin-bottom: 20px;
            color: #c00;
        }
        
        .form-errors .error-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .form-errors ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .form-errors li {
            margin-bottom: 5px;
        }
        
        .field-error {
            color: #ef4444;
            font-size: 0.8rem;
            margin-top: 5px;
        }
        
        input.error,
        textarea.error,
        select.error {
            border-color: #ef4444 !important;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
        }
        
        .alert {
            padding: 15px;
            border-radius: var(--border-radius);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .alert-error {
            background: #fee;
            border: 1px solid #f99;
            color: #c00;
        }
        
        .alert-success {
            background: #d1fae5;
            border: 1px solid #10b981;
            color: #065f46;
        }
        
        .recaptcha-error {
            color: #ef4444;
            font-size: 0.9rem;
            margin-top: 10px;
            display: none;
        }
    `;
    document.head.appendChild(style);
});