"""Pure-Python PDF 1.4 syllabus generator with zero external dependencies."""
import textwrap


def _pdf_safe(text):
    """Normalize text to WinAnsi-safe ASCII for standard Helvetica PDF fonts."""
    replacements = {
        '–': '-', '—': '-', '•': '*', '·': '|', '’': "'", '‘': "'",
        '“': '"', '”': '"', '→': '->', '✓': '[x]', '₹': 'Rs.',
        '&amp;': '&', '\u00a0': ' ',
    }
    s = str(text or '')
    for k, v in replacements.items():
        s = s.replace(k, v)
    s = s.encode('ascii', 'replace').decode('ascii')
    return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


class _PDFBuilder:
    WIDTH = 595
    HEIGHT = 842
    LEFT = 48
    RIGHT = 547
    BOTTOM = 54

    def __init__(self, header_title):
        self.header_title = header_title
        self.pages = []
        self.cmds = []
        self.y = 0
        self.new_page(first=True)

    def new_page(self, first=False):
        if self.cmds:
            self.pages.append('\n'.join(self.cmds))
        self.cmds = []
        if first:
            # Dark navy/crimson banner
            self.cmds.append('0.043 0.067 0.125 rg 0 742 595 100 re f')
            self.cmds.append('0.545 0.039 0.180 rg 0 738 595 4 re f')
            self.cmds.append(
                f'BT /F2 11 Tf 0.984 0.443 0.522 rg {self.LEFT} 808 Td '
                f'(BUNSHAI TECHNOHUB | MENTORSHIP PROGRAM SYLLABUS) Tj ET'
            )
            self.cmds.append(
                f'BT /F2 17 Tf 1 1 1 rg {self.LEFT} 782 Td '
                f'({_pdf_safe(self.header_title[:68])}) Tj ET'
            )
            self.cmds.append(
                f'BT /F1 9 Tf 0.88 0.90 0.94 rg {self.LEFT} 760 Td '
                f'(Live Mentor-Led Cohort  |  Capstone Projects  |  Career & Placement Support) Tj ET'
            )
            self.y = 710
        else:
            self.cmds.append('0.545 0.039 0.180 rg 0 834 595 8 re f')
            self.cmds.append(
                f'BT /F1 8.5 Tf 0.45 0.50 0.58 rg {self.LEFT} 814 Td '
                f'({_pdf_safe(self.header_title[:75])} - Syllabus) Tj ET'
            )
            self.y = 788

    def ensure_space(self, needed):
        if self.y - needed < self.BOTTOM:
            self.new_page(first=False)

    def section(self, title):
        self.ensure_space(34)
        self.y -= 8
        self.cmds.append(
            f'0.545 0.039 0.180 rg {self.LEFT} {self.y - 4} 180 2 re f'
        )
        self.cmds.append(
            f'BT /F2 12.5 Tf 0.545 0.039 0.180 rg {self.LEFT} {self.y + 4} Td '
            f'({_pdf_safe(title)}) Tj ET'
        )
        self.y -= 20

    def paragraph(self, text, font='F1', size=10, color='0.15 0.20 0.28', width=86, indent=0, leading=14):
        for line in textwrap.wrap(str(text), width=width) or ['']:
            self.ensure_space(leading + 2)
            self.cmds.append(
                f'BT /{font} {size} Tf {color} rg {self.LEFT + indent} {self.y} Td '
                f'({_pdf_safe(line)}) Tj ET'
            )
            self.y -= leading

    def bullet(self, text, indent=10, width=82):
        lines = textwrap.wrap(str(text), width=width) or ['']
        for idx, line in enumerate(lines):
            self.ensure_space(14)
            prefix = '* ' if idx == 0 else '  '
            self.cmds.append(
                f'BT /F1 9.5 Tf 0.15 0.20 0.28 rg {self.LEFT + indent} {self.y} Td '
                f'({_pdf_safe(prefix + line)}) Tj ET'
            )
            self.y -= 13.5

    def build(self):
        if self.cmds:
            self.pages.append('\n'.join(self.cmds))

        # Add page footers
        total = len(self.pages)
        for i in range(total):
            footer = (
                f'BT /F1 8 Tf 0.45 0.50 0.58 rg {self.LEFT} 28 Td '
                f'(BunShai TECHNOHUB  |  team.bunshailogicloop@gmail.com  |  +91 8091401208) Tj ET\n'
                f'BT /F1 8 Tf 0.45 0.50 0.58 rg 495 28 Td (Page {i + 1} of {total}) Tj ET'
            )
            self.pages[i] = self.pages[i] + '\n' + footer

        objects = []
        # 1: Catalog, 2: Pages, 3: F1 Helvetica, 4: F2 Helvetica-Bold
        objects.append('<< /Type /Catalog /Pages 2 0 R >>')
        page_refs = []
        # Reserve slot 2 for Pages
        objects.append('')
        objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
        objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')

        for content in self.pages:
            stream_bytes = content.encode('latin-1', 'replace')
            content_id = len(objects) + 1
            objects.append(
                f'<< /Length {len(stream_bytes)} >>\nstream\n{content}\nendstream'
            )
            page_id = len(objects) + 1
            page_refs.append(f'{page_id} 0 R')
            objects.append(
                f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.WIDTH} {self.HEIGHT}] '
                f'/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_id} 0 R >>'
            )

        objects[1] = f'<< /Type /Pages /Kids [{" ".join(page_refs)}] /Count {len(page_refs)} >>'

        out = bytearray(b'%PDF-1.4\n')
        offsets = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(len(out))
            out.extend(f'{idx} 0 obj\n{obj}\nendobj\n'.encode('latin-1', 'replace'))

        xref_pos = len(out)
        out.extend(f'xref\n0 {len(objects) + 1}\n'.encode('ascii'))
        out.extend(b'0000000000 65535 f \n')
        for off in offsets[1:]:
            out.extend(f'{off:010d} 00000 n \n'.encode('ascii'))
        out.extend(
            f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'
            f'startxref\n{xref_pos}\n%%EOF\n'.encode('ascii')
        )
        return bytes(out)


