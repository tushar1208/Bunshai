import json
import shutil
import tempfile
from pathlib import Path

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase, override_settings
from django.template.loader import get_template
from django.urls import reverse

from .admin import ContactMessageAdmin, SubscriberAdmin, custom_admin_site
from .courses_data import COURSE_CATEGORIES, COURSES
from .models import (
    CareerApplication,
    ChatbotMessage,
    ChatbotSession,
    ChatbotUnanswered,
    ContactMessage,
    CourseEnrollment,
    PageView,
    ProposalRequest,
    SecurityLog,
    ServiceInquiry,
    Subscriber,
    SupportTicket,
    SyllabusDownload,
    WhatsAppAutoReplyRule,
    WhatsAppConversation,
    WhatsAppMessage,
    WhatsAppScheduledMessage,
)
from .views import custom_400, custom_403, custom_404, custom_500


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    GOOGLE_SHEET_ID='',
)
class BunshaiSiteTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmp_media = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.ajax_headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

    def test_all_templates_compile(self):
        tpl_root = Path(__file__).resolve().parent / 'templates'
        for p in sorted(tpl_root.rglob('*.html')):
            rel = p.relative_to(tpl_root).as_posix()
            get_template(rel)

    def test_models_str_and_creation(self):
        cm = ContactMessage.objects.create(
            name='Alice', email='alice@example.com', message='Hello there team!'
        )
        sub = Subscriber.objects.create(email='sub@example.com')
        si = ServiceInquiry.objects.create(
            name='Bob', email='bob@example.com', phone='9876543210',
            service='cloud', message='Need cloud setup'
        )
        pr = ProposalRequest.objects.create(
            name='Carol', email='carol@example.com', phone='9876543210',
            service='web', budget='10k-25k', requirements='Build corporate portal'
        )
        ca = CareerApplication.objects.create(
            name='Dave', email='dave@example.com', phone='9876543210',
            position='dev', cover_letter='Experienced Python/Django developer',
            resume=SimpleUploadedFile('cv.pdf', b'%PDF-1.4\ntest', content_type='application/pdf'),
        )
        pv = PageView.objects.create(page_url='http://testserver/', ip_address='127.0.0.1')
        sl = SecurityLog.objects.create(event_type='spam', ip_address='127.0.0.1', details='test')
        cs = ChatbotSession.objects.create(session_id='sess-1', name='Eve')
        msg = ChatbotMessage.objects.create(session=cs, message='Hi Sharsh', is_user=True)
        tk = SupportTicket.objects.create(
            name='Frank', email='frank@example.com', issue_type='technical',
            priority='high', subject='Login help', description='Need help logging in cleanly'
        )
        ce = CourseEnrollment.objects.create(
            name='Grace', email='grace@example.com', phone='9876543210',
            course_slug=COURSES[0]['slug'], course_title=COURSES[0]['title']
        )
        sd = SyllabusDownload.objects.create(
            name='Heidi', email='heidi@example.com', phone='9876543210',
            course_slug=COURSES[0]['slug'], course_title=COURSES[0]['title']
        )

        self.assertIn('Alice', str(cm))
        self.assertEqual(str(sub), 'sub@example.com')
        self.assertIn('Cloud Services', str(si))
        self.assertIn('Web Development', str(pr))
        self.assertIn('Software Developer', str(ca))
        self.assertIn('http://testserver/', str(pv))
        self.assertIn('Spam Detection', str(sl))
        self.assertIn('Eve', str(cs))
        self.assertIn('User: Hi Sharsh', str(msg))
        self.assertTrue(tk.ticket_number.startswith('BST-'))
        self.assertIn('Grace', str(ce))
        self.assertIn('Heidi', str(sd))

    def test_admin_actions_and_custom_views(self):
        user = User.objects.create_superuser('adminuser', 'admin@example.com', 'StrongPass123!')
        self.client.force_login(user)

        sub = Subscriber.objects.create(email='action@example.com', is_active=False)
        ContactMessage.objects.create(name='Test', email='t@example.com', message='Test message body')

        rf = RequestFactory()
        req = rf.get('/admin/')
        req.user = user
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(req, 'session', 'session')
        setattr(req, '_messages', FallbackStorage(req))

        sub_admin = SubscriberAdmin(Subscriber, admin.site)
        sub_admin.activate_subscribers(req, Subscriber.objects.filter(pk=sub.pk))
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)

        sub_admin.deactivate_subscribers(req, Subscriber.objects.filter(pk=sub.pk))
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)

        txt_resp = sub_admin.export_emails(req, Subscriber.objects.all())
        self.assertEqual(txt_resp.status_code, 200)
        self.assertIn(b'action@example.com', txt_resp.content)

        cm_admin = ContactMessageAdmin(ContactMessage, admin.site)
        csv_resp = cm_admin.export_selected(req, ContactMessage.objects.all())
        self.assertEqual(csv_resp.status_code, 200)
        self.assertIn(b'Test', csv_resp.content)

        analytics_resp = custom_admin_site.analytics_view(req)
        self.assertEqual(analytics_resp.status_code, 200)
        export_resp = custom_admin_site.export_data_view(req)
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn(b'Course Enrollments', export_resp.content)

    def test_all_public_get_routes(self):
        static_routes = [
            '/', '/about/', '/company-profile/', '/md-profile/', '/team/',
            '/services/', '/courses/', '/courses/?category=cloud-computing',
            '/contact/', '/subscribe/', '/career/',
            '/privacy/', '/terms/', '/support/', '/sitemap/',
            '/sitemap.xml', '/robots.txt',
        ]
        service_slugs = [
            'it-consulting', 'digital-marketing', 'cloud-solutions',
            'software-development', 'cybersecurity', 'data-analytics',
        ]
        for path in static_routes + [f'/services/{s}/' for s in service_slugs]:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, f"GET {path} returned {resp.status_code}")

        for cat in COURSE_CATEGORIES:
            resp = self.client.get(f"/courses/?category={cat['slug']}")
            self.assertEqual(resp.status_code, 200)

        for course in COURSES:
            resp = self.client.get(f"/courses/{course['slug']}/")
            self.assertEqual(resp.status_code, 200, f"Course {course['slug']} failed")

        for pdf_url in ('/privacy/download-pdf/', '/terms/download-pdf/'):
            resp = self.client.get(pdf_url)
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.content.startswith(b'%PDF-1.4'))

    def test_contact_captcha_and_submission(self):
        get_resp = self.client.get('/contact/')
        self.assertEqual(get_resp.status_code, 200)
        captcha = get_resp.context['captcha_text']
        self.assertContains(get_resp, captcha)

        bad_resp = self.client.post(
            '/contact/',
            {
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'phone': '9876543210',
                'message': 'Hello, this is a test inquiry message.',
                'captcha': 'WRONG1',
            },
            **self.ajax_headers,
        )
        self.assertEqual(bad_resp.status_code, 400)
        new_captcha = bad_resp.json()['new_captcha']

        ok_resp = self.client.post(
            '/contact/',
            {
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'phone': '9876543210',
                'message': 'Hello, this is a test inquiry message.',
                'captcha': new_captcha,
            },
            **self.ajax_headers,
        )
        self.assertEqual(ok_resp.status_code, 200)
        self.assertTrue(ok_resp.json()['success'])
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_subscribe_proposal_inquiry_career_support(self):
        # Subscribe new + duplicate + invalid
        r1 = self.client.post('/subscribe/submit/', {'email': 'USER@example.com'}, **self.ajax_headers)
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.post('/subscribe/submit/', {'email': 'user@example.com'}, **self.ajax_headers)
        self.assertEqual(r2.status_code, 200)
        self.assertIn('already subscribed', r2.json()['message'].lower())
        r_bad = self.client.post('/subscribe/submit/', {'email': 'not-an-email'}, **self.ajax_headers)
        self.assertEqual(r_bad.status_code, 400)

        # Proposal request
        prop = self.client.post(
            '/proposal-request/',
            {
                'name': 'John Client',
                'email': 'john@client.com',
                'phone': '9876543210',
                'service': 'Cloud Solutions',
                'budget': 'Above 100000',
                'requirements': 'Migrate existing infrastructure cleanly.',
            },
            **self.ajax_headers,
        )
        self.assertEqual(prop.status_code, 200)
        self.assertEqual(ProposalRequest.objects.count(), 1)

        # Service inquiry
        inq = self.client.post(
            '/service-inquiry/',
            {
                'name': 'Sara Lead',
                'email': 'sara@lead.com',
                'phone': '9876543210',
                'service': 'Cybersecurity',
                'message': 'Requesting an enterprise security audit.',
            },
            **self.ajax_headers,
        )
        self.assertEqual(inq.status_code, 200)
        self.assertEqual(ServiceInquiry.objects.count(), 1)

        with override_settings(MEDIA_ROOT=self.tmp_media):
            # Support ticket rejects extensionless file
            bad_file = SimpleUploadedFile('noext', b'hello', content_type='text/plain')
            t_bad = self.client.post(
                '/support/ticket/',
                {
                    'name': 'Tim User',
                    'email': 'tim@user.com',
                    'issue_type': 'bug',
                    'priority': 'high',
                    'subject': 'Error report',
                    'description': 'Detailed bug description exceeding 10 chars.',
                    'attachments': bad_file,
                },
                **self.ajax_headers,
            )
            self.assertEqual(t_bad.status_code, 400)

            good_file = SimpleUploadedFile('log.txt', b'error log details', content_type='text/plain')
            t_ok = self.client.post(
                '/support/ticket/',
                {
                    'name': 'Tim User',
                    'email': 'tim@user.com',
                    'issue_type': 'bug',
                    'priority': 'high',
                    'subject': 'Error report',
                    'description': 'Detailed bug description exceeding 10 chars.',
                    'attachments': good_file,
                },
                **self.ajax_headers,
            )
            self.assertEqual(t_ok.status_code, 200)
            self.assertTrue(t_ok.json()['ticket_number'].startswith('BST-'))

            # Career application
            cv = SimpleUploadedFile('resume.pdf', b'%PDF-1.4\nresume', content_type='application/pdf')
            car = self.client.post(
                '/career/',
                {
                    'name': 'Priya Dev',
                    'email': 'priya@dev.com',
                    'phone': '9876543210',
                    'position': 'Software Developer',
                    'cover_letter': 'Excited to build scalable backend services.',
                    'resume': cv,
                },
                **self.ajax_headers,
            )
            self.assertEqual(car.status_code, 200)
            self.assertEqual(CareerApplication.objects.count(), 1)

    def test_courses_enrollment_and_syllabus_pdf_flow(self):
        course = COURSES[0]
        with override_settings(MEDIA_ROOT=self.tmp_media):
            enroll_resp = self.client.post(
                '/courses/enroll/',
                {
                    'name': 'Learner One',
                    'email': 'learner1@example.com',
                    'phone': '9876543210',
                    'course_slug': course['slug'],
                    'course_title': '',
                    'learning_mode': 'Live Online',
                    'experience_level': 'Beginner',
                    'message': 'Looking forward to joining!',
                },
                **self.ajax_headers,
            )
            self.assertEqual(enroll_resp.status_code, 200)
            self.assertEqual(CourseEnrollment.objects.first().course_title, course['title'])

            # Unauthorized download redirects back to course detail
            unauth = self.client.get(f"/courses/{course['slug']}/syllabus-download/")
            self.assertEqual(unauth.status_code, 302)

            syl_resp = self.client.post(
                '/courses/syllabus-request/',
                {
                    'name': 'Syllabus Seeker',
                    'email': 'seeker@example.com',
                    'phone': '9876543210',
                    'course_slug': course['slug'],
                    'course_title': course['title'],
                    'background': 'Graduate',
                },
                **self.ajax_headers,
            )
            self.assertEqual(syl_resp.status_code, 200)
            dl_url = syl_resp.json()['download_url']
            pdf_resp = self.client.get(dl_url)
            self.assertEqual(pdf_resp.status_code, 200)
            self.assertEqual(pdf_resp['Content-Type'], 'application/pdf')
            self.assertTrue(pdf_resp.content.startswith(b'%PDF-1.4'))

    def test_chatbot_api_and_malformed_json(self):
        # Non-dict JSON payloads should not raise 500
        bad_start = self.client.post(
            '/api/chatbot/start-session/',
            data=json.dumps(['unexpected', 'list']),
            content_type='application/json',
        )
        self.assertEqual(bad_start.status_code, 200)

        bad_send = self.client.post(
            '/api/chatbot/send-message/',
            data=json.dumps(['not', 'a', 'dict']),
            content_type='application/json',
        )
        self.assertEqual(bad_send.status_code, 400)

        start = self.client.post(
            '/api/chatbot/start-session/',
            data=json.dumps({'name': 'Sam', 'email': 'sam@example.com'}),
            content_type='application/json',
        )
        self.assertEqual(start.status_code, 200)
        sid = start.json()['session_id']

        check = self.client.post(
            '/api/chatbot/check-user/',
            data=json.dumps({'email': 'sam@example.com'}),
            content_type='application/json',
        )
        self.assertEqual(check.status_code, 200)
        self.assertTrue(check.json()['is_returning'])

        msg = self.client.post(
            '/api/chatbot/send-message/',
            data=json.dumps({'session_id': sid, 'message': 'What services do you offer?'}),
            content_type='application/json',
        )
        self.assertEqual(msg.status_code, 200)
        self.assertTrue(msg.json()['success'])
        self.assertTrue(msg.json()['response'])

    def test_chatbot_knowledge_and_fallback(self):
        def ask(msg, sid=None, **extra):
            payload = {'message': msg, **({'session_id': sid} if sid else {}), **extra}
            return self.client.post('/api/chatbot/send-message/', data=json.dumps(payload),
                                    content_type='application/json').json()

        first = ask('Tell me about the cloud computing course')
        self.assertTrue(first['success'])
        self.assertFalse(first['fallback'])
        self.assertIn('Cloud', first['response'])
        sid = first['session_id']  # session auto-created when missing

        team = ask('how much experience does the creative director have', sid)
        self.assertIn('4+', team['response'])
        self.assertFalse(team['fallback'])
        md = ask('what is the education of the managing director', sid)
        self.assertIn('MBA', md['response'])
        self.assertIn('B.Tech', md['response'])
        self.assertIn('2025', ask('what is your story', sid)['response'])

        # Unanswerable question -> redirect to the contact form + stored in DB
        miss = ask('who won the football world cup in 2018?', sid, user_info={'email': 'lead@example.com'})
        self.assertTrue(miss['fallback'])
        self.assertIn('/contact/?', miss['contact_url'])
        self.assertIn('source=chatbot', miss['contact_url'])
        self.assertEqual(ChatbotUnanswered.objects.count(), 1)
        self.assertEqual(ChatbotUnanswered.objects.first().email, 'lead@example.com')
        self.assertEqual(ChatbotSession.objects.get(session_id=sid).email, 'lead@example.com')
        self.assertGreaterEqual(ChatbotMessage.objects.filter(session__session_id=sid).count(), 8)

        # Contact form is prefilled via query-string JS; page must load with those params
        self.assertEqual(self.client.get(miss['contact_url']).status_code, 200)

    def test_custom_error_handlers(self):
        rf = RequestFactory()
        req = rf.get('/missing-page-check/')
        for fn, code in ((custom_400, 400), (custom_403, 403), (custom_404, 404), (custom_500, 500)):
            resp = fn(req) if fn is custom_500 else fn(req, Exception('test'))
            self.assertEqual(resp.status_code, code)

        with override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver', '*']):
            resp404 = self.client.get('/nonexistent-test-url-404/')
            self.assertEqual(resp404.status_code, 404)
            self.assertContains(resp404, '404', status_code=404)
            self.assertContains(resp404, '/nonexistent-test-url-404/', status_code=404)

    def test_sync_unsynced_management_command(self):
        call_command('sync_unsynced')

    def test_all_course_and_template_media_assets_exist(self):
        import re
        static_root = Path(__file__).resolve().parent / 'static'
        for cat in COURSE_CATEGORIES:
            asset = static_root / cat['image']
            self.assertTrue(asset.is_file() and asset.stat().st_size > 1000, f"Missing category image {cat['image']}")
        for course in COURSES:
            asset = static_root / course['image']
            self.assertTrue(asset.is_file() and asset.stat().st_size > 1000, f"Missing course image {course['image']}")
            for key in ('why_us', 'comparison_rows', 'build_projects', 'faqs', 'video_chapters'):
                self.assertTrue(course.get(key), f"Course {course['slug']} missing {key}")

        self.assertEqual(len({c['image'] for c in COURSES}), len(COURSES), "Course images must be unique per course")

        tpl_root = Path(__file__).resolve().parent / 'templates'
        for p in sorted(tpl_root.rglob('*.html')):
            txt = p.read_text(encoding='utf-8', errors='ignore')
            for m in re.finditer(r"""\{%\s*static\s+['"]([^'"]+)['"]\s*%\}""", txt):
                ref = m.group(1)
                asset = static_root / ref
                self.assertTrue(asset.is_file() and asset.stat().st_size > 0,
                                f"Missing static asset {ref} in {p.relative_to(tpl_root)}")

    def test_css_theme_consistency_and_csrf_connectivity(self):
        import re
        css_root = Path(__file__).resolve().parent / 'static' / 'css'
        forbidden = {'#7d0022', '#5a0018', '#a73356', '#8b0a2e', '#b91c48', '#fb7185', '#fda4af', '#fecdd3', '#007bff'}
        for p in sorted(css_root.glob('*.css')):
            txt = p.read_text(encoding='utf-8', errors='ignore')
            self.assertEqual(txt.count('{'), txt.count('}'), f"Unbalanced braces in {p.name}")
            found = {h.lower() for h in re.findall(r'#[0-9a-fA-F]{3,6}\b', txt)} & forbidden
            self.assertFalse(found, f"Legacy colors {found} found in {p.name}")

        # Verify every public page sets CSRF cookie or includes csrfmiddlewaretoken
        for path in ('/', '/about/', '/team/', '/services/', '/courses/', '/contact/', '/subscribe/', '/support/', '/career/', '/privacy/', '/terms/'):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200)
            has_csrf = ('csrftoken' in resp.cookies) or (b'csrfmiddlewaretoken' in resp.content)
            self.assertTrue(has_csrf, f"Missing CSRF token/cookie on {path}")

        # Verify every service detail page loads services.css
        for slug in ('it-consulting', 'digital-marketing', 'cloud-solutions', 'cybersecurity', 'data-analytics', 'software-development'):
            resp = self.client.get(f'/services/{slug}/')
            self.assertContains(resp, 'css/services.css')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    GOOGLE_SHEET_ID='',
    WHATSAPP_ENABLED=True,
    WHATSAPP_DRY_RUN=True,
    WHATSAPP_VERIFY_TOKEN='bunshai-verify-secret',
    WHATSAPP_APP_SECRET='bunshai-app-secret',
    WHATSAPP_ADMIN_PHONE='918091401208',
    WHATSAPP_DEFAULT_COUNTRY_CODE='91',
    WHATSAPP_API_KEY='bunshai-wa-api-key',
)
class WhatsAppAutomationTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.ajax_headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        self.api_headers = {'HTTP_X_API_KEY': 'bunshai-wa-api-key'}

    @staticmethod
    def _sign(raw_body: bytes, secret: str = 'bunshai-app-secret') -> str:
        import hashlib
        import hmac
        digest = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
        return f'sha256={digest}'

    @staticmethod
    def _meta_webhook(wa_id: str, phone: str, text: str, name: str = 'Riya') -> bytes:
        return json.dumps({
            'object': 'whatsapp_business_account',
            'entry': [{
                'id': 'waba-1',
                'changes': [{
                    'field': 'messages',
                    'value': {
                        'messaging_product': 'whatsapp',
                        'contacts': [{'profile': {'name': name}, 'wa_id': phone}],
                        'messages': [{
                            'from': phone,
                            'id': wa_id,
                            'timestamp': '1730000000',
                            'type': 'text',
                            'text': {'body': text},
                        }],
                    },
                }],
            }],
        }).encode('utf-8')

    def test_webhook_get_verification(self):
        ok = self.client.get('/whatsapp/webhook/', {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'bunshai-verify-secret',
            'hub.challenge': '99887766',
        })
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.content, b'99887766')

        bad = self.client.get('/whatsapp/webhook/', {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'wrong',
            'hub.challenge': '99887766',
        })
        self.assertEqual(bad.status_code, 403)

    def test_webhook_signature_dedup_and_status_update(self):
        raw = self._meta_webhook('wamid.1001', '919876543210', 'hi', name='Riya')
        bad = self.client.post(
            '/whatsapp/webhook/', data=raw, content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256='sha256=deadbeef',
        )
        self.assertEqual(bad.status_code, 403)

        good = self.client.post(
            '/whatsapp/webhook/', data=raw, content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=self._sign(raw),
        )
        self.assertEqual(good.status_code, 200)
        self.assertEqual(good.json()['processed'], 1)

        # Duplicate delivery is ignored
        dup = self.client.post(
            '/whatsapp/webhook/', data=raw, content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=self._sign(raw),
        )
        self.assertEqual(dup.status_code, 200)
        self.assertEqual(dup.json()['processed'], 0)

        outbound = WhatsAppMessage.objects.filter(direction='outbound').first()
        self.assertIsNotNone(outbound)
        self.assertEqual(outbound.message_type, 'interactive')

        # Status webhook updates stored message status
        status_body = json.dumps({
            'entry': [{'changes': [{'value': {
                'statuses': [{'id': outbound.wa_message_id, 'status': 'delivered'}]
            }}]}]
        }).encode('utf-8')
        st_resp = self.client.post(
            '/whatsapp/webhook/', data=status_body, content_type='application/json',
            HTTP_X_HUB_SIGNATURE_256=self._sign(status_body),
        )
        self.assertEqual(st_resp.status_code, 200)
        outbound.refresh_from_db()
        self.assertEqual(outbound.status, 'delivered')

    def _sim(self, phone: str, text: str, name: str = 'Riya'):
        return self.client.post(
            '/api/whatsapp/simulate/',
            data=json.dumps({'phone': phone, 'text': text, 'contact_name': name}),
            content_type='application/json',
            **self.api_headers,
        )

    def test_interactive_flows_create_real_records(self):
        # 1. Course Enrollment flow
        m = self._sim('9876543210', 'hi')
        self.assertEqual(m.status_code, 200)
        self.assertEqual(m.json()['source'], 'flow:menu')

        self.assertEqual(self._sim('9876543210', '1').json()['source'], 'flow:course_enroll:start')
        self.assertEqual(self._sim('9876543210', 'Cloud Computing').json()['source'], 'flow:course_enroll:ask_contact')
        done_enroll = self._sim('9876543210', 'Riya Sharma, riya@example.com').json()
        self.assertEqual(done_enroll['source'], 'flow:course_enroll:completed')
        self.assertEqual(CourseEnrollment.objects.count(), 1)
        self.assertEqual(CourseEnrollment.objects.first().email, 'riya@example.com')
        self.assertEqual(done_enroll['team_alert']['phone'], '918091401208')

        # 2. Service Inquiry flow
        self.assertEqual(self._sim('9876543211', '2').json()['source'], 'flow:service_inquiry:start')
        self.assertEqual(self._sim('9876543211', 'Cloud Solutions').json()['source'], 'flow:service_inquiry:ask_details')
        done_svc = self._sim('9876543211', 'Need AWS migration for SaaS app lead@saas.io').json()
        self.assertEqual(done_svc['source'], 'flow:service_inquiry:completed')
        self.assertEqual(ServiceInquiry.objects.count(), 1)
        self.assertEqual(ServiceInquiry.objects.first().service, 'cloud')

        # 3. Support Ticket flow
        self.assertEqual(self._sim('9876543212', '3').json()['source'], 'flow:support_ticket:start')
        done_tkt = self._sim('9876543212', 'Cannot access LMS dashboard after reset').json()
        self.assertEqual(done_tkt['source'], 'flow:support_ticket:completed')
        self.assertEqual(SupportTicket.objects.count(), 1)
        self.assertTrue(SupportTicket.objects.first().ticket_number.startswith('BST-'))

    def test_human_handoff_pause_and_resume(self):
        self.assertEqual(self._sim('9876543215', '4', 'Karan').json()['source'], 'flow:human_handoff:start')
        handed = self._sim('9876543215', 'Need enterprise pricing call', 'Karan').json()
        self.assertEqual(handed['source'], 'flow:human_handoff:handed_off')
        self.assertEqual(handed['team_alert']['phone'], '918091401208')
        self.assertTrue(WhatsAppConversation.objects.get(phone='919876543215').human_handoff)

        # Follow-up stays paused
        paused = self._sim('9876543215', 'Are you there?', 'Karan').json()
        self.assertEqual(paused['source'], 'flow:human_handoff_paused')
        self.assertIsNone(paused['reply'])

        # Resume via API
        resumed = self.client.post('/api/whatsapp/conversations/9876543215/resume/', **self.api_headers)
        self.assertEqual(resumed.status_code, 200)
        self.assertTrue(resumed.json()['resumed'])

        # Now Sharsh answers normally
        after = self._sim('9876543215', 'Tell me about the cloud computing course', 'Karan').json()
        self.assertTrue(after['source'].startswith('sharsh:'))
        self.assertIn('Cloud', after['reply']['body'])

    def test_custom_rules_and_sharsh_knowledge_base(self):
        WhatsAppAutoReplyRule.objects.create(
            name='Low Priority', match_type='contains', pattern='discount',
            reply_text='Generic discount info', priority=50,
        )
        WhatsAppAutoReplyRule.objects.create(
            name='VIP Regex', match_type='regex', pattern=r'vip\s+discount',
            reply_text='Hi {name}, VIP scholarship code is BUNSHAI20!', priority=10,
        )

        r_match = self._sim('9876543216', 'Any VIP discount available?', 'Maya').json()
        self.assertEqual(r_match['source'], 'rule:VIP Regex')
        self.assertIn('Hi Maya', r_match['reply']['body'])

        # Sharsh KB answer
        kb_hit = self._sim('9876543216', 'Tell me about the cloud computing course', 'Maya').json()
        self.assertTrue(kb_hit['source'].startswith('sharsh:'))
        self.assertIn('Cloud', kb_hit['reply']['body'])

        # Sharsh fallback logs ChatbotUnanswered
        kb_miss = self._sim('9876543216', 'who won the cricket world cup in 2011?', 'Maya').json()
        self.assertEqual(kb_miss['source'], 'sharsh:fallback')
        self.assertEqual(ChatbotUnanswered.objects.count(), 1)

    def test_website_forms_trigger_whatsapp_notifications(self):
        course = COURSES[0]
        self.client.post('/courses/enroll/', {
            'name': 'Learner WhatsApp',
            'email': 'learner@example.com',
            'phone': '9876543220',
            'course_slug': course['slug'],
            'learning_mode': 'Live Online',
        }, **self.ajax_headers)
        self.assertTrue(WhatsAppMessage.objects.filter(phone='919876543220', direction='outbound').exists())

        self.client.post('/proposal-request/', {
            'name': 'Prop Lead',
            'email': 'prop@example.com',
            'phone': '9876543221',
            'service': 'web',
            'budget': '5k-10k',
            'requirements': 'Build custom web platform for client.',
        }, **self.ajax_headers)
        self.assertTrue(WhatsAppMessage.objects.filter(phone='919876543221', direction='outbound').exists())

        self.client.post('/support/ticket/', {
            'name': 'Ticket User',
            'email': 'tkt@example.com',
            'phone': '9876543222',
            'issue_type': 'technical',
            'priority': 'high',
            'subject': 'API Help',
            'description': 'Need assistance with API keys and access.',
        }, **self.ajax_headers)
        self.assertTrue(WhatsAppMessage.objects.filter(phone='919876543222', direction='outbound').exists())

        self.client.post('/courses/syllabus-request/', {
            'name': 'Syl User',
            'email': 'syl@example.com',
            'phone': '9876543223',
            'course_slug': course['slug'],
            'course_title': course['title'],
            'background': 'Student',
        }, **self.ajax_headers)
        self.assertTrue(WhatsAppMessage.objects.filter(phone='919876543223', direction='outbound').exists())
        # Team alerts sent to WHATSAPP_ADMIN_PHONE
        self.assertGreaterEqual(WhatsAppMessage.objects.filter(phone='918091401208', direction='outbound').count(), 4)

    def test_scheduled_messages_management_command(self):
        from datetime import timedelta
        from django.utils import timezone

        past = timezone.now() - timedelta(minutes=5)
        once_job = WhatsAppScheduledMessage.objects.create(
            name='One-off Reminder', phone='919876543230',
            body='Session starts soon!', scheduled_for=past, recurrence='once',
        )
        daily_job = WhatsAppScheduledMessage.objects.create(
            name='Daily Tip', phone='919876543231',
            body='Daily SQL tip!', scheduled_for=past, recurrence='daily',
        )
        call_command('send_scheduled_whatsapp')

        once_job.refresh_from_db()
        daily_job.refresh_from_db()
        self.assertEqual(once_job.status, 'sent')
        self.assertIsNotNone(once_job.last_run_at)
        self.assertEqual(daily_job.status, 'pending')
        self.assertGreater(daily_job.scheduled_for, past)

    def test_broadcast_auth_and_staff_dashboard(self):
        CourseEnrollment.objects.create(
            name='Aarav', email='aarav@example.com', phone='9876543240',
            course_slug=COURSES[0]['slug'], course_title=COURSES[0]['title'],
        )
        # Unauthorized without API key or staff login
        unauth = self.client.post(
            '/api/whatsapp/broadcast/',
            data=json.dumps({'audience': 'course_enrollments', 'message_template': 'Hi {name}'}),
            content_type='application/json',
        )
        self.assertEqual(unauth.status_code, 401)

        # Audience broadcast with X-API-Key
        ok = self.client.post(
            '/api/whatsapp/broadcast/',
            data=json.dumps({
                'audience': 'course_enrollments',
                'message_template': 'Hi {name}, batch update for {extra}!',
            }),
            content_type='application/json',
            **self.api_headers,
        )
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.json()['sent'], 1)
        self.assertEqual(ok.json()['results'][0]['phone'], '919876543240')

        # CSV upload broadcast
        csv_bytes = b'phone,name\n9876543241,Neha\n9876543242,Vikram\n'
        csv_file = SimpleUploadedFile('leads.csv', csv_bytes, content_type='text/csv')
        csv_resp = self.client.post(
            '/api/whatsapp/broadcast/',
            {'file': csv_file, 'message_template': 'Hello {name} from BunShai!'},
            **self.api_headers,
        )
        self.assertEqual(csv_resp.status_code, 200)
        self.assertEqual(csv_resp.json()['sent'], 2)

        # Staff dashboard access
        admin_user = User.objects.create_superuser('waadmin', 'wa@example.com', 'StrongPass123!')
        self.client.force_login(admin_user)
        dash = self.client.get('/whatsapp/dashboard/')
        self.assertEqual(dash.status_code, 200)
        self.assertContains(dash, 'BunShai TECHNOHUB')


