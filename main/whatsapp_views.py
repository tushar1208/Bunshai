"""Webhook, staff dashboard, and API views for WhatsApp Cloud API automation."""

import csv
from datetime import datetime
import hmac
import io
import json
import logging
import uuid
from typing import Any

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .courses_data import COURSES
from .models import (
    WhatsAppAutoReplyRule,
    WhatsAppConversation,
    WhatsAppMessage,
    WhatsAppScheduledMessage,
)
from .whatsapp_service import (
    WhatsAppAPIError,
    collect_audience_phones,
    is_live_whatsapp_configured,
    normalize_whatsapp_phone,
    process_inbound_message,
    render_template_text,
    run_due_scheduled_messages,
    send_whatsapp_template,
    send_whatsapp_text,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)


def _json_body(request) -> dict[str, Any]:
    try:
        parsed = json.loads(request.body.decode('utf-8') or '{}')
        return parsed if isinstance(parsed, dict) else {}
    except (ValueError, TypeError, UnicodeDecodeError):
        return {}


def _require_staff_or_api_key(request) -> JsonResponse | None:
    if request.user.is_authenticated and request.user.is_staff:
        return None
    configured_key = getattr(settings, 'WHATSAPP_API_KEY', '').strip()
    provided_key = request.headers.get('X-API-Key', '').strip()
    if configured_key and provided_key and hmac.compare_digest(provided_key, configured_key):
        return None
    return JsonResponse({'error': 'Unauthorized'}, status=401)


def _extract_message_text(msg: dict[str, Any]) -> str:
    msg_type = msg.get('type', 'text')
    if msg_type == 'text':
        return str((msg.get('text') or {}).get('body', '')).strip()
    if msg_type == 'button':
        return str((msg.get('button') or {}).get('text', '')).strip()
    if msg_type == 'interactive':
        interactive = msg.get('interactive') or {}
        btn_reply = interactive.get('button_reply') or {}
        list_reply = interactive.get('list_reply') or {}
        return str(btn_reply.get('title') or list_reply.get('title') or '[interactive]').strip()
    return f'[{msg_type} message]'


def _serialize_message(msg: WhatsAppMessage | None) -> dict[str, Any] | None:
    if not msg:
        return None
    return {
        'id': str(msg.pk),
        'wa_message_id': msg.wa_message_id,
        'direction': msg.direction,
        'phone': msg.phone,
        'contact_name': msg.contact_name,
        'message_type': msg.message_type,
        'body': msg.body,
        'status': msg.status,
        'source': msg.source,
        'created_at': msg.created_at.isoformat(),
    }


