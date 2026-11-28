# bunshai_technohub/wsgi.py
"""
WSGI config for bunshai_technohub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bunshai_technohub.settings')

application = get_wsgi_application()

from main.management.commands.ensure_superuser import bootstrap_production_superuser

bootstrap_production_superuser('bunshai_technohub.wsgi')
