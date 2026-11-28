import json
import logging
import os
import threading
import uuid
from datetime import datetime, time as dt_time
from email.utils import format_datetime
from xml.sax.saxutils import escape as xml_escape

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from ipware import get_client_ip

from .blog_engine import ensure_blog_seeded, get_week_context, get_weekly_blog_feed
from .courses_data import COURSE_CATEGORIES, COURSES, COURSES_BY_SLUG
from .forms import (
    CareerApplicationForm, ContactForm, CourseEnrollmentForm, ProposalRequestForm,
    ServiceInquiryForm, SubscribeForm, SupportTicketForm, SyllabusDownloadForm,
)
from .google_sheets import save_to_google_sheet
from .models import (
    BlogPost, ChatbotMessage, ChatbotSession, ChatbotUnanswered, ContactMessage, PageView,
    Subscriber, SupportTicket, SyllabusDownload,
)
from .syllabus_pdf import (
    generate_course_syllabus_pdf, generate_privacy_policy_pdf, generate_terms_pdf,
)
from .security import (
    check_rate_limit, generate_captcha_text, log_security_event,
    validate_captcha,
)
from .whatsapp_service import trigger_form_whatsapp_async

logger = logging.getLogger(__name__)

SKIP_FIELDS = {'csrfmiddlewaretoken', 'captcha', 'honeypot', 'g-recaptcha-response'}


# ---------------------------------------------------------------- helpers
def get_client_info(request):
    ip, _ = get_client_ip(request)
    return ip or request.META.get('REMOTE_ADDR') or '0.0.0.0', request.META.get('HTTP_USER_AGENT', '')


