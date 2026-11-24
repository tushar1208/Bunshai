"""Knowledge base for the Sharsh assistant.

Everything Sharsh can answer is derived from information that is published on the
website: company, leadership team, services, courses (generated from
``courses_data``), careers, support, legal pages and contact details.
Each entry is a dict:

    id, title, keywords (phrases/words), answer, links [(label, url)], suggestions [str]
"""
from django.conf import settings

from .courses_data import COURSE_CATEGORIES, COURSES

# ------------------------------------------------------------------ helpers
PHONE = getattr(settings, 'SITE_PHONE', '+91 8091401208')
EMAIL = getattr(settings, 'SITE_EMAIL', 'team.bunshailogicloop@gmail.com')
HOURS = (f"{getattr(settings, 'BUSINESS_DAYS', 'Monday to Friday')}, "
         f"{getattr(settings, 'BUSINESS_HOURS_START', '9:00 AM')} - "
         f"{getattr(settings, 'BUSINESS_HOURS_END', '6:00 PM')} IST")
WHATSAPP = 'https://wa.me/918091401208'

L_CONTACT = ('Contact Form', '/contact/')
L_COURSES = ('All Courses', '/courses/')
L_SERVICES = ('Our Services', '/services/')
L_ABOUT = ('About Us', '/about/')
L_TEAM = ('Our Team', '/team/')
L_MD = ('MD Profile', '/md-profile/')
L_CAREER = ('Careers', '/career/')
L_SUPPORT = ('Support Center', '/support/')


def _entry(id_, title, keywords, answer, links=(), suggestions=()):
    return {
        'id': id_, 'title': title, 'keywords': list(keywords), 'answer': answer,
        'links': [{'label': a, 'url': b} for a, b in links],
        'suggestions': list(suggestions),
    }


