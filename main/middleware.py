from django.conf import settings

class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Only add CSP in production (DEBUG=False)
        if not settings.DEBUG:
            # Content Security Policy - adjust based on your needs
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
            response['Content-Security-Policy'] = csp
        
        return response