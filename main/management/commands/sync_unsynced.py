from django.core.management.base import BaseCommand
from django.utils import timezone

from ...google_sheets import _configured, sync_to_google_sheets
from ...models import (
    CareerApplication,
    ContactMessage,
    CourseEnrollment,
    ProposalRequest,
    ServiceInquiry,
    Subscriber,
    SupportTicket,
    SyllabusDownload,
)


class Command(BaseCommand):
    help = 'Sync unsynced records to Google Sheets (and local CSV backup)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=[
                'all', 'syllabi', 'contacts', 'subscribers', 'inquiries',
                'proposals', 'applications', 'tickets', 'enrollments',
            ],
            default='syllabi',
            help='Specify which model to sync (default: unsynced syllabus downloads)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='sync_all',
            help='Sync recent records across all models in addition to unsynced syllabi',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of records per model to sync',
        )

    def handle(self, *args, **options):
        model_type = options['model']
        sync_all = options['sync_all'] or model_type == 'all'
        limit = options['limit']

        if not _configured():
            self.stdout.write(self.style.WARNING(
                'Google Sheets credentials or GOOGLE_SHEET_ID not configured. '
                'Skipping remote Google Sheets sync (local CSV backups remain active).'
            ))
            return

        self.stdout.write(self.style.SUCCESS('Syncing records to Google Sheets...'))
        synced_count = 0
        failed_count = 0

        if model_type in ('syllabi', 'all') or sync_all:
            unsynced = SyllabusDownload.objects.filter(synced_to_google=False)[:limit]
            for obj in unsynced:
                if sync_to_google_sheets('syllabus_downloads', obj):
                    SyllabusDownload.objects.filter(pk=obj.pk).update(synced_to_google=True)
                    synced_count += 1
                else:
                    failed_count += 1

        extra_targets = [
            ('contacts', 'contact_messages', ContactMessage),
            ('subscribers', 'subscribers', Subscriber),
            ('inquiries', 'service_inquiries', ServiceInquiry),
            ('proposals', 'proposal_requests', ProposalRequest),
            ('applications', 'career_applications', CareerApplication),
            ('tickets', 'support_tickets', SupportTicket),
            ('enrollments', 'course_enrollments', CourseEnrollment),
        ]

        for key, sheet_name, model_cls in extra_targets:
            if sync_all or model_type == key:
                for obj in model_cls.objects.all()[:limit]:
                    if sync_to_google_sheets(sheet_name, obj):
                        synced_count += 1
                    else:
                        failed_count += 1

        self.stdout.write(self.style.SUCCESS(f'Sync completed at {timezone.now()}'))
        self.stdout.write(self.style.SUCCESS(f'Successfully synced: {synced_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.WARNING(f'Failed to sync: {failed_count}'))
