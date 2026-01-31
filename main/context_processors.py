from django.conf import settings
from .models import ContactMessage, Subscriber, ServiceInquiry

def site_info(request):
    """Add site information to template context"""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
        'current_path': request.path,
        'is_homepage': request.path == '/',
    }

def form_counts(request):
    """Add form submission counts to admin context"""
    if request.user.is_staff:
        return {
            'unread_contacts': ContactMessage.objects.filter(is_verified=False, is_spam=False).count(),
            'new_subscribers': Subscriber.objects.filter(is_verified=False).count(),
            'pending_inquiries': ServiceInquiry.objects.count(),
        }
    return {}