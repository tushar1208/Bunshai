from django.urls import path
from . import views, whatsapp_views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('company-profile/', views.company_profile, name='company_profile'),
    path('md-profile/', views.md_profile, name='md_profile'),
    path('team/', views.team, name='team'),

    # Services
    path('services/', views.services, name='services'),
    path('services/<str:service_slug>/', views.service_detail, name='service_detail'),

    # Courses & Mentorship Programs
    path('courses/', views.courses, name='courses'),
    path('courses/enroll/', views.course_enroll, name='course_enroll'),
    path('courses/syllabus-request/', views.syllabus_request, name='syllabus_request'),
    path('courses/<slug:course_slug>/syllabus-download/', views.syllabus_download, name='syllabus_download'),
    path('courses/<slug:course_slug>/', views.course_detail, name='course_detail'),

    # Contact & Forms
    path('contact/', views.contact, name='contact'),
    path('subscribe/', views.subscribe_page, name='subscribe_page'),
    path('subscribe/submit/', views.subscribe, name='subscribe'),
    path('proposal-request/', views.proposal_request, name='proposal_request'),
    path('proposal/', views.proposal_request, name='proposal'),
    path('service-inquiry/', views.service_inquiry, name='service_inquiry'),
    path('support/ticket/', views.support_ticket, name='support_ticket'),
    path('career/', views.career, name='career'),
    path('get-captcha/', views.get_captcha, name='get_captcha'),
    path('verify-captcha/', views.verify_captcha, name='verify_captcha'),

    # Legal pages
    path('privacy/', views.privacy, name='privacy'),
    path('privacy/download-pdf/', views.privacy_pdf, name='privacy_pdf'),
    path('terms/', views.terms, name='terms'),
    path('terms/download-pdf/', views.terms_pdf, name='terms_pdf'),
    path('support/', views.support, name='support'),
    path('sitemap/', views.sitemap, name='sitemap'),

    # Chatbot API
    path('api/chatbot/start-session/', views.chatbot_start_session, name='chatbot_start_session'),
    path('api/chatbot/send-message/', views.chatbot_send_message, name='chatbot_send_message'),
    path('api/chatbot/check-user/', views.chatbot_check_user, name='chatbot_check_user'),

    # WhatsApp Cloud API Automation
    path('whatsapp/webhook/', whatsapp_views.whatsapp_webhook, name='whatsapp_webhook'),
    path('whatsapp/dashboard/', whatsapp_views.whatsapp_dashboard, name='whatsapp_dashboard'),
    path('api/whatsapp/simulate/', whatsapp_views.api_whatsapp_simulate, name='api_whatsapp_simulate'),
    path('api/whatsapp/send/', whatsapp_views.api_whatsapp_send, name='api_whatsapp_send'),
    path('api/whatsapp/schedule/', whatsapp_views.api_whatsapp_schedule, name='api_whatsapp_schedule'),
    path('api/whatsapp/schedule/run-due/', whatsapp_views.api_whatsapp_run_due_schedules, name='api_whatsapp_run_due_schedules'),
    path('api/whatsapp/broadcast/', whatsapp_views.api_whatsapp_broadcast, name='api_whatsapp_broadcast'),
    path('api/whatsapp/conversations/<str:phone>/resume/', whatsapp_views.api_whatsapp_resume_conversation, name='api_whatsapp_resume_conversation'),
]
