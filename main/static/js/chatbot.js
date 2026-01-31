// Chatbot functionality
class Chatbot {
    constructor() {
        this.sessionId = null;
        this.isOpen = false;
        this.userInfo = {};
        this.init();
    }
    
    init() {
        this.loadSession();
        this.bindEvents();
        this.checkReturningUser();
        this.setupCloseButton();
    }
    
    bindEvents() {
        // Chatbot toggle
        document.getElementById('chatbot-toggle').addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Send message on Enter
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button
        document.getElementById('chatbot-send').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            const chatbot = document.getElementById('chatbot-container');
            if (!chatbot.contains(e.target)) {
                this.close();
            }
        });
    }
    setupCloseButton() {
        // Check if close button exists or create it
        let closeBtn = document.querySelector('.chatbot-close');
        
        if (!closeBtn) {
            // Get the header or create close button
            const header = document.querySelector('.chatbot-header');
            if (header) {
                closeBtn = document.createElement('button');
                closeBtn.className = 'chatbot-close';
                closeBtn.innerHTML = '&times;';
                closeBtn.setAttribute('aria-label', 'Close chatbot');
                header.appendChild(closeBtn);
                
                // Add event listener
                closeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.close();
                });
            }
        } else {
            // Add event listener to existing close button
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.close();
            });
        }
    }
    toggle() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        if (this.isOpen) {
            window.classList.remove('open');
            toggle.classList.remove('active');
            this.isOpen = false;
        } else {
            window.classList.add('open');
            toggle.classList.add('active');
            this.isOpen = true;
            this.focusInput();
            
            // Show intro if first time
            if (!this.sessionId) {
                setTimeout(() => this.showIntro(), 500);
            }
        }
    }
    
    open() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        window.classList.add('open');
        toggle.classList.add('active');
        this.isOpen = true;
        this.focusInput();
    }
    
    close() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        window.classList.remove('open');
        toggle.classList.remove('active');
        this.isOpen = false;
    }
    
    focusInput() {
        setTimeout(() => {
            document.getElementById('chatbot-input').focus();
        }, 300);
    }
    
    loadSession() {
        this.sessionId = localStorage.getItem('chatbot_session_id');
        const savedInfo = localStorage.getItem('chatbot_user_info');
        
        if (savedInfo) {
            this.userInfo = JSON.parse(savedInfo);
        }
    }
    
    saveSession() {
        if (this.sessionId) {
            localStorage.setItem('chatbot_session_id', this.sessionId);
        }
        
        if (Object.keys(this.userInfo).length > 0) {
            localStorage.setItem('chatbot_user_info', JSON.stringify(this.userInfo));
        }
    }
    
    checkReturningUser() {
        if (this.userInfo.email) {
            // Check if user has chatted before
            fetch('/api/chatbot/check-user/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    email: this.userInfo.email
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_returning) {
                    this.addMessage('bot', 'Welcome back! How can I help you today?');
                }
            })
            .catch(() => {
                // Silently fail
            });
        }
    }
    
    showIntro() {
        if (!this.sessionId || !this.userInfo.name) {
            this.addMessage('bot', "👋 Hello! I'm Sharsh, your AI assistant at BunShai TECHNOHUB. What's your name?");
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addMessage('user', message);
        input.value = '';
        
        // Check if we need to collect user info
        if (!this.userInfo.name) {
            this.userInfo.name = message;
            this.addMessage('bot', `Nice to meet you, ${message}! What's your email address?`);
            this.saveSession();
            return;
        }
        
        if (!this.userInfo.email && this.validateEmail(message)) {
            this.userInfo.email = message;
            this.addMessage('bot', `Thank you! What's your phone number?`);
            this.saveSession();
            return;
        }
        
        if (!this.userInfo.phone && this.validatePhone(message)) {
            this.userInfo.phone = message;
            this.addMessage('bot', `Perfect! Now, how can I help you today? You can ask about our services, pricing, or anything else!`);
            
            // Create session on server
            this.createSession();
            return;
        }
        
        // Process the message
        this.processMessage(message);
    }
    
    async createSession() {
        try {
            const response = await fetch('/api/chatbot/start-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(this.userInfo)
            });
            
            const data = await response.json();
            if (data.success) {
                this.sessionId = data.session_id;
                this.saveSession();
            }
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    }
    
    async processMessage(message) {
        // Show typing indicator
        this.showTyping();
        
        try {
            const response = await fetch('/api/chatbot/send-message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message,
                    user_info: this.userInfo
                })
            });
            
            const data = await response.json();
            this.hideTyping();
            
            if (data.success) {
                this.addMessage('bot', data.response);
            } else {
                this.addMessage('bot', "I apologize, but I'm having trouble processing your request. Please try again or contact our team directly.");
            }
        } catch (error) {
            this.hideTyping();
            this.addMessage('bot', "I'm having connection issues. Please try again or contact our team at +91 8091401208");
        }
    }
    
    addMessage(sender, text) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        
        messageDiv.className = `chatbot-message ${sender}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.formatMessage(text)}</div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showTyping() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingDiv = document.createElement('div');
        
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chatbot-message bot typing';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    formatMessage(text) {
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    }
    
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    validatePhone(phone) {
        const re = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        return re.test(phone);
    }
    
    getCSRFToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}

// Quick actions
function quickChatbotAction(action) {
    const chatbot = new Chatbot();
    const messages = {
        'services': 'What services do you offer?',
        'pricing': 'What are your pricing plans?',
        'contact': 'How can I contact your team?'
    };
    
    if (messages[action]) {
        document.getElementById('chatbot-input').value = messages[action];
        chatbot.sendMessage();
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new Chatbot();
    
    // Auto-open chatbot on service pages
    if (window.location.pathname.includes('/services/')) {
        setTimeout(() => {
            chatbot.open();
            chatbot.addMessage('bot', "I see you're interested in our services! How can I assist you?");
        }, 3000);
    }
});