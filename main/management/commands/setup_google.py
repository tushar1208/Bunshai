from django.core.management.base import BaseCommand
from django.conf import settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

class Command(BaseCommand):
    help = 'Setup Google Sheets integration by creating required sheets'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sheet-id',
            type=str,
            help='Google Sheet ID (optional, will use from settings if not provided)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Google Sheets integration...'))
        
        sheet_id = options.get('sheet_id') or settings.GOOGLE_SHEET_ID
        if not sheet_id:
            self.stderr.write(self.style.ERROR(
                'Google Sheet ID not found. Please provide --sheet-id or set GOOGLE_SHEET_ID in settings.'
            ))
            return
        
        try:
            # Initialize Google Sheets client
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds_path = settings.GOOGLE_SHEETS_CREDENTIALS
            if hasattr(settings, 'GOOGLE_SHEETS_JSON'):
                creds_info = json.loads(settings.GOOGLE_SHEETS_JSON)
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
            else:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            
            client = gspread.authorize(credentials)
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(sheet_id)
            self.stdout.write(self.style.SUCCESS(f'Connected to spreadsheet: {spreadsheet.title}'))
            
            # Define sheets to create
            sheets_config = {
                'Contact Messages': [
                    ['Timestamp', 'Name', 'Email', 'Phone', 'Company', 'Subject', 'Service', 'Message', 'IP Address', 'Date', 'Status']
                ],
                'Subscribers': [
                    ['Timestamp', 'Email', 'Name', 'IP Address', 'Subscription Date', 'Status', 'Verified']
                ],
                'Service Inquiries': [
                    ['Timestamp', 'Name', 'Email', 'Phone', 'Company', 'Service', 'Message', 'IP Address', 'Date', 'Status']
                ],
                'Proposal Requests': [
                    ['Timestamp', 'Name', 'Email', 'Phone', 'Service', 'Budget', 'Requirements', 'IP Address', 'Date', 'Status']
                ],
                'Career Applications': [
                    ['Timestamp', 'Name', 'Email', 'Phone', 'LinkedIn', 'Position', 'Cover Letter', 'Resume', 'IP Address', 'Date', 'Status']
                ],
                'Chatbot Sessions': [
                    ['Timestamp', 'Session ID', 'Name', 'Email', 'Phone', 'IP Address', 'Messages Count', 'Last Active', 'Status']
                ]
            }
            
            # Create or update sheets
            for sheet_name, headers in sheets_config.items():
                try:
                    worksheet = spreadsheet.worksheet(sheet_name)
                    self.stdout.write(self.style.WARNING(f'Sheet "{sheet_name}" already exists'))
                    
                    # Check if headers match
                    existing_headers = worksheet.row_values(1)
                    if existing_headers != headers[0]:
                        self.stdout.write(self.style.WARNING(
                            f'Headers mismatch for "{sheet_name}". Expected: {headers[0]}, Found: {existing_headers}'
                        ))
                        
                        # Ask for confirmation to update headers
                        if input(f'Update headers for "{sheet_name}"? (y/n): ').lower() == 'y':
                            worksheet.clear()
                            worksheet.append_row(headers[0])
                            self.stdout.write(self.style.SUCCESS(f'Updated headers for "{sheet_name}"'))
                    
                except gspread.exceptions.WorksheetNotFound:
                    # Create new worksheet
                    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
                    worksheet.append_row(headers[0])
                    self.stdout.write(self.style.SUCCESS(f'Created sheet: {sheet_name}'))
            
            # Format the sheets
            self.format_spreadsheet(spreadsheet)
            
            self.stdout.write(self.style.SUCCESS('Google Sheets setup completed successfully!'))
            
            # Print sharing instructions
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('Next steps:'))
            self.stdout.write('1. Share the spreadsheet with team.bunshailogicloop@gmail.com')
            self.stdout.write('2. Grant "Editor" access')
            self.stdout.write('3. Test form submissions to verify data sync')
            self.stdout.write('='*50)
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error setting up Google Sheets: {str(e)}'))
    
    def format_spreadsheet(self, spreadsheet):
        """Apply basic formatting to the spreadsheet"""
        try:
            # Format each worksheet
            for worksheet in spreadsheet.worksheets():
                # Freeze header row
                worksheet.freeze(rows=1)
                
                # Format header row
                header_format = {
                    "backgroundColor": {
                        "red": 0.2,
                        "green": 0.2,
                        "blue": 0.2
                    },
                    "textFormat": {
                        "foregroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        },
                        "bold": True,
                        "fontSize": 11
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE"
                }
                
                worksheet.format('A1:Z1', header_format)
                
                # Auto-resize columns
                self.resize_columns(worksheet)
                
                # Add filters
                worksheet.set_basic_filter()
            
            self.stdout.write(self.style.SUCCESS('Applied formatting to spreadsheet'))
            
        except Exception as e:
            self.stderr.write(self.style.WARNING(f'Could not format spreadsheet: {str(e)}'))
    
    def resize_columns(self, worksheet):
        """Auto-resize columns based on content"""
        try:
            # Get all values
            all_values = worksheet.get_all_values()
            
            if not all_values:
                return
            
            # Calculate max width for each column
            col_widths = []
            for col_idx in range(len(all_values[0])):
                max_len = 0
                for row_idx, row in enumerate(all_values):
                    if row_idx == 0:  # Header row
                        cell_len = len(str(row[col_idx])) + 5
                    else:
                        cell_len = len(str(row[col_idx])) + 2
                    max_len = max(max_len, cell_len)
                
                # Limit max width
                max_len = min(max_len, 50)
                col_widths.append(max_len)
            
            # Apply column widths
            for i, width in enumerate(col_widths):
                col_letter = chr(65 + i)  # A, B, C, etc.
                worksheet.update_column_width(i + 1, width)
                
        except Exception as e:
            # Some versions of gspread don't support update_column_width
            self.stderr.write(self.style.WARNING(f'Could not resize columns: {str(e)}'))