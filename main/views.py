from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from ipware import get_client_ip
import uuid
import json
import logging
from datetime import datetime
from .security import generate_captcha_text, validate_captcha  # Make sure these exist in security.py
from .forms import *
from .models import *
from .google_sheets import save_to_google_sheet
from .security import log_security_event, check_rate_limit, validate_form_data
# main/views.py
from django.http import JsonResponse
import json
# main/views.py
from django.conf import settings

def home(request):
    # If you're accessing settings directly
    support_email = getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
    contact_email = getattr(settings, 'CONTACT_EMAIL', 'contact@example.com')
    
    # Or pass them in context
    context = {
        'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
        'contact_email': getattr(settings, 'CONTACT_EMAIL', 'contact@example.com'),
    }
    return render(request, 'home.html', context)

@csrf_exempt
def get_captcha(request):
    """Generate and return new CAPTCHA via AJAX"""
    captcha_type = request.GET.get('type', 'contact')
    session_key = f'{captcha_type}_captcha'
    
    captcha_text = generate_captcha_text()
    request.session[session_key] = f"{captcha_text}|{datetime.now().isoformat()}"
    
    return JsonResponse({
        'success': True,
        'captcha_text': captcha_text
    })

@csrf_exempt
def verify_captcha(request):
    """Verify CAPTCHA via AJAX (for real-time validation)"""
    if request.method == 'POST':
        data = json.loads(request.body)
        captcha_input = data.get('captcha', '')
        captcha_type = data.get('type', 'contact')
        
        is_valid, message = validate_captcha(request, captcha_input, f'{captcha_type}_captcha')
        
        return JsonResponse({
            'valid': is_valid,
            'message': message
        })
logger = logging.getLogger(__name__)

def get_client_info(request):
    ip, is_routable = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return ip, user_agent

def log_page_view(request, page_url):
    ip, user_agent = get_client_info(request)
    referrer = request.META.get('HTTP_REFERER', '')
    
    PageView.objects.create(
        page_url=page_url,
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer
    )

def send_form_email(form_type, form_data):
    """Send email notifications for form submissions"""
    try:
        subject = f'New {form_type} Submission - {settings.SITE_NAME}'
        
        # Create email content
        content = f"""
        New {form_type} Submission:
        
        Details:
        """
        
        for key, value in form_data.items():
            if key not in ['csrfmiddletoken', 'captcha', 'g-recaptcha-response']:
                content += f"{key.replace('_', ' ').title()}: {value}\n"
        
        # Send to admin
        send_mail(
            subject,
            content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.SITE_EMAIL],
            fail_silently=False,
        )
        
        # Send confirmation to user if email provided
        if 'email' in form_data:
            user_subject = f'Thank you for contacting {settings.SITE_NAME}'
            user_content = f"""
            Dear {form_data.get('name', 'User')},
            
            Thank you for your submission. We have received your {form_type} and will contact you within 24 hours.
            
            Best regards,
            {settings.SITE_NAME} Team
            """
            
            send_mail(
                user_subject,
                user_content,
                settings.DEFAULT_FROM_EMAIL,
                [form_data['email']],
                fail_silently=True,
            )
            
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")

def home(request):
    log_page_view(request, request.path)
    return render(request, 'index.html')

def about(request):
    log_page_view(request, request.path)
    return render(request, 'about.html')

def company_profile(request):
    log_page_view(request, request.path)
    return render(request, 'company-profile.html')

def md_profile(request):
    log_page_view(request, request.path)
    return render(request, 'md-profile.html')

def services(request):
    log_page_view(request, request.path)
    
    if request.method == 'POST':
        form = ServiceInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            ip, user_agent = get_client_info(request)
            inquiry.ip_address = ip
            inquiry.save()
            
            # Send email and save to Google Sheets
            form_data = form.cleaned_data
            send_form_email('Service Inquiry', form_data)
            save_to_google_sheet('service_inquiries', form_data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your inquiry! We will contact you soon.'
                })
            else:
                messages.success(request, 'Thank you for your inquiry! We will contact you soon.')
                return redirect('services')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            else:
                messages.error(request, 'Please fill all required fields correctly.')
                return redirect('services')
    else:
        form = ServiceInquiryForm()
    
    return render(request, 'services.html', {'inquiry_form': form})

def service_detail(request, service_slug):
    log_page_view(request, request.path)
    templates = {
        'it-consulting': 'services/it-consulting.html',
        'digital-marketing': 'services/digital-marketing.html',
        'cloud-solutions': 'services/cloud-solutions.html',
        'software-development': 'services/software-development.html',
        'cybersecurity': 'services/cybersecurity.html',
        'data-analytics': 'services/data-analytics.html',
    }
    
    template = templates.get(service_slug, 'services.html')
    return render(request, template)

