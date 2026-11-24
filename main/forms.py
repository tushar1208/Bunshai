# main/forms.py
import re
from django import forms
from .models import (
    ContactMessage, ServiceInquiry, ProposalRequest, CareerApplication,
    CourseEnrollment, SyllabusDownload,
)

TEXT = {'class': 'form-control'}


def _clean_phone(value, required=False):
    value = (value or '').strip()
    if not value:
        if required:
            raise forms.ValidationError("Phone number is required")
        return ''
    digits = re.sub(r'\D', '', value)
    if len(digits) < 10 or len(digits) > 15:
        raise forms.ValidationError("Please enter a valid phone number (10-15 digits)")
    return value


class HoneypotMixin(forms.Form):
    """Hidden field that real users never fill in; bots usually do."""
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput, label='')

    def clean_honeypot(self):
        if self.cleaned_data.get('honeypot'):
            raise forms.ValidationError("Spam detected.")
        return ''


class ContactForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput, label='')

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'company', 'subject', 'service', 'message']

    def clean_honeypot(self):
        if self.cleaned_data.get('honeypot'):
            raise forms.ValidationError("Spam detected.")
        return ''

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter a valid name (minimum 2 characters)")
        return name

    def clean_phone(self):
        return _clean_phone(self.cleaned_data.get('phone'))

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError("Please enter a message (minimum 10 characters)")
        if len(message) > 5000:
            raise forms.ValidationError("Message must be under 5000 characters")
        return message


class SubscribeForm(forms.Form):
    email = forms.EmailField(max_length=254)
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_honeypot(self):
        if self.cleaned_data.get('honeypot'):
            raise forms.ValidationError("Spam detected.")
        return ''


class ServiceInquiryForm(forms.ModelForm):
    class Meta:
        model = ServiceInquiry
        fields = ['name', 'email', 'phone', 'company', 'service', 'message']

    def clean_phone(self):
        return _clean_phone(self.cleaned_data.get('phone'), required=True)


class ProposalRequestForm(forms.ModelForm):
    class Meta:
        model = ProposalRequest
        fields = ['name', 'email', 'phone', 'service', 'budget', 'requirements']

    def clean_phone(self):
        return _clean_phone(self.cleaned_data.get('phone'), required=True)


class CareerApplicationForm(forms.ModelForm):
    class Meta:
        model = CareerApplication
        fields = ['name', 'email', 'phone', 'linkedin_url', 'position', 'cover_letter', 'resume']

    def clean_phone(self):
        return _clean_phone(self.cleaned_data.get('phone'), required=True)

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file size must be under 5MB")
            ext = resume.name.rsplit('.', 1)[-1].lower() if '.' in resume.name else ''
            if ext not in ('pdf', 'doc', 'docx'):
                raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed")
        return resume


class SupportTicketForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    account_number = forms.CharField(max_length=100, required=False)
    issue_type = forms.CharField(max_length=50)
    priority = forms.ChoiceField(choices=[('low', 'low'), ('medium', 'medium'),
                                          ('high', 'high'), ('critical', 'critical')])
    subject = forms.CharField(max_length=200)
    description = forms.CharField(min_length=10)

    def clean_phone(self):
        return _clean_phone(self.cleaned_data.get('phone'))


class CourseEnrollmentForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput, label='')
    course_title = forms.CharField(max_length=200, required=False)

    class Meta:
        model = CourseEnrollment
        fields = [
            'name', 'email', 'phone', 'course_slug', 'course_title',
            'learning_mode', 'experience_level', 'message',
        ]

    def clean_honeypot(self):
        if self.cleaned_data.get('honeypot'):
            raise forms.ValidationError("Spam detected.")
        return ''

    def clean_phone(self):
        return _clean_phone(self.cleaned_data.get('phone'), required=True)


class SyllabusDownloadForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput, label='')
    course_title = forms.CharField(max_length=200, required=False)

    class Meta:
        model = SyllabusDownload
        fields = ['name', 'email', 'phone', 'course_slug', 'course_title', 'background']

    def clean_honeypot(self):
        if self.cleaned_data.get('honeypot'):
            raise forms.ValidationError("Spam detected.")
        return ''

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name")
        return name

    def clean_phone(self):
        return _clean_phone(self.cleaned_data.get('phone'), required=True)
