"""WhatsApp Cloud API automation service for BunShai TECHNOHUB."""

from datetime import timedelta
import hashlib
import hmac
import logging
import re
import threading
import uuid
from typing import Any

from django.conf import settings
from django.utils import timezone
import requests

from .chatbot_ai import EMAIL_RE, get_chatbot_response
from .courses_data import COURSE_CATEGORIES, COURSES
from .google_sheets import save_to_google_sheet
from .models import (
    ChatbotUnanswered,
    CourseEnrollment,
    ContactMessage,
    ProposalRequest,
    ServiceInquiry,
    SupportTicket,
    SyllabusDownload,
    WhatsAppAutoReplyRule,
    WhatsAppConversation,
    WhatsAppMessage,
    WhatsAppScheduledMessage,
)

logger = logging.getLogger(__name__)

MENU_TRIGGERS = {'hi', 'hello', 'hey', 'start', 'menu', '0', 'resume bot'}
CANCEL_TRIGGERS = {'cancel', 'stop', 'exit'}
COURSE_FLOW_TRIGGERS = {'1', 'explore courses', 'enroll', 'btn_courses'}
SERVICE_FLOW_TRIGGERS = {'2', 'request proposal', 'quote', 'service inquiry', 'btn_proposal'}
SUPPORT_FLOW_TRIGGERS = {'3', 'support', 'raise ticket', 'raise support ticket'}
HANDOFF_FLOW_TRIGGERS = {'4', 'talk to team', 'human', 'agent', 'talk to human', 'btn_human'}

SERVICE_CHOICES_MAP = {
    'web': 'web',
    'website': 'web',
    'software': 'web',
    'mobile': 'mobile',
    'app': 'mobile',
    'ai': 'ai',
    'ml': 'ai',
    'genai': 'ai',
    'cloud': 'cloud',
    'aws': 'cloud',
    'azure': 'cloud',
    'cyber': 'cyber',
    'security': 'cyber',
    'consulting': 'consulting',
    'it consulting': 'consulting',
    'marketing': 'marketing',
    'seo': 'marketing',
    'data': 'data',
    'analytics': 'data',
}


class WhatsAppAPIError(RuntimeError):
    """Raised when Meta WhatsApp Cloud API fails."""


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return f'{{{key}}}'


def render_template_text(template: str, context: dict[str, Any]) -> str:
    """Safely format {placeholders} without crashing on missing keys."""
    if not template:
        return ''
    clean_ctx = _SafeDict({str(k): ('' if v is None else str(v)) for k, v in context.items()})
    return template.format_map(clean_ctx)


def normalize_whatsapp_phone(raw: str) -> str:
    """Normalize phone to E.164 digits, prepending default country code for 10-digit numbers."""
    digits = re.sub(r'\D', '', str(raw or ''))
    default_cc = re.sub(r'\D', '', str(getattr(settings, 'WHATSAPP_DEFAULT_COUNTRY_CODE', '91') or ''))
    if len(digits) == 10 and default_cc:
        digits = f'{default_cc}{digits}'
    if not (7 <= len(digits) <= 15):
        raise ValueError(f"Invalid WhatsApp phone number '{raw}': must contain 7-15 digits.")
    return digits


def is_live_whatsapp_configured() -> bool:
    """Return True only when dry-run is disabled and Meta credentials are present."""
    return (
        not getattr(settings, 'WHATSAPP_DRY_RUN', True)
        and bool(getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '').strip())
        and bool(getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '').strip())
    )


