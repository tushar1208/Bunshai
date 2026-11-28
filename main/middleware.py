from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalDomainMiddleware:
    """
    Redirect alternate hostnames (e.g., www or onrender.com) to CANONICAL_HOST
    in production when ENFORCE_CUSTOM_DOMAIN is enabled.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        canonical = getattr(settings, 'CANONICAL_HOST', '').strip().lower()
        if (
            not settings.DEBUG
            and getattr(settings, 'ENFORCE_CUSTOM_DOMAIN', False)
            and canonical
            and request.method in ('GET', 'HEAD')
            and request.path.rstrip('/') != '/healthz'
        ):
            request_host = request.get_host().split(':')[0].lower()
            if request_host and request_host != canonical:
                return HttpResponsePermanentRedirect(
                    f'https://{canonical}{request.get_full_path()}'
                )
        return self.get_response(request)


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
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "media-src 'self'; "
                "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com data:; "
                "frame-src 'self' https://www.google.com https://maps.google.com; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
            response['Content-Security-Policy'] = csp
        
        return response