# --------------------------------------------------------------- static data
STATIC_ENTRIES = [
    _entry(
        'company', 'About BunShai TECHNOHUB',
        ['about company', 'about bunshai', 'who are you', 'what is bunshai', 'tell me about', 'company',
         'bunshai technohub', 'overview', 'what do you do', 'organisation', 'organization', 'firm'],
        "BunShai TECHNOHUB is a technology company that delivers IT consulting, software development, cloud, "
        "cybersecurity, data analytics and digital marketing services, and also runs career-focused "
        "mentorship programs (courses) in Digital Marketing, Data Science & Analytics, AI, Full Stack with AI "
        "Engineering, Cyber Security and Cloud Computing.\n\n"
        "We started in 2025 and are a remote-first team serving clients worldwide - 50+ projects delivered and "
        "30+ happy clients so far.",
        [L_ABOUT, ('Company Profile', '/company-profile/')],
        ['Tell me about your story', 'Who leads the company?', 'What services do you offer?']),
    _entry(
        'story', 'Our story 2025 - 2027',
        ['story', 'history', 'founded', 'founding', 'started', 'since when', 'journey', 'timeline', 'when was',
         'established', 'milestones', 'roadmap', '2025', '2026', '2027', 'year'],
        "Our story:\n"
        "• 2025 - The Beginning: BunShai TECHNOHUB was founded to provide affordable, high-quality technology "
        "solutions and skill-building programs, starting with a small team of passionate engineers and creatives.\n"
        "• 2026 - Growth & Learning: we expanded our services, launched mentorship programs (14 programs across 6 "
        "career tracks) and began serving international clients.\n"
        "• 2027 - Vision Ahead: scaling AI-driven products, bigger mentorship cohorts and a wider global presence.",
        [L_ABOUT],
        ['Who leads the company?', 'Show me your courses']),
    _entry(
        'mission', 'Mission, vision & values',
        ['mission', 'vision', 'values', 'core values', 'goal', 'purpose', 'philosophy'],
        "Mission: deliver reliable, innovative and affordable technology solutions and career-ready training.\n"
        "Vision: to be a trusted global technology partner for digital transformation.\n"
        "Core values: Innovation, Integrity, Collaboration and Excellence.",
        [L_ABOUT, ('Company Profile', '/company-profile/')]),
    _entry(
        'team', 'Leadership team',
        ['team', 'our team', 'leadership', 'leaders', 'directors', 'management', 'staff', 'who works', 'people',
         'experience of team', 'team members', 'who leads', 'who runs'],
        "Our leadership team:\n"
        "• Managing Director - 4+ years of experience (MBA & B.Tech), leads vision, strategy and partnerships.\n"
        "• Technical Director - 3+ years of experience, owns architecture, cloud and security standards.\n"
        "• Creative Director - 4+ years of experience, leads brand, UI/UX and digital creative.\n"
        "• Development Team Head - 3+ years of experience, leads our engineers and delivery quality.\n\n"
        "See the full team page for responsibilities and expertise of each leader.",
        [L_TEAM, L_MD],
        ['Tell me about the Managing Director', 'How can I join your team?']),
    _entry(
        'md', 'Managing Director',
        ['managing director', 'md', 'founder', 'ceo', 'owner', 'md profile', 'director profile', 'who is the md',
         'education of md', 'md education', 'md experience', 'mba', 'btech', 'b.tech', 'keynote', 'speaker',
         'certifications', 'day in the life', 'daily routine'],
        "Our Managing Director has 4+ years of professional experience and holds two degrees - an MBA and a "
        "B.Tech - along with several professional certifications (cloud, project management and agile). "
        "He has been a Keynote Speaker at an International Conference and is hands-on in strategy, client "
        "relationships and mentoring.\n\nThe MD profile page also has a realistic 'A Day in the Life' timeline.",
        [L_MD, L_TEAM],
        ['Who else is on the leadership team?']),
    _entry(
        'tech_director', 'Technical Director',
        ['technical director', 'tech director', 'cto', 'chief technology', 'architecture', 'technical lead'],
        "Our Technical Director has 3+ years of experience and is responsible for solution architecture, cloud & "
        "DevOps standards, security practices and technology choices across all client projects.",
        [L_TEAM]),
    _entry(
        'creative_director', 'Creative Director',
        ['creative director', 'designer', 'design lead', 'ui ux', 'brand design', 'design head'],
        "Our Creative Director has 4+ years of experience and leads brand identity, UI/UX design and digital "
        "creative so every product feels intuitive and beautiful.",
        [L_TEAM]),
    _entry(
        'dev_head', 'Development Team Head',
        ['development team head', 'dev team head', 'head of development', 'engineering head', 'developers',
         'development team', 'engineers', 'programmers'],
        "Our Development Team Head has 3+ years of experience and leads our developers, engineers and "
        "architects - code quality, delivery timelines and mentoring juniors.",
        [L_TEAM]),
    _entry(
        'services', 'Services overview',
        ['services', 'service', 'what do you offer', 'offerings', 'solutions', 'what can you do', 'capabilities',
         'work with', 'it services', 'business services'],
        "We offer six core services:\n"
        "• IT Consulting\n• Software Development (web & mobile)\n• Cloud Solutions\n• Cybersecurity\n"
        "• Data Analytics & AI\n• Digital Marketing\n\nTell me which one you want to know more about!",
        [L_SERVICES],
        ['IT Consulting', 'Software development', 'Cloud solutions', 'Cybersecurity services']),
    _entry(
        'svc_it', 'IT Consulting',
        ['it consulting', 'consulting', 'digital transformation', 'technology strategy', 'consultancy'],
        "IT Consulting: technology strategy, digital-transformation roadmaps, architecture reviews and vendor "
        "selection to help your business use technology for growth.",
        [('IT Consulting', '/services/it-consulting/')]),
    _entry(
        'svc_dev', 'Software Development',
        ['software development', 'web development', 'website', 'web app', 'mobile app', 'app development',
         'custom software', 'application development', 'ecommerce', 'api development', 'build an app',
         'build a website'],
        "Software Development: custom web applications, mobile apps (iOS & Android), e-commerce platforms, "
        "APIs and integrations using modern stacks like Django, React, Node.js, Flutter and React Native.",
        [('Software Development', '/services/software-development/'), L_CONTACT]),
    _entry(
        'svc_cloud', 'Cloud Solutions',
        ['cloud solutions', 'cloud migration', 'aws services', 'azure services', 'devops services',
         'cloud services', 'infrastructure'],
        "Cloud Solutions: cloud migration, AWS/Azure/GCP architecture, DevOps automation, cost optimisation and "
        "secure infrastructure.",
        [('Cloud Solutions', '/services/cloud-solutions/')]),
    _entry(
        'svc_cyber', 'Cybersecurity services',
        ['cybersecurity services', 'security audit', 'penetration testing service', 'vapt', 'security services',
         'protect my business', 'security assessment'],
        "Cybersecurity services: vulnerability assessments, penetration testing (VAPT), security monitoring, "
        "incident response and compliance audits.",
        [('Cybersecurity', '/services/cybersecurity/')]),
    _entry(
        'svc_data', 'Data Analytics services',
        ['data analytics service', 'business intelligence', 'bi dashboard', 'predictive analytics',
         'machine learning service', 'ai solutions', 'ai service', 'chatbot development', 'data services'],
        "Data Analytics & AI: dashboards, business intelligence, predictive analytics, machine-learning models "
        "and AI solutions such as chatbots and automation.",
        [('Data Analytics', '/services/data-analytics/')]),
    _entry(
        'svc_marketing', 'Digital Marketing services',
        ['digital marketing service', 'seo service', 'social media marketing', 'ppc', 'content marketing',
         'brand strategy', 'online advertising', 'marketing services'],
        "Digital Marketing services: SEO, social media management, PPC advertising, content marketing and brand "
        "strategy to grow your online presence.",
        [('Digital Marketing', '/services/digital-marketing/')]),
    _entry(
        'courses_overview', 'Courses overview',
        ['courses', 'course', 'programs', 'program', 'mentorship', 'training', 'learn', 'bootcamp', 'syllabus',
         'curriculum', 'classes', 'certification program', 'upskill', 'which courses'],
        "We run career-focused mentorship programs in 6 tracks (14 programs, 16-32 weeks each):\n" +
        "\n".join(f"• {c['name']}" for c in COURSE_CATEGORIES) +
        "\n\nEvery program has live mentor-led sessions, real projects and a capstone. You can download any "
        "course syllabus (PDF) from its page.",
        [L_COURSES],
        [c['name'] for c in COURSE_CATEGORIES][:4]),
    _entry(
        'syllabus', 'Download syllabus',
        ['syllabus download', 'download syllabus', 'brochure', 'course syllabus', 'course details pdf',
         'get syllabus', 'curriculum pdf'],
        "To download a syllabus: open any course page → click 'View / Download Syllabus' → fill in your name, "
        "email and phone → the PDF downloads instantly.",
        [L_COURSES]),
    _entry(
        'enroll', 'Enrol in a course',
        ['enroll', 'enrol', 'enrollment', 'admission', 'join course', 'register', 'apply for course',
         'how to join', 'batch', 'batches', 'start date', 'next batch', 'seat'],
        "To enrol: open the course page and click 'Enroll Now', fill the short form and our academic counsellor "
        "will contact you within 24 hours with batch dates and next steps.",
        [L_COURSES],
        ['Show me your courses']),
    _entry(
        'fees', 'Fees & pricing',
        ['fee', 'fees', 'price', 'pricing', 'cost', 'how much', 'charges', 'payment', 'emi', 'discount',
         'scholarship', 'budget', 'quote', 'quotation', 'rates'],
        "Course fees and project prices depend on the program/cohort and the scope of your requirements, so "
        "our team shares exact details personally. For courses, enrol or request a callback and a counsellor "
        "will share fee, EMI and discount options. For projects, request a free proposal.",
        [L_CONTACT, L_COURSES],
        ['I want a free proposal', 'How do I enroll?']),
    _entry(
        'contact', 'Contact details',
        ['contact', 'phone', 'call', 'email', 'mail', 'whatsapp', 'reach', 'talk to', 'speak to', 'address',
         'location', 'office', 'where are you', 'number', 'human', 'agent', 'support team'],
        f"You can reach us at:\n📞 {PHONE}\n📧 {EMAIL}\n💬 WhatsApp: {WHATSAPP}\n"
        f"🕘 Business hours: {HOURS}\n📍 We are a remote-first company serving clients worldwide.\n\n"
        "Or simply fill in our contact form and we'll respond within 24 hours.",
        [L_CONTACT, ('WhatsApp', WHATSAPP)]),
    _entry(
        'hours', 'Business hours',
        ['hours', 'timing', 'timings', 'open', 'working hours', 'business hours', 'available', 'when are you'],
        f"Our business hours are {HOURS}. Our support desk handles urgent tickets around the clock and the "
        "chatbot is available 24/7.",
        [L_SUPPORT]),
    _entry(
        'careers', 'Careers & jobs',
        ['career', 'careers', 'job', 'jobs', 'hiring', 'vacancy', 'vacancies', 'opening', 'openings', 'intern',
         'internship', 'apply for job', 'work with you', 'join your team', 'resume', 'recruitment', 'position'],
        "We're always looking for talented people. Open positions include Software Developer, UI/UX Designer, "
        "DevOps Engineer, Data Scientist, Security Analyst, Project Manager, Marketing Specialist, Sales "
        "Executive and Interns. Apply with your resume (PDF/DOC/DOCX, up to 5 MB) on the careers page.",
        [L_CAREER]),
    _entry(
        'support', 'Support & tickets',
        ['support', 'help', 'ticket', 'issue', 'problem', 'complaint', 'raise a ticket', 'customer support',
         'faq', 'knowledge base', 'technical support', 'not working', 'bug', 'error'],
        "Our Support Center lets you raise a ticket (priority-based, answered within 2 hours), browse FAQs, "
        "and reach live chat, phone or WhatsApp support.",
        [L_SUPPORT]),
    _entry(
        'privacy', 'Privacy policy',
        ['privacy', 'privacy policy', 'data protection', 'gdpr', 'personal data', 'my data', 'cookies',
         'data safe', 'data security'],
        "We take privacy seriously. Our Privacy Policy explains what data we collect, how it is used and "
        "protected, and your rights. You can read it online or download it as a PDF.",
        [('Privacy Policy', '/privacy/'), ('Download PDF', '/privacy/download-pdf/')]),
    _entry(
        'terms', 'Terms & conditions',
        ['terms', 'terms and conditions', 'conditions', 'refund', 'refund policy', 'cancellation', 'legal',
         'agreement', 'tnc'],
        "Our Terms & Conditions cover service usage, payments, intellectual property, cancellations and "
        "liability. Read online or download the PDF.",
        [('Terms & Conditions', '/terms/'), ('Download PDF', '/terms/download-pdf/')]),
    _entry(
        'subscribe', 'Newsletter',
        ['newsletter', 'subscribe', 'updates', 'blog', 'news', 'unsubscribe'],
        "Subscribe to our newsletter for tech insights, course announcements and offers - use the subscribe "
        "box in the footer or visit the subscribe page.",
        [('Subscribe', '/subscribe/')]),
    _entry(
        'proposal', 'Free proposal',
        ['proposal', 'free proposal', 'free consultation', 'consultation', 'estimate', 'project requirement',
         'schedule a call', 'book a call', 'meeting', 'project discussion', 'hire you'],
        "Great! You can request a free customised proposal - click 'Get Proposal' at the top of the website, "
        "share your requirement and budget and we'll get back to you within 24 hours.",
        [L_CONTACT, L_SERVICES]),
    _entry(
        'projects', 'Projects & portfolio',
        ['projects', 'portfolio', 'case study', 'case studies', 'clients', 'previous work', 'past work',
         'experience', 'success stories', 'testimonials', 'company projects', 'work done'],
        "We have delivered 50+ projects for 30+ clients across web & mobile apps, cloud migrations, cybersecurity "
        "audits, data-analytics dashboards and digital-marketing campaigns. Visit the Company Profile and About "
        "pages for highlights and client testimonials. For specific case studies relevant to your industry, our "
        "team can share details directly.",
        [('Company Profile', '/company-profile/'), L_ABOUT, L_CONTACT]),
    _entry(
        'process', 'How we work',
        ['process', 'how we work', 'methodology', 'workflow', 'engagement model', 'how it works', 'steps',
         'phases', 'timeline of project', 'delivery'],
        "How we work: 1) Discovery & Analysis → 2) Strategy & Planning → 3) Design & Development → 4) Testing & "
        "Deployment → 5) Support & Maintenance. Engagement models: Project-Based, Dedicated Team, and Time & "
        "Material.",
        [L_ABOUT]),
    _entry(
        'tech', 'Technologies',
        ['technology', 'technologies', 'tech stack', 'stack', 'languages', 'frameworks', 'tools', 'react',
         'django', 'python', 'node', 'flutter', 'angular', 'database', 'postgresql', 'mysql', 'mongodb'],
        "Our stack covers Frontend (React, Angular, Vue), Backend (Django, Node.js, Python, Java), Mobile "
        "(Flutter, React Native), Cloud & DevOps (AWS, Azure, GCP, Docker, Kubernetes), Databases (PostgreSQL, "
        "MySQL, MongoDB) and AI/ML (TensorFlow, PyTorch, LLM tooling).",
        [L_ABOUT, L_SERVICES]),
    _entry(
        'sitemap', 'Find a page',
        ['sitemap', 'site map', 'pages', 'find page', 'navigation', 'where can i find', 'all pages'],
        "You can find every page of the website on the Sitemap page.",
        [('Sitemap', '/sitemap/')]),
]

