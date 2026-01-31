from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('company-profile/', views.company_profile, name='company_profile'),
    path('md-profile/', views.md_profile, name='md_profile'),
    
    # Services
    path('services/', views.services, name='services'),
    path('services/<str:service_slug>/', views.service_detail, name='service_detail'),
    
    # Contact & Forms
    path('contact/', views.contact, name='contact'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('proposal-request/', views.proposal_request, name='proposal_request'),
    path('career/', views.career, name='career'),
    
    # Legal pages
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('support/', views.support, name='support'),
    path('sitemap/', views.sitemap, name='sitemap'),
    
    # Chatbot API
    path('api/chatbot/start-session/', views.chatbot_start_session, name='chatbot_start_session'),
    path('api/chatbot/send-message/', views.chatbot_send_message, name='chatbot_send_message'),
    # path('api/chatbot/check-user/', views.chatbot_check_user, name='chatbot_check_user'),
    
    # Security API
    # path('api/security/log/', views.security_log, name='security_log'),
]

# Error handlers
handler404 = 'main.views.custom_404'
handler500 = 'main.views.custom_500'
handler403 = 'main.views.custom_403'
handler400 = 'main.views.custom_400'