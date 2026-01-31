// ===== GLOBAL VARIABLES =====
let chatbotSessionId = null;
let isChatbotOpen = false;
let unreadMessages = 0;

// ===== DOM READY =====
document.addEventListener('DOMContentLoaded', function() {
    initializeWebsite();
    setupEventListeners();
    setupFormValidation();
    initializeAnimations();
    
    // Check for saved chatbot session
    const savedSession = localStorage.getItem('chatbot_session');
    if (savedSession) {
        chatbotSessionId = savedSession;
    }
    
    // Set current year in footer
    document.getElementById('currentYear').textContent = new Date().getFullYear();
});

// ===== WEBSITE INITIALIZATION =====
function initializeWebsite() {
    // Initialize loader
    setTimeout(() => {
        document.querySelector('.loader').classList.add('hidden');
        document.body.classList.remove('loading');
    }, 1000);
    
    // Initialize header scroll effect
    window.addEventListener('scroll', handleHeaderScroll);
    handleHeaderScroll(); // Initial check
    
    // Initialize back to top button
    window.addEventListener('scroll', handleBackToTop);
    
    // Check for any messages in URL
    checkUrlMessages();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize lazy loading for images
    initLazyLoading();
    
    // Initialize intersection observer for animations
    initIntersectionObserver();
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Mobile menu
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const navClose = document.getElementById('nav-close');
    const mainNav = document.getElementById('main-nav');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMobileMenu);
    }
    
    if (navClose) {
        navClose.addEventListener('click', toggleMobileMenu);
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (mainNav && mainNav.classList.contains('show')) {
            if (!mainNav.contains(e.target) && !menuToggle.contains(e.target)) {
                closeMobileMenu();
            }
        }
    });
    
    // Escape key to close menus and popups
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllPopups();
            closeMobileMenu();
        }
    });
    
    // Form submissions
    setupFormSubmissionListeners();
    
    // Newsletter subscription
    const newsletterForm = document.getElementById('footerSubscribeForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletterSubscription);
    }
    
    // Proposal form
    const proposalForm = document.getElementById('proposalForm');
    if (proposalForm) {
        proposalForm.addEventListener('submit', handleProposalSubmission);
    }
}

// ===== HEADER SCROLL EFFECT =====
function handleHeaderScroll() {
    const header = document.getElementById('main-header');
    const backToTop = document.querySelector('.back-to-top');
    
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
    
    if (window.scrollY > 300) {
        backToTop.classList.add('visible');
    } else {
        backToTop.classList.remove('visible');
    }
}

// ===== MOBILE MENU =====
function toggleMobileMenu() {
    const mainNav = document.getElementById('main-nav');
    const body = document.body;
    
    if (mainNav.classList.contains('show')) {
        closeMobileMenu();
    } else {
        mainNav.classList.add('show');
        body.classList.add('menu-open');
        body.style.overflow = 'hidden';
    }
}

function closeMobileMenu() {
    const mainNav = document.getElementById('main-nav');
    const body = document.body;
    
    mainNav.classList.remove('show');
    body.classList.remove('menu-open');
    body.style.overflow = 'auto';
}

// ===== POPUP FUNCTIONS =====
function openLogoPopup() {
    const popup = document.getElementById('logo-popup');
    popup.classList.add('show');
    document.body.classList.add('popup-open');
    document.body.style.overflow = 'hidden';
}

function closeLogoPopup() {
    const popup = document.getElementById('logo-popup');
    popup.classList.remove('show');
    document.body.classList.remove('popup-open');
    document.body.style.overflow = 'auto';
}

function showProposalPopup() {
    const popup = document.getElementById('proposalPopup');
    popup.classList.add('active');
    document.body.classList.add('popup-open');
    document.body.style.overflow = 'hidden';
    closeMobileMenu();
    
    // Focus on first input
    setTimeout(() => {
        const firstInput = popup.querySelector('input, textarea, select');
        if (firstInput) firstInput.focus();
    }, 300);
}

function closeProposalPopup() {
    const popup = document.getElementById('proposalPopup');
    popup.classList.remove('active');
    document.body.classList.remove('popup-open');
    document.body.style.overflow = 'auto';
}