# -------------------------------------------------------- dynamic (courses)
_STOP = {'with', 'and', 'the', 'for', 'program', 'mentorship', 'in', 'of', 'a', 'to', 'professional',
         'certification', 'bootcamp'}


def _course_entries():
    entries = []
    for cat in COURSE_CATEGORIES:
        members = [c for c in COURSES if c['category'] == cat['slug']]
        entries.append(_entry(
            f"cat_{cat['slug']}", cat['name'],
            [cat['name'].lower(), cat['slug'].replace('-', ' ')] +
            [w for w in cat['name'].lower().replace('&', ' ').split() if w not in _STOP and len(w) > 3],
            f"{cat['name']} - {cat['description']}\n\nPrograms:\n" +
            "\n".join(f"• {c['title']} ({c['duration']})" for c in members),
            [{'label': c['short_title'], 'url': f"/courses/{c['slug']}/"} for c in members][:3] and
            [(c['short_title'], f"/courses/{c['slug']}/") for c in members][:3] +
            [('Browse track', f"/courses/?category={cat['slug']}")],
            [c['short_title'] for c in members][:3]))
    for c in COURSES:
        words = {w for w in c['title'].lower().replace('&', ' ').replace('(', ' ').replace(')', ' ').split()
                 if w not in _STOP and len(w) > 2}
        kws = [c['title'].lower(), c['short_title'].lower(), c['slug'].replace('-', ' ')] + \
              [t.lower() for t in c.get('tools', [])] + [r.lower() for r in c.get('roles', [])]
        kws += sorted(words)
        modules = "\n".join(f"  {i}. {m['milestone'].split(': ', 1)[-1]} ({m['duration']})"
                            for i, m in enumerate(c.get('curriculum', []), 1))
        answer = (
            f"{c['title']}\n"
            f"⏱ Duration: {c['duration']} | {c['hours']} | Mode: {c['mode']}\n"
            f"🎯 Level: {c['level']} | {c['projects']}\n\n"
            f"{c['summary']}\n\n"
            f"Key highlights:\n" + "\n".join(f"• {h}" for h in c.get('highlights', [])) +
            f"\n\nTools you'll learn: {', '.join(c.get('tools', []))}\n"
            f"Career roles: {', '.join(c.get('roles', []))}\n\n"
            f"Syllabus modules:\n{modules}\n\n"
            f"Capstone: {c['capstone']}")
        entries.append(_entry(
            f"course_{c['slug']}", c['title'], kws, answer,
            [('View Course & Syllabus', f"/courses/{c['slug']}/"), ('Browse all', '/courses/')],
            ['How do I enroll?', 'What are the fees?']))
    return entries