def verify_webhook_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verify Meta X-Hub-Signature-256 HMAC header when WHATSAPP_APP_SECRET is set."""
    secret = getattr(settings, 'WHATSAPP_APP_SECRET', '').strip()
    if not secret:
        return True
    if not signature_header or not signature_header.startswith('sha256='):
        return False
    expected = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    provided = signature_header.split('=', 1)[1].strip()
    return hmac.compare_digest(expected, provided)


def _graph_messages_url() -> str:
    version = getattr(settings, 'WHATSAPP_API_VERSION', 'v21.0')
    phone_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
    return f'https://graph.facebook.com/{version}/{phone_id}/messages'


def _sync_message_to_sheets(msg: WhatsAppMessage) -> None:
    if not getattr(settings, 'GOOGLE_SHEET_ID', ''):
        return
    save_to_google_sheet(
        'whatsapp_messages',
        {
            'direction': msg.direction,
            'phone': msg.phone,
            'contact_name': msg.contact_name,
            'message_type': msg.message_type,
            'body': msg.body,
            'status': msg.status,
            'source': msg.source,
        },
        on_success=lambda pk=msg.pk: WhatsAppMessage.objects.filter(pk=pk).update(synced_to_google=True),
    )


def _dispatch_whatsapp(
    *,
    phone: str,
    body: str,
    message_type: str,
    payload: dict[str, Any],
    source: str = '',
    contact_name: str = '',
) -> WhatsAppMessage:
    if not is_live_whatsapp_configured():
        msg = WhatsAppMessage.objects.create(
            wa_message_id=f'dryrun_{uuid.uuid4().hex[:12]}',
            direction='outbound',
            phone=phone,
            contact_name=contact_name[:120],
            message_type=message_type,
            body=body,
            status='dry_run',
            source=source[:80],
            raw_payload=payload,
        )
        _sync_message_to_sheets(msg)
        return msg

    headers = {
        'Authorization': f"Bearer {getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')}",
        'Content-Type': 'application/json',
    }
    try:
        resp = requests.post(_graph_messages_url(), headers=headers, json=payload, timeout=15)
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400:
            detail = (data.get('error') or {}).get('message') or resp.text
            WhatsAppMessage.objects.create(
                wa_message_id=f'failed_{uuid.uuid4().hex[:12]}',
                direction='outbound',
                phone=phone,
                contact_name=contact_name[:120],
                message_type=message_type,
                body=body,
                status='failed',
                source=source[:80],
                raw_payload={'request': payload, 'response': data},
            )
            raise WhatsAppAPIError(f'Meta API error ({resp.status_code}): {detail}')

        messages_meta = data.get('messages') or []
        wa_id = (
            messages_meta[0].get('id')
            if messages_meta and isinstance(messages_meta[0], dict)
            else f'sent_{uuid.uuid4().hex[:12]}'
        )
        msg = WhatsAppMessage.objects.create(
            wa_message_id=wa_id,
            direction='outbound',
            phone=phone,
            contact_name=contact_name[:120],
            message_type=message_type,
            body=body,
            status='sent',
            source=source[:80],
            raw_payload=data,
        )
        _sync_message_to_sheets(msg)
        return msg
    except WhatsAppAPIError:
        raise
    except Exception as exc:  # noqa: BLE001
        WhatsAppMessage.objects.create(
            wa_message_id=f'failed_{uuid.uuid4().hex[:12]}',
            direction='outbound',
            phone=phone,
            contact_name=contact_name[:120],
            message_type=message_type,
            body=body,
            status='failed',
            source=source[:80],
            raw_payload={'request': payload, 'error': str(exc)},
        )
        raise WhatsAppAPIError(f'WhatsApp API request failed: {exc}') from exc


def send_whatsapp_text(
    phone: str,
    body: str,
    *,
    source: str = '',
    contact_name: str = '',
    preview_url: bool = False,
) -> WhatsAppMessage:
    norm_phone = normalize_whatsapp_phone(phone)
    payload = {
        'messaging_product': 'whatsapp',
        'to': norm_phone,
        'type': 'text',
        'text': {'preview_url': preview_url, 'body': body},
    }
    return _dispatch_whatsapp(
        phone=norm_phone,
        body=body,
        message_type='text',
        payload=payload,
        source=source,
        contact_name=contact_name,
    )


def send_whatsapp_template(
    phone: str,
    template_name: str,
    language_code: str = 'en_US',
    body_params: list[str] | None = None,
    *,
    source: str = '',
    contact_name: str = '',
) -> WhatsAppMessage:
    norm_phone = normalize_whatsapp_phone(phone)
    tpl_obj: dict[str, Any] = {
        'name': template_name,
        'language': {'code': language_code},
    }
    if body_params:
        tpl_obj['components'] = [
            {
                'type': 'body',
                'parameters': [{'type': 'text', 'text': str(p)} for p in body_params],
            }
        ]
    payload = {
        'messaging_product': 'whatsapp',
        'to': norm_phone,
        'type': 'template',
        'template': tpl_obj,
    }
    summary = f'[template:{template_name}]'
    if body_params:
        summary = f"{summary} ({', '.join(str(p) for p in body_params)})"
    return _dispatch_whatsapp(
        phone=norm_phone,
        body=summary,
        message_type='template',
        payload=payload,
        source=source,
        contact_name=contact_name,
    )


def send_whatsapp_interactive_buttons(
    phone: str,
    body: str,
    buttons: list[dict[str, str]],
    *,
    header: str | None = None,
    footer: str | None = None,
    source: str = '',
    contact_name: str = '',
) -> WhatsAppMessage:
    norm_phone = normalize_whatsapp_phone(phone)
    action_buttons = [
        {
            'type': 'reply',
            'reply': {'id': str(b['id'])[:256], 'title': str(b['title'])[:20]},
        }
        for b in buttons[:3]
    ]
    interactive_obj: dict[str, Any] = {
        'type': 'button',
        'body': {'text': body},
        'action': {'buttons': action_buttons},
    }
    if header:
        interactive_obj['header'] = {'type': 'text', 'text': header[:60]}
    if footer:
        interactive_obj['footer'] = {'type': 'text', 'text': footer[:60]}

    payload = {
        'messaging_product': 'whatsapp',
        'to': norm_phone,
        'type': 'interactive',
        'interactive': interactive_obj,
    }
    btn_labels = ' | '.join(f"[{b['reply']['title']}]" for b in action_buttons)
    logged_body = f'{body}\n{btn_labels}'.strip() if btn_labels else body
    return _dispatch_whatsapp(
        phone=norm_phone,
        body=logged_body,
        message_type='interactive',
        payload=payload,
        source=source,
        contact_name=contact_name,
    )


def mark_whatsapp_message_read(wa_message_id: str) -> None:
    if not wa_message_id or not is_live_whatsapp_configured():
        return
    try:
        requests.post(
            _graph_messages_url(),
            headers={
                'Authorization': f"Bearer {getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')}",
                'Content-Type': 'application/json',
            },
            json={'messaging_product': 'whatsapp', 'status': 'read', 'message_id': wa_message_id},
            timeout=10,
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug('mark_whatsapp_message_read failed: %s', exc)


def _send_team_alert(summary_text: str, source: str = 'team_alert') -> WhatsAppMessage | None:
    if not getattr(settings, 'WHATSAPP_AUTO_NOTIFY_TEAM', True):
        return None
    raw_admin = getattr(settings, 'WHATSAPP_ADMIN_PHONE', '').strip()
    if not raw_admin:
        return None
    try:
        return send_whatsapp_text(raw_admin, summary_text, source=source, contact_name='BunShai Admin')
    except Exception as exc:  # noqa: BLE001
        logger.warning('Team WhatsApp alert failed: %s', exc)
        return None


def _build_user_form_message(form_type: str, data: dict[str, Any]) -> str | None:
    name = (data.get('name') or 'there').strip()
    site_name = getattr(settings, 'SITE_NAME', 'BunShai TECHNOHUB')
    if form_type == 'Contact Message':
        return (
            f"Hi {name}! Thanks for contacting {site_name}. "
            "We have received your message and our team will reply within 24 hours. "
            "Reply 'menu' anytime to explore services or courses."
        )
    if form_type == 'Service Inquiry':
        svc = data.get('service') or 'IT Services'
        return (
            f"Hi {name}! Thanks for your {site_name} service inquiry regarding *{svc}*. "
            "Our solutions team will connect with you shortly!"
        )
    if form_type == 'Proposal Request':
        svc = data.get('service') or 'Custom Project'
        budget = data.get('budget') or 'Custom'
        return (
            f"Hi {name}! Your {site_name} proposal request (*{svc}*, Budget: {budget}) is received. "
            "We are preparing your project estimate and will reach out soon."
        )
    if form_type == 'Course Enrollment':
        title = data.get('course_title') or data.get('course_slug') or 'Mentorship Program'
        mode = data.get('learning_mode') or 'Live Online'
        return (
            f"Hi {name}! Welcome to {site_name}. Your enrollment request for *{title}* "
            f"({mode}) is received! Our academic counselor will reach out within 24 hours."
        )
    if form_type == 'Syllabus Download':
        title = data.get('course_title') or data.get('course_slug') or 'our course'
        return (
            f"Hi {name}! Your {site_name} syllabus for *{title}* is ready.\n"
            "Have questions about batch timings, fees, or placement support? Just reply here!"
        )
    if form_type == 'Support Ticket':
        ticket_no = data.get('ticket_number') or 'BST'
        return (
            f"Hi {name}! Your {site_name} support ticket *{ticket_no}* has been logged. "
            "Our support team will respond within 2 hours."
        )
    if form_type == 'Career Application':
        pos = data.get('position') or 'our open role'
        return (
            f"Hi {name}! Thanks for applying for *{pos}* at {site_name}. "
            "Our hiring team has received your application and will review it shortly."
        )
    return None


def notify_form_submission(form_type: str, data: dict[str, Any]) -> None:
    """Send WhatsApp confirmation to the user (if phone given) and alert to admin team."""
    if not getattr(settings, 'WHATSAPP_ENABLED', True):
        return
    try:
        raw_phone = str(data.get('phone') or '').strip()
        if getattr(settings, 'WHATSAPP_AUTO_NOTIFY_USERS', True) and raw_phone:
            user_text = _build_user_form_message(form_type, data)
            if user_text:
                try:
                    norm = normalize_whatsapp_phone(raw_phone)
                    send_whatsapp_text(
                        norm,
                        user_text,
                        source=f"form:{form_type.lower().replace(' ', '_')}",
                        contact_name=str(data.get('name') or ''),
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning('User WhatsApp form notification failed (%s): %s', form_type, exc)

        summary_lines = [f'[{getattr(settings, "SITE_NAME", "BunShai TECHNOHUB")}] New {form_type}']
        for key in ('ticket_number', 'name', 'email', 'phone', 'service', 'budget', 'course_title', 'position', 'subject'):
            val = str(data.get(key) or '').strip()
            if val:
                summary_lines.append(f"{key.replace('_', ' ').title()}: {val}")
        _send_team_alert('\n'.join(summary_lines), source=f"team:{form_type.lower().replace(' ', '_')}")
    except Exception as exc:  # noqa: BLE001
        logger.warning('notify_form_submission failed: %s', exc)


def trigger_form_whatsapp_async(form_type: str, data: dict[str, Any]) -> None:
    """Run synchronously in dry-run (SQLite/TestCase safe), or in a background thread when live."""
    if not getattr(settings, 'WHATSAPP_ENABLED', True):
        return
    clean_data = {k: ('' if v is None else str(v)) for k, v in dict(data).items()}
    if getattr(settings, 'WHATSAPP_DRY_RUN', True):
        notify_form_submission(form_type, clean_data)
    else:
        threading.Thread(
            target=notify_form_submission,
            args=(form_type, clean_data),
            daemon=True,
        ).start()


def _match_course(user_text: str) -> dict[str, Any] | None:
    low = user_text.strip().lower()
    for c in COURSES:
        if low == c['slug'].lower() or low in c['title'].lower() or low in c['short_title'].lower():
            return c
    tokens = [t for t in re.findall(r'[a-z0-9]+', low) if len(t) >= 3]
    best = None
    best_hits = 0
    for c in COURSES:
        hay = f"{c['slug']} {c['title']} {c['category_name']}".lower()
        hits = sum(1 for t in tokens if t in hay)
        if hits > best_hits:
            best_hits = hits
            best = c
    return best if best_hits > 0 else None


def _match_service_code(user_text: str) -> str:
    low = user_text.strip().lower()
    for kw, code in SERVICE_CHOICES_MAP.items():
        if kw in low:
            return code
    return 'other'


def _extract_name_email(text: str, phone: str, default_name: str) -> tuple[str, str]:
    email_match = EMAIL_RE.search(text)
    email = email_match.group(0) if email_match else f'whatsapp+{phone}@bunshaitechnohub.com'
    cleaned = EMAIL_RE.sub('', text).strip(' ,|-')
    name = cleaned[:100] if cleaned else (default_name or 'WhatsApp Visitor')
    return name, email


def _abs_link(url: str) -> str:
    if url.startswith('http://') or url.startswith('https://'):
        return url
    base = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    return f'{base}{url}' if url.startswith('/') else f'{base}/{url}'


def _eval_auto_reply_rules(phone: str, text: str, contact_name: str) -> tuple[str | None, str]:
    rules = WhatsAppAutoReplyRule.objects.filter(is_active=True).order_by('priority', 'created_at')
    clean = text.strip()
    for rule in rules:
        matched = False
        if rule.match_type == 'exact':
            matched = clean.lower() == rule.pattern.strip().lower()
        elif rule.match_type == 'contains':
            matched = rule.pattern.lower() in clean.lower()
        elif rule.match_type == 'regex':
            try:
                matched = re.search(rule.pattern, clean, re.IGNORECASE) is not None
            except re.error:
                logger.warning('Invalid regex in WhatsAppAutoReplyRule %s', rule.pk)
        if matched:
            rendered = render_template_text(
                rule.reply_text,
                {'name': contact_name or 'there', 'phone': phone},
            )
            return rendered, f'rule:{rule.name}'
    return None, ''


def process_inbound_message(
    *,
    phone: str,
    text: str,
    contact_name: str = '',
    wa_message_id: str | None = None,
    msg_type: str = 'text',
    raw_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Store inbound message and route through flows, rules, or Sharsh AI."""
    norm_phone = normalize_whatsapp_phone(phone)

    if wa_message_id and WhatsAppMessage.objects.filter(wa_message_id=wa_message_id).exists():
        return {'skipped': True, 'reason': 'duplicate'}

    inbound = WhatsAppMessage.objects.create(
        wa_message_id=wa_message_id,
        direction='inbound',
        phone=norm_phone,
        contact_name=(contact_name or '')[:120],
        message_type=msg_type,
        body=text,
        status='received',
        source='webhook',
        raw_payload=raw_payload or {},
    )
    _sync_message_to_sheets(inbound)
    if wa_message_id:
        mark_whatsapp_message_read(wa_message_id)

    conv, _ = WhatsAppConversation.objects.get_or_create(phone=norm_phone)
    if contact_name and conv.contact_name != contact_name:
        conv.contact_name = contact_name[:120]
        conv.save(update_fields=['contact_name', 'updated_at'])

    effective_name = contact_name or conv.contact_name or 'there'
    clean = (text or '').strip().lower()
    created_record: dict[str, Any] | None = None
    team_alert: WhatsAppMessage | None = None

    # 1. Menu / Reset triggers
    if clean in MENU_TRIGGERS:
        conv.flow = 'idle'
        conv.step = ''
        conv.draft_data = {}
        conv.human_handoff = False
        conv.save()
        menu_body = (
            f"Hi {effective_name}! Welcome to {getattr(settings, 'SITE_NAME', 'BunShai TECHNOHUB')}.\n"
            "How can we help you today?\n\n"
            "1. Explore & Enroll in Courses (AI, Full Stack, Cloud, Data, Cyber)\n"
            "2. Request Service / Project Proposal\n"
            "3. Raise a Support Ticket\n"
            "4. Talk to our Human Team\n\n"
            "Tap a button below, reply 1-4, or ask any question!"
        )
        reply = send_whatsapp_interactive_buttons(
            norm_phone,
            menu_body,
            [
                {'id': 'btn_courses', 'title': 'Explore Courses'},
                {'id': 'btn_proposal', 'title': 'Request Proposal'},
                {'id': 'btn_human', 'title': 'Talk to Team'},
            ],
            header='BunShai TECHNOHUB',
            footer="Reply 'menu' anytime",
            source='flow:menu',
            contact_name=conv.contact_name,
        )
        return {
            'skipped': False,
            'inbound': inbound,
            'reply': reply,
            'source': 'flow:menu',
            'created_record': None,
            'team_alert': None,
        }

    # 2. Human handoff pause check
    if conv.human_handoff:
        return {
            'skipped': False,
            'inbound': inbound,
            'reply': None,
            'source': 'flow:human_handoff_paused',
            'created_record': None,
            'team_alert': None,
        }

    # 3. Cancel active flow
    if conv.flow != 'idle' and clean in CANCEL_TRIGGERS:
        conv.flow = 'idle'
        conv.step = ''
        conv.draft_data = {}
        conv.save()
        reply = send_whatsapp_text(
            norm_phone,
            "Flow cancelled. Type 'menu' anytime or ask me a question!",
            source='flow:cancelled',
            contact_name=conv.contact_name,
        )
        return {
            'skipped': False,
            'inbound': inbound,
            'reply': reply,
            'source': 'flow:cancelled',
            'created_record': None,
            'team_alert': None,
        }

    # 4. Active multi-step flows
    if conv.flow == 'course_enroll':
        if conv.step == 'ask_course':
            matched = _match_course(text)
            draft = {
                'course_slug': matched['slug'] if matched else 'custom-course',
                'course_title': matched['title'] if matched else text.strip()[:200],
            }
            conv.step = 'ask_contact'
            conv.draft_data = draft
            conv.save()
            reply = send_whatsapp_text(
                norm_phone,
                (
                    f"Great choice: *{draft['course_title']}*!\n"
                    "Please reply with your *Full Name and Email* (e.g. `Riya Sharma, riya@example.com`) "
                    "to complete your enrollment inquiry."
                ),
                source='flow:course_enroll:ask_contact',
                contact_name=conv.contact_name,
            )
            return {
                'skipped': False, 'inbound': inbound, 'reply': reply,
                'source': 'flow:course_enroll:ask_contact', 'created_record': None, 'team_alert': None,
            }

        draft = conv.draft_data or {}
        lead_name, lead_email = _extract_name_email(text, norm_phone, conv.contact_name)
        enrollment = CourseEnrollment.objects.create(
            name=lead_name,
            email=lead_email,
            phone=norm_phone,
            course_slug=draft.get('course_slug') or 'custom-course',
            course_title=draft.get('course_title') or 'Mentorship Program',
            learning_mode='Live Online',
            message='Captured via WhatsApp Bot',
        )
        conv.flow = 'idle'
        conv.step = ''
        conv.draft_data = {}
        conv.save()
        created_record = {'model': 'CourseEnrollment', 'id': str(enrollment.pk), 'course_title': enrollment.course_title}
        reply = send_whatsapp_text(
            norm_phone,
            (
                f"Awesome {lead_name}! Your enrollment inquiry for *{enrollment.course_title}* is confirmed.\n"
                "Our academic counselor will reach out within 24 hours. Type 'menu' anytime."
            ),
            source='flow:course_enroll:completed',
            contact_name=conv.contact_name,
        )
        team_alert = _send_team_alert(
            (
                f"[BunShai WhatsApp] New Course Enrollment\n"
                f"Name: {lead_name}\nPhone: {norm_phone}\nEmail: {lead_email}\n"
                f"Course: {enrollment.course_title}"
            ),
            source='team:course_enroll',
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:course_enroll:completed', 'created_record': created_record, 'team_alert': team_alert,
        }

    if conv.flow == 'service_inquiry':
        if conv.step == 'ask_service':
            conv.step = 'ask_details'
            conv.draft_data = {'service': _match_service_code(text), 'service_label': text.strip()[:100]}
            conv.save()
            reply = send_whatsapp_text(
                norm_phone,
                (
                    f"Got it ({text.strip()}). Briefly share your *project requirements* "
                    "and optional email so our consulting team can prepare an estimate:"
                ),
                source='flow:service_inquiry:ask_details',
                contact_name=conv.contact_name,
            )
            return {
                'skipped': False, 'inbound': inbound, 'reply': reply,
                'source': 'flow:service_inquiry:ask_details', 'created_record': None, 'team_alert': None,
            }

        draft = conv.draft_data or {}
        email_match = EMAIL_RE.search(text)
        lead_email = email_match.group(0) if email_match else f'whatsapp+{norm_phone}@bunshaitechnohub.com'
        lead_name = conv.contact_name or 'WhatsApp Lead'
        inquiry = ServiceInquiry.objects.create(
            name=lead_name,
            email=lead_email,
            phone=norm_phone,
            service=draft.get('service') or 'other',
            message=text.strip(),
        )
        conv.flow = 'idle'
        conv.step = ''
        conv.draft_data = {}
        conv.save()
        created_record = {'model': 'ServiceInquiry', 'id': str(inquiry.pk), 'service': inquiry.service}
        reply = send_whatsapp_text(
            norm_phone,
            (
                f"Thank you {lead_name}! Your inquiry for *{draft.get('service_label') or inquiry.service}* "
                "is logged. Our team will follow up within 24 hours."
            ),
            source='flow:service_inquiry:completed',
            contact_name=conv.contact_name,
        )
        team_alert = _send_team_alert(
            (
                f"[BunShai WhatsApp] New Service Inquiry\n"
                f"Name: {lead_name}\nPhone: {norm_phone}\nService: {inquiry.service}\n"
                f"Details: {text.strip()}"
            ),
            source='team:service_inquiry',
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:service_inquiry:completed', 'created_record': created_record, 'team_alert': team_alert,
        }

    if conv.flow == 'support_ticket':
        email_match = EMAIL_RE.search(text)
        lead_email = email_match.group(0) if email_match else f'whatsapp+{norm_phone}@bunshaitechnohub.com'
        lead_name = conv.contact_name or 'WhatsApp User'
        ticket = SupportTicket.objects.create(
            name=lead_name,
            email=lead_email,
            phone=norm_phone,
            issue_type='technical',
            priority='medium',
            subject=text.strip()[:180] or 'WhatsApp Support Request',
            description=text.strip(),
        )
        conv.flow = 'idle'
        conv.step = ''
        conv.draft_data = {}
        conv.save()
        created_record = {
            'model': 'SupportTicket',
            'id': str(ticket.pk),
            'ticket_number': ticket.ticket_number,
        }
        reply = send_whatsapp_text(
            norm_phone,
            (
                f"Support ticket *{ticket.ticket_number}* has been created!\n"
                "Our team will review it and reply within 2 hours."
            ),
            source='flow:support_ticket:completed',
            contact_name=conv.contact_name,
        )
        team_alert = _send_team_alert(
            (
                f"[BunShai WhatsApp] Support Ticket {ticket.ticket_number}\n"
                f"From: {lead_name} ({norm_phone})\nIssue: {text.strip()}"
            ),
            source='team:support_ticket',
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:support_ticket:completed', 'created_record': created_record, 'team_alert': team_alert,
        }

    if conv.flow == 'human_handoff':
        unanswered = ChatbotUnanswered.objects.create(
            question=text.strip(),
            name=conv.contact_name or '',
            phone=norm_phone,
        )
        conv.flow = 'human_handoff'
        conv.step = 'handed_off'
        conv.human_handoff = True
        conv.draft_data = {'unanswered_id': str(unanswered.pk)}
        conv.save()
        created_record = {'model': 'ChatbotUnanswered', 'id': str(unanswered.pk)}
        reply = send_whatsapp_text(
            norm_phone,
            (
                "Got it! A BunShai TECHNOHUB team member has been notified.\n"
                "Bot auto-replies are paused so our team can chat with you directly. "
                "Type 'menu' anytime to restart the automated assistant."
            ),
            source='flow:human_handoff:handed_off',
            contact_name=conv.contact_name,
        )
        team_alert = _send_team_alert(
            (
                f"[BunShai WhatsApp] Human Handoff Requested\n"
                f"From: {conv.contact_name or 'Unknown'} ({norm_phone})\nTopic: {text.strip()}"
            ),
            source='team:human_handoff',
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:human_handoff:handed_off', 'created_record': created_record, 'team_alert': team_alert,
        }

    # 5. Idle menu choice triggers
    if clean in COURSE_FLOW_TRIGGERS:
        conv.flow = 'course_enroll'
        conv.step = 'ask_course'
        conv.draft_data = {}
        conv.save()
        tracks = '\n'.join(f"- {c['name']}" for c in COURSE_CATEGORIES)
        reply = send_whatsapp_text(
            norm_phone,
            (
                f"Which BunShai TECHNOHUB program interests you?\n{tracks}\n\n"
                "Reply with a program or topic name (e.g. 'Cloud Computing' or 'Full Stack AI')."
            ),
            source='flow:course_enroll:start',
            contact_name=conv.contact_name,
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:course_enroll:start', 'created_record': None, 'team_alert': None,
        }

    if clean in SERVICE_FLOW_TRIGGERS:
        conv.flow = 'service_inquiry'
        conv.step = 'ask_service'
        conv.draft_data = {}
        conv.save()
        reply = send_whatsapp_text(
            norm_phone,
            (
                "Let's scope your project! Which service do you need?\n"
                "- Web / Software Development\n"
                "- Mobile App Development\n"
                "- AI / ML & Automation\n"
                "- Cloud Solutions\n"
                "- Cybersecurity\n"
                "- Digital Marketing / Data Analytics\n\n"
                "Reply with the service name (or 'cancel' to exit)."
            ),
            source='flow:service_inquiry:start',
            contact_name=conv.contact_name,
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:service_inquiry:start', 'created_record': None, 'team_alert': None,
        }

    if clean in SUPPORT_FLOW_TRIGGERS:
        conv.flow = 'support_ticket'
        conv.step = 'ask_issue'
        conv.draft_data = {}
        conv.save()
        reply = send_whatsapp_text(
            norm_phone,
            "Sure! Please describe the issue you are facing so I can generate a support ticket (BST-...):",
            source='flow:support_ticket:start',
            contact_name=conv.contact_name,
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:support_ticket:start', 'created_record': None, 'team_alert': None,
        }

    if clean in HANDOFF_FLOW_TRIGGERS:
        conv.flow = 'human_handoff'
        conv.step = 'ask_topic'
        conv.draft_data = {}
        conv.save()
        reply = send_whatsapp_text(
            norm_phone,
            "I'll connect you with our team. Briefly tell us what you'd like to discuss:",
            source='flow:human_handoff:start',
            contact_name=conv.contact_name,
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': 'flow:human_handoff:start', 'created_record': None, 'team_alert': None,
        }

    # 6. Custom auto-reply rules
    rule_reply, rule_source = _eval_auto_reply_rules(norm_phone, text, effective_name)
    if rule_reply:
        reply = send_whatsapp_text(
            norm_phone, rule_reply, source=rule_source, contact_name=conv.contact_name
        )
        return {
            'skipped': False, 'inbound': inbound, 'reply': reply,
            'source': rule_source, 'created_record': None, 'team_alert': None,
        }

    # 7. Sharsh Knowledge Base fallback
    kb = get_chatbot_response(text, session=None)
    reply_parts = [kb['reply']]
    links = kb.get('links') or []
    if links:
        reply_parts.append('')
        for lnk in links[:3]:
            reply_parts.append(f"- {lnk['label']}: {_abs_link(lnk['url'])}")

    if kb.get('fallback'):
        unans = ChatbotUnanswered.objects.create(
            question=text.strip(),
            name=conv.contact_name or '',
            phone=norm_phone,
        )
        created_record = {'model': 'ChatbotUnanswered', 'id': str(unans.pk)}
        reply_parts.append("\nReply '4' anytime to talk directly with our human team.")

    final_text = '\n'.join(reply_parts).strip()
    source_tag = f"sharsh:{kb.get('intent', 'answer')}"
    reply = send_whatsapp_text(
        norm_phone, final_text, source=source_tag, contact_name=conv.contact_name
    )
    return {
        'skipped': False,
        'inbound': inbound,
        'reply': reply,
        'source': source_tag,
        'created_record': created_record,
        'team_alert': None,
    }