def log_page_view(request, page_url=None):
    """Record a page view; analytics must never break a page."""
    try:
        ip, user_agent = get_client_info(request)
        full_url = page_url or request.build_absolute_uri()
        PageView.objects.create(
            page_url=full_url[:200],
            ip_address=ip,
            user_agent=user_agent[:500],
            referrer=request.META.get('HTTP_REFERER', '')[:200] or None,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Page view logging failed: %s", e)


def is_ajax(request):
    return (request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or 'application/json' in request.headers.get('Accept', ''))


def respond(request, ok, message, fallback='home', errors=None, status=None, **extra):
    """JSON for AJAX callers, flash message + redirect for plain form posts."""
    if is_ajax(request):
        payload = {'success': ok, 'message': message}
        if errors:
            payload['errors'] = errors
        payload.update(extra)
        return JsonResponse(payload, status=status or (200 if ok else 400))
    (messages.success if ok else messages.error)(request, message)
    target = request.META.get('HTTP_REFERER') or None
    return redirect(target) if target else redirect(fallback)


def form_errors(form):
    return {k: [str(e) for e in v] for k, v in form.errors.items()}


def _send_mails(form_type, data):
    try:
        lines = [f"{k.replace('_', ' ').title()}: {v}" for k, v in data.items()
                 if k not in SKIP_FIELDS]
        send_mail(f'New {form_type} - {settings.SITE_NAME}',
                  f'New {form_type} received:\n\n' + '\n'.join(lines),
                  settings.DEFAULT_FROM_EMAIL, [settings.SITE_EMAIL], fail_silently=True)
        if data.get('email'):
            send_mail(f'Thank you for contacting {settings.SITE_NAME}',
                      f"Dear {data.get('name') or 'there'},\n\nThank you for your "
                      f"{form_type.lower()}. We have received it and will get back to you "
                      f"within 24 hours.\n\nBest regards,\n{settings.SITE_NAME} Team",
                      settings.DEFAULT_FROM_EMAIL, [data['email']], fail_silently=True)
    except Exception as e:  # noqa: BLE001
        logger.error("Email sending failed: %s", e)


def notify(form_type, sheet_name, data):
    """Email + Google Sheets backup + WhatsApp notification, run off the request thread."""
    data = {k: ('' if v is None else str(v)) for k, v in dict(data).items()}
    threading.Thread(target=_send_mails, args=(form_type, data), daemon=True).start()
    save_to_google_sheet(sheet_name, data)
    trigger_form_whatsapp_async(form_type, data)


def rate_limited(request, action, limit=10):
    ip, ua = get_client_info(request)
    if not check_rate_limit(ip, action, limit=limit, period=60):
        return True
    return False


# ------------------------------------------------------------ static pages
SERVICE_DISPLAY_NAMES = {
    'it-consulting': 'IT Consulting & AI Strategy',
    'digital-marketing': 'Digital Marketing, SEO & AEO',
    'cloud-solutions': 'Cloud Solutions & FinOps',
    'software-development': 'Software & Web Development',
    'cybersecurity': 'Cybersecurity & VAPT Defense',
    'data-analytics': 'Data Analytics & BI Consulting',
}


@ensure_csrf_cookie
def home(request):
    log_page_view(request)
    blog_feed = get_weekly_blog_feed()
    return render(request, 'index.html', {
        'latest_blog_posts': blog_feed['trending_posts'],
        'blog_week_info': blog_feed['week_info'],
    })


@ensure_csrf_cookie
def blog_list(request):
    log_page_view(request)
    selected_category = request.GET.get('category', '').strip()
    search_query = request.GET.get('q', '').strip()
    feed = get_weekly_blog_feed(category=selected_category, query=search_query)

    base_url = f"{request.scheme}://{request.get_host()}"
    blog_schema = {
        '@context': 'https://schema.org',
        '@type': 'Blog',
        'name': 'BunShai TECHNOHUB Weekly Insights & SEO Tech Blog',
        'description': 'Weekly updated engineering, AI automation, Cloud FinOps, Cybersecurity, Data Analytics, and SEO/AEO growth guides.',
        'url': f"{base_url}/blog/",
        'publisher': {
            '@type': 'Organization',
            'name': 'BunShai TECHNOHUB',
            'url': f"{base_url}/",
        },
        'blogPost': [
            {
                '@type': 'BlogPosting',
                'headline': p.title,
                'description': p.seo_description,
                'url': f"{base_url}/blog/{p.slug}/",
                'datePublished': p.publish_date.isoformat(),
                'author': {'@type': 'Person', 'name': p.author_name},
            }
            for p in feed['all_posts'][:6]
        ],
    }

    return render(request, 'blog.html', {
        'featured_post': feed['featured_post'],
        'posts': feed['posts'],
        'categories': feed['categories'],
        'selected_category': selected_category,
        'search_query': search_query,
        'week_info': feed['week_info'],
        'total_count': feed['total_count'],
        'blog_schema_json': json.dumps(blog_schema),
    })


@ensure_csrf_cookie
def blog_detail(request, slug):
    log_page_view(request)
    ensure_blog_seeded()
    today = timezone.localdate()
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        is_published=True,
        publish_date__lte=today,
    )
    BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)

    week_info = get_week_context(today)
    all_live = get_weekly_blog_feed(today=today)['all_posts']
    same_cat = [p for p in all_live if p.slug != post.slug and p.category == post.category]
    other_cat = [p for p in all_live if p.slug != post.slug and p.category != post.category]
    related_posts = (same_cat + other_cat)[:3]

    related_course = COURSES_BY_SLUG.get(post.related_course_slug)
    related_service_title = SERVICE_DISPLAY_NAMES.get(post.related_service_slug, '')

    base_url = f"{request.scheme}://{request.get_host()}"
    post_url = f"{base_url}/blog/{post.slug}/"
    cover_url = f"{base_url}{settings.STATIC_URL}{post.cover_image}"

    schemas = [
        {
            '@context': 'https://schema.org',
            '@type': 'BlogPosting',
            'mainEntityOfPage': {'@type': 'WebPage', '@id': post_url},
            'headline': post.seo_title,
            'description': post.seo_description,
            'image': [cover_url],
            'keywords': post.tags,
            'articleSection': post.category,
            'datePublished': post.publish_date.isoformat(),
            'dateModified': post.updated_at.date().isoformat(),
            'author': {'@type': 'Person', 'name': post.author_name},
            'publisher': {
                '@type': 'Organization',
                'name': 'BunShai TECHNOHUB',
                'logo': {
                    '@type': 'ImageObject',
                    'url': f"{base_url}{settings.STATIC_URL}images/Logo1.png",
                },
            },
        },
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f"{base_url}/"},
                {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': f"{base_url}/blog/"},
                {'@type': 'ListItem', 'position': 3, 'name': post.title, 'item': post_url},
            ],
        },
    ]
    if post.faqs:
        schemas.append({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'mainEntity': [
                {
                    '@type': 'Question',
                    'name': item.get('q', ''),
                    'acceptedAnswer': {'@type': 'Answer', 'text': item.get('a', '')},
                }
                for item in post.faqs
            ],
        })

    return render(request, 'blog_detail.html', {
        'post': post,
        'week_info': week_info,
        'related_posts': related_posts,
        'related_course': related_course,
        'related_service_title': related_service_title,
        'post_schemas_json': json.dumps(schemas),
    })


