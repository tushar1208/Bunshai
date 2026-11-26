import csv
from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from .models import *
from .whatsapp_service import execute_scheduled_message, send_whatsapp_text

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

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscribers activated.')
    activate_subscribers.short_description = "Activate selected subscribers"

    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscribers deactivated.')
    deactivate_subscribers.short_description = "Deactivate selected subscribers"

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

        recent_activities = []
        for sub in Subscriber.objects.order_by('-subscribed_at')[:3]:
            recent_activities.append({
                'icon': 'fas fa-user-plus',
                'text': f'New subscriber registered: {sub.email}',
                'timestamp': sub.subscribed_at,
            })
        for msg in ContactMessage.objects.order_by('-date_sent')[:3]:
            recent_activities.append({
                'icon': 'fas fa-comment',
                'text': f'New contact message from {msg.name}',
                'timestamp': msg.date_sent,
            })
        for enr in CourseEnrollment.objects.order_by('-created_at')[:3]:
            recent_activities.append({
                'icon': 'fas fa-graduation-cap',
                'text': f'Course enrollment: {enr.name} ({enr.course_title})',
                'timestamp': enr.created_at,
            })
        for prop in ProposalRequest.objects.order_by('-created_at')[:2]:
            recent_activities.append({
                'icon': 'fas fa-file-contract',
                'text': f'Proposal request from {prop.name} ({prop.get_service_display()})',
                'timestamp': prop.created_at,
            })
        for app in CareerApplication.objects.order_by('-applied_at')[:2]:
            recent_activities.append({
                'icon': 'fas fa-briefcase',
                'text': f'Career application from {app.name} ({app.get_position_display()})',
                'timestamp': app.applied_at,
            })
        for tkt in SupportTicket.objects.order_by('-created_at')[:2]:
            recent_activities.append({
                'icon': 'fas fa-life-ring',
                'text': f'Support ticket {tkt.ticket_number} from {tkt.name}',
                'timestamp': tkt.created_at,
            })
        recent_activities.sort(key=lambda item: item['timestamp'], reverse=True)

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
            'total_whatsapp_messages': WhatsAppMessage.objects.count(),
            'recent_activities': recent_activities[:6],
        }
        
        return render(request, 'admin/dashboard.html', context)
    
    def analytics_view(self, request):
        return self.dashboard_view(request)

    def export_data_view(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bunshai_summary.csv"'
        writer = csv.writer(response)
        writer.writerow(['Metric', 'Total'])
        writer.writerow(['Contact Messages', ContactMessage.objects.count()])
        writer.writerow(['Active Subscribers', Subscriber.objects.filter(is_active=True).count()])
        writer.writerow(['Service Inquiries', ServiceInquiry.objects.count()])
        writer.writerow(['Proposal Requests', ProposalRequest.objects.count()])
        writer.writerow(['Career Applications', CareerApplication.objects.count()])
        writer.writerow(['Support Tickets', SupportTicket.objects.count()])
        writer.writerow(['Course Enrollments', CourseEnrollment.objects.count()])
        writer.writerow(['Syllabus Downloads', SyllabusDownload.objects.count()])
        writer.writerow(['WhatsApp Messages', WhatsAppMessage.objects.count()])
        return response

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

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'name', 'email', 'issue_type', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'issue_type')
    search_fields = ('ticket_number', 'name', 'email', 'subject', 'description')
    readonly_fields = ('ticket_number', 'created_at', 'ip_address', 'attachments')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'course_title', 'learning_mode', 'experience_level', 'created_at')
    list_filter = ('learning_mode', 'experience_level', 'created_at')
    search_fields = ('name', 'email', 'phone', 'course_title', 'course_slug')
    readonly_fields = ('created_at', 'ip_address')
    actions = ['send_whatsapp_followup']

    def send_whatsapp_followup(self, request, queryset):
        sent = 0
        for obj in queryset:
            if not obj.phone:
                continue
            try:
                send_whatsapp_text(
                    obj.phone,
                    f"Hi {obj.name}! Following up on your {obj.course_title} enrollment inquiry at BunShai TECHNOHUB. Reply here if you'd like batch timings or fee details!",
                    source='admin:course_followup',
                    contact_name=obj.name,
                )
                sent += 1
            except Exception:  # noqa: BLE001
                pass
        self.message_user(request, f'Sent WhatsApp follow-up to {sent} enrolled lead(s).')
    send_whatsapp_followup.short_description = "Send WhatsApp follow-up to selected"


@admin.register(SyllabusDownload)
class SyllabusDownloadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'course_title', 'background', 'synced_to_google', 'created_at')
    list_filter = ('synced_to_google', 'background', 'created_at')
    search_fields = ('name', 'email', 'phone', 'course_title', 'course_slug')
    readonly_fields = ('created_at', 'ip_address')
    actions = ['send_whatsapp_followup']

    def send_whatsapp_followup(self, request, queryset):
        sent = 0
        for obj in queryset:
            if not obj.phone:
                continue
            try:
                send_whatsapp_text(
                    obj.phone,
                    f"Hi {obj.name}! Hope you found the {obj.course_title} syllabus helpful. Reply here if you want to book a free counseling call with BunShai TECHNOHUB!",
                    source='admin:syllabus_followup',
                    contact_name=obj.name,
                )
                sent += 1
            except Exception:  # noqa: BLE001
                pass
        self.message_user(request, f'Sent WhatsApp follow-up to {sent} syllabus lead(s).')
    send_whatsapp_followup.short_description = "Send WhatsApp follow-up to selected"


