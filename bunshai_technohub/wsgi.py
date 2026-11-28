# bunshai_technohub/wsgi.py
"""
WSGI config for bunshai_technohub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bunshai_technohub.settings')

application = get_wsgi_application()

logger = logging.getLogger('bunshai_technohub.wsgi')
try:
    from django.db import close_old_connections
    from main.management.commands.ensure_superuser import sync_env_superuser

    _su_status, _su_username, _su_fields = sync_env_superuser()
    if _su_status == 'created':
        logger.info('Created superuser "%s" on WSGI startup.', _su_username)
    elif _su_status == 'synced':
        logger.info('Synced superuser "%s" on WSGI startup (%s).', _su_username, ', '.join(_su_fields))
except Exception as exc:  # noqa: BLE001
    logger.warning('WSGI startup superuser sync skipped: %s', exc)
finally:
    try:
        from django.db import close_old_connections
        close_old_connections()
    except Exception:  # noqa: BLE001
        pass
