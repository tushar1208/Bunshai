"""
URL configuration for bunshai_technohub project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.ico', permanent=True)),
    
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

# Custom error handlers (must be configured in ROOT_URLCONF)
handler400 = 'main.views.custom_400'
handler403 = 'main.views.custom_403'
handler404 = 'main.views.custom_404'
handler500 = 'main.views.custom_500'