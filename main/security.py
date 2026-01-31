import re
import time
from django.core.cache import cache
from django.conf import settings
from ipware import get_client_ip
from .models import SecurityLog
import random
import string
from datetime import datetime, timedelta
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# ===== CAPTCHA FUNCTIONS =====
def generate_captcha_text(length=6):
    """
    Generate random CAPTCHA text excluding confusing characters
    (no I, O, 0, 1 to avoid confusion)
    """
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choice(chars) for _ in range(length))

def validate_captcha(request, user_input, session_key='captcha'):
    """
    Validate CAPTCHA input against session storage
    Returns: (is_valid, message)
    """
    if not user_input:
        return False, "Please enter the CAPTCHA code"
    
    if session_key not in request.session:
        return False, "CAPTCHA expired. Please refresh the page."
    
    stored_data = request.session.get(session_key)
    if not stored_data or '|' not in stored_data:
        return False, "Invalid CAPTCHA session. Please refresh."
    
    try:
        captcha_text, timestamp_str = stored_data.split('|')
        timestamp = datetime.fromisoformat(timestamp_str)
        
        # Check if CAPTCHA expired (10 minutes)
        if datetime.now() - timestamp > timedelta(minutes=10):
            del request.session[session_key]
            return False, "CAPTCHA expired. Please refresh."
        
        # Compare CAPTCHA (case insensitive)
        if user_input.upper() != captcha_text.upper():
            return False, "Incorrect CAPTCHA code. Please try again."
        
        # Clear CAPTCHA after successful validation
        del request.session[session_key]
        return True, "CAPTCHA validated successfully."
        
    except (ValueError, AttributeError) as e:
        logger.error(f"CAPTCHA validation error: {str(e)}")
        return False, "CAPTCHA validation error. Please refresh the page."

# ===== RATE LIMITING =====
def check_rate_limit(ip, action, limit=5, period=3600):
    """
    Check if IP has exceeded rate limit for specific action
    limit: maximum attempts allowed
    period: time window in seconds (default 1 hour)
    """
    cache_key = f'rate_limit:{action}:{ip}'
    attempts = cache.get(cache_key, 0)
    
    if attempts >= limit:
        return False  # Rate limit exceeded
    
    cache.set(cache_key, attempts + 1, period)
    return True  # Within limit

# ===== SECURITY LOGGING =====
def log_security_event(event_type, ip, user_agent, details=None):
    """
    Log security events for monitoring
    """
    logger.warning(
        f"SECURITY EVENT - Type: {event_type}, IP: {ip}, "
        f"User-Agent: {user_agent[:100]}, Details: {details}"
    )
    
    # You could also save to database here
    # from .models import SecurityLog
    # SecurityLog.objects.create(...)

# ===== FORM VALIDATION =====
def validate_form_data(form_data, required_fields=None):
    """
    Basic form data validation
    """
    errors = {}
    
    if required_fields:
        for field in required_fields:
            if field not in form_data or not form_data.get(field, '').strip():
                errors[field] = f"{field.replace('_', ' ').title()} is required"
    
    # Email validation
    if 'email' in form_data and form_data['email']:
        email = form_data['email'].strip()
        if '@' not in email or '.' not in email:
            errors['email'] = "Please enter a valid email address"
    
    # Phone validation (basic)
    if 'phone' in form_data and form_data['phone']:
        phone = form_data['phone'].strip()
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            errors['phone'] = "Please enter a valid phone number (at least 10 digits)"
    
    return errors
def log_security_event(event_type, ip, user_agent, details):
    """Log security events to database"""
    try:
        SecurityLog.objects.create(
            event_type=event_type,
            ip_address=ip,
            user_agent=user_agent[:500] if user_agent else '',
            details=details[:1000]
        )
    except Exception as e:
        # Fallback to console logging if database fails
        print(f"Security Event - {event_type}: {details}")

def check_rate_limit(ip, action, limit=5, period=60):
    """Implement rate limiting for actions"""
    cache_key = f"rate_limit:{ip}:{action}"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= limit:
        log_security_event('rate_limit', ip, '', f'Rate limit exceeded for {action}')
        return False
    
    cache.set(cache_key, attempts + 1, period)
    return True

def validate_form_data(form_data):
    """Validate form data for malicious content"""
    # SQL injection patterns
    sql_patterns = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
    ]
    
    # XSS patterns
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<applet[^>]*>.*?</applet>",
    ]
    
    # Check each form field
    for key, value in form_data.items():
        if isinstance(value, str):
            # Check for SQL injection
            for pattern in sql_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    return False, f"SQL injection detected in {key}"
            
            # Check for XSS
            for pattern in xss_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    return False, f"XSS attack detected in {key}"
    
    return True, "Valid"

def sanitize_input(input_string):
    """Sanitize user input"""
    if not input_string:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', input_string)
    
    # Escape special characters
    clean = clean.replace('&', '&amp;')
    clean = clean.replace('<', '&lt;')
    clean = clean.replace('>', '&gt;')
    clean = clean.replace('"', '&quot;')
    clean = clean.replace("'", '&#x27;')
    clean = clean.replace('/', '&#x2F;')
    
    # Remove control characters
    clean = ''.join(char for char in clean if ord(char) >= 32 or char in '\n\r\t')
    
    return clean.strip()

def check_bot_activity(user_agent, ip):
    """Check for bot-like activity"""
    if not user_agent:
        return True
    
    bot_indicators = [
        'bot', 'crawl', 'spider', 'scrape', 'curl', 'wget',
        'python', 'java', 'php', 'ruby', 'perl', 'go-http',
        'okhttp', 'requests', 'libwww', 'lwp', 'http-client'
    ]
    
    user_agent_lower = user_agent.lower()
    
    for indicator in bot_indicators:
        if indicator in user_agent_lower:
            log_security_event('bot', ip, user_agent, 'Bot detected')
            return True
    
    return False

def generate_csrf_token():
    """Generate custom CSRF token"""
    import hashlib
    import secrets
    import time
    
    token_data = f"{secrets.token_hex(16)}-{int(time.time())}"
    token_hash = hashlib.sha256(token_data.encode()).hexdigest()
    return f"{token_data}:{token_hash}"

def verify_csrf_token(token):
    """Verify custom CSRF token"""
    try:
        if not token or ':' not in token:
            return False
        
        token_data, token_hash = token.split(':', 1)
        
        if not token_data or not token_hash:
            return False
        
        # Check token expiration (1 hour)
        timestamp = int(token_data.split('-')[-1])
        current_time = int(time.time())
        
        if current_time - timestamp > 3600:  # 1 hour
            return False
        
        # Verify hash
        import hashlib
        expected_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return token_hash == expected_hash
    
    except:
        return False

class SecurityMiddleware:
    """Custom security middleware"""
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add security headers
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP Header (adjust based on your needs)
        csp = [
            "default-src 'self'",
            "script-src 'self' https://www.google.com https://www.gstatic.com",
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
            "img-src 'self' data: https:",
            "font-src 'self' https://cdnjs.cloudflare.com",
            "connect-src 'self'",
            "frame-ancestors 'none'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp)
        
        return response