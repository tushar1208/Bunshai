from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import *

# Unregister default Group
admin.site.unregister(Group)

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_max_show_all = 100
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(ContactMessage)
class ContactMessageAdmin(BaseAdmin):
    list_display = ('name', 'email', 'phone', 'is_spam', 'is_verified', 'date_sent', 'ip_address')
    list_filter = ('is_spam', 'is_verified', 'date_sent')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('date_sent', 'ip_address', 'user_agent', 'verification_token')
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_verified', 'is_spam')
        }),
        ('Technical Information', {
            'fields': ('date_sent', 'ip_address', 'user_agent', 'verification_token'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_verified', 'mark_as_spam', 'export_selected']
    
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} messages marked as verified.')
    mark_as_verified.short_description = "Mark selected as verified"
    
    def mark_as_spam(self, request, queryset):
        updated = queryset.update(is_spam=True)
        self.message_user(request, f'{updated} messages marked as spam.')
    mark_as_spam.short_description = "Mark selected as spam"
    
    def export_selected(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_messages.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Message', 'Date', 'IP Address', 'Status'])
        
        for obj in queryset:
            status = 'Verified' if obj.is_verified else 'Pending'
            status = 'Spam' if obj.is_spam else status
            writer.writerow([obj.name, obj.email, obj.phone or '', obj.message, 
                           obj.date_sent, obj.ip_address or '', status])
        
        return response
    export_selected.short_description = "Export selected to CSV"

@admin.register(Subscriber)
class SubscriberAdmin(BaseAdmin):
    list_display = ('email', 'is_active', 'is_verified', 'subscribed_at', 'ip_address')
    list_filter = ('is_active', 'is_verified', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'ip_address', 'verification_token')
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'is_active', 'is_verified')
        }),
        ('Technical Information', {
            'fields': ('subscribed_at', 'ip_address', 'verification_token'),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_emails']
    
    def export_emails(self, request, queryset):
        emails = '\n'.join([sub.email for sub in queryset])
        response = HttpResponse(emails, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="subscribers.txt"'
        return response
    export_emails.short_description = "Export emails to text file"

@admin.register(ServiceInquiry)
class ServiceInquiryAdmin(BaseAdmin):
    list_display = ('name', 'email', 'service', 'company', 'created_at', 'ip_address')
    list_filter = ('service', 'created_at')
    search_fields = ('name', 'email', 'company', 'message')
    readonly_fields = ('created_at', 'ip_address')
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Inquiry Details', {
            'fields': ('service', 'message')
        }),
        ('Technical Information', {
            'fields': ('created_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'

@admin.register(ProposalRequest)
class ProposalRequestAdmin(BaseAdmin):
    list_display = ('name', 'email', 'service', 'budget', 'created_at', 'ip_address')
    list_filter = ('service', 'budget', 'created_at')
    search_fields = ('name', 'email', 'requirements')
    readonly_fields = ('created_at', 'ip_address')
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Project Details', {
            'fields': ('service', 'budget', 'requirements')
        }),
        ('Technical Information', {
            'fields': ('created_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'

@admin.register(CareerApplication)
class CareerApplicationAdmin(BaseAdmin):
    list_display = ('name', 'email', 'position', 'applied_at', 'resume_link', 'ip_address')
    list_filter = ('position', 'applied_at')
    search_fields = ('name', 'email', 'cover_letter')
    readonly_fields = ('applied_at', 'ip_address', 'resume_preview')
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'linkedin_url')
        }),
        ('Application Details', {
            'fields': ('position', 'cover_letter', 'resume', 'resume_preview')
        }),
        ('Technical Information', {
            'fields': ('applied_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank" class="button">📄 Download</a>', obj.resume.url)
        return "No resume"
    resume_link.short_description = "Resume"
    
    def resume_preview(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">View Resume</a>', obj.resume.url)
        return "No resume uploaded"
    resume_preview.short_description = "Resume Preview"
    
    date_hierarchy = 'applied_at'

@admin.register(PageView)
class PageViewAdmin(BaseAdmin):
    list_display = ('page_url', 'ip_address', 'viewed_at', 'referrer_short')
    list_filter = ('viewed_at',)
    search_fields = ('page_url', 'ip_address', 'referrer')
    readonly_fields = ('viewed_at', 'ip_address', 'user_agent', 'referrer')
    fieldsets = (
        ('Page View Information', {
            'fields': ('page_url', 'referrer')
        }),
        ('Technical Information', {
            'fields': ('viewed_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def referrer_short(self, obj):
        if obj.referrer:
            return obj.referrer[:50] + '...' if len(obj.referrer) > 50 else obj.referrer
        return "Direct"
    referrer_short.short_description = "Referrer"
    
    date_hierarchy = 'viewed_at'
    
    def has_add_permission(self, request):
        return False

@admin.register(SecurityLog)
class SecurityLogAdmin(BaseAdmin):
    list_display = ('event_type', 'ip_address', 'created_at', 'details_short')
    list_filter = ('event_type', 'created_at')
    search_fields = ('ip_address', 'details')
    readonly_fields = ('created_at', 'ip_address', 'user_agent', 'details')
    fieldsets = (
        ('Security Event', {
            'fields': ('event_type', 'details')
        }),
        ('Technical Information', {
            'fields': ('created_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def details_short(self, obj):
        return obj.details[:100] + '...' if len(obj.details) > 100 else obj.details
    details_short.short_description = "Details"
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False

@admin.register(ChatbotSession)
class ChatbotSessionAdmin(BaseAdmin):
    list_display = ('session_id', 'name', 'email', 'is_returning', 'last_activity')
    list_filter = ('is_returning', 'created_at', 'last_activity')
    search_fields = ('session_id', 'name', 'email')
    readonly_fields = ('created_at', 'last_activity')
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'name', 'email', 'phone', 'is_returning')
        }),
        ('Activity', {
            'fields': ('created_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'

@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(BaseAdmin):
    list_display = ('session', 'message_short', 'is_user', 'created_at')
    list_filter = ('is_user', 'created_at')
    search_fields = ('message', 'session__session_id')
    readonly_fields = ('created_at',)
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = "Message"
    
    date_hierarchy = 'created_at'

# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = '🚀 BunShai TECHNOHUB Admin'
    site_title = 'BunShai TECHNOHUB Admin Portal'
    index_title = 'Dashboard Overview'
    site_url = '/'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
            path('export-data/', self.admin_view(self.export_data_view), name='export_data'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        context = {
            'title': 'Dashboard',
            'total_contacts': ContactMessage.objects.count(),
            'recent_contacts': ContactMessage.objects.filter(date_sent__gte=thirty_days_ago).count(),
            'total_subscribers': Subscriber.objects.filter(is_active=True).count(),
            'new_subscribers': Subscriber.objects.filter(subscribed_at__gte=thirty_days_ago).count(),
            'total_inquiries': ServiceInquiry.objects.count(),
            'recent_inquiries': ServiceInquiry.objects.filter(created_at__gte=thirty_days_ago).count(),
            'total_proposals': ProposalRequest.objects.count(),
            'recent_proposals': ProposalRequest.objects.filter(created_at__gte=thirty_days_ago).count(),
            'total_applications': CareerApplication.objects.count(),
            'recent_applications': CareerApplication.objects.filter(applied_at__gte=thirty_days_ago).count(),
            'page_views_today': PageView.objects.filter(viewed_at__date=timezone.now().date()).count(),
            'total_chatbot_sessions': ChatbotSession.objects.count(),
            'recent_chatbot_sessions': ChatbotSession.objects.filter(last_activity__gte=thirty_days_ago).count(),
            'security_events_today': SecurityLog.objects.filter(created_at__date=timezone.now().date()).count(),
        }
        
        return render(request, 'admin/dashboard.html', context)
    
    def analytics_view(self, request):
        # Analytics data
        return render(request, 'admin/analytics.html', {'title': 'Analytics'})
    
    def export_data_view(self, request):
        # Data export interface
        return render(request, 'admin/export_data.html', {'title': 'Export Data'})

# Create and register custom admin site
custom_admin_site = CustomAdminSite(name='customadmin')

# Re-register all models with custom admin site
custom_admin_site.register(ContactMessage, ContactMessageAdmin)
custom_admin_site.register(Subscriber, SubscriberAdmin)
custom_admin_site.register(ServiceInquiry, ServiceInquiryAdmin)
custom_admin_site.register(ProposalRequest, ProposalRequestAdmin)
custom_admin_site.register(CareerApplication, CareerApplicationAdmin)
custom_admin_site.register(PageView, PageViewAdmin)
custom_admin_site.register(SecurityLog, SecurityLogAdmin)
custom_admin_site.register(ChatbotSession, ChatbotSessionAdmin)
custom_admin_site.register(ChatbotMessage, ChatbotMessageAdmin)