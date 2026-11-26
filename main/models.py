from django.db import models
import uuid
from django.utils import timezone
from django.core.validators import EmailValidator
import re

class ContactMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30, blank=True, null=True)
    company = models.CharField(max_length=150, blank=True, default='')
    subject = models.CharField(max_length=200, blank=True, default='')
    service = models.CharField(max_length=100, blank=True, default='')
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    
    class Meta:
        ordering = ['-date_sent']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

class Subscriber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"

class ServiceInquiry(models.Model):
    SERVICES = [
        ('web', 'Web Development'),
        ('mobile', 'Mobile App Development'),
        ('ai', 'AI/ML Solutions'),
        ('cloud', 'Cloud Services'),
        ('cyber', 'Cybersecurity'),
        ('consulting', 'IT Consulting'),
        ('marketing', 'Digital Marketing'),
        ('data', 'Data Analytics'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)
    company = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {dict(self.SERVICES).get(self.service, self.service)}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Service Inquiry"
        verbose_name_plural = "Service Inquiries"

class ProposalRequest(models.Model):
    SERVICES = [
        ('web', 'Web Development'),
        ('mobile', 'Mobile App Development'),
        ('ai', 'AI/ML Solutions'),
        ('cloud', 'Cloud Services'),
        ('cyber', 'Cybersecurity'),
        ('consulting', 'IT Consulting'),
        ('marketing', 'Digital Marketing'),
        ('data', 'Data Analytics'),
        ('custom', 'Custom Solution'),
    ]
    
    BUDGET_RANGES = [
        ('1k-5k', '$1,000 - $5,000'),
        ('5k-10k', '$5,000 - $10,000'),
        ('10k-25k', '$10,000 - $25,000'),
        ('25k-50k', '$25,000 - $50,000'),
        ('50k+', '$50,000+'),
        ('custom', 'Custom Budget'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)
    service = models.CharField(max_length=100)
    budget = models.CharField(max_length=100)
    requirements = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {dict(self.SERVICES).get(self.service, self.service)}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Proposal Request"
        verbose_name_plural = "Proposal Requests"

class CareerApplication(models.Model):
    POSITIONS = [
        ('dev', 'Software Developer'),
        ('designer', 'UI/UX Designer'),
        ('devops', 'DevOps Engineer'),
        ('data', 'Data Scientist'),
        ('security', 'Security Analyst'),
        ('pm', 'Project Manager'),
        ('marketing', 'Marketing Specialist'),
        ('sales', 'Sales Executive'),
        ('intern', 'Intern'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)
    linkedin_url = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=100)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {dict(self.POSITIONS).get(self.position, self.position)}"
    
    class Meta:
        ordering = ['-applied_at']
        verbose_name = "Career Application"
        verbose_name_plural = "Career Applications"

class PageView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page_url = models.URLField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.page_url} - {self.viewed_at}"
    
    class Meta:
        ordering = ['-viewed_at']
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"

class SecurityLog(models.Model):
    EVENT_TYPES = [
        ('login_attempt', 'Login Attempt'),
        ('failed_login', 'Failed Login'),
        ('suspicious', 'Suspicious Activity'),
        ('spam', 'Spam Detection'),
        ('bruteforce', 'Brute Force Attempt'),
        ('sql_injection', 'SQL Injection Attempt'),
        ('xss', 'XSS Attempt'),
        ('bot', 'Bot Detection'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.ip_address}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Security Log"
        verbose_name_plural = "Security Logs"

class ChatbotSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_returning = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.session_id} - {self.name or 'Anonymous'}"
    
    class Meta:
        ordering = ['-last_activity']

class ChatbotMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatbotSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'User' if self.is_user else 'Bot'}: {self.message[:40]}"
    
    class Meta:
        ordering = ['created_at']


