document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    const messageTextarea = document.getElementById('message');
    const charCount = document.getElementById('charCount');
    const captchaText = document.getElementById('captchaText');
    const refreshCaptchaBtn = document.getElementById('refreshCaptcha');
    const captchaInput = document.getElementById('captchaInput');
    const captchaHidden = document.getElementById('captchaHidden');
    const captchaError = document.getElementById('captchaError');
    const submitBtn = document.getElementById('submitBtn');
    const successMessage = document.getElementById('successMessage');

    // Character counter for message
    messageTextarea.addEventListener('input', function() {
        const length = this.value.length;
        charCount.textContent = length;

        if (length > 4500) {
            charCount.parentElement.classList.add('error');
            charCount.parentElement.classList.remove('warning');
        } else if (length > 4000) {
            charCount.parentElement.classList.add('warning');
            charCount.parentElement.classList.remove('error');
        } else {
            charCount.parentElement.classList.remove('warning', 'error');
        }
    });

    // Generate CAPTCHA - Get from server session
    function generateCaptcha() {
        // Fetch new CAPTCHA from server
        fetch('/get-captcha/?type=contact')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    captchaText.textContent = data.captcha_text;
                    captchaInput.value = '';
                    captchaError.classList.remove('show');
                }
            })
            .catch(error => {
                console.error('Error fetching CAPTCHA:', error);
                // Fallback to client-side generation
                const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
                let captcha = '';
                for (let i = 0; i < 6; i++) {
                    captcha += chars.charAt(Math.floor(Math.random() * chars.length));
                }
                captchaText.textContent = captcha;
            });
    }

    // Initialize with current CAPTCHA from server
    captchaText.textContent = '{{ captcha_text|default:"ABCD12" }}';

    // Refresh CAPTCHA
    refreshCaptchaBtn.addEventListener('click', function() {
        generateCaptcha();
    });

    // CAPTCHA validation
    function validateCaptcha() {
        const userInput = captchaInput.value.trim().toUpperCase();
        if (userInput === '') {
            captchaError.textContent = 'Please enter the CAPTCHA code';
            captchaError.classList.add('show');
            return false;
        }

        // Set the CAPTCHA value in hidden field for form submission
        if (captchaHidden) {
            captchaHidden.value = userInput;
        }

        captchaError.classList.remove('show');
        return true;
    }

    // Form validation
    function validateForm() {
        let isValid = true;

        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => {
            el.classList.remove('show');
        });

        // Validate name
        const name = document.getElementById('name').value.trim();
        if (!name || name.length < 2) {
            document.querySelector('#name + .error-message').textContent = 'Please enter a valid name (minimum 2 characters)';
            document.querySelector('#name + .error-message').classList.add('show');
            isValid = false;
        }

        // Validate email
        const email = document.getElementById('email').value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailPattern.test(email)) {
            document.querySelector('#email + .error-message').textContent = 'Please enter a valid email address';
            document.querySelector('#email + .error-message').classList.add('show');
            isValid = false;
        }

        // Validate phone (optional but must be valid if provided)
        const phone = document.getElementById('phone').value.trim();
        if (phone) {
            const phonePattern = /^[\d\s\-\+\(\)]{10,20}$/;
            const phoneDigits = phone.replace(/\D/g, '');
            if (phoneDigits.length < 10 || phoneDigits.length > 15) {
                document.querySelector('#phone + .error-message').textContent = 'Please enter a valid phone number (10-15 digits)';
                document.querySelector('#phone + .error-message').classList.add('show');
                isValid = false;
            }
        }

        // Validate subject
        const subject = document.getElementById('subject').value.trim();
        if (!subject || subject.length < 5) {
            document.querySelector('#subject + .error-message').textContent = 'Please enter a subject (minimum 5 characters)';
            document.querySelector('#subject + .error-message').classList.add('show');
            isValid = false;
        }

        // Validate message
        const message = messageTextarea.value.trim();
        if (!message || message.length < 10) {
            document.querySelector('#message + .error-message').textContent = 'Please enter a message (minimum 10 characters)';
            document.querySelector('#message + .error-message').classList.add('show');
            isValid = false;
        }

        // Validate CAPTCHA
        if (!validateCaptcha()) {
            isValid = false;
        }

        return isValid;
    }

    // Form submission
    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

        // Collect form data
        const formData = new FormData(this);

        try {
            // Send form data to server
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const data = await response.json();

            if (data.success) {
                // Show success message
                successMessage.style.display = 'flex';
                contactForm.reset();
                generateCaptcha(); // Get new CAPTCHA
                charCount.textContent = '0';

                // Show success message from server
                messages.success(data.message);
            } else {
                // Show errors
                if (data.errors) {
                    Object.keys(data.errors).forEach(field => {
                        const errorElement = document.querySelector(`#${field} + .error-message`);
                        if (errorElement) {
                            errorElement.textContent = data.errors[field][0];
                            errorElement.classList.add('show');
                        }

                        // Handle CAPTCHA error specially
                        if (field === 'captcha') {
                            captchaError.textContent = data.errors[field][0];
                            captchaError.classList.add('show');
                            generateCaptcha(); // Refresh CAPTCHA on error
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Form submission error:', error);
            // Fallback to traditional form submission
            this.submit();
        } finally {
            // Reset button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
        }
    });

    // Real-time validation
    const inputs = contactForm.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });

        input.addEventListener('input', function() {
            clearError(this);
        });
    });

    function validateField(field) {
        const errorEl = field.nextElementSibling;
        if (!errorEl || !errorEl.classList.contains('error-message')) return;

        const value = field.value.trim();

        if (field.required && !value) {
            errorEl.textContent = 'This field is required';
            errorEl.classList.add('show');
            return false;
        }

        if (field.type === 'email' && value) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(value)) {
                errorEl.textContent = 'Please enter a valid email address';
                errorEl.classList.add('show');
                return false;
            }
        }

        if (field.id === 'phone' && value) {
            const phoneDigits = value.replace(/\D/g, '');
            if (phoneDigits.length < 10 || phoneDigits.length > 15) {
                errorEl.textContent = 'Please enter a valid phone number (10-15 digits)';
                errorEl.classList.add('show');
                return false;
            }
        }

        errorEl.classList.remove('show');
        return true;
    }

    function clearError(field) {
        const errorEl = field.nextElementSibling;
        if (errorEl && errorEl.classList.contains('error-message')) {
            errorEl.classList.remove('show');
        }
    }
});
