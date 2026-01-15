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
        print("🔌 [Google Sheets] Starting connection process...")
        try:
            # Check SPREADSHEET_ID
            if not SPREADSHEET_ID:
                print("⚠️ [Google Sheets] SPREADSHEET_ID not set")
                print("⚠️ [Google Sheets] Google Sheets integration disabled")
                self.enabled = False
                return
            
            print(f"📋 [Google Sheets] SPREADSHEET_ID: {SPREADSHEET_ID}")
            print(f"📋 [Google Sheets] WORKSHEET_NAME: {WORKSHEET_NAME}")
            
            # Try to read from credentials.json first, fallback to embedded credentials
            import json
            import os
            
            # Try multiple possible locations for credentials.json (important for Docker)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            current_dir = os.getcwd()
            possible_paths = [
                os.path.join(script_dir, 'credentials.json'),  # Same directory as script (best for Docker)
                'credentials.json',  # Current working directory
                os.path.join(current_dir, 'credentials.json'),  # Explicit current directory
                '/app/credentials.json',  # Common Docker working directory
            ]
            
            print(f"📂 [Google Sheets] Script directory: {script_dir}")
            print(f"📂 [Google Sheets] Current working directory: {current_dir}")
            
            creds_data = None
            credentials_path = None
            
            for path in possible_paths:
                print(f"🔍 [Google Sheets] Checking for credentials.json at: {path}")
                if os.path.exists(path):
                    credentials_path = path
                    print(f"📁 [Google Sheets] Found credentials.json at: {path}")
                    try:
                        with open(path, 'r') as f:
                            creds_data = json.load(f)
                        print(f"✅ [Google Sheets] Successfully loaded credentials from {path}")
                        break
                    except Exception as e:
                        print(f"⚠️ [Google Sheets] Error reading {path}: {e}")
                        print("🔄 [Google Sheets] Trying next location...")
                        creds_data = None
            
            if not credentials_path:
                print("⚠️ [Google Sheets] credentials.json not found in any of the checked locations")
                print(f"   Checked locations: {possible_paths}")
                print("🔄 [Google Sheets] Falling back to embedded credentials...")
            
            if creds_data is None:
                print("📝 [Google Sheets] Using embedded credentials...")
                creds_data = GOOGLE_CREDENTIALS
                if not creds_data or not creds_data.get('private_key'):
                    print("❌ [Google Sheets] Embedded credentials are missing or invalid")
                    self.enabled = False
                    return
            
            # Check required fields in credentials
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if not creds_data.get(field)]
            if missing_fields:
                print(f"❌ [Google Sheets] Missing required credential fields: {missing_fields}")
                self.enabled = False
                return
            
            print(f"✅ [Google Sheets] Credentials loaded - Project ID: {creds_data.get('project_id')}")
            print(f"✅ [Google Sheets] Client Email: {creds_data.get('client_email')}")
            
            # Create credentials object
            print("🔐 [Google Sheets] Creating credentials object...")
            creds = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
            print("✅ [Google Sheets] Credentials object created")
            
            # Authorize gspread client
            print("🔑 [Google Sheets] Authorizing gspread client...")
            self.client = gspread.authorize(creds)
            print("✅ [Google Sheets] gspread client authorized")
            
            # Open spreadsheet
            print(f"📊 [Google Sheets] Opening spreadsheet: {SPREADSHEET_ID}...")
            self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
            print(f"✅ [Google Sheets] Spreadsheet opened: {self.spreadsheet.title}")
            
            # Get or create worksheet
            print(f"📄 [Google Sheets] Getting/creating worksheet: {WORKSHEET_NAME}...")
            self.worksheet = self._get_or_create_worksheet()
            print(f"✅ [Google Sheets] Worksheet ready: {WORKSHEET_NAME}")
            
            self.enabled = True
            print(f"✅ [Google Sheets] Successfully connected to spreadsheet: {SPREADSHEET_ID}")
        except FileNotFoundError as e:
            print(f"❌ [Google Sheets] File not found: {e}")
            print("⚠️ [Google Sheets] Google Sheets integration disabled")
            self.client = None
            self.enabled = False
        except gspread.exceptions.SpreadsheetNotFound as e:
            print(f"❌ [Google Sheets] Spreadsheet not found: {e}")
            print(f"❌ [Google Sheets] Check if SPREADSHEET_ID is correct: {SPREADSHEET_ID}")
            print("⚠️ [Google Sheets] Google Sheets integration disabled")
            self.client = None
            self.enabled = False
        except gspread.exceptions.APIError as e:
            print(f"❌ [Google Sheets] API Error: {e}")
            print(f"❌ [Google Sheets] Error details: {e.response}")
            print("⚠️ [Google Sheets] Google Sheets integration disabled")
            self.client = None
            self.enabled = False
        except Exception as e:
            print(f"❌ [Google Sheets] Unexpected error connecting: {type(e).__name__}: {e}")
            import traceback
            print("📋 [Google Sheets] Full traceback:")
            traceback.print_exc()
            print("⚠️ [Google Sheets] Google Sheets integration disabled")
            self.client = None
            self.enabled = False
    
    def _get_or_create_worksheet(self):
        """Get existing worksheet or create new one"""
        print(f"🔍 [Google Sheets] Looking for worksheet: {WORKSHEET_NAME}...")
        try:
            worksheet = self.spreadsheet.worksheet(WORKSHEET_NAME)
            print(f"✅ [Google Sheets] Found existing worksheet: {WORKSHEET_NAME}")
            
            # Check if headers exist (check first row)
            print(f"📋 [Google Sheets] Checking headers in row 1...")
            existing_headers = worksheet.row_values(1)
            print(f"📋 [Google Sheets] Existing headers: {existing_headers}")
            
            expected_headers = ['Timestamp', 'Search Name', 'URL', 'Checkin Date', 'Checkout Date', 'Nights', 'Price', 'Price Per Night', 'Cleaning Fee', 'Total']
            print(f"📋 [Google Sheets] Expected headers: {expected_headers}")
            
            if not existing_headers or existing_headers != expected_headers:
                # Add headers if they don't exist or don't match
                if not existing_headers:
                    print(f"📝 [Google Sheets] No headers found, adding headers...")
                    worksheet.append_row(expected_headers)
                    print(f"✅ [Google Sheets] Added headers to worksheet: {WORKSHEET_NAME}")
                else:
                    print(f"⚠️ [Google Sheets] Worksheet headers don't match expected format, but continuing...")
                    print(f"   Existing: {existing_headers}")
                    print(f"   Expected: {expected_headers}")
            else:
                print(f"✅ [Google Sheets] Using existing worksheet with correct headers: {WORKSHEET_NAME}")
        except gspread.exceptions.WorksheetNotFound:
            print(f"📄 [Google Sheets] Worksheet '{WORKSHEET_NAME}' not found, creating new one...")
            worksheet = self.spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=10)
            print(f"✅ [Google Sheets] Created new worksheet: {WORKSHEET_NAME}")
            # Add headers
            headers = ['Timestamp', 'Search Name', 'URL', 'Checkin Date', 'Checkout Date', 'Nights', 'Price', 'Price Per Night', 'Cleaning Fee', 'Total']
            print(f"📝 [Google Sheets] Adding headers to new worksheet...")
            worksheet.append_row(headers)
            print(f"✅ [Google Sheets] Headers added to new worksheet")
        except Exception as e:
            print(f"❌ [Google Sheets] Error in _get_or_create_worksheet: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
        
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
        print(f"📝 [Google Sheets] write_pricing_data called for: {search_name}")
        print(f"📊 [Google Sheets] Enabled: {self.enabled}, Worksheet: {self.worksheet is not None}")
        
        if not self.enabled:
            print("⚠️ [Google Sheets] Not enabled, skipping write")
            print(f"   Reason: Google Sheets integration was disabled during initialization")
            return
        
        if not self.worksheet:
            print("⚠️ [Google Sheets] Worksheet not available, skipping write")
            print(f"   Reason: Worksheet was not created or connection failed")
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
                # Check actual data (not row_count, which includes empty allocated rows)
                existing_data = self.worksheet.get_all_values()
                
                # If sheet already has data rows (beyond headers)
                if len(existing_data) > 1:
                    # Insert empty separator row right after the last data row
                    empty_row = ['-'] * 10  # Use dashes for visible separator
                    self.worksheet.insert_row(empty_row, len(existing_data) + 1)
                    print(f"✅ [Google Sheets] Added empty separator row after row {len(existing_data)}")
                
                # Append data rows (they will be added after headers or after empty separator)
                self.worksheet.append_rows(rows_to_add)
                print(f"✅ [Google Sheets] Wrote {len(rows_to_add)} rows to Google Sheets")
            except Exception as e:
                print(f"❌ [Google Sheets] Error writing data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ [Google Sheets] No pricing data to write (all prices are 0)")

# Global instance
sheets_writer = GoogleSheetsWriter()