class SiteMetricsAndUiRegressionTests(TestCase):
    def test_site_metrics_defaults_and_admin_update(self):
        from main.models import SiteMetrics

        metrics = SiteMetrics.get_solo()
        self.assertEqual(
            (
                metrics.projects_delivered,
                metrics.happy_clients,
                metrics.countries_served,
                metrics.years_experience,
            ),
            (46, 58, 10, 4),
        )

        home_resp = self.client.get('/')
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, 'data-target="46">46+</h3>')
        self.assertContains(home_resp, 'data-target="58">58+</h3>')
        self.assertContains(home_resp, 'data-target="10">10+</h3>')
        self.assertContains(home_resp, 'data-target="4">4+</h3>')

        # Updating SiteMetrics in DB updates rendered pages without code edits
        metrics.projects_delivered = 72
        metrics.happy_clients = 89
        metrics.countries_served = 14
        metrics.years_experience = 6
        metrics.save()

        updated_home = self.client.get('/')
        self.assertContains(updated_home, 'data-target="72">72+</h3>')
        self.assertContains(updated_home, 'data-target="89">89+</h3>')
        self.assertContains(updated_home, 'data-target="14">14+</h3>')
        self.assertContains(updated_home, 'data-target="6">6+</h3>')

        about_resp = self.client.get('/about/')
        self.assertContains(about_resp, '<h3>72+</h3>')
        self.assertContains(about_resp, '<h3>89+</h3>')
        self.assertContains(about_resp, '<h3>14+</h3>')

    def test_footer_copyright_and_inspect_protection_script(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'BunShai TECHNOHUB®. All rights reserved.')
        self.assertNotContains(resp, 'Crafted with')
        self.assertContains(resp, 'js/security.js')
        sec_resp = self.client.get('/static/js/security.js')
        self.assertEqual(sec_resp.status_code, 200)
        self.assertContains(sec_resp, 'contextmenu')

    def test_seo_links_placeholders_and_real_admin_activity(self):
        from django.template.loader import render_to_string

        home = self.client.get('/')
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, '<link rel="canonical"')
        self.assertContains(home, 'http://testserver/static/images/Logo1.png')
        self.assertContains(home, 'application/ld+json')
        self.assertContains(home, '/services/software-development/')
        self.assertContains(home, '/services/cloud-solutions/')
        self.assertContains(home, '/services/cybersecurity/')
        self.assertNotContains(home, 'randomuser.me')

        for path in ('/', '/about/', '/contact/', '/md-profile/', '/subscribe/'):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200)
            self.assertNotContains(resp, 'https://twitter.com"')
            self.assertNotContains(resp, 'https://instagram.com"')
            self.assertNotContains(resp, 'https://calendly.com')
            self.assertNotContains(resp, 'careers@bunshai.com')

        about = self.client.get('/about/')
        self.assertNotContains(about, 'href="#contact"')

        # Email templates should point to configured SITE_URL & live inbox
        conf_html = render_to_string(
            'emails/contact_confirmation.html',
            {
                'subscriber': {'email': 'lead@example.com'},
                'verification_token': 'tok123456',
                'site_name': 'BunShai TECHNOHUB',
                'site_url': 'https://bunshai-technohub.onrender.com',
                'support_email': 'team.bunshailogicloop@gmail.com',
            },
        )
        self.assertNotIn('https://bunshai.com/blog', conf_html)
        self.assertIn('https://bunshai-technohub.onrender.com/courses/', conf_html)

        # Custom admin dashboard shows real DB activity rather than dummy john@example.com
        ContactMessage.objects.create(
            name='Real Lead', email='reallead@example.com', message='Interested in cloud migration.'
        )
        superuser = User.objects.create_superuser('dashadmin', 'dash@example.com', 'StrongPass123!')
        rf = RequestFactory()
        req = rf.get('/customadmin/dashboard/')
        req.user = superuser
        dash = custom_admin_site.dashboard_view(req)
        self.assertEqual(dash.status_code, 200)
        self.assertContains(dash, 'Real Lead')
        self.assertNotContains(dash, 'john@example.com')