def execute_scheduled_message(job: WhatsAppScheduledMessage) -> WhatsAppMessage:
    """Execute a single scheduled WhatsApp job and update its recurrence/status."""
    now = timezone.now()
    try:
        if job.message_type == 'template':
            msg = send_whatsapp_template(
                job.phone,
                job.template_name,
                language_code=job.template_lang or 'en_US',
                body_params=list(job.template_params or []),
                source=f'schedule:{job.pk}',
                contact_name=job.name,
            )
        else:
            msg = send_whatsapp_text(
                job.phone,
                job.body,
                source=f'schedule:{job.pk}',
                contact_name=job.name,
            )
        job.last_run_at = now
        job.last_error = ''
        if job.recurrence == 'once':
            job.status = 'sent'
        else:
            delta_days = {'daily': 1, 'weekly': 7, 'monthly': 30}.get(job.recurrence, 1)
            base_dt = job.scheduled_for if job.scheduled_for > now else now
            job.scheduled_for = base_dt + timedelta(days=delta_days)
            job.status = 'pending'
        job.save(update_fields=['status', 'scheduled_for', 'last_run_at', 'last_error'])
        return msg
    except Exception as exc:  # noqa: BLE001
        job.last_run_at = now
        job.last_error = str(exc)
        job.status = 'failed'
        job.save(update_fields=['status', 'last_run_at', 'last_error'])
        raise


