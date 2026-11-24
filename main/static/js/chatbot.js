// Sharsh - BunShai TECHNOHUB AI assistant widget
class Chatbot {
    constructor() {
        this.sessionId = null;
        this.isOpen = false;
        this.userInfo = {};
        this.awaitingName = false;
        this.greeted = false;
        this.busy = false;
        this.$ = (id) => document.getElementById(id);
        if (!this.$('chatbot-toggle') || !this.$('chatbot-window')) return;
        this.init();
    }

    init() {
        this.loadSession();
        this.bindEvents();
    }

    bindEvents() {
        this.$('chatbot-toggle').addEventListener('click', (e) => { e.stopPropagation(); this.toggle(); });
        this.$('chatbot-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.sendMessage(); }
        });
        this.$('chatbot-send').addEventListener('click', () => this.sendMessage());
        document.querySelectorAll('.chatbot-close').forEach((btn) =>
            btn.addEventListener('click', (e) => { e.stopPropagation(); this.close(); }));
        document.addEventListener('click', (e) => {
            const box = this.$('chatbot-container');
            const path = e.composedPath ? e.composedPath() : [];
            if (this.isOpen && box && !path.includes(box) && !box.contains(e.target)) this.close();
        });
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && this.isOpen) this.close(); });
    }

    // ---------- open / close ----------
    setOpen(state) {
        this.$('chatbot-window').classList.toggle('open', state);
        this.$('chatbot-toggle').classList.toggle('active', state);
        this.isOpen = state;
        if (state) {
            setTimeout(() => this.$('chatbot-input').focus(), 300);
            if (!this.greeted) this.greet();
        }
    }
    toggle() { this.setOpen(!this.isOpen); }
    open() { this.setOpen(true); }
    close() { this.setOpen(false); }

    // ---------- session ----------
    loadSession() {
        this.sessionId = localStorage.getItem('chatbot_session_id');
        try { this.userInfo = JSON.parse(localStorage.getItem('chatbot_user_info') || '{}') || {}; }
        catch (e) { this.userInfo = {}; }
    }
    saveSession() {
        if (this.sessionId) localStorage.setItem('chatbot_session_id', this.sessionId);
        localStorage.setItem('chatbot_user_info', JSON.stringify(this.userInfo));
    }

    greet() {
        this.greeted = true;
        const welcome = document.querySelector('#chatbot-messages .chatbot-welcome');
        if (welcome) welcome.remove();
        if (this.userInfo.name) {
            this.addMessage('bot', `👋 Welcome back, ${this.userInfo.name}! Ask me anything about our courses, services, team or company.`,
                { suggestions: ['Show me your courses', 'What services do you offer?', 'Who leads the company?', 'How can I contact you?'] });
        } else {
            this.awaitingName = true;
            this.addMessage('bot', "👋 Hello! I'm Sharsh, the AI assistant of BunShai TECHNOHUB. I can answer questions about our courses, services, leadership team, careers and company.\n\nMay I know your name? (or just type your question)",
                { suggestions: ['Show me your courses', 'What services do you offer?', 'Who leads the company?', 'How can I contact you?'] });
        }
    }

    looksLikeName(text) {
        return /^[A-Za-z][A-Za-z .'-]{1,40}$/.test(text) && text.trim().split(/\s+/).length <= 3 &&
            !/\b(course|service|price|fee|contact|hi|hello|hey|help|team|career|job|about|syllabus)\b/i.test(text);
    }

    // ---------- sending ----------
    async sendMessage(preset) {
        const input = this.$('chatbot-input');
        const message = (preset || input.value).trim();
        if (!message || this.busy) return;
        input.value = '';
        this.clearChips();
        this.addMessage('user', message);

        if (this.awaitingName) {
            this.awaitingName = false;
            if (this.looksLikeName(message)) {
                this.userInfo.name = message.replace(/\s+/g, ' ');
                this.saveSession();
                this.addMessage('bot', `Nice to meet you, ${this.userInfo.name}! 😊 What would you like to know?`,
                    { suggestions: ['Show me your courses', 'What services do you offer?', 'Who leads the company?'] });
                return;
            }
        }
        await this.processMessage(message);
    }

    async post(message) {
        const res = await fetch('/api/chatbot/send-message/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCSRFToken() },
            body: JSON.stringify({ session_id: this.sessionId, message, user_info: this.userInfo, page: location.pathname }),
        });
        let data = {};
        try { data = await res.json(); } catch (e) { /* ignore */ }
        return { res, data };
    }

    async processMessage(message) {
        this.busy = true;
        this.showTyping();
        try {
            let { res, data } = await this.post(message);
            if (res.status === 404 && data.error === 'Invalid session') {
                this.sessionId = null;
                localStorage.removeItem('chatbot_session_id');
                ({ res, data } = await this.post(message));
            }
            this.hideTyping();
            if (data.success) {
                if (data.session_id && data.session_id !== this.sessionId) {
                    this.sessionId = data.session_id;
                    this.saveSession();
                }
                this.addMessage('bot', data.response, {
                    links: data.links, suggestions: data.suggestions,
                    fallback: data.fallback, contactUrl: data.contact_url,
                });
            } else {
                this.addMessage('bot', data.error || "I'm having trouble right now.", {
                    links: [{ label: '📝 Open Contact Form', url: '/contact/?source=chatbot&subject=Chatbot%20enquiry&message=' + encodeURIComponent(message) }],
                });
            }
        } catch (err) {
            this.hideTyping();
            this.addMessage('bot', "I'm having connection issues. Please try again, or contact our team directly.", {
                links: [{ label: '📝 Open Contact Form', url: '/contact/?source=chatbot&subject=Chatbot%20enquiry&message=' + encodeURIComponent(message) }],
            });
        } finally {
            this.busy = false;
        }
    }

    // ---------- rendering ----------
    addMessage(sender, text, extra = {}) {
        const box = this.$('chatbot-messages');
        const div = document.createElement('div');
        div.className = `chatbot-message ${sender}`;
        const content = document.createElement('div');
        content.className = 'message-content';
        const body = document.createElement('div');
        body.className = 'message-text';
        body.innerHTML = this.formatMessage(text);
        content.appendChild(body);

        if (extra.links && extra.links.length) {
            const wrap = document.createElement('div');
            wrap.className = 'chat-links';
            extra.links.forEach((l, i) => {
                const a = document.createElement('a');
                a.href = l.url;
                a.textContent = l.label;
                a.className = 'chat-link-btn' + (extra.fallback && i === 0 ? ' primary' : '');
                if (/^https?:/.test(l.url)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
                wrap.appendChild(a);
            });
            content.appendChild(wrap);
        }
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        content.appendChild(time);
        div.appendChild(content);
        box.appendChild(div);

        if (extra.suggestions && extra.suggestions.length) {
            const chips = document.createElement('div');
            chips.className = 'chat-chips';
            extra.suggestions.forEach((s) => {
                const b = document.createElement('button');
                b.type = 'button';
                b.className = 'chat-chip';
                b.textContent = s;
                b.addEventListener('click', () => this.sendMessage(s));
                chips.appendChild(b);
            });
            box.appendChild(chips);
        }
        box.scrollTop = box.scrollHeight;
    }

    clearChips() { document.querySelectorAll('#chatbot-messages .chat-chips').forEach((c) => c.remove()); }

    showTyping() {
        const box = this.$('chatbot-messages');
        const el = document.createElement('div');
        el.id = 'typing-indicator';
        el.className = 'chatbot-message bot typing';
        el.innerHTML = '<div class="message-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
        box.appendChild(el);
        box.scrollTop = box.scrollHeight;
    }
    hideTyping() { const t = this.$('typing-indicator'); if (t) t.remove(); }

    formatMessage(text) {
        const safe = String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return safe.replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    }

    getCSRFToken() {
        const c = document.cookie.split(';').find((x) => x.trim().startsWith('csrftoken='));
        return c ? c.trim().split('=')[1] : '';
    }
}

// Quick actions in the widget footer
function quickChatbotAction(action) {
    const bot = window.chatbot;
    if (!bot) return;
    if (!bot.isOpen) bot.open();
    const messages = {
        services: 'What services do you offer?',
        pricing: 'What are your fees and pricing?',
        contact: 'How can I contact your team?',
        courses: 'Show me your courses',
        team: 'Who is on your leadership team?',
    };
    if (messages[action]) {
        bot.awaitingName = false;
        bot.sendMessage(messages[action]);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    window.chatbot = new Chatbot();
});