@csrf_exempt
def whatsapp_webhook(request):
    """Meta WhatsApp Cloud API verification handshake (GET) and event receiver (POST)."""
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        expected = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', '')
        if mode == 'subscribe' and verify_token == expected and challenge is not None:
            return HttpResponse(challenge, content_type='text/plain', status=200)
        return HttpResponse('Verification failed', status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    raw_body = request.body
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_webhook_signature(raw_body, signature):
        return JsonResponse({'error': 'Invalid webhook signature'}, status=403)

    payload = _json_body(request)
    processed = 0
    for entry in payload.get('entry') or []:
        for change in entry.get('changes') or []:
            value = change.get('value') or {}
            contacts = {
                c.get('wa_id'): (c.get('profile') or {}).get('name', '')
                for c in (value.get('contacts') or [])
                if c.get('wa_id')
            }

            for status_item in value.get('statuses') or []:
                wa_id = status_item.get('id')
                status_val = status_item.get('status')
                if wa_id and status_val:
                    WhatsAppMessage.objects.filter(wa_message_id=wa_id).update(status=status_val)

            for msg in value.get('messages') or []:
                from_phone = msg.get('from')
                if not from_phone:
                    continue
                wa_id = msg.get('id')
                msg_type = msg.get('type', 'text')
                text_body = _extract_message_text(msg)
                contact_name = contacts.get(from_phone, '')
                try:
                    result = process_inbound_message(
                        phone=from_phone,
                        text=text_body,
                        contact_name=contact_name,
                        wa_message_id=wa_id,
                        msg_type=msg_type,
                        raw_payload=msg,
                    )
                    if not result.get('skipped'):
                        processed += 1
                except Exception as exc:  # noqa: BLE001
                    logger.warning('Skipping inbound WhatsApp message: %s', exc)

    return JsonResponse({'status': 'ok', 'processed': processed})


@staff_member_required
def whatsapp_dashboard(request):
    """Staff control panel for BunShai TECHNOHUB WhatsApp automation."""
    context = {
        'dry_run': not is_live_whatsapp_configured(),
        'admin_phone': getattr(settings, 'WHATSAPP_ADMIN_PHONE', ''),
        'total_messages': WhatsAppMessage.objects.count(),
        'inbound_count': WhatsAppMessage.objects.filter(direction='inbound').count(),
        'outbound_count': WhatsAppMessage.objects.filter(direction='outbound').count(),
        'active_rules': WhatsAppAutoReplyRule.objects.filter(is_active=True).count(),
        'pending_schedules': WhatsAppScheduledMessage.objects.filter(status='pending').count(),
        'paused_conversations': WhatsAppConversation.objects.filter(human_handoff=True),
        'recent_messages': WhatsAppMessage.objects.all()[:30],
        'rules': WhatsAppAutoReplyRule.objects.all()[:30],
        'schedules': WhatsAppScheduledMessage.objects.all()[:30],
        'courses': COURSES,
    }
    return render(request, 'whatsapp_dashboard.html', context)


@csrf_exempt
@require_POST
def api_whatsapp_simulate(request):
    auth_err = _require_staff_or_api_key(request)
    if auth_err:
        return auth_err
    data = _json_body(request)
    phone = str(data.get('phone') or '').strip()
    text = str(data.get('text') or '').strip()
    contact_name = str(data.get('contact_name') or '').strip()
    if not phone or not text:
        return JsonResponse({'error': 'phone and text are required'}, status=400)
    try:
        result = process_inbound_message(
            phone=phone,
            text=text,
            contact_name=contact_name,
            wa_message_id=f'sim_{uuid.uuid4().hex[:12]}',
            msg_type='text',
            raw_payload={'simulated': True, 'text': text},
        )
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=422)
    return JsonResponse({
        'inbound': _serialize_message(result.get('inbound')),
        'reply': _serialize_message(result.get('reply')),
        'source': result.get('source'),
        'created_record': result.get('created_record'),
        'team_alert': _serialize_message(result.get('team_alert')),
    })


@csrf_exempt
@require_POST
def api_whatsapp_send(request):
    auth_err = _require_staff_or_api_key(request)
    if auth_err:
        return auth_err
    data = _json_body(request)
    phone = str(data.get('phone') or '').strip()
    msg_type = str(data.get('message_type') or 'text').strip()
    if not phone:
        return JsonResponse({'error': 'phone is required'}, status=400)
    try:
        if msg_type == 'template':
            template_name = str(data.get('template_name') or '').strip()
            if not template_name:
                return JsonResponse({'error': 'template_name is required'}, status=422)
            msg = send_whatsapp_template(
                phone,
                template_name,
                language_code=str(data.get('template_lang') or 'en_US'),
                body_params=list(data.get('template_params') or []),
                source='api:send',
            )
        else:
            body = str(data.get('body') or '').strip()
            if not body:
                return JsonResponse({'error': 'body is required'}, status=422)
            msg = send_whatsapp_text(phone, body, source='api:send')
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=422)
    except WhatsAppAPIError as exc:
        return JsonResponse({'error': str(exc)}, status=502)
    return JsonResponse({'message': _serialize_message(msg)})


@csrf_exempt
@require_POST
def api_whatsapp_schedule(request):
    auth_err = _require_staff_or_api_key(request)
    if auth_err:
        return auth_err
    data = _json_body(request)
    try:
        phone = normalize_whatsapp_phone(str(data.get('phone') or ''))
        scheduled_raw = str(data.get('scheduled_for') or '').strip()
        if not scheduled_raw:
            raise ValueError('scheduled_for ISO datetime is required.')
        dt = datetime.fromisoformat(scheduled_raw.replace('Z', '+00:00'))
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())

        msg_type = str(data.get('message_type') or 'text')
        body = str(data.get('body') or '').strip()
        template_name = str(data.get('template_name') or '').strip()
        if msg_type == 'text' and not body:
            raise ValueError('body is required for text scheduled messages.')
        if msg_type == 'template' and not template_name:
            raise ValueError('template_name is required for template scheduled messages.')

        recurrence = str(data.get('recurrence') or 'once')
        if recurrence not in ('once', 'daily', 'weekly', 'monthly'):
            raise ValueError('Invalid recurrence.')

        job = WhatsAppScheduledMessage.objects.create(
            name=str(data.get('name') or '')[:150],
            phone=phone,
            message_type=msg_type,
            body=body,
            template_name=template_name,
            template_lang=str(data.get('template_lang') or 'en_US'),
            template_params=list(data.get('template_params') or []),
            scheduled_for=dt,
            recurrence=recurrence,
        )
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=422)

    return JsonResponse({
        'schedule': {
            'id': str(job.pk),
            'name': job.name,
            'phone': job.phone,
            'scheduled_for': job.scheduled_for.isoformat(),
            'recurrence': job.recurrence,
            'status': job.status,
        }
    }, status=201)