def run_due_scheduled_messages() -> dict[str, int]:
    """Process all pending WhatsAppScheduledMessage jobs whose scheduled_for <= now."""
    due_jobs = WhatsAppScheduledMessage.objects.filter(
        status='pending', scheduled_for__lte=timezone.now()
    ).order_by('scheduled_for')
    processed = 0
    sent = 0
    failed = 0
    for job in due_jobs:
        processed += 1
        try:
            execute_scheduled_message(job)
            sent += 1
        except Exception:  # noqa: BLE001
            failed += 1
    return {'processed': processed, 'sent': sent, 'failed': failed}


def collect_audience_phones(audience: str, course_slug: str = '') -> list[dict[str, str]]:
    """Collect deduplicated contacts from existing BunShai TECHNOHUB models."""
    rows: list[dict[str, str]] = []
    if audience == 'course_enrollments':
        qs = CourseEnrollment.objects.all()
        if course_slug:
            qs = qs.filter(course_slug=course_slug)
        for item in qs:
            rows.append({'phone': item.phone, 'name': item.name, 'extra': item.course_title})
    elif audience == 'syllabus_downloads':
        qs = SyllabusDownload.objects.all()
        if course_slug:
            qs = qs.filter(course_slug=course_slug)
        for item in qs:
            rows.append({'phone': item.phone, 'name': item.name, 'extra': item.course_title})
    elif audience == 'service_inquiries':
        for item in ServiceInquiry.objects.all():
            rows.append({'phone': item.phone, 'name': item.name, 'extra': item.service})
    elif audience == 'proposal_requests':
        for item in ProposalRequest.objects.all():
            rows.append({'phone': item.phone, 'name': item.name, 'extra': item.service})
    elif audience == 'contact_messages':
        for item in ContactMessage.objects.exclude(phone__isnull=True).exclude(phone=''):
            rows.append({'phone': item.phone or '', 'name': item.name, 'extra': item.service or item.subject})
    else:
        raise ValueError(f'Unknown audience: {audience}')

    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        try:
            norm = normalize_whatsapp_phone(row['phone'])
        except ValueError:
            continue
        if norm not in seen:
            seen.add(norm)
            deduped.append({'phone': norm, 'name': row['name'], 'extra': row['extra']})
    return deduped