def generate_course_syllabus_pdf(course):
    """Generate a structured multi-page PDF syllabus for a course dictionary."""
    pdf = _PDFBuilder(course['title'])

    pdf.section('Program Overview')
    pdf.paragraph(
        f"Category: {course['category_name']}   |   Duration: {course['duration']}   |   "
        f"Live Hours: {course['hours']}   |   Projects: {course['projects']}",
        font='F2', size=9.5, color='0.06 0.09 0.16'
    )
    pdf.paragraph(f"Level: {course['level']}   |   Mode: {course['mode']}", font='F1', size=9.5)
    pdf.y -= 4
    pdf.paragraph(course['summary'])

    pdf.section('Key Program Highlights')
    for item in course.get('highlights', []):
        pdf.bullet(item)

    pdf.section('Detailed Curriculum & Milestones')
    for idx, mod in enumerate(course.get('curriculum', []), start=1):
        pdf.ensure_space(46)
        pdf.paragraph(
            f"{idx}. {mod['milestone']} ({mod['duration']})",
            font='F2', size=10.5, color='0.06 0.09 0.16', leading=15
        )
        for topic in mod.get('topics', []):
            pdf.bullet(topic, indent=14, width=80)
        pdf.y -= 4

    if course.get('capstone'):
        pdf.section('Capstone Project')
        pdf.paragraph(course['capstone'])

    pdf.section('Tools & Technologies Covered')
    pdf.paragraph('  |  '.join(course.get('tools', [])))

    pdf.section('Target Career Roles')
    pdf.paragraph('  |  '.join(course.get('roles', [])))

    pdf.section('Admissions & Academic Counseling')
    pdf.paragraph('Website: https://bunshaitechnohub.com/courses/')
    pdf.paragraph('Email: team.bunshailogicloop@gmail.com   |   Phone / WhatsApp: +91 8091401208')

    return pdf.build()


