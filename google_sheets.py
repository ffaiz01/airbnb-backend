"""
Google Sheets integration for writing pricing data
"""
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
from typing import Dict, List, Optional

# Google Sheets configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Environment variables
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID', '1yBOYJHltGzbnuvaLyqQChTQDHuNTtBU11uj9bA8oyXE')
WORKSHEET_NAME = os.getenv('GOOGLE_WORKSHEET_NAME', 'Sheet1')

class GoogleSheetsWriter:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.enabled = False
        self._connect()
    
    def _connect(self):
        """Connect to Google Sheets API"""
        try:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"⚠️ [Google Sheets] Credentials file not found: {CREDENTIALS_FILE}")
                print("⚠️ [Google Sheets] Google Sheets integration disabled")
                return
            
            if not SPREADSHEET_ID:
                print("⚠️ [Google Sheets] SPREADSHEET_ID not set in environment variables")
                print("⚠️ [Google Sheets] Google Sheets integration disabled")
                return
            
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
            self.worksheet = self._get_or_create_worksheet()
            self.enabled = True
            print(f"✅ [Google Sheets] Connected to spreadsheet: {SPREADSHEET_ID}")
        except Exception as e:
            print(f"❌ [Google Sheets] Error connecting: {e}")
            print("⚠️ [Google Sheets] Google Sheets integration disabled")
            self.client = None
            self.enabled = False
    
    def _get_or_create_worksheet(self):
        """Get existing worksheet or create new one"""
        try:
            worksheet = self.spreadsheet.worksheet(WORKSHEET_NAME)
            # Check if headers exist (check first row)
            existing_headers = worksheet.row_values(1)
            expected_headers = ['Timestamp', 'Search Name', 'URL', 'Checkin Date', 'Checkout Date', 'Nights', 'Price', 'Price Per Night', 'Cleaning Fee', 'Total']
            
            if not existing_headers or existing_headers != expected_headers:
                # Add headers if they don't exist or don't match
                if not existing_headers:
                    worksheet.append_row(expected_headers)
                    print(f"✅ [Google Sheets] Added headers to worksheet: {WORKSHEET_NAME}")
                else:
                    print(f"⚠️ [Google Sheets] Worksheet headers don't match expected format, but continuing...")
            else:
                print(f"✅ [Google Sheets] Using existing worksheet with headers: {WORKSHEET_NAME}")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=10)
            # Add headers
            headers = ['Timestamp', 'Search Name', 'URL', 'Checkin Date', 'Checkout Date', 'Nights', 'Price', 'Price Per Night', 'Cleaning Fee', 'Total']
            worksheet.append_row(headers)
            print(f"✅ [Google Sheets] Created new worksheet: {WORKSHEET_NAME}")
        return worksheet
    
    def write_pricing_data(self, search_name: str, url: str, cleaning_fee: float, pricing_data: Dict, timestamp: Optional[datetime] = None):
        """
        Write pricing data to Google Sheets
        
        Args:
            search_name: Name of the search
            url: Airbnb URL
            cleaning_fee: Cleaning fee amount
            pricing_data: Dictionary with pricing data (oneNight, twoNights, etc.)
            timestamp: When the data was scraped (defaults to now)
        """
        if not self.enabled or not self.worksheet:
            print("⚠️ [Google Sheets] Not connected, skipping write")
            return
        
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        rows_to_add = []
        
        # Process 1-night prices
        if pricing_data.get('oneNight'):
            for item in pricing_data['oneNight']:
                checkin = item.get('checkin', '')
                checkout = item.get('checkout', '')
                price = item.get('price', 0)
                if checkin and checkout and price > 0:
                    price_per_night = price / 1
                    total = price + cleaning_fee
                    rows_to_add.append([
                        timestamp_str,
                        search_name,
                        url,
                        checkin,
                        checkout,
                        '1N',
                        price,
                        price_per_night,
                        cleaning_fee,
                        total
                    ])
        
        # Process 2-night prices
        if pricing_data.get('twoNights'):
            for item in pricing_data['twoNights']:
                checkin = item.get('checkin', '')
                checkout = item.get('checkout', '')
                price = item.get('price', 0)
                if checkin and checkout and price > 0:
                    price_per_night = price / 2
                    total = price + cleaning_fee
                    rows_to_add.append([
                        timestamp_str,
                        search_name,
                        url,
                        checkin,
                        checkout,
                        '2N',
                        price,
                        price_per_night,
                        cleaning_fee,
                        total
                    ])
        
        # Process 3-night prices
        if pricing_data.get('threeNights'):
            for item in pricing_data['threeNights']:
                checkin = item.get('checkin', '')
                checkout = item.get('checkout', '')
                price = item.get('price', 0)
                if checkin and checkout and price > 0:
                    price_per_night = price / 3
                    total = price + cleaning_fee
                    rows_to_add.append([
                        timestamp_str,
                        search_name,
                        url,
                        checkin,
                        checkout,
                        '3N',
                        price,
                        price_per_night,
                        cleaning_fee,
                        total
                    ])
        
        # Process 14-night price
        if pricing_data.get('fourteenNights'):
            item = pricing_data['fourteenNights']
            checkin = item.get('checkin', '')
            checkout = item.get('checkout', '')
            price = item.get('price', 0)
            if checkin and checkout and price > 0:
                price_per_night = price / 14
                total = price + cleaning_fee
                rows_to_add.append([
                    timestamp_str,
                    search_name,
                    url,
                    checkin,
                    checkout,
                    '14N',
                    price,
                    price_per_night,
                    cleaning_fee,
                    total
                ])
        
        # Process 30-night price
        if pricing_data.get('thirtyNights'):
            item = pricing_data['thirtyNights']
            checkin = item.get('checkin', '')
            checkout = item.get('checkout', '')
            price = item.get('price', 0)
            if checkin and checkout and price > 0:
                price_per_night = price / 30
                total = price + cleaning_fee
                rows_to_add.append([
                    timestamp_str,
                    search_name,
                    url,
                    checkin,
                    checkout,
                    '30N',
                    price,
                    price_per_night,
                    cleaning_fee,
                    total
                ])
        
        # Write all rows at once
        if rows_to_add:
            try:
                self.worksheet.append_rows(rows_to_add)
                print(f"✅ [Google Sheets] Wrote {len(rows_to_add)} rows to Google Sheets")
            except Exception as e:
                print(f"❌ [Google Sheets] Error writing data: {e}")
        else:
            print("⚠️ [Google Sheets] No pricing data to write (all prices are 0)")

# Global instance
sheets_writer = GoogleSheetsWriter()