@require_GET
def blog_rss_feed(request):
    feed = get_weekly_blog_feed()
    base_url = f"{request.scheme}://{request.get_host()}"
    items_xml = []
    tz = timezone.get_current_timezone()
    for p in feed['all_posts']:
        pub_dt = timezone.make_aware(datetime.combine(p.publish_date, dt_time(9, 0)), tz)
        link = f"{base_url}/blog/{p.slug}/"
        items_xml.append(
            f"<item>"
            f"<title>{xml_escape(p.title)}</title>"
            f"<link>{xml_escape(link)}</link>"
            f"<guid isPermaLink=\"true\">{xml_escape(link)}</guid>"
            f"<category>{xml_escape(p.category)}</category>"
            f"<description>{xml_escape(p.seo_description)}</description>"
            f"<pubDate>{xml_escape(format_datetime(pub_dt))}</pubDate>"
            f"</item>"
        )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '<channel>\n'
        f'<title>BunShai TECHNOHUB Weekly Insights</title>\n'
        f'<link>{xml_escape(base_url)}/blog/</link>\n'
        f'<atom:link href="{xml_escape(base_url)}/blog/feed.xml" rel="self" type="application/rss+xml"/>\n'
        '<description>Weekly SEO, AI, Cloud, Security, and Software Engineering articles from BunShai TECHNOHUB.</description>\n'
        '<language>en-us</language>\n'
        + '\n'.join(items_xml)
        + '\n</channel>\n</rss>'
    )
    return HttpResponse(rss, content_type='application/rss+xml; charset=utf-8')


@ensure_csrf_cookie
def about(request):
    log_page_view(request)
    return render(request, 'about.html')


@ensure_csrf_cookie
def company_profile(request):
    log_page_view(request)
    return render(request, 'company-profile.html')


@ensure_csrf_cookie
def md_profile(request):
    log_page_view(request)
    return render(request, 'md-profile.html')


@ensure_csrf_cookie
def team(request):
    log_page_view(request)
    return render(request, 'team.html')


@ensure_csrf_cookie
def privacy(request):
    log_page_view(request)
    return render(request, 'privacy.html')


@require_GET
def privacy_pdf(request):
    pdf_bytes = generate_privacy_policy_pdf()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="BunShai-Privacy-Policy.pdf"'
    response['Content-Length'] = len(pdf_bytes)
    return response


@ensure_csrf_cookie
def terms(request):
    log_page_view(request)
    return render(request, 'terms.html')


@require_GET
def terms_pdf(request):
    pdf_bytes = generate_terms_pdf()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="BunShai-Terms-and-Conditions.pdf"'
    response['Content-Length'] = len(pdf_bytes)
    return response


@ensure_csrf_cookie
def support(request):
    log_page_view(request)
    return render(request, 'support.html')


@ensure_csrf_cookie
def sitemap(request):
    log_page_view(request)
    return render(request, 'sitemap.html')


@ensure_csrf_cookie
def services(request):
    log_page_view(request)
    return render(request, 'services.html')


@ensure_csrf_cookie
def service_detail(request, service_slug):
    log_page_view(request)
    templates = {
        'it-consulting': 'services/it-consulting.html',
        'digital-marketing': 'services/digital-marketing.html',
        'cloud-solutions': 'services/cloud-solutions.html',
        'software-development': 'services/software-development.html',
        'cybersecurity': 'services/cybersecurity.html',
        'data-analytics': 'services/data-analytics.html',
    }
    if service_slug not in templates:
        return redirect('services')
    return render(request, templates[service_slug])