def generate_legal_pdf(title, subtitle, sections):
    """Generate a clean multi-page legal PDF (Privacy Policy / Terms & Conditions)."""
    pdf = _PDFBuilder(title)
    pdf.paragraph(subtitle, font='F2', size=9.5, color='0.06 0.09 0.16')
    pdf.y -= 6
    for heading, body_items in sections:
        pdf.section(heading)
        for item in body_items:
            if item.startswith('* '):
                pdf.bullet(item[2:])
            else:
                pdf.paragraph(item)
        pdf.y -= 4
    return pdf.build()


def generate_privacy_policy_pdf():
    return generate_legal_pdf(
        'BunShai TECHNOHUB - Privacy Policy',
        'Effective Date: December 15, 2024  |  Updated: 2026  |  team.bunshailogicloop@gmail.com',
        [
            ('1. Introduction', [
                'BunShai TECHNOHUB respects your privacy and is committed to protecting your personal data across our website, IT consulting services, mentorship courses, and support center.',
            ]),
            ('2. Information We Collect', [
                '* Identity & Contact Data: Full name, email address, phone/WhatsApp number, and company or academic background submitted via forms.',
                '* Course & Syllabus Data: Selected mentorship program, learning mode, and syllabus download requests.',
                '* Technical & Usage Data: IP address, browser user-agent, page views, and chatbot session history.',
            ]),
            ('3. How We Use Information', [
                '* To respond to service inquiries, proposal requests, career applications, and support tickets.',
                '* To deliver requested course syllabi, schedule live mentorship demos, and provide academic counseling.',
                '* To securely store leads in our primary database and optional Google Sheets backup, and prevent spam/abuse.',
            ]),
            ('4. Data Security & Retention', [
                'We apply CSRF protection, rate limiting, input validation, and encrypted transport in production. Contact and inquiry records are retained only as long as necessary to fulfill your request or legal obligations.',
            ]),
            ('5. Your Rights & Contact', [
                'You may request access, correction, or deletion of your personal data at any time by contacting our Privacy Team at team.bunshailogicloop@gmail.com or +91 8091401208.',
            ]),
        ],
    )


def generate_terms_pdf():
    return generate_legal_pdf(
        'BunShai TECHNOHUB - Terms & Conditions',
        'Legal Agreement for Website, IT Services & Mentorship Courses  |  +91 8091401208',
        [
            ('1. Agreement to Terms', [
                'By accessing BunShai TECHNOHUB services, mentorship courses, or website resources, you agree to be bound by these Terms & Conditions.',
            ]),
            ('2. Services & Mentorship Programs', [
                '* IT Consulting & Software Services: Delivered according to mutually agreed Statements of Work (SOWs), SLAs, and project milestones.',
                '* Mentorship Courses & Syllabi: Live cohort schedules, capstone projects, and downloadable syllabi are provided for personal educational use only and may not be redistributed commercially.',
            ]),
            ('3. User Responsibilities', [
                '* Provide accurate contact information when submitting inquiries, support tickets, or course enrollments.',
                '* Do not attempt unauthorized access, automated scraping, or abuse of forms and APIs.',
            ]),
            ('4. Intellectual Property & Confidentiality', [
                'All website content, course curricula, code samples, and brand assets remain the intellectual property of BunShai TECHNOHUB unless explicitly transferred in a signed client contract.',
            ]),
            ('5. Governing Law & Contact', [
                'These Terms are governed by the laws of India, with jurisdiction in Himachal Pradesh, India. Contact legal inquiries to team.bunshailogicloop@gmail.com or +91 8091401208.',
            ]),
        ],
    )
