import logging
import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import IntegrityError, OperationalError, ProgrammingError, close_old_connections


def _clean_env(name):
    val = os.getenv(name, '').strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
        val = val[1:-1].strip()
    return val


def sync_env_superuser():
    """
    Create or sync a Django superuser from DJANGO_SUPERUSER_* env vars.
    Concurrency-safe for multi-worker Gunicorn boot; returns (status, username, fields).
    """
    username = _clean_env('DJANGO_SUPERUSER_USERNAME')
    email = _clean_env('DJANGO_SUPERUSER_EMAIL')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '').strip()

    if not (username and password):
        return ('skipped', '', [])

    User = get_user_model()
    user = User.objects.filter(username=username).first()
    if user is None:
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            return ('created', username, [])
        except IntegrityError:
            user = User.objects.filter(username=username).first()
            if user is None:
                raise

    update_fields = []
    if not user.is_staff:
        user.is_staff = True
        update_fields.append('is_staff')
    if not user.is_superuser:
        user.is_superuser = True
        update_fields.append('is_superuser')
    if not user.is_active:
        user.is_active = True
        update_fields.append('is_active')
    if email and user.email != email:
        user.email = email
        update_fields.append('email')
    if not user.check_password(password):
        user.set_password(password)
        update_fields.append('password')

    if update_fields:
        user.save(update_fields=update_fields)
        return ('synced', username, update_fields)

    return ('unchanged', username, [])


def bootstrap_production_superuser(logger_name='bunshai_technohub.startup'):
    """
    Ensure migrations are applied if starting against an unmigrated DB and sync
    the superuser from environment variables without crashing WSGI/ASGI startup.
    """
    log = logging.getLogger(logger_name)
    try:
        try:
            status, username, fields = sync_env_superuser()
        except (OperationalError, ProgrammingError):
            log.info('Database tables missing on startup; running pending migrations first.')
            call_command('migrate', interactive=False, verbosity=0)
            status, username, fields = sync_env_superuser()

        if status == 'created':
            log.info('Created superuser "%s" on startup.', username)
        elif status == 'synced':
            log.info('Synced superuser "%s" on startup (%s).', username, ', '.join(fields))
    except Exception as exc:  # noqa: BLE001
        log.warning('Startup superuser sync skipped: %s', exc)
    finally:
        try:
            close_old_connections()
        except Exception:  # noqa: BLE001
            pass


class Command(BaseCommand):
    help = 'Create or sync a Django superuser from DJANGO_SUPERUSER_* env vars.'

    def handle(self, *args, **options):
        status, username, update_fields = sync_env_superuser()
        if status == 'skipped':
            self.stdout.write(
                'DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set; skipping superuser sync.'
            )
        elif status == 'created':
            self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}".'))
        elif status == 'synced':
            self.stdout.write(
                self.style.SUCCESS(
                    f'Synced superuser "{username}" ({", ".join(update_fields)}).'
                )
            )
        else:
            self.stdout.write(f'Superuser "{username}" already up to date.')