class ChatbotUnanswered(models.Model):
    """Questions Sharsh could not answer; visitors are redirected to the contact form."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatbotSession, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='unanswered')
    question = models.TextField()
    name = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    resolved = models.BooleanField(default=False)
    synced_to_google = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question[:60]}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Unanswered Chatbot Question"
        verbose_name_plural = "Unanswered Chatbot Questions"


class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default='')
    account_number = models.CharField(max_length=100, blank=True, default='')
    issue_type = models.CharField(max_length=50)
    priority = models.CharField(max_length=20, default='medium')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    attachments = models.TextField(blank=True, default='', help_text='Saved attachment paths, one per line')
    status = models.CharField(max_length=20, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = 'BST-' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"


class CourseEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)
    course_slug = models.CharField(max_length=100)
    course_title = models.CharField(max_length=200)
    learning_mode = models.CharField(max_length=50, default='Live Online')
    experience_level = models.CharField(max_length=60, blank=True, default='')
    message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.course_title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Course Enrollment"
        verbose_name_plural = "Course Enrollments"


class SyllabusDownload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)
    course_slug = models.CharField(max_length=100)
    course_title = models.CharField(max_length=200)
    background = models.CharField(max_length=60, blank=True, default='')
    synced_to_google = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.course_title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Syllabus Download"
        verbose_name_plural = "Syllabus Downloads"


class WhatsAppMessage(models.Model):
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wa_message_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    direction = models.CharField(max_length=16, choices=DIRECTION_CHOICES)
    phone = models.CharField(max_length=30, db_index=True)
    contact_name = models.CharField(max_length=120, blank=True, default='')
    message_type = models.CharField(max_length=24, default='text')
    body = models.TextField()
    status = models.CharField(max_length=24, default='received')
    source = models.CharField(max_length=80, blank=True, default='')
    raw_payload = models.JSONField(default=dict, blank=True)
    synced_to_google = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.direction}] {self.phone}: {self.body[:40]}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "WhatsApp Message"
        verbose_name_plural = "WhatsApp Messages"


class WhatsAppConversation(models.Model):
    phone = models.CharField(max_length=30, primary_key=True)
    contact_name = models.CharField(max_length=120, blank=True, default='')
    flow = models.CharField(max_length=40, default='idle')
    step = models.CharField(max_length=40, blank=True, default='')
    draft_data = models.JSONField(default=dict, blank=True)
    human_handoff = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone} ({self.flow}/{self.step or 'idle'})"

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "WhatsApp Conversation"
        verbose_name_plural = "WhatsApp Conversations"


class WhatsAppAutoReplyRule(models.Model):
    MATCH_TYPES = [
        ('exact', 'Exact'),
        ('contains', 'Contains'),
        ('regex', 'Regex'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    match_type = models.CharField(max_length=16, choices=MATCH_TYPES, default='contains')
    pattern = models.CharField(max_length=200)
    reply_text = models.TextField()
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.match_type}: {self.pattern})"

    class Meta:
        ordering = ['priority', 'created_at']
        verbose_name = "WhatsApp Auto-Reply Rule"
        verbose_name_plural = "WhatsApp Auto-Reply Rules"


class WhatsAppScheduledMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('template', 'Approved Template'),
    ]
    RECURRENCE_CHOICES = [
        ('once', 'One-Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=30)
    message_type = models.CharField(max_length=16, choices=MESSAGE_TYPES, default='text')
    body = models.TextField(blank=True, default='')
    template_name = models.CharField(max_length=120, blank=True, default='')
    template_lang = models.CharField(max_length=20, default='en_US')
    template_params = models.JSONField(default=list, blank=True)
    scheduled_for = models.DateTimeField(db_index=True)
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='once')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or self.phone} ({self.status} @ {self.scheduled_for})"

    class Meta:
        ordering = ['scheduled_for']
        verbose_name = "WhatsApp Scheduled Message"
        verbose_name_plural = "WhatsApp Scheduled Messages"


class SiteMetrics(models.Model):
    """Singleton settings model for site-wide headline statistics editable from Django Admin."""

    projects_delivered = models.PositiveIntegerField(
        default=46,
        help_text="Total projects delivered (displayed with '+' across the site)",
    )
    happy_clients = models.PositiveIntegerField(
        default=58,
        help_text="Total happy clients (displayed with '+' across the site)",
    )
    countries_served = models.PositiveIntegerField(
        default=10,
        help_text="Total countries served (displayed with '+' across the site)",
    )
    years_experience = models.PositiveIntegerField(
        default=4,
        help_text="Years of industry experience (displayed with '+' across the site)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Metrics"
        verbose_name_plural = "Site Metrics"

    def __str__(self):
        return (
            f"Site Metrics ({self.projects_delivered}+ Projects, "
            f"{self.happy_clients}+ Clients, "
            f"{self.countries_served}+ Countries, "
            f"{self.years_experience}+ Years)"
        )

    @classmethod
    def get_solo(cls):
        """Return the singleton SiteMetrics row, creating defaults if missing or safely falling back."""
        try:
            obj = cls.objects.first()
            if obj is None:
                obj = cls.objects.create()
            return obj
        except Exception:  # noqa: BLE001 - safe fallback before migrations run
            return cls()


class BlogPost(models.Model):
    """SEO/AEO pillar article with weekly auto-rotation spotlight support."""

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.CharField(max_length=80, db_index=True)
    excerpt = models.TextField(max_length=400)
    content_sections = models.JSONField(
        default=list,
        help_text="List of {heading, body, bullets, tip} dicts",
    )
    faqs = models.JSONField(
        default=list,
        help_text="List of {q, a} dicts for FAQPage schema",
    )
    cover_image = models.CharField(max_length=200, default='images/courses/ai-genai.png')
    primary_keyword = models.CharField(max_length=160, blank=True)
    meta_title = models.CharField(max_length=220, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    tags = models.CharField(max_length=260, blank=True, help_text="Comma-separated SEO tags")
    author_name = models.CharField(max_length=120, default='BunShai Editorial Team')
    author_role = models.CharField(max_length=120, default='Technology & Growth Architects')
    reading_time = models.PositiveSmallIntegerField(default=6)
    related_service_slug = models.CharField(max_length=80, blank=True)
    related_course_slug = models.CharField(max_length=120, blank=True)
    rotation_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True, db_index=True)
    publish_date = models.DateField(default=timezone.localdate, db_index=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rotation_order', '-publish_date', '-id']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def seo_title(self):
        return self.meta_title or self.title

    @property
    def seo_description(self):
        return self.meta_description or self.excerpt


