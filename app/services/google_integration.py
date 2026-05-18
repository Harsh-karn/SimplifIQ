import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required for Sheets and Drive
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_credentials():
    """Gets Google Cloud service account credentials from credentials.json."""
    cred_path = os.path.join(os.getcwd(), 'credentials.json')
    if os.path.exists(cred_path):
        try:
            return Credentials.from_service_account_file(cred_path, scopes=SCOPES)
        except Exception as e:
            print(f"Error loading Google credentials: {e}")
            return None
    return None

def log_to_sheets(name: str, email: str, company_name: str, status: str):
    """
    Appends a new row to the specified Google Sheet.
    """
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("Warning: GOOGLE_SHEET_ID not found. Skipping Google Sheets logging.")
        return
        
    creds = get_credentials()
    if not creds:
        print("Warning: credentials.json not found or invalid. Skipping Google Sheets logging.")
        return
        
    try:
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1 # Assumes first sheet
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, name, email, company_name, status]
        
        sheet.append_row(row)
        print(f"Successfully logged lead {email} to Google Sheets.")
    except Exception as e:
        print(f"Failed to log to Google Sheets: {e}")

def upload_to_drive(pdf_path: str, filename: str):
    """
    Uploads the generated PDF to a specific Google Drive folder.
    """
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        print("Warning: GOOGLE_DRIVE_FOLDER_ID not found. Skipping Google Drive upload.")
        return
        
    creds = get_credentials()
    if not creds:
        print("Warning: credentials.json not found or invalid. Skipping Google Drive upload.")
        return
        
    try:
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(pdf_path, mimetype='application/pdf', resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"Successfully uploaded PDF to Google Drive with ID: {file.get('id')}")
    except Exception as e:
        print(f"Failed to upload to Google Drive: {e}")
