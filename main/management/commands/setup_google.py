import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ...google_sheets import (
    OWNER_EMAIL, SHEET_SPEC, credentials_available, get_gspread_client, initialize_google_sheets,
)


class Command(BaseCommand):
    help = ('Link the website to Google Sheets: creates (or opens) the spreadsheet, adds one worksheet per '
            'form/chatbot table with headers, and shares it with the team Gmail account.')

    def add_arguments(self, parser):
        parser.add_argument('--sheet-id', type=str, help='Existing Google Sheet ID (defaults to GOOGLE_SHEET_ID)')
        parser.add_argument('--share-with', type=str, default=OWNER_EMAIL,
                            help=f'Gmail account to share with (default {OWNER_EMAIL})')
        parser.add_argument('--title', type=str, default='BunShai TECHNOHUB - Leads & Chatbot Data',
                            help='Title when creating a new spreadsheet')

    def handle(self, *args, **options):
        if not credentials_available():
            self.stderr.write(self.style.ERROR(
                'No Google credentials found.\n'
                f'  1. Create a Google Cloud service account and download its JSON key.\n'
                f'  2. Save it as {settings.GOOGLE_SHEETS_CREDENTIALS}\n'
                '     (or put the JSON text in the GOOGLE_SHEETS_JSON environment variable).\n'
                '  3. Enable the Google Sheets API + Google Drive API for the project.\n'
                '  4. Re-run: python manage.py setup_google'))
            return

        client = get_gspread_client()
        if client is None:
            self.stderr.write(self.style.ERROR('Could not authorise with Google - check the credentials file.'))
            return

        sheet_id = options.get('sheet_id') or settings.GOOGLE_SHEET_ID
        share_with = options['share_with']
        try:
            if sheet_id:
                spreadsheet = client.open_by_key(sheet_id)
                self.stdout.write(self.style.SUCCESS(f'Opened spreadsheet: {spreadsheet.title}'))
            else:
                spreadsheet = client.create(options['title'])
                self.stdout.write(self.style.SUCCESS(f'Created spreadsheet: {spreadsheet.title}'))
                self.stdout.write(self.style.WARNING(
                    f'ADD THIS TO YOUR .env FILE ->  GOOGLE_SHEET_ID={spreadsheet.id}'))

            try:
                spreadsheet.share(share_with, perm_type='user', role='writer', notify=True)
                self.stdout.write(self.style.SUCCESS(f'Shared spreadsheet with {share_with} (editor).'))
            except Exception as e:  # noqa: BLE001
                self.stderr.write(self.style.WARNING(f'Could not share automatically ({e}). '
                                                     f'Share it manually with {share_with}.'))

            initialize_google_sheets(spreadsheet)
            for ws_name in SHEET_SPEC:
                self.stdout.write(f'  ✔ worksheet ready: {ws_name}')
            try:
                default = spreadsheet.sheet1
                if default.title in ('Sheet1', 'Sheet 1') and len(spreadsheet.worksheets()) > 1:
                    spreadsheet.del_worksheet(default)
            except Exception:  # noqa: BLE001
                pass

            self.stdout.write(self.style.SUCCESS('Google Sheets integration is ready.'))
            self.stdout.write(f'Open: https://docs.google.com/spreadsheets/d/{spreadsheet.id}')
        except Exception as e:  # noqa: BLE001
            self.stderr.write(self.style.ERROR(f'Error setting up Google Sheets: {e}'))
