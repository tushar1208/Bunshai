import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create or sync a Django superuser from DJANGO_SUPERUSER_* env vars.'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '').strip()

        if not (username and password):
            self.stdout.write(
                'DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set; skipping superuser sync.'
            )
            return

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is None:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}".'))
            return

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
            self.stdout.write(
                self.style.SUCCESS(
                    f'Synced superuser "{username}" ({", ".join(update_fields)}).'
                )
            )
        else:
            self.stdout.write(f'Superuser "{username}" already up to date.')