@csrf_exempt
@require_POST
def api_whatsapp_run_due_schedules(request):
    auth_err = _require_staff_or_api_key(request)
    if auth_err:
        return auth_err
    summary = run_due_scheduled_messages()
    return JsonResponse(summary)


@csrf_exempt
@require_POST
def api_whatsapp_broadcast(request):
    auth_err = _require_staff_or_api_key(request)
    if auth_err:
        return auth_err

    contacts: list[dict[str, Any]] = []
    if request.FILES.get('file'):
        upload = request.FILES['file']
        raw_bytes = upload.read()
        try:
            csv_text = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            csv_text = raw_bytes.decode('latin-1')
        reader = csv.DictReader(io.StringIO(csv_text))
        if not reader.fieldnames:
            return JsonResponse({'error': 'CSV file has no header row.'}, status=422)
        phone_col = str(request.POST.get('phone_column') or 'phone').strip()
        message_template = str(request.POST.get('message_template') or '')
        template_name = str(request.POST.get('template_name') or '').strip()
        template_lang = str(request.POST.get('template_lang') or 'en_US').strip()
        param_cols = [
            c.strip() for c in str(request.POST.get('template_param_columns') or '').split(',') if c.strip()
        ]
        for row in reader:
            contacts.append({
                'phone': str(row.get(phone_col) or '').strip(),
                'row': row,
            })
    else:
        data = _json_body(request)
        message_template = str(data.get('message_template') or '')
        template_name = str(data.get('template_name') or '').strip()
        template_lang = str(data.get('template_lang') or 'en_US').strip()
        param_cols = []
        raw_phones = data.get('phones') or []
        if raw_phones:
            for p in raw_phones:
                contacts.append({'phone': str(p), 'row': {'phone': str(p), 'name': 'there'}})
        else:
            audience = str(data.get('audience') or 'course_enrollments').strip()
            course_slug = str(data.get('course_slug') or '').strip()
            try:
                for item in collect_audience_phones(audience, course_slug=course_slug):
                    contacts.append({'phone': item['phone'], 'row': item})
            except ValueError as exc:
                return JsonResponse({'error': str(exc)}, status=422)

    if not message_template.strip() and not template_name:
        return JsonResponse({'error': 'Provide either message_template or template_name.'}, status=422)

    results: list[dict[str, Any]] = []
    sent = 0
    failed = 0
    for idx, item in enumerate(contacts, start=1):
        raw_phone = item['phone']
        row = item['row']
        try:
            norm = normalize_whatsapp_phone(raw_phone)
            if template_name:
                params = [str(row.get(col, '') or '') for col in param_cols] if param_cols else [
                    str(row.get('name') or 'there')
                ]
                msg = send_whatsapp_template(
                    norm,
                    template_name,
                    language_code=template_lang or 'en_US',
                    body_params=params,
                    source='broadcast',
                    contact_name=str(row.get('name') or ''),
                )
            else:
                rendered = render_template_text(message_template, row)
                msg = send_whatsapp_text(
                    norm,
                    rendered,
                    source='broadcast',
                    contact_name=str(row.get('name') or ''),
                )
            sent += 1
            results.append({'row': idx, 'phone': norm, 'status': msg.status, 'message_id': str(msg.pk)})
        except Exception as exc:  # noqa: BLE001
            failed += 1
            results.append({'row': idx, 'phone': raw_phone, 'status': 'failed', 'error': str(exc)})

    return JsonResponse({'total': len(results), 'sent': sent, 'failed': failed, 'results': results})


@csrf_exempt
@require_POST
def api_whatsapp_resume_conversation(request, phone: str):
    auth_err = _require_staff_or_api_key(request)
    if auth_err:
        return auth_err
    try:
        norm = normalize_whatsapp_phone(phone)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=422)

    conv, _ = WhatsAppConversation.objects.get_or_create(phone=norm)
    conv.flow = 'idle'
    conv.step = ''
    conv.draft_data = {}
    conv.human_handoff = False
    conv.save()
    return JsonResponse({'resumed': True, 'phone': norm, 'flow': 'idle'})