@admin.register(ChatbotUnanswered)
class ChatbotUnansweredAdmin(admin.ModelAdmin):
    list_display = ('question', 'name', 'email', 'phone', 'resolved', 'synced_to_google', 'created_at')
    list_filter = ('resolved', 'synced_to_google', 'created_at')
    search_fields = ('question', 'name', 'email', 'phone')
    readonly_fields = ('created_at',)
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        self.message_user(request, f'{queryset.update(resolved=True)} questions marked resolved.')
    mark_resolved.short_description = "Mark selected as resolved"


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('direction', 'phone', 'contact_name', 'message_type', 'body_short', 'status', 'source', 'created_at')
    list_filter = ('direction', 'message_type', 'status', 'synced_to_google', 'created_at')
    search_fields = ('phone', 'contact_name', 'body', 'wa_message_id', 'source')
    readonly_fields = ('wa_message_id', 'raw_payload', 'created_at')

    def body_short(self, obj):
        return obj.body[:60] + '...' if len(obj.body) > 60 else obj.body
    body_short.short_description = 'Body'


@admin.register(WhatsAppConversation)
class WhatsAppConversationAdmin(admin.ModelAdmin):
    list_display = ('phone', 'contact_name', 'flow', 'step', 'human_handoff', 'updated_at')
    list_filter = ('flow', 'human_handoff')
    search_fields = ('phone', 'contact_name')
    readonly_fields = ('updated_at',)
    actions = ['resume_bot_conversations']

    def resume_bot_conversations(self, request, queryset):
        updated = queryset.update(flow='idle', step='', draft_data={}, human_handoff=False)
        self.message_user(request, f'Resumed bot automation for {updated} conversation(s).')
    resume_bot_conversations.short_description = "Resume bot automation for selected"


@admin.register(WhatsAppAutoReplyRule)
class WhatsAppAutoReplyRuleAdmin(admin.ModelAdmin):
    list_display = ('priority', 'name', 'match_type', 'pattern', 'is_active', 'created_at')
    list_filter = ('match_type', 'is_active')
    search_fields = ('name', 'pattern', 'reply_text')


@admin.register(WhatsAppScheduledMessage)
class WhatsAppScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'message_type', 'recurrence', 'scheduled_for', 'status', 'last_run_at')
    list_filter = ('status', 'recurrence', 'message_type')
    search_fields = ('name', 'phone', 'body', 'template_name')
    readonly_fields = ('last_run_at', 'last_error', 'created_at')
    actions = ['send_selected_now']

    def send_selected_now(self, request, queryset):
        sent = 0
        for job in queryset:
            try:
                execute_scheduled_message(job)
                sent += 1
            except Exception:  # noqa: BLE001
                pass
        self.message_user(request, f'Executed {sent} scheduled message(s).')
    send_selected_now.short_description = "Send selected scheduled messages now"


@admin.register(SiteMetrics)
class SiteMetricsAdmin(BaseAdmin):
    list_display = (
        'label',
        'projects_delivered',
        'happy_clients',
        'countries_served',
        'years_experience',
        'updated_at',
    )
    list_display_links = ('label',)
    list_editable = (
        'projects_delivered',
        'happy_clients',
        'countries_served',
        'years_experience',
    )
    readonly_fields = ('updated_at',)

    def label(self, obj):
        return "Website Statistics"
    label.short_description = "Configuration"

    def has_add_permission(self, request):
        return not SiteMetrics.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        SiteMetrics.get_solo()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(BlogPost)
class BlogPostAdmin(BaseAdmin):
    list_display = (
        'title',
        'category',
        'primary_keyword',
        'is_published',
        'publish_date',
        'rotation_order',
        'views_count',
    )
    list_editable = ('is_published', 'publish_date', 'rotation_order')
    list_filter = ('category', 'is_published', 'publish_date')
    search_fields = ('title', 'slug', 'primary_keyword', 'tags', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')


custom_admin_site.register(ChatbotUnanswered, ChatbotUnansweredAdmin)
custom_admin_site.register(SupportTicket, SupportTicketAdmin)
custom_admin_site.register(CourseEnrollment, CourseEnrollmentAdmin)
custom_admin_site.register(SyllabusDownload, SyllabusDownloadAdmin)
custom_admin_site.register(WhatsAppMessage, WhatsAppMessageAdmin)
custom_admin_site.register(WhatsAppConversation, WhatsAppConversationAdmin)
custom_admin_site.register(WhatsAppAutoReplyRule, WhatsAppAutoReplyRuleAdmin)
custom_admin_site.register(WhatsAppScheduledMessage, WhatsAppScheduledMessageAdmin)
custom_admin_site.register(SiteMetrics, SiteMetricsAdmin)
custom_admin_site.register(BlogPost, BlogPostAdmin)
