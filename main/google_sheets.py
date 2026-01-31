import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_google_sheet():
    """Initialize and return Google Sheets client"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            settings.GOOGLE_SHEETS_CREDENTIALS, scope
        )
        
        client = gspread.authorize(creds)
        return client.open_by_key(settings.GOOGLE_SHEET_ID)
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets: {str(e)}")
        return None

def save_to_google_sheet(sheet_name, data):
    """Save form data to Google Sheets"""
    try:
        sheet = get_google_sheet()
        if not sheet:
            return False
        
        worksheet = sheet.worksheet(sheet_name)
        
        # Prepare row data
        row_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('name', ''),
            data.get('email', ''),
            data.get('phone', ''),
            str(data)
        ]
        
        # Append to sheet
        worksheet.append_row(row_data)
        logger.info(f"Data saved to Google Sheets: {sheet_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save to Google Sheets: {str(e)}")
        return False

def initialize_google_sheets():
    """Create sheets if they don't exist"""
    try:
        sheet = get_google_sheet()
        if not sheet:
            return False
        
        sheets_to_create = [
            'contact_messages',
            'service_inquiries',
            'proposal_requests',
            'career_applications',
            'subscribers',
            'chatbot_sessions'
        ]
        
        for sheet_name in sheets_to_create:
            try:
                sheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                
                # Add headers
                worksheet = sheet.worksheet(sheet_name)
                headers = ['Timestamp', 'Name', 'Email', 'Phone', 'Data']
                worksheet.append_row(headers)
                
            except gspread.exceptions.WorksheetNotFound:
                pass  # Sheet already exists
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets: {str(e)}")
        return False