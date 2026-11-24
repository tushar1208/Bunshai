"""Sharsh - retrieval based assistant that answers from the website knowledge base.

``get_chatbot_response(message, session)`` returns a dict::

    {reply, links, suggestions, fallback, contact_url, intent, confidence, entry_id}

When nothing in the knowledge base matches confidently, ``fallback`` is True and a
pre-filled contact-form URL is returned so the visitor is handed to the human team.
"""
import difflib
import re
from urllib.parse import urlencode

from .knowledge_base import (
    DEFAULT_SUGGESTIONS, EMAIL, ENTRIES, PHONE, SMALLTALK, WHATSAPP,
)

STOPWORDS = {
    'the', 'is', 'are', 'a', 'an', 'what', 'whats', 'do', 'does', 'you', 'your', 'yours', 'me', 'my', 'i', 'can',
    'could', 'would', 'should', 'how', 'to', 'of', 'and', 'in', 'for', 'on', 'about', 'please', 'tell', 'show',
    'give', 'there', 'any', 'have', 'has', 'we', 'us', 'it', 'its', 'with', 'at', 'be', 'am', 'want', 'need',
    'know', 'like', 'some', 'get', 'will', 'shall', 'u', 'ur', 'kindly', 'hey', 'hi', 'hello', 'which', 'who',
    'when', 'where', 'why', 'that', 'this', 'these', 'those', 'also', 'more', 'info', 'information', 'details',
}
GENERIC = {'course', 'program', 'service', 'team', 'contact', 'help', 'support', 'career', 'company',
           'project', 'work', 'year', 'time'}
AFFIRM = {'yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'please do', 'yes please', 'definitely', 'go ahead'}
THRESHOLD = 1.7

EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
PHONE_RE = re.compile(r'(?<!\d)(\+?\d[\d\s\-()]{8,16}\d)(?!\d)')


def _stem(word):
    if len(word) > 4 and word.endswith('ies'):
        return word[:-3] + 'y'
    if len(word) > 4 and word.endswith('es') and not word.endswith(('ses', 'xes')):
        return word[:-2]
    if len(word) > 3 and word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


def _tokens(text):
    words = re.findall(r"[a-z0-9+#.]+", text.lower().replace('&', ' and '))
    return [_stem(w.strip('.')) for w in words if w.strip('.')]


def _norm(text):
    return ' ' + ' '.join(_tokens(text)) + ' '


def extract_contact(message):
    email = EMAIL_RE.search(message)
    phone = PHONE_RE.search(message)
    return (email.group(0) if email else None), (phone.group(1).strip() if phone else None)


def _score(entry, q_norm, q_tokens, q_set):
    score = 0.0
    matched = set()
    for kw in entry['keywords']:
        kw_norm = _norm(kw)
        kw_tokens = kw_norm.split()
        if not kw_tokens:
            continue
        if len(kw_tokens) > 1:
            if kw_norm in q_norm:
                score += 3 + len(kw_tokens)
                matched.update(kw_tokens)
        else:
            tok = kw_tokens[0]
            if tok in q_set:
                score += 1.8 if tok in GENERIC else 2.5
                matched.add(tok)
            elif len(tok) >= 5:
                for qt in q_tokens:
                    if len(qt) >= 5 and difflib.SequenceMatcher(None, qt, tok).ratio() >= 0.86:
                        score += 1.8
                        matched.add(qt)
                        break
    if score:
        title_tokens = set(_tokens(entry['title']))
        score += 0.6 * len(title_tokens & q_set)
        if entry['id'].startswith(('course_', 'cat_', 'svc_')) and matched - GENERIC:
            score += 0.4
    return score


def _smalltalk(q_norm, q_tokens):
    clean = ' '.join(q_tokens)
    for intent, data in SMALLTALK.items():
        for pattern in data['patterns']:
            p = ' '.join(_tokens(pattern))
            if clean == p or (len(q_tokens) <= 6 and f' {p} ' in q_norm and len(q_tokens) <= len(p.split()) + 2):
                return intent, data['reply']
    return None, None


def contact_url(question='', session=None):
    params = {'subject': 'Chatbot enquiry', 'source': 'chatbot'}
    if question:
        params['message'] = question[:500]
    if session is not None:
        for field in ('name', 'email', 'phone'):
            value = getattr(session, field, None)
            if value:
                params[field] = value
    return '/contact/?' + urlencode(params)


def _pack(reply, **kw):
    out = {'reply': reply, 'links': [], 'suggestions': [], 'fallback': False, 'contact_url': '',
           'intent': 'answer', 'confidence': 1.0, 'entry_id': ''}
    out.update(kw)
    return out


def fallback_response(message, session=None):
    url = contact_url(message, session)
    return _pack(
        "I'm sorry - I couldn't find a reliable answer to that on our website. 🙏 Rather than guess, let me "
        "connect you with our team: please fill in the contact form (I've pre-filled your question) and we'll "
        f"reply within 24 hours.\n\nYou can also call {PHONE}, WhatsApp us or email {EMAIL}.",
        links=[{'label': '📝 Open Contact Form', 'url': url},
               {'label': '💬 WhatsApp Us', 'url': WHATSAPP}],
        suggestions=DEFAULT_SUGGESTIONS[:3],
        fallback=True, contact_url=url, intent='fallback', confidence=0.0)


def get_chatbot_response(message, session=None):
    message = (message or '').strip()
    q_tokens = _tokens(message)
    q_norm = ' ' + ' '.join(q_tokens) + ' '
    if not q_tokens:
        return fallback_response(message, session)

    intent, reply = _smalltalk(q_norm, q_tokens)
    if intent:
        return _pack(reply, intent=intent, suggestions=DEFAULT_SUGGESTIONS)

    if ' '.join(q_tokens) in {' '.join(_tokens(a)) for a in AFFIRM}:
        url = contact_url('', session)
        return _pack("Wonderful! The quickest way to move ahead is our contact form - our team will personally "
                     "guide you and reply within 24 hours.",
                     links=[{'label': '📝 Open Contact Form', 'url': url}, {'label': 'Browse Courses', 'url': '/courses/'}],
                     intent='affirm', contact_url=url)

    content = [t for t in q_tokens if t not in STOPWORDS]
    q_set = set(content) or set(q_tokens)
    scored = sorted(((_score(e, q_norm, content or q_tokens, q_set), e) for e in ENTRIES),
                    key=lambda x: x[0], reverse=True)
    best_score, best = scored[0]
    if best_score < THRESHOLD:
        return fallback_response(message, session)

    suggestions = list(best['suggestions'])
    for s, e in scored[1:4]:
        if s >= THRESHOLD and e['title'] not in suggestions and len(suggestions) < 4:
            suggestions.append(e['title'])
    if not suggestions:
        suggestions = DEFAULT_SUGGESTIONS[:3]
    links = list(best['links'])
    if best['id'] in ('fees', 'enroll', 'proposal', 'projects') and not any('/contact/' in l['url'] for l in links):
        links.append({'label': 'Contact Form', 'url': contact_url(message, session)})
    return _pack(best['answer'], links=links, suggestions=suggestions[:4], intent=best['id'],
                 confidence=min(1.0, best_score / 7), entry_id=best['id'],
                 contact_url=contact_url(message, session))