# ------------------------------------------------- conversational intents
SMALLTALK = {
    'greeting': {
        'patterns': ['hi', 'hii', 'hello', 'hey', 'hola', 'namaste', 'good morning', 'good afternoon',
                     'good evening', 'howdy', 'yo'],
        'reply': "Hello! 👋 I'm Sharsh, the BunShai TECHNOHUB assistant. I can answer anything about our "
                 "courses, services, team, careers and company. What would you like to know?",
    },
    'thanks': {
        'patterns': ['thanks', 'thank you', 'thx', 'ty', 'thank u', 'great thanks', 'awesome', 'perfect',
                     'nice', 'cool'],
        'reply': "You're welcome! 😊 Anything else I can help you with?",
    },
    'bye': {
        'patterns': ['bye', 'goodbye', 'see you', 'good night', 'take care', 'see ya'],
        'reply': "Thanks for chatting with me! Have a wonderful day - I'm here 24/7 whenever you need me. 👋",
    },
    'identity': {
        'patterns': ['who are you', 'what are you', 'your name', 'are you a bot', 'are you human',
                     'are you ai', 'what is sharsh', 'who is sharsh'],
        'reply': "I'm Sharsh, the AI assistant of BunShai TECHNOHUB. I answer questions using the information "
                 "published on this website - and if I can't help, I'll connect you with our human team.",
    },
    'howareyou': {
        'patterns': ['how are you', 'how r u', 'whats up', "what's up", 'how do you do'],
        'reply': "I'm doing great, thanks for asking! How can I help you today?",
    },
}

DEFAULT_SUGGESTIONS = ['Show me your courses', 'What services do you offer?', 'Who leads the company?',
                       'How can I contact you?']


def all_entries():
    return STATIC_ENTRIES + _course_entries()


ENTRIES = all_entries()
ENTRIES_BY_ID = {e['id']: e for e in ENTRIES}
