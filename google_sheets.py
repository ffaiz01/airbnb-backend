"""
Google Sheets integration for writing pricing data
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, List, Optional

# Google Sheets configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Embedded Google Service Account Credentials
GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "mystic-fountain-475115-n3",
    "private_key_id": "2485cebf193356a8363bf58192cc4b395442a0e6",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCeRGPdmVvnmn4h\nPWHidiB1bp3w1n1nqX1rw65fS4q/2mUYF95zIVwpsdp+jL3mxoHQZGRLkhxu6E1g\nu/rbOu2MaBO+lYEZgZj3NpEuUUFEQ76M9616p+1VgvWZhRp7XU7chpaykssMxCw8\nj0RFiuA51SgsFoF8zc+lJQdHsWHyIgRqDy/XrBFb0ACI4B7sF1eg55X8SUWhnFJs\nhZp7RKLEz2FwxKT6jw3qzUDDPA0CqgWisqS/ThOgjhtKgSa2ZySI3qNfHaouV7R9\nPlxnWUvpcKfH87DFo22enfMMGc9eu9sbbI5XWNByZk63nYIPrLvPl/dCaBjQeZ3O\nxHW2Rc5XAgMBAAECggEAANzZv67zysRIDjJyV2G7sY+026IaB5m+RGSkYEYiBgOy\nr5vvWIqbXR6Vel94BnhsENg0qLFEUOGCOf9ojeJt70r+4ffzPtlY4VgX61Kn1D6M\naDzk6dWZjvDi7IqojPFc+EW0PtJ5bqLpd0ndkv4OoCITuoK8MG3KxTOfPAHtWDjT\nSatOYKIyDtK391zKXLD0JkViHV/SyA3hwwybjY7ISF3zxVhxSjmhz0JFgsaXwfLo\n2DCShyMCV1kKFBlcXNpw+pNwgAL1CAfK7tZuLSVInFas6ZUiOJWm0DZr0EuBNXtb\nRHrBxdMGH7vsF/Z4LhQ1T4NqQ8adGPiG01Dir4g+iQKBgQDNpjnC9g3eXk3ioDAI\n/TzGeDX0y1p7lsWWCFWrpXU99voH9Z1KBkFvzHKjcDR8Q8HEUnV/ZfZsgf5koo6I\n5eCC8xHkfPxlaxfo9uArzN3uOVhZe+6Vr9cST0/phfhXQbmMU3V7ZUT7BDxvBu9G\nlMEpgUVx4PhAWteFcziR9ZvCtQKBgQDFBFMtxzLNN7bVY3IFnI3VtWadUW9/5bCM\nw8e4AEWJ6zcBYIc4qyNQAF3bV0FFaHpBXmYcaPna9zZLfHepACGqrZHi+yMCIF3V\nsiiEn+1l4i3rY0xGlDl16/23Jesb7r2Q3orEzCiGsRzjL+BrZTpUqnTTGhLGwfKr\nq+NQwhA4WwKBgF5TXDMcgQf54WeNafr1jKbMBJOfooUFhuNmN0VfwwMFAXIdKmQF\nsoYBFKP6l1hYC8xsthAVSI5Eodau6QnJxszJiO9wlKRAFtt4QSJV+YWHMAr7WVe3\nK8LuNg06scn0D5NZxI0wyg8Ixl92otGQ8XiEHsI5GiUKhchkLRJlwWfxAoGBAL3h\nVDVrpeepiboRtSP5Za2RvotioD645bZVPph1EpBBNWtLWCfisQ76u3qZltvJPQLh\nczJwblZ+KkMIe99StB/mVxNXDb+P6D/8DBb+d/PY0H7r3eisFNE1F/s7PWRXbTZB\ndacESQ6/hmLjkryO/G/7NMr8dxo+dJ7F9DiyQKW/AoGBAIYc8e8Xx3XbncA1r+Sk\nKqbkbXDHGiKrRTEFDqTHbq2YKK3v76/Gu1kYmqICI0dbeXnO/4k2LY3soOjYYKf5\n3CDv9m59G8UrXo5C58yontjd0pn6AuG6a+vBolBY4cA1WdCJV4apc8w8MU2fjHCE\npivvaHcxYUk3OfNyvSrjVjhy\n-----END PRIVATE KEY-----\n",
    "client_email": "wasifali@mystic-fountain-475115-n3.iam.gserviceaccount.com",
    "client_id": "116011004154147736219",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/wasifali%40mystic-fountain-475115-n3.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Google Sheets configuration
SPREADSHEET_ID = '1yBOYJHltGzbnuvaLyqQChTQDHuNTtBU11uj9bA8oyXE'
WORKSHEET_NAME = 'Sheet1'

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
            if not SPREADSHEET_ID:
                print("⚠️ [Google Sheets] SPREADSHEET_ID not set")
                print("⚠️ [Google Sheets] Google Sheets integration disabled")
                return
            
            # Try to read from credentials.json first, fallback to embedded credentials
            import json
            import os
            
            creds_data = None
            script_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(script_dir, 'credentials.json')
            
            if os.path.exists(credentials_path):
                try:
                    with open(credentials_path, 'r') as f:
                        creds_data = json.load(f)
                    print(f"✅ [Google Sheets] Loaded credentials from credentials.json")
                except Exception as e:
                    print(f"⚠️ [Google Sheets] Error reading credentials.json: {e}")
                    print("🔄 [Google Sheets] Falling back to embedded credentials...")
            
            # Use embedded credentials if file not found or failed to load
            if creds_data is None:
                print("📝 [Google Sheets] Using embedded credentials (credentials.json not found)")
                creds_data = GOOGLE_CREDENTIALS
            
            # Create credentials object
            creds = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
            self.worksheet = self._get_or_create_worksheet()
            self.enabled = True
            print(f"✅ [Google Sheets] Connected to spreadsheet: {SPREADSHEET_ID}")
        except Exception as e:
            print(f"❌ [Google Sheets] Error connecting: {e}")
            import traceback
            traceback.print_exc()
            print("⚠️ [Google Sheets] Google Sheets integration disabled")
            self.client = None
            self.enabled = False
    
    def _get_or_create_worksheet(self):
        """Get existing worksheet or create new one"""
        try:
            worksheet = self.spreadsheet.worksheet(WORKSHEET_NAME)
            print(f"✅ [Google Sheets] Found existing worksheet: {WORKSHEET_NAME}")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=10)
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
        
        # Process 1-night prices (include even if price is 0)
        if pricing_data.get('oneNight'):
            for item in pricing_data['oneNight']:
                checkin = item.get('checkin', '')
                checkout = item.get('checkout', '')
                price = item.get('price', 0)
                if checkin and checkout:
                    price_per_night = price / 1 if price > 0 else 0
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
        
        # Process 2-night prices (include even if price is 0)
        if pricing_data.get('twoNights'):
            for item in pricing_data['twoNights']:
                checkin = item.get('checkin', '')
                checkout = item.get('checkout', '')
                price = item.get('price', 0)
                if checkin and checkout:
                    price_per_night = price / 2 if price > 0 else 0
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
        
        # Process 3-night prices (include even if price is 0)
        if pricing_data.get('threeNights'):
            for item in pricing_data['threeNights']:
                checkin = item.get('checkin', '')
                checkout = item.get('checkout', '')
                price = item.get('price', 0)
                if checkin and checkout:
                    price_per_night = price / 3 if price > 0 else 0
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
        
        # Process 14-night price (include even if price is 0)
        if pricing_data.get('fourteenNights'):
            item = pricing_data['fourteenNights']
            checkin = item.get('checkin', '')
            checkout = item.get('checkout', '')
            price = item.get('price', 0)
            if checkin and checkout:
                price_per_night = price / 14 if price > 0 else 0
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
        
        # Process 30-night price (include even if price is 0)
        if pricing_data.get('thirtyNights'):
            item = pricing_data['thirtyNights']
            checkin = item.get('checkin', '')
            checkout = item.get('checkout', '')
            price = item.get('price', 0)
            if checkin and checkout:
                price_per_night = price / 30 if price > 0 else 0
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
                # Check actual data (not row_count, which includes empty allocated rows)
                existing_data = self.worksheet.get_all_values()
                expected_headers = ['Timestamp', 'Search Name', 'URL', 'Checkin Date', 'Checkout Date', 'Nights', 'Price', 'Price Per Night', 'Cleaning Fee', 'Total']
                
                # Check if sheet is empty or doesn't have correct headers
                needs_headers = False
                if len(existing_data) == 0:
                    # Sheet is completely empty
                    needs_headers = True
                    print(f"📋 [Google Sheets] Sheet is empty, will add headers as first row")
                else:
                    # Check if first row has correct headers
                    existing_headers = existing_data[0] if existing_data else []
                    if existing_headers != expected_headers:
                        needs_headers = True
                        print(f"📋 [Google Sheets] Headers missing or incorrect, will add headers as first row in new data")
                
                # Prepare rows to append
                rows_to_append = rows_to_add.copy()
                
                # If headers are needed, add them as the first row
                if needs_headers:
                    rows_to_append.insert(0, expected_headers)
                    print(f"📋 [Google Sheets] Added headers as first row in new data batch")
                
                # If sheet already has data rows (beyond potential headers), add separator at start of new batch
                if len(existing_data) > 0:
                    # Add empty separator row at the start of new data batch (before headers if headers were added)
                    empty_row = ['-'] * 10  # Use dashes for visible separator
                    rows_to_append.insert(0, empty_row)
                    print(f"✅ [Google Sheets] Added empty separator row at start of new data batch")
                
                # Append all rows (separator + headers + data, or separator + data, or headers + data, or just data)
                self.worksheet.append_rows(rows_to_append)
                print(f"✅ [Google Sheets] Wrote {len(rows_to_append)} rows to Google Sheets ({len(rows_to_add)} data rows + {'1 header row' if needs_headers else '0 header rows'})")
            except Exception as e:
                print(f"❌ [Google Sheets] Error writing data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ [Google Sheets] No pricing data to write (all prices are 0)")

# Global instance
sheets_writer = GoogleSheetsWriter()