# ---------------------------------------------------------------- captcha
def _new_captcha(request, captcha_type='contact'):
    text = generate_captcha_text()
    request.session[f'{captcha_type}_captcha'] = f"{text}|{datetime.now().isoformat()}"
    return text


@require_GET
def get_captcha(request):
    text = _new_captcha(request, request.GET.get('type', 'contact'))
    return JsonResponse({'success': True, 'captcha_text': text})


@require_POST
def verify_captcha(request):
    data = _json_body(request)
    ok, message = validate_captcha(request, data.get('captcha', ''),
                                   f"{data.get('type', 'contact')}_captcha")
    return JsonResponse({'valid': ok, 'message': message})


# ------------------------------------------------------------------ forms
@ensure_csrf_cookie
def contact(request):
    if request.method != 'POST':
        log_page_view(request)
        return render(request, 'contact.html', {
            'form': ContactForm(), 'captcha_text': _new_captcha(request)})

    ip, user_agent = get_client_info(request)
    if rate_limited(request, 'contact_form'):
        return respond(request, False, 'Too many submission attempts. Please try again later.',
                       'contact', status=429)

    ok, captcha_msg = validate_captcha(request, request.POST.get('captcha', '').strip(),
                                       'contact_captcha')
    form = ContactForm(request.POST)
    if not ok:
        return respond(request, False, captcha_msg, 'contact',
                       errors={**form_errors(form), 'captcha': [captcha_msg]},
                       new_captcha=_new_captcha(request))
    if not form.is_valid():
        return respond(request, False, 'Please correct the highlighted fields.', 'contact',
                       errors=form_errors(form), new_captcha=_new_captcha(request))

    obj = form.save(commit=False)
    obj.ip_address, obj.user_agent = ip, user_agent
    obj.verification_token = uuid.uuid4().hex
    text = f"{obj.subject} {obj.message}".lower()
    if any(k in text for k in ('buy now', 'click here', 'earn money', 'make money',
                               'lottery', 'viagra', 'casino')):
        obj.is_spam = True
        log_security_event('spam', ip, user_agent, f'Potential spam from {obj.email}')
    obj.save()
    notify('Contact Message', 'contact_messages', form.cleaned_data)
    return respond(request, True, 'Thank you for your message! We will get back to you soon.',
                   'contact', new_captcha=_new_captcha(request))


@require_POST
def subscribe(request):
    if rate_limited(request, 'subscribe'):
        return respond(request, False, 'Too many attempts. Please try again later.', status=429)
    form = SubscribeForm(request.POST)
    if not form.is_valid():
        return respond(request, False, 'Please enter a valid email address.',
                       errors=form_errors(form))
    email = form.cleaned_data['email']
    ip, _ = get_client_info(request)
    sub, created = Subscriber.objects.get_or_create(
        email=email, defaults={'ip_address': ip, 'verification_token': uuid.uuid4().hex})
    if created:
        message = 'Thank you for subscribing!'
        notify('Subscription', 'subscribers', {'email': email})
    else:
        if not sub.is_active:
            sub.is_active = True
            sub.save(update_fields=['is_active'])
            message = 'You have been resubscribed successfully!'
        else:
            message = 'You are already subscribed. Thank you!'
    return respond(request, True, message)


@ensure_csrf_cookie
def subscribe_page(request):
    log_page_view(request)
    return render(request, 'subscribe.html')


def _handle_model_form(request, form_cls, label, sheet, fallback, files=False):
    if rate_limited(request, sheet):
        return respond(request, False, 'Too many submission attempts. Please try again later.',
                       fallback, status=429)
    form = form_cls(request.POST, request.FILES) if files else form_cls(request.POST)
    if not form.is_valid():
        return respond(request, False, 'Please fill all required fields correctly.', fallback,
                       errors=form_errors(form))
    obj = form.save(commit=False)
    obj.ip_address, _ = get_client_info(request)
    obj.save()
    data = dict(form.cleaned_data)
    if 'resume' in data:
        data['resume'] = obj.resume.name
    notify(label, sheet, data)
    return obj


