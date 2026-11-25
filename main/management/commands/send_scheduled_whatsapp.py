"""Management command to dispatch due scheduled WhatsApp messages."""

from django.core.management.base import BaseCommand

from main.whatsapp_service import run_due_scheduled_messages


class Command(BaseCommand):
    help = 'Execute all pending scheduled WhatsApp messages whose scheduled_for <= now.'

    def handle(self, *args, **options):
        summary = run_due_scheduled_messages()
        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {summary['processed']}, sent {summary['sent']}, failed {summary['failed']}"
            )
        )
