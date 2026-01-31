from django.db import models
import uuid
from django.utils import timezone
from django.core.validators import EmailValidator
import re

class ContactMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True, null=True)
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
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(max_length=50, choices=SERVICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_service_display()}"
    
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
    phone = models.CharField(max_length=20)
    service = models.CharField(max_length=50, choices=SERVICES)
    budget = models.CharField(max_length=20, choices=BUDGET_RANGES)
    requirements = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_service_display()}"
    
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
    phone = models.CharField(max_length=20)
    linkedin_url = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=50, choices=POSITIONS)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_position_display()}"
    
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
    
    class Meta:
        ordering = ['created_at']