function closeAllPopups() {
    closeLogoPopup();
    closeProposalPopup();
    // Add other popup close functions here
}

// ===== SERVICE INQUIRY POPUP =====
function showServiceInquiryPopup(serviceName, serviceDescription) {
    // This would open a service inquiry popup
    // Implementation depends on your specific needs
    console.log('Inquiry for:', serviceName, serviceDescription);
    
    // You can redirect to contact page with pre-filled service
    // or open a custom popup
    showProposalPopup(); // Using proposal popup for now
}

// ===== BACK TO TOP =====
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function handleBackToTop() {
    const backToTop = document.querySelector('.back-to-top');
    if (window.scrollY > 300) {
        backToTop.classList.add('visible');
    } else {
        backToTop.classList.remove('visible');
    }
}
// ===== IMPORTANT: Attach event listener =====
window.addEventListener('scroll', handleBackToTop);

// ===== Also run on page load to check initial state =====
document.addEventListener('DOMContentLoaded', function() {
    handleBackToTop(); // Check initial scroll position
    
    // Add click event to button
    const backToTop = document.querySelector('.back-to-top');
    if (backToTop) {
        backToTop.addEventListener('click', scrollToTop);
    }
});
// ===== FORM VALIDATION =====
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            // Live validation
            input.addEventListener('input', function() {
                validateField(this);
            });
            
            // Blur validation
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormError(this, 'Please fix the errors before submitting.');
            }
        });
    });
}

