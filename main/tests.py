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

        tpl_root = Path(__file__).resolve().parent / 'templates'
        for p in sorted(tpl_root.rglob('*.html')):
            txt = p.read_text(encoding='utf-8', errors='ignore')
            for m in re.finditer(r"""\{%\s*static\s+['"]([^'"]+)['"]\s*%\}""", txt):
                ref = m.group(1)
                asset = static_root / ref
                self.assertTrue(asset.is_file() and asset.stat().st_size > 0,
                                f"Missing static asset {ref} in {p.relative_to(tpl_root)}")