@ensure_csrf_cookie
def career(request):
    if request.method == 'POST':
        result = _handle_model_form(request, CareerApplicationForm, 'Career Application',
                                    'career_applications', 'career', files=True)
        if not hasattr(result, 'pk'):
            return result
        return respond(request, True, 'Application submitted successfully! We will review it soon.',
                       'career')
    log_page_view(request)
    return render(request, 'career.html', {'form': CareerApplicationForm()})


@require_POST
def proposal_request(request):
    result = _handle_model_form(request, ProposalRequestForm, 'Proposal Request',
                                'proposal_requests', 'home')
    if not hasattr(result, 'pk'):
        return result
    return respond(request, True, 'Proposal request submitted successfully! We will contact you soon.')


@require_POST
def service_inquiry(request):
    result = _handle_model_form(request, ServiceInquiryForm, 'Service Inquiry',
                                'service_inquiries', 'services')
    if not hasattr(result, 'pk'):
        return result
    return respond(request, True, 'Thank you for your inquiry! We will contact you soon.', 'services')


@ensure_csrf_cookie
def courses(request):
    log_page_view(request)
    active_category = request.GET.get('category', 'all')
    valid_slugs = {c['slug'] for c in COURSE_CATEGORIES}
    if active_category != 'all' and active_category not in valid_slugs:
        active_category = 'all'
    return render(request, 'courses.html', {
        'categories': COURSE_CATEGORIES,
        'courses': COURSES,
        'active_category': active_category,
    })


@ensure_csrf_cookie
def course_detail(request, course_slug):
    course = COURSES_BY_SLUG.get(course_slug)
    if not course:
        return redirect('courses')
    log_page_view(request)
    related_courses = [
        c for c in COURSES if c['slug'] != course_slug and c['category'] == course['category']
    ]
    if len(related_courses) < 3:
        extra = [c for c in COURSES if c['slug'] != course_slug and c not in related_courses]
        related_courses.extend(extra[:3 - len(related_courses)])
    return render(request, 'course_detail.html', {
        'course': course,
        'related_courses': related_courses[:3],
    })


@require_POST
def course_enroll(request):
    if rate_limited(request, 'course_enroll'):
        return respond(request, False, 'Too many submission attempts. Please try again later.',
                       'courses', status=429)
    form = CourseEnrollmentForm(request.POST)
    if not form.is_valid():
        return respond(request, False, 'Please fill all required fields correctly.', 'courses',
                       errors=form_errors(form))
    obj = form.save(commit=False)
    matched = COURSES_BY_SLUG.get(obj.course_slug)
    if matched and not obj.course_title:
        obj.course_title = matched['title']
    obj.ip_address, _ = get_client_info(request)
    obj.save()
    notify('Course Enrollment', 'course_enrollments', {**form.cleaned_data, 'course_title': obj.course_title})
    return respond(
        request,
        True,
        f"Enrollment request received for {obj.course_title}! Our academic counselor will reach out within 24 hours.",
        'courses',
    )


@require_POST
def syllabus_request(request):
    if rate_limited(request, 'syllabus_request'):
        return respond(request, False, 'Too many submission attempts. Please try again later.',
                       'courses', status=429)
    form = SyllabusDownloadForm(request.POST)
    if not form.is_valid():
        return respond(request, False, 'Please fill all required fields correctly.', 'courses',
                       errors=form_errors(form))
    obj = form.save(commit=False)
    matched = COURSES_BY_SLUG.get(obj.course_slug)
    if not matched:
        return respond(request, False, 'Requested course could not be found.', 'courses', status=404)
    if not obj.course_title:
        obj.course_title = matched['title']
    ip, _ = get_client_info(request)
    obj.ip_address = ip
    obj.save()

    payload = {
        **{k: ('' if v is None else str(v)) for k, v in form.cleaned_data.items()},
        'course_title': obj.course_title,
        'ip_address': ip,
    }

    def _mark_synced():
        SyllabusDownload.objects.filter(pk=obj.pk).update(synced_to_google=True)

    threading.Thread(target=_send_mails, args=('Syllabus Download', payload), daemon=True).start()
    save_to_google_sheet('syllabus_downloads', payload, on_success=_mark_synced)
    trigger_form_whatsapp_async('Syllabus Download', payload)

    unlocked = list(request.session.get('unlocked_syllabi', []))
    if obj.course_slug not in unlocked:
        unlocked.append(obj.course_slug)
        request.session['unlocked_syllabi'] = unlocked

    token = TimestampSigner().sign(obj.course_slug)
    download_url = f"/courses/{obj.course_slug}/syllabus-download/?token={token}"
    return respond(
        request,
        True,
        f"Thank you! Your {obj.course_title} syllabus PDF is downloading now.",
        'courses',
        download_url=download_url,
    )


