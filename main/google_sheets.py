"""Google Sheets sync + structured local CSV spreadsheet backup.

The database is always the primary store. Every lead is also appended to a
structured CSV file under media/exports/ and, when Google credentials are
configured, synced asynchronously to the target Google Sheet worksheet
(shared with team.bunshailogicloop@gmail.com).

Credentials: either a service-account JSON file at ``GOOGLE_SHEETS_CREDENTIALS``
or the JSON content in the ``GOOGLE_SHEETS_JSON`` environment variable.
"""
import csv
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# sheet name -> [(column header, data key), ...]; Timestamp is always prepended.
SHEET_SPEC = {
    'contact_messages': [('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'), ('Company', 'company'),
                         ('Subject', 'subject'), ('Service', 'service'), ('Message', 'message')],
    'subscribers': [('Email', 'email')],
    'service_inquiries': [('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'), ('Company', 'company'),
                          ('Service', 'service'), ('Message', 'message')],
    'proposal_requests': [('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'), ('Service', 'service'),
                          ('Budget', 'budget'), ('Requirements', 'requirements')],
    'career_applications': [('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'), ('LinkedIn', 'linkedin_url'),
                            ('Position', 'position'), ('Cover Letter', 'cover_letter'), ('Resume', 'resume')],
    'support_tickets': [('Ticket No', 'ticket_number'), ('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'),
                        ('Issue Type', 'issue_type'), ('Priority', 'priority'), ('Subject', 'subject'),
                        ('Description', 'description')],
    'course_enrollments': [('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'), ('Course', 'course_title'),
                           ('Learning Mode', 'learning_mode'), ('Experience Level', 'experience_level'),
                           ('Message', 'message')],
    'syllabus_downloads': [('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'), ('Course', 'course_title'),
                           ('Course Slug', 'course_slug'), ('Background', 'background'),
                           ('IP Address', 'ip_address')],
    'chatbot_sessions': [('Session ID', 'session_id'), ('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'),
                         ('Returning', 'is_returning'), ('Page', 'page')],
    'chatbot_messages': [('Session ID', 'session_id'), ('Name', 'name'), ('Email', 'email'),
                         ('User Question', 'question'), ('Sharsh Reply', 'reply'), ('Intent', 'intent'),
                         ('Answered', 'answered')],
    'chatbot_unanswered': [('Session ID', 'session_id'), ('Name', 'name'), ('Email', 'email'),
                           ('Phone', 'phone'), ('Unanswered Question', 'question'),
                           ('Status', 'status')],
}

HEADERS = ['Timestamp', 'Name', 'Email', 'Phone', 'Data']
SHEET_HEADERS = {name: ['Timestamp'] + [h for h, _ in cols] for name, cols in SHEET_SPEC.items()}

OWNER_EMAIL = getattr(settings, 'SITE_EMAIL', 'team.bunshailogicloop@gmail.com')

_csv_lock = threading.Lock()


def _cell(value):
    if value is None:
        return ''
    text = str(value)
    # Neutralise spreadsheet formula injection
    if text[:1] in ('=', '+', '-', '@') and not text.replace('+', '').replace('-', '').replace(' ', '').isdigit():
        text = "'" + text
    return text[:2000]


def _creds_file():
    return Path(str(getattr(settings, 'GOOGLE_SHEETS_CREDENTIALS', '')))


def _creds_json():
    raw = getattr(settings, 'GOOGLE_SHEETS_JSON', '') or ''
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        logger.error("GOOGLE_SHEETS_JSON is not valid JSON")
        return None


def _configured():
    return bool(getattr(settings, 'GOOGLE_SHEET_ID', '')) and (_creds_file().is_file() or _creds_json() is not None)


def credentials_available():
    return _creds_file().is_file() or _creds_json() is not None


def _format_row(sheet_name, data):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    spec = SHEET_SPEC.get(sheet_name)
    if spec:
        return [ts] + [_cell(data.get(key)) for _, key in spec]
    return [ts, _cell(data.get('name')), _cell(data.get('email')), _cell(data.get('phone')),
            _cell({k: str(v) for k, v in data.items()})]


def _append_local_csv(sheet_name, row):
    try:
        export_dir = Path(getattr(settings, 'MEDIA_ROOT', Path(settings.BASE_DIR) / 'media')) / 'exports'
        export_dir.mkdir(parents=True, exist_ok=True)
        csv_path = export_dir / f'{sheet_name}.csv'
        headers = SHEET_HEADERS.get(sheet_name, HEADERS)
        with _csv_lock:
            is_new = not csv_path.exists() or csv_path.stat().st_size == 0
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if is_new:
                    writer.writerow(headers)
                writer.writerow(row)
    except Exception as e:  # noqa: BLE001
        logger.warning("Local CSV backup failed for %s: %s", sheet_name, e)


def get_gspread_client():
    """Authorised gspread client or None when credentials are missing/invalid."""
    if not credentials_available():
        return None
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        info = _creds_json()
        if info is not None:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name(str(_creds_file()), scope)
        return gspread.authorize(creds)
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to authorise Google Sheets client: %s", e)
        return None


def get_google_sheet():
    """Return the spreadsheet or None when Sheets is not configured/reachable."""
    if not _configured():
        return None
    client = get_gspread_client()
    if not client:
        return None
    try:
        return client.open_by_key(settings.GOOGLE_SHEET_ID)
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to open Google Sheet: %s", e)
        return None


def _worksheet(sheet, sheet_name):
    headers = SHEET_HEADERS.get(sheet_name, HEADERS)
    try:
        return sheet.worksheet(sheet_name)
    except Exception:  # worksheet missing -> create it
        ws = sheet.add_worksheet(title=sheet_name, rows=1000, cols=max(10, len(headers)))
        ws.append_row(headers)
        return ws


def _save(sheet_name, data, on_success=None):
    row = _format_row(sheet_name, data)
    _append_local_csv(sheet_name, row)
    if not _configured():
        return False
    try:
        sheet = get_google_sheet()
        if not sheet:
            return False
        _worksheet(sheet, sheet_name).append_row(row, value_input_option='USER_ENTERED')
        if on_success:
            try:
                on_success()
            except Exception as cb_err:  # noqa: BLE001
                logger.warning("Google Sheets on_success callback failed: %s", cb_err)
        return True
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to save to Google Sheets: %s", e)
        return False


def save_to_google_sheet(sheet_name, data, on_success=None):
    """Fire-and-forget backup of a submission to CSV + Google Sheets."""
    threading.Thread(target=_save, args=(sheet_name, dict(data), on_success), daemon=True).start()
    return True


def initialize_google_sheets(sheet=None):
    sheet = sheet or get_google_sheet()
    if not sheet:
        return False
    for name in SHEET_SPEC:
        _worksheet(sheet, name)
    return True


def sync_to_google_sheets(sheet_name, obj):
    """Used by the sync_unsynced management command."""
    data = {f.name: getattr(obj, f.name) for f in obj._meta.fields}
    for key in ('course_title', 'ticket_number'):
        if hasattr(obj, key):
            data[key] = getattr(obj, key)
    if hasattr(obj, 'session') and getattr(obj, 'session', None) is not None:
        data['session_id'] = obj.session.session_id
    if sheet_name == 'chatbot_unanswered':
        data['status'] = 'Resolved' if getattr(obj, 'resolved', False) else 'Pending contact-form follow-up'
    return _save(sheet_name, data)
