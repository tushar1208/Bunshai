"""
URL configuration for bunshai_technohub project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# REMOVE or COMMENT OUT these lines:
# admin.site = custom_admin_site  # This causes the error!
# admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    
    # reCAPTCHA verification endpoint - not needed in django-recaptcha 4.0.0
    # path('captcha/', include('django_recaptcha.urls')),
    
    # Robots.txt
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', 
        content_type='text/plain'
    )),
    
    # Sitemap
    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml',
        content_type='application/xml'
    )),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers - REMOVE THESE FROM HERE since they're in main/urls.py
# handler400 = 'main.views.custom_400'
# handler403 = 'main.views.custom_403'
# handler404 = 'main.views.custom_404'
# handler500 = 'main.views.custom_500'