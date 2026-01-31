# main/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import (
    ContactMessage, Subscriber, ServiceInquiry, 
    ProposalRequest, CareerApplication, SecurityLog
)
import logging

logger = logging.getLogger(__name__)

# Email templates
def send_contact_confirmation_email(contact_message):
    """Send confirmation email for contact form submission"""
    try:
        subject = f'Thank you for contacting BunShai TECHNOHUB - #{contact_message.id[:8]}'
        html_message = render_to_string('emails/contact_confirmation.html', {
            'contact': contact_message,
            'support_email': settings.SUPPORT_EMAIL,
            'site_name': settings.SITE_NAME
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_message.email],
            fail_silently=False,
        )
        logger.info(f'Contact confirmation email sent to {contact_message.email}')
    except Exception as e:
        logger.error(f'Error sending contact confirmation email: {e}')
        # Log security event for email failure
        SecurityLog.objects.create(
            event_type='other',
            ip_address=contact_message.ip_address or '0.0.0.0',
            details=f'Failed to send contact confirmation email to {contact_message.email}: {str(e)}'
        )

def send_subscription_confirmation_email(subscriber):
    """Send confirmation email for subscription"""
    try:
        subject = 'Welcome to BunShai TECHNOHUB Newsletter!'
        html_message = render_to_string('emails/subscription_confirmation.html', {
            'subscriber': subscriber,
            'verification_token': subscriber.verification_token,
            'site_name': settings.SITE_NAME
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=False,
        )
        logger.info(f'Subscription confirmation email sent to {subscriber.email}')
    except Exception as e:
        logger.error(f'Error sending subscription confirmation email: {e}')

def send_service_inquiry_email(inquiry):
    """Send notification for service inquiry"""
    try:
        subject = f'New Service Inquiry - {inquiry.get_service_display()}'
        html_message = render_to_string('emails/service_inquiry.html', {
            'inquiry': inquiry,
            'site_name': settings.SITE_NAME
        })
        plain_message = strip_tags(html_message)
        
        # Send to admin
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        logger.info(f'Service inquiry notification sent for {inquiry.email}')
    except Exception as e:
        logger.error(f'Error sending service inquiry email: {e}')

def send_proposal_request_email(proposal):
    """Send notification for proposal request"""
    try:
        subject = f'New Proposal Request - {proposal.get_service_display()}'
        html_message = render_to_string('emails/proposal_request.html', {
            'proposal': proposal,
            'site_name': settings.SITE_NAME
        })
        plain_message = strip_tags(html_message)
        
        # Send to admin
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        logger.info(f'Proposal request notification sent for {proposal.email}')
    except Exception as e:
        logger.error(f'Error sending proposal request email: {e}')

def send_career_application_email(application):
    """Send notification for career application"""
    try:
        subject = f'New Career Application - {application.get_position_display()}'
        html_message = render_to_string('emails/career_application.html', {
            'application': application,
            'site_name': settings.SITE_NAME
        })
        plain_message = strip_tags(html_message)
        
        # Send to HR/admin
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        logger.info(f'Career application notification sent for {application.email}')
    except Exception as e:
        logger.error(f'Error sending career application email: {e}')

# Signal receivers
@receiver(post_save, sender=ContactMessage)
def handle_contact_message_save(sender, instance, created, **kwargs):
    """Handle contact message save signal"""
    if created:
        # Send confirmation email to user
        send_contact_confirmation_email(instance)
        
        # Log the contact submission
        SecurityLog.objects.create(
            event_type='other',
            ip_address=instance.ip_address or '0.0.0.0',
            user_agent=instance.user_agent or '',
            details=f'Contact form submitted by {instance.email}'
        )

@receiver(post_save, sender=Subscriber)
def handle_subscriber_save(sender, instance, created, **kwargs):
    """Handle subscriber save signal"""
    if created:
        # Send confirmation email
        send_subscription_confirmation_email(instance)
        
        # Log subscription
        SecurityLog.objects.create(
            event_type='other',
            ip_address=instance.ip_address or '0.0.0.0',
            details=f'New subscription from {instance.email}'
        )

@receiver(post_save, sender=ServiceInquiry)
def handle_service_inquiry_save(sender, instance, created, **kwargs):
    """Handle service inquiry save signal"""
    if created:
        # Send notification email to admin
        send_service_inquiry_email(instance)
        
        # Log inquiry
        SecurityLog.objects.create(
            event_type='other',
            ip_address=instance.ip_address or '0.0.0.0',
            details=f'Service inquiry from {instance.email} for {instance.get_service_display()}'
        )

@receiver(post_save, sender=ProposalRequest)
def handle_proposal_request_save(sender, instance, created, **kwargs):
    """Handle proposal request save signal"""
    if created:
        # Send notification email to admin
        send_proposal_request_email(instance)
        
        # Log proposal request
        SecurityLog.objects.create(
            event_type='other',
            ip_address=instance.ip_address or '0.0.0.0',
            details=f'Proposal request from {instance.email} for {instance.get_service_display()}'
        )

@receiver(post_save, sender=CareerApplication)
def handle_career_application_save(sender, instance, created, **kwargs):
    """Handle career application save signal"""
    if created:
        # Send notification email to HR/admin
        send_career_application_email(instance)
        
        # Log application
        SecurityLog.objects.create(
            event_type='other',
            ip_address=instance.ip_address or '0.0.0.0',
            details=f'Career application from {instance.email} for {instance.get_position_display()}'
        )

@receiver(pre_save, sender=ContactMessage)
def check_spam_before_save(sender, instance, **kwargs):
    """Check for spam in contact messages before saving"""
    if not instance.pk:  # Only for new messages
        spam_keywords = [
            'buy now', 'click here', 'http://', 'https://', 'www.', '.com',
            'urgent', 'ASAP', 'earn money', 'make money', 'work from home',
            'investment', 'lottery', 'winner', 'prize', 'free', 'discount',
            'viagra', 'cialis', 'pharmacy', 'drug', 'medication'
        ]
        
        message_lower = instance.message.lower()
        if any(keyword in message_lower for keyword in spam_keywords):
            instance.is_spam = True
            logger.warning(f'Potential spam detected from {instance.email}')

@receiver(pre_save, sender=Subscriber)
def validate_email_before_save(sender, instance, **kwargs):
    """Validate email before saving subscriber"""
    # Check if email is already subscribed (active)
    existing = Subscriber.objects.filter(email=instance.email).exclude(pk=instance.pk).first()
    if existing:
        # If existing subscriber is trying to subscribe again
        if not instance.pk:  # New subscription attempt
            instance.pk = existing.pk
            instance.id = existing.id
            instance.subscribed_at = existing.subscribed_at
            instance.is_active = True  # Reactivate
            logger.info(f'Reactivated existing subscriber: {instance.email}')

# Rate limiting check
def check_rate_limit(ip_address, model_class, time_window_minutes=15, max_requests=5):
    """Check if an IP address has exceeded rate limits"""
    time_threshold = timezone.now() - timezone.timedelta(minutes=time_window_minutes)
    recent_requests = model_class.objects.filter(
        ip_address=ip_address,
        created_at__gte=time_threshold
    ).count()
    
    if recent_requests >= max_requests:
        # Log security event for rate limiting
        SecurityLog.objects.create(
            event_type='bruteforce',
            ip_address=ip_address,
            details=f'Rate limit exceeded for {model_class.__name__} ({recent_requests} requests in {time_window_minutes} minutes)'
        )
        return True
    return False