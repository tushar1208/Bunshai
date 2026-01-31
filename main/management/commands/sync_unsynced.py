from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import (
    ContactMessage, Subscriber, ServiceInquiry, 
    ProposalRequest, CareerApplication
)
from ...google_sheets import sync_to_google_sheets

class Command(BaseCommand):
    help = 'Sync unsynced records to Google Sheets'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['all', 'contacts', 'subscribers', 'inquiries', 'proposals', 'applications'],
            default='all',
            help='Specify which model to sync'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of records to sync'
        )
    
    def handle(self, *args, **options):
        model_type = options['model']
        limit = options['limit']
        
        self.stdout.write(self.style.SUCCESS(f'Syncing {model_type} records to Google Sheets...'))
        
        synced_count = 0
        failed_count = 0
        
        # Sync based on model type
        if model_type in ['all', 'contacts']:
            contacts = ContactMessage.objects.filter(synced_to_google=False)[:limit]
            for contact in contacts:
                if sync_to_google_sheets('contact_messages', contact):
                    synced_count += 1
                else:
                    failed_count += 1
        
        if model_type in ['all', 'subscribers']:
            subscribers = Subscriber.objects.filter(synced_to_google=False)[:limit]
            for subscriber in subscribers:
                if sync_to_google_sheets('subscribers', subscriber):
                    synced_count += 1
                else:
                    failed_count += 1
        
        if model_type in ['all', 'inquiries']:
            inquiries = ServiceInquiry.objects.filter(synced_to_google=False)[:limit]
            for inquiry in inquiries:
                if sync_to_google_sheets('service_inquiries', inquiry):
                    synced_count += 1
                else:
                    failed_count += 1
        
        if model_type in ['all', 'proposals']:
            proposals = ProposalRequest.objects.filter(synced_to_google=False)[:limit]
            for proposal in proposals:
                if sync_to_google_sheets('proposal_requests', proposal):
                    synced_count += 1
                else:
                    failed_count += 1
        
        if model_type in ['all', 'applications']:
            applications = CareerApplication.objects.filter(synced_to_google=False)[:limit]
            for application in applications:
                if sync_to_google_sheets('career_applications', application):
                    synced_count += 1
                else:
                    failed_count += 1
        
        # Output results
        self.stdout.write(self.style.SUCCESS(f'Sync completed at {timezone.now()}'))
        self.stdout.write(self.style.SUCCESS(f'Successfully synced: {synced_count}'))
        
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'Failed to sync: {failed_count}'))
            self.stdout.write(self.style.WARNING(
                'Check your Google Sheets configuration and credentials.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('All records synced successfully!'))