function validateField(field) {
    const errorElement = field.nextElementSibling?.classList.contains('error-message') 
        ? field.nextElementSibling 
        : field.parentElement.querySelector('.error-message');
    
    // Remove previous error
    field.classList.remove('error');
    if (errorElement) errorElement.style.display = 'none';
    
    // Check required fields
    // if (field.hasAttribute('required') && !field.value.trim()) {
    //     showFieldError(field, 'This field is required');
    //     return false;
    // }
    
    // Email validation
    if (field.type === 'email' && field.value.trim()) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value.trim())) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Phone validation
    if (field.type === 'tel' && field.value.trim()) {
        const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
        if (!phoneRegex.test(field.value.trim())) {
            showFieldError(field, 'Please enter a valid phone number');
            return false;
        }
    }
    
    // URL validation
    if (field.type === 'url' && field.value.trim()) {
        try {
            new URL(field.value.trim());
        } catch {
            showFieldError(field, 'Please enter a valid URL');
            return false;
        }
    }
    
    return true;
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Check checkbox agreement
    const agreementCheckbox = form.querySelector('input[type="checkbox"][required]');
    if (agreementCheckbox && !agreementCheckbox.checked) {
        showFieldError(agreementCheckbox, 'You must agree to continue');
        isValid = false;
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('error');
    
    let errorElement = field.nextElementSibling?.classList.contains('error-message') 
        ? field.nextElementSibling 
        : field.parentElement.querySelector('.error-message');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        field.parentNode.insertBefore(errorElement, field.nextSibling);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Scroll to error
    errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showFormError(form, message) {
    // Create or show form-level error
    let formError = form.querySelector('.form-error');
    
    if (!formError) {
        formError = document.createElement('div');
        formError.className = 'alert alert-error form-error';
        form.insertBefore(formError, form.firstChild);
    }
    
    formError.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    formError.style.display = 'block';
    
    // Scroll to error
    formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ===== FORM SUBMISSION HANDLERS =====
function setupFormSubmissionListeners() {
    // Contact form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmission);
    }
    
    // Career form
    const careerForm = document.getElementById('careerApplicationForm');
    if (careerForm) {
        careerForm.addEventListener('submit', handleCareerSubmission);
    }
}

function handleProposalSubmission(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('.submit-btn');
    
    if (!validateForm(form)) return;
    
    // Show loading state
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    submitBtn.disabled = true;
    
    // Get form data
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Simulate API call (replace with actual fetch)
    setTimeout(() => {
        // Show success message
        showAlert('success', 'Proposal request submitted successfully! We will contact you soon.');
        
        // Reset form
        form.reset();
        
        // Close popup
        closeProposalPopup();
        
        // Restore button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        // Send to Google Sheets (in production)
        // sendToGoogleSheets('proposal', data);
        
        // Send email notification
        // sendEmailNotification('proposal', data);
        
    }, 1500);
}

function handleContactSubmission(e) {
    e.preventDefault();
    const form = e.target;
    
    if (!validateForm(form)) return;
    
    const submitBtn = form.querySelector('.submit-btn');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    submitBtn.disabled = true;
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Simulate API call
    setTimeout(() => {
        showAlert('success', 'Thank you for your message! We will respond as soon as possible.');
        form.reset();
        
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        // In production: send to backend
        // fetch('/contact/', { method: 'POST', body: formData })
        //     .then(response => response.json())
        //     .then(data => {
        //         if (data.success) {
        //             showAlert('success', data.message);
        //             form.reset();
        //         } else {
        //             showAlert('error', data.errors || 'Something went wrong');
        //         }
        //     })
        //     .catch(error => {
        //         showAlert('error', 'Network error. Please try again.');
        //     })
        //     .finally(() => {
        //         submitBtn.innerHTML = originalText;
        //         submitBtn.disabled = false;
        //     });
        
    }, 1500);
}

function handleCareerSubmission(e) {
    e.preventDefault();
    const form = e.target;
    
    if (!validateForm(form)) return;
    
    // Check file size
    const resumeInput = form.querySelector('input[type="file"]');
    if (resumeInput.files[0]) {
        const fileSize = resumeInput.files[0].size;
        const maxSize = 5 * 1024 * 1024; // 5MB
        
        if (fileSize > maxSize) {
            showFieldError(resumeInput, 'File size must be less than 5MB');
            return;
        }
        
        // Check file type
        const allowedTypes = ['.pdf', '.doc', '.docx'];
        const fileName = resumeInput.files[0].name.toLowerCase();
        const isValidType = allowedTypes.some(type => fileName.endsWith(type));
        
        if (!isValidType) {
            showFieldError(resumeInput, 'Only PDF, DOC, and DOCX files are allowed');
            return;
        }
    }
    
    const submitBtn = form.querySelector('.submit-btn');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    submitBtn.disabled = true;
    
    // Simulate submission
    setTimeout(() => {
        showAlert('success', 'Application submitted successfully! We will review it soon.');
        form.reset();
        
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }, 1500);
}

function handleNewsletterSubscription(e) {
    e.preventDefault();
    const form = e.target;
    const emailInput = form.querySelector('input[type="email"]');
    const messageElement = form.nextElementSibling?.id === 'subscribe-message' 
        ? form.nextElementSibling 
        : document.getElementById('subscribe-message');
    
    if (!emailInput.value.trim()) {
        showFieldError(emailInput, 'Email is required');
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailInput.value.trim())) {
        showFieldError(emailInput, 'Please enter a valid email address');
        return;
    }
    
    // Show loading
    const originalPlaceholder = emailInput.placeholder;
    emailInput.placeholder = 'Subscribing...';
    emailInput.disabled = true;
    
    // Simulate subscription
    setTimeout(() => {
        if (messageElement) {
            messageElement.textContent = 'Thank you for subscribing!';
            messageElement.className = 'alert alert-success';
            messageElement.style.display = 'block';
            
            setTimeout(() => {
                messageElement.style.display = 'none';
            }, 5000);
        }
        
        form.reset();
        emailInput.placeholder = originalPlaceholder;
        emailInput.disabled = false;
        
        // Save to localStorage
        const subscribers = JSON.parse(localStorage.getItem('newsletter_subscribers') || '[]');
        subscribers.push({
            email: emailInput.value.trim(),
            date: new Date().toISOString()
        });
        localStorage.setItem('newsletter_subscribers', JSON.stringify(subscribers));
        
    }, 1000);
}

