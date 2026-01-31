# main/forms.py
from django import forms
from django.core.validators import EmailValidator
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .models import ContactMessage, Subscriber, ServiceInquiry, ProposalRequest, CareerApplication
import re

class ContactForm(forms.ModelForm):
    # Using django-recaptcha's ReCaptchaField
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    # Honeypot field for spam protection
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display:none;'}),
        label=''
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone (Optional)'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message',
                'rows': 5,
                'required': True
            }),
        }
    
    def clean_honeypot(self):
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise forms.ValidationError("Spam detected.")
        return honeypot
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'\D', '', phone)
            if len(phone) < 10:
                raise forms.ValidationError("Phone number must be at least 10 digits")
        return phone

class SubscribeForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display:none;'}),
        label=''
    )
    
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'required': True
            }),
        }
    
    def clean_honeypot(self):
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise forms.ValidationError("Spam detected.")
        return honeypot

class ServiceInquiryForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = ServiceInquiry
        fields = ['name', 'email', 'phone', 'company', 'service', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone',
                'required': True
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Company (Optional)'
            }),
            'service': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about your project',
                'rows': 5,
                'required': True
            }),
        }

class ProposalRequestForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = ProposalRequest
        fields = ['name', 'email', 'phone', 'service', 'budget', 'requirements']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone',
                'required': True
            }),
            'service': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'budget': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Project requirements and details',
                'rows': 6,
                'required': True
            }),
        }

class CareerApplicationForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = CareerApplication
        fields = ['name', 'email', 'phone', 'linkedin_url', 'position', 'cover_letter', 'resume']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone',
                'required': True
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'LinkedIn Profile URL (Optional)'
            }),
            'position': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Why are you interested in this position?',
                'rows': 5,
                'required': True
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'required': True
            }),
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume file size must be under 5MB")
            
            allowed_extensions = ['.pdf', '.doc', '.docx']
            ext = resume.name.split('.')[-1].lower()
            if f'.{ext}' not in allowed_extensions:
                raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed")
        
        return resume