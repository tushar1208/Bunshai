from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def site_info(request):
    """Add site information to all templates"""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'BunShai TECHNOHUB'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'Your trusted technology partner'),
        'SITE_EMAIL': getattr(settings, 'SITE_EMAIL', 'team.bunshailogicloop@gmail.com'),
        'SITE_PHONE': getattr(settings, 'SITE_PHONE', '+91 8091401208'),
        'SITE_ADDRESS': getattr(settings, 'SITE_ADDRESS', 'Global / Remote-first Company'),
        'SITE_FACEBOOK': getattr(settings, 'SITE_FACEBOOK', 'https://www.facebook.com/share/1DFuBTBXN2/'),
        'SITE_YOUTUBE': getattr(settings, 'SITE_YOUTUBE', 'https://www.youtube.com/@Bun_Shai'),
        'SITE_LINKEDIN': getattr(settings, 'SITE_LINKEDIN', 'https://www.linkedin.com/company/bunshai-technohub'),
        'SITE_TWITTER': getattr(settings, 'SITE_TWITTER', 'https://twitter.com'),
        'SITE_INSTAGRAM': getattr(settings, 'SITE_INSTAGRAM', 'https://instagram.com'),
        'DEBUG': settings.DEBUG,
    }
def send_form_submission_email(form_type, data):
    """Send email notification for form submissions"""
    try:
        subject = f'New {form_type} - BunShai TECHNOHUB'
        
        # Create email content
        context = {
            'form_type': form_type,
            'data': data,
            'site_name': settings.SITE_NAME,
            'timestamp': data.get('timestamp', '')
        }
        
        html_message = render_to_string('emails/form_submission.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Also send confirmation to user if email is provided
        if 'email' in data and data['email']:
            send_user_confirmation_email(form_type, data)
            
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_user_confirmation_email(form_type, data):
    """Send confirmation email to user"""
    try:
        subject = f'Thank you for your {form_type} - BunShai TECHNOHUB'
        
        context = {
            'form_type': form_type,
            'name': data.get('name', 'User'),
            'data': data,
            'site_name': settings.SITE_NAME
        }
        
        html_message = render_to_string('emails/user_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[data['email']],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")