// ===== ALERT SYSTEM =====
function showAlert(type, message, duration = 5000) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.global-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `global-alert alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i>
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    
    // Add to page
    document.body.appendChild(alertDiv);
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => alertDiv.remove(), 300);
            }
        }, duration);
    }
    
    return alertDiv;
}

function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Add CSS for alerts animation
const alertStyles = document.createElement('style');
alertStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .alert-close {
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        margin-left: auto;
        opacity: 0.7;
        transition: opacity 0.2s;
    }
    
    .alert-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(alertStyles);

// ===== URL MESSAGE HANDLING =====
function checkUrlMessages() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.has('success')) {
        const message = urlParams.get('message') || 'Action completed successfully!';
        showAlert('success', decodeURIComponent(message));
        
        // Clean URL
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }
    
    if (urlParams.has('error')) {
        const message = urlParams.get('message') || 'Something went wrong!';
        showAlert('error', decodeURIComponent(message));
        
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }
}

// ===== TOOLTIPS =====
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
        element.addEventListener('focus', showTooltip);
        element.addEventListener('blur', hideTooltip);
    });
}

function showTooltip(e) {
    const element = e.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    // Remove existing tooltip
    hideTooltip();
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-element';
    tooltip.textContent = tooltipText;
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.cssText = `
        position: fixed;
        background: var(--dark);
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 9999;
        white-space: nowrap;
        pointer-events: none;
        top: ${rect.top - 35}px;
        left: ${rect.left + (rect.width / 2)}px;
        transform: translateX(-50%);
    `;
    
    // Add arrow
    const arrow = document.createElement('div');
    arrow.style.cssText = `
        position: absolute;
        bottom: -5px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid var(--dark);
    `;
    
    tooltip.appendChild(arrow);
    document.body.appendChild(tooltip);
    
    // Store reference
    element.tooltipElement = tooltip;
}

function hideTooltip() {
    const existingTooltip = document.querySelector('.tooltip-element');
    if (existingTooltip) {
        existingTooltip.remove();
    }
}

// ===== LAZY LOADING =====
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    
                    if (src) {
                        img.src = src;
                        img.classList.add('loaded');
                    }
                    
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.getAttribute('data-src');
        });
    }
}

// ===== ANIMATIONS =====
function initializeAnimations() {
    // Add animation classes on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight * 0.85) {
                element.classList.add('animated');
            }
        });
    };
    
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Initial check
}

function initIntersectionObserver() {
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right').forEach(el => {
            observer.observe(el);
        });
    }
}

// ===== UTILITY FUNCTIONS =====
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== COOKIE FUNCTIONS =====
function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/;SameSite=Strict";
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function deleteCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999; path=/;';
}

// ===== SESSION STORAGE HELPERS =====
function saveToSession(key, data) {
    try {
        sessionStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
        console.error('Error saving to session storage:', e);
    }
}

function getFromSession(key) {
    try {
        const data = sessionStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Error reading from session storage:', e);
        return null;
    }
}

function removeFromSession(key) {
    try {
        sessionStorage.removeItem(key);
    } catch (e) {
        console.error('Error removing from session storage:', e);
    }
}

// ===== PERFORMANCE MONITORING =====
function monitorPerformance() {
    if ('performance' in window) {
        // Log page load time
        window.addEventListener('load', () => {
            const timing = performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            console.log(`Page loaded in ${loadTime}ms`);
            
            // Send to analytics if needed
            if (loadTime > 3000) {
                console.warn('Page load time exceeds 3 seconds');
            }
        });
        
        // Monitor long tasks
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.duration > 50) {
                        console.warn('Long task detected:', entry);
                    }
                }
            });
            observer.observe({ entryTypes: ['longtask'] });
        }
    }
}

// Initialize performance monitoring
monitorPerformance();

// ===== ERROR HANDLING =====
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    
    // Send to error tracking service (in production)
    // trackError(e.error);
    
    // Show user-friendly message for critical errors
    if (e.error.message.includes('critical')) {
        showAlert('error', 'Something went wrong. Please refresh the page.');
    }
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    // trackError(e.reason);
});

// ===== EXPORT FOR MODULE SUPPORT =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showAlert,
        validateForm,
        showFieldError,
        debounce,
        throttle
    };
}