@require_GET
def syllabus_download(request, course_slug):
    course = COURSES_BY_SLUG.get(course_slug)
    if not course:
        return redirect('courses')

    token = request.GET.get('token', '')
    authorized = False
    if token:
        try:
            authorized = TimestampSigner().unsign(token, max_age=3600) == course_slug
        except (BadSignature, SignatureExpired):
            authorized = False
    if not authorized and course_slug in request.session.get('unlocked_syllabi', []):
        authorized = True

    if not authorized:
        messages.info(request, 'Please fill in your details to download the syllabus PDF.')
        return redirect('course_detail', course_slug=course_slug)

    pdf_bytes = generate_course_syllabus_pdf(course)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BunShai-{course_slug}-Syllabus.pdf"'
    response['Content-Length'] = len(pdf_bytes)
    return response


@require_POST
def support_ticket(request):
    if rate_limited(request, 'support_ticket'):
        return respond(request, False, 'Too many submission attempts. Please try again later.',
                       'support', status=429)
    form = SupportTicketForm(request.POST)
    files = request.FILES.getlist('attachments')
    errors = form_errors(form) if not form.is_valid() else {}
    allowed = {'jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'txt'}
    if sum(f.size for f in files) > 10 * 1024 * 1024:
        errors['attachments'] = ['Attachments must total less than 10MB']
    for f in files:
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        if ext not in allowed:
            errors['attachments'] = ['Unsupported attachment type']
    if errors:
        return respond(request, False, 'Please fill all required fields correctly.', 'support',
                       errors=errors)
    saved = []
    for f in files[:5]:
        name = default_storage.save(f"tickets/{uuid.uuid4().hex[:8]}_{os.path.basename(f.name)}", f)
        saved.append(name)
    ip, _ = get_client_info(request)
    ticket = SupportTicket.objects.create(
        ip_address=ip, attachments='\n'.join(saved), **form.cleaned_data)
    notify('Support Ticket', 'support_tickets',
           {**form.cleaned_data, 'ticket_number': ticket.ticket_number})
    return respond(request, True,
                   f'Ticket {ticket.ticket_number} submitted! We will get back to you within 2 hours.',
                   'support', ticket_number=ticket.ticket_number)


# ---------------------------------------------------------------- chatbot
def _json_body(request):
    try:
        parsed = json.loads(request.body or '{}')
        return parsed if isinstance(parsed, dict) else {}
    except (ValueError, TypeError):
        return {}


@csrf_exempt
@require_POST
def chatbot_start_session(request):
    data = _json_body(request)
    ip, user_agent = get_client_info(request)
    if rate_limited(request, 'chatbot_session', limit=20):
        return JsonResponse({'success': False, 'error': 'Too many requests'}, status=429)
    session = ChatbotSession.objects.create(
        session_id=str(uuid.uuid4()),
        name=(str(data.get('name') or '')[:100] or None), email=(str(data.get('email') or '')[:254] or None),
        phone=(str(data.get('phone') or '')[:20] or None))
    if session.email and ChatbotSession.objects.filter(email=session.email).exclude(pk=session.pk).exists():
        session.is_returning = True
        session.save(update_fields=['is_returning'])
    _sync_chatbot_session(session, str(data.get('page') or '')[:200])
    return JsonResponse({'success': True, 'session_id': session.session_id,
                         'is_returning': session.is_returning})


def _sync_chatbot_session(session, page=''):
    save_to_google_sheet('chatbot_sessions', {
        'session_id': session.session_id, 'name': session.name or '', 'email': session.email or '',
        'phone': session.phone or '', 'is_returning': 'Yes' if session.is_returning else 'No', 'page': page})


@csrf_exempt
@require_POST
def chatbot_check_user(request):
    email = _json_body(request).get('email')
    prev = ChatbotSession.objects.filter(email=email).exclude(name=None).first() if email else None
    return JsonResponse({'success': True, 'is_returning': bool(prev),
                         'name': prev.name if prev else None})


@csrf_exempt
@require_POST
def chatbot_send_message(request):
    from .chatbot_ai import extract_contact, get_chatbot_response

    data = _json_body(request)
    session_id, message = data.get('session_id'), str(data.get('message') or '').strip()
    if not message:
        return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)
    if rate_limited(request, 'chatbot_message', limit=40):
        return JsonResponse({'success': False, 'error': 'Too many messages. Please slow down.'}, status=429)
    message = message[:1000]

    session = ChatbotSession.objects.filter(session_id=session_id).first() if session_id else None
    if not session and session_id:
        return JsonResponse({'success': False, 'error': 'Invalid session'}, status=404)
    if not session:
        session = ChatbotSession.objects.create(session_id=str(uuid.uuid4()))

    # Capture name / email / phone shared by the visitor during the conversation
    user_info = data.get('user_info') if isinstance(data.get('user_info'), dict) else {}
    changed = []
    email, phone = extract_contact(message)
    for field, value in (('name', user_info.get('name')), ('email', email or user_info.get('email')),
                         ('phone', phone or user_info.get('phone'))):
        value = str(value or '').strip()
        if value and not getattr(session, field):
            setattr(session, field, value[:254 if field == 'email' else 100 if field == 'name' else 20])
            changed.append(field)
    if changed:
        if 'email' in changed and ChatbotSession.objects.filter(email=session.email).exclude(pk=session.pk).exists():
            session.is_returning = True
            changed.append('is_returning')
        session.save(update_fields=changed + ['last_activity'])
        _sync_chatbot_session(session, 'updated contact details')

    ChatbotMessage.objects.create(session=session, message=message, is_user=True)
    try:
        result = get_chatbot_response(message, session)
    except Exception as e:  # noqa: BLE001
        logger.error("Chatbot error: %s", e)
        from .chatbot_ai import fallback_response
        result = fallback_response(message, session)
    reply = result['reply']
    ChatbotMessage.objects.create(session=session, message=reply, is_user=False)

    save_to_google_sheet('chatbot_messages', {
        'session_id': session.session_id, 'name': session.name or '', 'email': session.email or '',
        'question': message, 'reply': reply[:500], 'intent': result['intent'],
        'answered': 'No' if result['fallback'] else 'Yes'})

    if result['fallback']:
        item = ChatbotUnanswered.objects.create(
            session=session, question=message, name=session.name or '', email=session.email or '',
            phone=session.phone or '')
        save_to_google_sheet('chatbot_unanswered', {
            'session_id': session.session_id, 'name': item.name, 'email': item.email, 'phone': item.phone,
            'question': message, 'status': 'Redirected to contact form'},
            on_success=lambda pk=item.pk: ChatbotUnanswered.objects.filter(pk=pk).update(synced_to_google=True))

    return JsonResponse({
        'success': True, 'response': reply, 'session_id': session.session_id,
        'links': result['links'], 'suggestions': result['suggestions'],
        'fallback': result['fallback'], 'contact_url': result['contact_url'],
        'intent': result['intent'],
    })


# --------------------------------------------------------- error handlers
def custom_404(request, exception=None):
    return render(request, '404.html', {'request_path': request.path}, status=404)


def custom_500(request):
    try:
        return render(request, '500.html', status=500)
    except Exception:  # noqa: BLE001
        return HttpResponse(
            '<!DOCTYPE html><html><head><title>500 Server Error</title></head>'
            '<body style="font-family:sans-serif;text-align:center;padding:60px;">'
            '<h1>500 - Server Error</h1>'
            '<p>Something went wrong on our side. Please <a href="/">return home</a>.</p>'
            '</body></html>',
            status=500,
        )


def custom_403(request, exception=None):
    return render(request, '403.html', status=403)


def custom_400(request, exception=None):
    return render(request, '400.html', status=400)


@require_GET
def healthz(request):
    """Lightweight health check endpoint for Render (no DB writes)."""
    return JsonResponse({'status': 'ok'})
