// Security protection against inspection and screenshots
// (function() {
//     'use strict';
    
//     // Prevent right-click
//     document.addEventListener('contextmenu', function(e) {
//         e.preventDefault();
//         showSecurityAlert('Right-click is disabled for security reasons.');
//     });
    
//     // Prevent F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
//     document.addEventListener('keydown', function(e) {
//         if (e.key === 'F12' || 
//             (e.ctrlKey && e.shiftKey && e.key === 'I') ||
//             (e.ctrlKey && e.shiftKey && e.key === 'J') ||
//             (e.ctrlKey && e.key === 'U')) {
//             e.preventDefault();
//             showSecurityAlert('Developer tools are disabled.');
//             return false;
//         }
//     });
    
//     // Detect DevTools opening
//     let devtools = /./;
//     devtools.toString = function() {
//         showSecurityAlert('Developer tools detected. This action has been logged.');
//         return '';
//     };
    
//     console.log('%c', devtools);
    
//     // Anti-screenshot protection (CSS method)
//     const style = document.createElement('style');
//     style.textContent = `
//         @media print {
//             * {
//                 display: none !important;
//             }
//         }
//         @media screen and (max-width: 99999px) {
//             body::selection {
//                 background: transparent !important;
//                 color: inherit !important;
//             }
//             body::-moz-selection {
//                 background: transparent !important;
//                 color: inherit !important;
//             }
//         }
//     `;
//     document.head.appendChild(style);
    
//     // Prevent copy
//     document.addEventListener('copy', function(e) {
//         e.preventDefault();
//         showSecurityAlert('Copying is disabled.');
//     });
    
//     // Prevent cut
//     document.addEventListener('cut', function(e) {
//         e.preventDefault();
//         showSecurityAlert('Cutting is disabled.');
//     });
    
//     // Prevent paste
//     document.addEventListener('paste', function(e) {
//         e.preventDefault();
//         showSecurityAlert('Pasting is disabled.');
//     });
    
//     // Detect iframe embedding
//     if (window.self !== window.top) {
//         document.body.innerHTML = '<div style="padding: 20px; text-align: center;"><h2>This website cannot be embedded in iframes.</h2><p>Please visit directly.</p></div>';
//     }
    
//     // Mouse jitter detection (bot detection)
//     let mouseMovementCount = 0;
//     let lastMouseMove = Date.now();
    
//     document.addEventListener('mousemove', function() {
//         mouseMovementCount++;
//         lastMouseMove = Date.now();
        
//         // If too many mouse movements in short time (bot-like behavior)
//         if (mouseMovementCount > 100 && (Date.now() - lastMouseMove) < 1000) {
//             showSecurityAlert('Suspicious activity detected.');
//         }
//     });
    
//     // Reset counter every 5 seconds
//     setInterval(function() {
//         mouseMovementCount = 0;
//     }, 5000);
    
//     // Form submission rate limiting
//     let formSubmissionTimes = [];
    
//     window.addEventListener('submit', function(e) {
//         const now = Date.now();
//         formSubmissionTimes.push(now);
        
//         // Keep only submissions from last minute
//         formSubmissionTimes = formSubmissionTimes.filter(time => now - time < 60000);
        
//         if (formSubmissionTimes.length > 5) {
//             e.preventDefault();
//             showSecurityAlert('Too many form submissions. Please wait a moment.');
//             return false;
//         }
//     });
    
//     // Security alert function
//     function showSecurityAlert(message) {
//         const alertDiv = document.createElement('div');
//         alertDiv.style.cssText = `
//             position: fixed;
//             top: 20px;
//             right: 20px;
//             background: #ef4444;
//             color: white;
//             padding: 15px 20px;
//             border-radius: 8px;
//             z-index: 9999;
//             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
//             animation: slideIn 0.3s ease;
//         `;
        
//         alertDiv.innerHTML = `
//             <strong>Security Alert:</strong> ${message}
//             <button onclick="this.parentElement.remove()" 
//                     style="background: none; border: none; color: white; margin-left: 10px; cursor: pointer;">
//                 ×
//             </button>
//         `;
        
//         document.body.appendChild(alertDiv);
        
//         setTimeout(() => {
//             if (alertDiv.parentElement) {
//                 alertDiv.remove();
//             }
//         }, 5000);
//     }
    
//     // Add CSS for animation
//     const alertStyle = document.createElement('style');
//     alertStyle.textContent = `
//         @keyframes slideIn {
//             from { transform: translateX(100%); opacity: 0; }
//             to { transform: translateX(0); opacity: 1; }
//         }
//     `;
//     document.head.appendChild(alertStyle);
    
//     // Log security events to server
//     function logSecurityEvent(event, details) {
//         fetch('/security-log/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': getCSRFToken()
//             },
//             body: JSON.stringify({
//                 event: event,
//                 details: details,
//                 url: window.location.href,
//                 timestamp: new Date().toISOString()
//             })
//         }).catch(() => {
//             // Silently fail if logging fails
//         });
//     }
    
//     function getCSRFToken() {
//         const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
//         return cookie ? cookie.split('=')[1] : '';
//     }
    
//     // Protect sensitive form fields
//     document.querySelectorAll('input[type="password"], input[type="email"]').forEach(input => {
//         input.addEventListener('focus', function() {
//             this.style.backgroundColor = '#fff9c4';
//         });
        
//         input.addEventListener('blur', function() {
//             this.style.backgroundColor = '';
//         });
        
//         // Prevent autocomplete capture
//         input.setAttribute('autocomplete', 'off');
//     });
    
//     // Session timeout warning
//     let idleTime = 0;
//     const idleInterval = setInterval(() => {
//         idleTime++;
//         if (idleTime > 900) { // 15 minutes
//             showSecurityAlert('Your session will expire soon due to inactivity.');
//         }
//         if (idleTime > 1200) { // 20 minutes
//             window.location.reload();
//         }
//     }, 1000);
    
//     // Reset idle time on user activity
//     ['mousemove', 'keypress', 'click', 'scroll'].forEach(event => {
//         document.addEventListener(event, () => {
//             idleTime = 0;
//         });
//     });
    
//     // Console message
//     console.log('%c🔒 Security Alert 🔒', 'color: #ef4444; font-size: 24px; font-weight: bold;');
//     console.log('%cThis website is protected by advanced security measures.', 'color: #666; font-size: 14px;');
//     console.log('%cAny attempt to tamper with or inspect this website will be logged and may result in legal action.', 'color: #ef4444; font-size: 12px;');
// })();