def contact(request):
    log_page_view(request, request.path)
    
    if request.method == 'POST':
        # Rate limiting check
        ip, _ = get_client_info(request)
        if not check_rate_limit(ip, 'contact_form'):
            messages.error(request, 'Too many submission attempts. Please try again later.')
            return redirect('contact')
        
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            ip, user_agent = get_client_info(request)
            contact_message.ip_address = ip
            contact_message.user_agent = user_agent
            contact_message.verification_token = str(uuid.uuid4())
            
            # Check for spam
            spam_keywords = ['buy now', 'click here', 'http://', 'https://', 'www.', '.com']
            message_lower = contact_message.message.lower()
            if any(keyword in message_lower for keyword in spam_keywords):
                contact_message.is_spam = True
                log_security_event('spam', ip, user_agent, f'Potential spam message from {contact_message.email}')
            
            contact_message.save()
            
            # Send email and save to Google Sheets
            form_data = form.cleaned_data
            send_form_email('Contact Message', form_data)
            save_to_google_sheet('contact_messages', form_data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your message! We will get back to you soon.'
                })
            else:
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('contact')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

@require_POST
@csrf_exempt
def subscribe(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        subscriber = form.save(commit=False)
        ip, user_agent = get_client_info(request)
        subscriber.ip_address = ip
        subscriber.verification_token = str(uuid.uuid4())
        
        existing = Subscriber.objects.filter(email=subscriber.email).first()
        if existing:
            existing.is_active = True
            existing.save()
            message = 'You have been resubscribed successfully!'
        else:
            subscriber.save()
            message = 'Thank you for subscribing!'
        
        # Send email and save to Google Sheets
        form_data = form.cleaned_data
        send_form_email('Subscription', form_data)
        save_to_google_sheet('subscribers', form_data)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message
            })
        else:
            messages.success(request, message)
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        else:
            messages.error(request, 'Please enter a valid email address.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
def proposal_request(request):
    form = ProposalRequestForm(request.POST)
    if form.is_valid():
        proposal = form.save(commit=False)
        ip, user_agent = get_client_info(request)
        proposal.ip_address = ip
        proposal.save()
        
        # Send email and save to Google Sheets
        form_data = form.cleaned_data
        send_form_email('Proposal Request', form_data)
        save_to_google_sheet('proposal_requests', form_data)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Proposal request submitted successfully! We will contact you soon.'
            })
        else:
            messages.success(request, 'Proposal request submitted successfully! We will contact you soon.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        else:
            messages.error(request, 'Please fill all required fields correctly.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

def career(request):
    log_page_view(request, request.path)
    
    if request.method == 'POST':
        form = CareerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            ip, user_agent = get_client_info(request)
            application.ip_address = ip
            application.save()
            
            # Send email and save to Google Sheets
            form_data = form.cleaned_data
            form_data['resume'] = str(application.resume)
            send_form_email('Career Application', form_data)
            save_to_google_sheet('career_applications', form_data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Application submitted successfully! We will review it soon.'
                })
            else:
                messages.success(request, 'Application submitted successfully! We will review it soon.')
                return redirect('career')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            else:
                messages.error(request, 'Please fill all required fields correctly.')
                return redirect('career')
    else:
        form = CareerApplicationForm()
    
    return render(request, 'career.html', {'form': form})

def privacy(request):
    log_page_view(request, request.path)
    return render(request, 'privacy.html')

def terms(request):
    log_page_view(request, request.path)
    return render(request, 'terms.html')

def support(request):
    log_page_view(request, request.path)
    return render(request, 'support.html')

def sitemap(request):
    return render(request, 'sitemap.xml')

# Chatbot API Views
@csrf_exempt
@require_POST
def chatbot_start_session(request):
    """Start a new chatbot session"""
    data = json.loads(request.body)
    session_id = str(uuid.uuid4())
    
    session = ChatbotSession.objects.create(
        session_id=session_id,
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone')
    )
    
    # Check if returning user
    if data.get('email'):
        existing = ChatbotSession.objects.filter(email=data['email']).exclude(id=session.id).first()
        if existing:
            session.is_returning = True
            session.save()
    
    return JsonResponse({
        'success': True,
        'session_id': session_id,
        'is_returning': session.is_returning
    })

@csrf_exempt
@require_POST
def chatbot_send_message(request):
    """Handle chatbot messages"""
    data = json.loads(request.body)
    session_id = data.get('session_id')
    message = data.get('message')
    
    if not session_id or not message:
        return JsonResponse({'success': False, 'error': 'Missing parameters'})
    
    session = ChatbotSession.objects.filter(session_id=session_id).first()
    if not session:
        return JsonResponse({'success': False, 'error': 'Invalid session'})
    
    # Save user message
    ChatbotMessage.objects.create(
        session=session,
        message=message,
        is_user=True
    )
    
    # Get bot response (simplified - in production, use AI)
    from .chatbot_ai import get_chatbot_response
    bot_response = get_chatbot_response(message, session)
    
    # Save bot response
    ChatbotMessage.objects.create(
        session=session,
        message=bot_response,
        is_user=False
    )
    
    return JsonResponse({
        'success': True,
        'response': bot_response
    })

# Error handlers
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_400(request, exception):
    return render(request, '400.html', status=400)