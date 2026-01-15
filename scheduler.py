"""
Scheduler service for running scheduled Airbnb price searches
Uses thread pool with maximum 3 concurrent threads
"""
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo import MongoClient
from bson import ObjectId
import requests
import os
from typing import List, Dict, Optional
import pytz
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/')
NEXTJS_API_URL = os.getenv('NEXTJS_API_URL', 'http://localhost:3000')
PYTHON_API_URL = os.getenv('PYTHON_API_URL', 'http://127.0.0.1:5000')
MAX_WORKERS = 3  # Maximum concurrent threads
CHECK_INTERVAL = 60  # Check for scheduled tasks every 60 seconds

# Timezone configuration - use system local timezone or set explicitly
# For PKT (Pakistan Time): 'Asia/Karachi'
# For UTC: 'UTC'
# For system local: None (uses system default)
SCHEDULER_TIMEZONE = os.getenv('SCHEDULER_TIMEZONE', 'Asia/Karachi')  # Default to PKT
if SCHEDULER_TIMEZONE:
    try:
        TZ = pytz.timezone(SCHEDULER_TIMEZONE)
        print(f"🌍 [Scheduler] Using timezone: {SCHEDULER_TIMEZONE}")
    except Exception as e:
        print(f"⚠️ [Scheduler] Invalid timezone '{SCHEDULER_TIMEZONE}', using system default: {e}")
        TZ = None
else:
    TZ = None  # Use system local timezone
    print(f"🌍 [Scheduler] Using system local timezone")

class Scheduler:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.running_tasks = {}  # Track running tasks: {search_id: future}
        self.lock = threading.Lock()
        self.running = False
        
    def connect_db(self):
        """Connect to MongoDB"""
        try:
            # Add SSL configuration for MongoDB Atlas
            import ssl
            client = MongoClient(
                MONGODB_URI,
                tls=True,
                tlsAllowInvalidCertificates=False,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000
            )
            # Extract database name from URI or use default
            # MongoDB URI format: mongodb+srv://user:pass@host/dbname?options
            uri_parts = MONGODB_URI.rstrip('/').split('/')
            if len(uri_parts) > 3 and uri_parts[-1] and uri_parts[-1] != '':
                db_name = uri_parts[-1].split('?')[0]
            else:
                db_name = 'airbnb-price-spy'  # Default database name (matches Next.js)
            
            # Validate database name - check if it's a valid string
            if db_name == '' or db_name == MONGODB_URI or db_name is None:
                db_name = 'airbnb-price-spy'  # Default database name (matches Next.js)
            
            db = client[db_name]
            collection = db.searches
            # Test connection
            client.admin.command('ping')
            return collection
        except Exception as e:
            print(f"❌ [Scheduler] MongoDB connection error: {e}")
            return None
    
    def get_scheduled_searches(self) -> List[Dict]:
        """Get all searches with enabled schedules"""
        try:
            collection = self.connect_db()
            if collection is None:
                print("⚠️ [Scheduler] MongoDB connection failed, skipping check")
                return []
            
            searches = collection.find({
                'schedule.enabled': True
            })
            search_list = list(searches)
            if len(search_list) > 0:
                print(f"📋 [Scheduler] Found {len(search_list)} scheduled search(es)")
            return search_list
        except Exception as e:
            print(f"❌ [Scheduler] Error fetching scheduled searches: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def should_run_now(self, schedule: Dict, last_run: str) -> bool:
        """Check if a search should run now based on its schedule"""
        if not schedule or not schedule.get('enabled'):
            return False
        
        times = schedule.get('times', [])
        # Use local timezone (system default or configured TZ)
        if TZ:
            current_time = datetime.now(TZ)
        else:
            current_time = datetime.now()
        current_hour_minute = current_time.strftime('%H:%M')
        
        # Check if current time matches any enabled schedule time
        for time_slot in times:
            if time_slot.get('enabled') and time_slot.get('time') == current_hour_minute:
                # Check if we already ran in this minute (avoid duplicate runs)
                if last_run and last_run != 'Never':
                    try:
                        # Parse last run time
                        last_run_time = datetime.strptime(last_run, '%H:%M')
                        time_diff = abs((current_time - last_run_time).total_seconds())
                        # Only run if last run was more than 30 seconds ago
                        if time_diff < 30:
                            print(f"⏸️ [Scheduler] Skipping {time_slot.get('time')} - ran {int(time_diff)}s ago (last: {last_run})")
                            return False
                    except:
                        pass
                print(f"✅ [Scheduler] Time match! Current: {current_hour_minute}, Scheduled: {time_slot.get('time')}")
                return True
        
        return False
    
    def build_airbnb_url(self, base_url: str, checkin: str, checkout: str) -> str:
        """Build Airbnb URL with specific checkin/checkout dates"""
        try:
            parsed = urlparse(base_url)
            query_params = parse_qs(parsed.query)
            query_params['checkin'] = [checkin]
            query_params['checkout'] = [checkout]
            new_query = urlencode(query_params, doseq=True)
            new_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            return new_url
        except Exception as e:
            print(f"⚠️ [Scheduler] Error building URL: {e}")
            return base_url
    
    def fetch_price_from_python_api(self, url: str) -> Optional[float]:
        """Fetch lowest price from Python API"""
        try:
            response = requests.post(
                f"{PYTHON_API_URL}/api/search/simple",
                json={'url': url},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('lowest_price')
            else:
                print(f"⚠️ [Scheduler] API returned status {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️ [Scheduler] Error fetching price: {e}")
            return None
    
    def generate_date_ranges(self, start_date_str: str) -> Dict:
        """Generate date ranges for pricing data starting from a given date"""
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        ranges = {
            'oneNight': [],
            'twoNights': [],
            'threeNights': [],
            'fourteenNights': {'checkin': '', 'checkout': '', 'price': 0, 'date': ''},
            'thirtyNights': {'checkin': '', 'checkout': '', 'price': 0, 'date': ''}
        }
        
        # Generate 7 days of 1, 2, and 3-night stays
        for i in range(7):
            current_checkin = start_date + timedelta(days=i)
            ranges['oneNight'].append({
                'checkin': current_checkin.strftime('%Y-%m-%d'),
                'checkout': (current_checkin + timedelta(days=1)).strftime('%Y-%m-%d'),
                'price': 0,
                'date': current_checkin.strftime('%Y-%m-%d')
            })
            ranges['twoNights'].append({
                'checkin': current_checkin.strftime('%Y-%m-%d'),
                'checkout': (current_checkin + timedelta(days=2)).strftime('%Y-%m-%d'),
                'price': 0,
                'date': current_checkin.strftime('%Y-%m-%d')
            })
            ranges['threeNights'].append({
                'checkin': current_checkin.strftime('%Y-%m-%d'),
                'checkout': (current_checkin + timedelta(days=3)).strftime('%Y-%m-%d'),
                'price': 0,
                'date': current_checkin.strftime('%Y-%m-%d')
            })
        
        # 14-night stay (single)
        fourteen_checkin = start_date
        fourteen_checkout = start_date + timedelta(days=14)
        ranges['fourteenNights'] = {
            'checkin': fourteen_checkin.strftime('%Y-%m-%d'),
            'checkout': fourteen_checkout.strftime('%Y-%m-%d'),
            'price': 0,
            'date': fourteen_checkin.strftime('%Y-%m-%d')
        }
        
        # 30-night stay (single)
        thirty_checkin = start_date
        thirty_checkout = start_date + timedelta(days=30)
        ranges['thirtyNights'] = {
            'checkin': thirty_checkin.strftime('%Y-%m-%d'),
            'checkout': thirty_checkout.strftime('%Y-%m-%d'),
            'price': 0,
            'date': thirty_checkin.strftime('%Y-%m-%d')
        }
        
        return ranges
    
    def run_search(self, search_id: str, search_name: str) -> bool:
        """Run a single search by fetching prices directly"""
        collection = None
        try:
            print(f"🚀 [Scheduler] Starting search: {search_name} (ID: {search_id[:8]}...)")
            
            # Connect to MongoDB
            collection = self.connect_db()
            if collection is None:
                print(f"❌ [Scheduler] Failed to connect to MongoDB for {search_name}")
                return False
            
            # Get search document
            search = collection.find_one({'_id': ObjectId(search_id)})
            if not search:
                print(f"❌ [Scheduler] Search not found: {search_id}")
                return False
            
            # Get current time and today's date
            current_time = datetime.now(TZ if TZ else None)
            last_run_str = current_time.strftime('%H:%M')
            today = current_time.strftime('%Y-%m-%d')
            
            # Get base URL
            base_url = search.get('url', '')
            
            if not base_url:
                print(f"❌ [Scheduler] No URL found for {search_name}")
                collection.update_one(
                    {'_id': ObjectId(search_id)},
                    {'$set': {'status': 'error'}}
                )
                return False
            
            # STEP 1: Generate date ranges starting from today (with prices = 0)
            print(f"📅 [Scheduler] Regenerating date ranges starting from {today}")
            pricing_data = self.generate_date_ranges(today)
            
            # STEP 2: Update database immediately with new dates (prices = 0) and set status to running
            collection.update_one(
                {'_id': ObjectId(search_id)},
                {
                    '$set': {
                        'status': 'running',
                        'lastRun': last_run_str,
                        'pricingData': pricing_data,
                        'checkinDate': today
                    }
                }
            )
            print(f"📊 [Scheduler] Updated database with new dates (prices = 0) and set status to 'running' for {search_name}")
            
            # STEP 3: Now start fetching prices for all date ranges
            total_fetched = 0
            
            # 1-night prices (7 dates)
            if pricing_data.get('oneNight'):
                print(f"📅 [Scheduler] Fetching 1-night prices ({len(pricing_data['oneNight'])} dates)")
                for i, item in enumerate(pricing_data['oneNight']):
                    checkin = item.get('checkin')
                    checkout = item.get('checkout')
                    if checkin and checkout:
                        url = self.build_airbnb_url(base_url, checkin, checkout)
                        price = self.fetch_price_from_python_api(url)
                        if price is not None:
                            pricing_data['oneNight'][i]['price'] = price
                            total_fetched += 1
                            # Update MongoDB incrementally
                            collection.update_one(
                                {'_id': ObjectId(search_id)},
                                {'$set': {'pricingData': pricing_data}}
                            )
                            print(f"  ✓ [{i+1}/{len(pricing_data['oneNight'])}] {checkin} → {checkout}: {price}")
            
            # 2-night prices (7 dates)
            if pricing_data.get('twoNights'):
                print(f"📅 [Scheduler] Fetching 2-night prices ({len(pricing_data['twoNights'])} dates)")
                for i, item in enumerate(pricing_data['twoNights']):
                    checkin = item.get('checkin')
                    checkout = item.get('checkout')
                    if checkin and checkout:
                        url = self.build_airbnb_url(base_url, checkin, checkout)
                        price = self.fetch_price_from_python_api(url)
                        if price is not None:
                            pricing_data['twoNights'][i]['price'] = price
                            total_fetched += 1
                            collection.update_one(
                                {'_id': ObjectId(search_id)},
                                {'$set': {'pricingData': pricing_data}}
                            )
                            print(f"  ✓ [{i+1}/{len(pricing_data['twoNights'])}] {checkin} → {checkout}: {price}")
            
            # 3-night prices (7 dates)
            if pricing_data.get('threeNights'):
                print(f"📅 [Scheduler] Fetching 3-night prices ({len(pricing_data['threeNights'])} dates)")
                for i, item in enumerate(pricing_data['threeNights']):
                    checkin = item.get('checkin')
                    checkout = item.get('checkout')
                    if checkin and checkout:
                        url = self.build_airbnb_url(base_url, checkin, checkout)
                        price = self.fetch_price_from_python_api(url)
                        if price is not None:
                            pricing_data['threeNights'][i]['price'] = price
                            total_fetched += 1
                            collection.update_one(
                                {'_id': ObjectId(search_id)},
                                {'$set': {'pricingData': pricing_data}}
                            )
                            print(f"  ✓ [{i+1}/{len(pricing_data['threeNights'])}] {checkin} → {checkout}: {price}")
            
            # 14-night price
            if pricing_data.get('fourteenNights') and pricing_data['fourteenNights'].get('checkin'):
                print(f"📅 [Scheduler] Fetching 14-night price")
                checkin = pricing_data['fourteenNights']['checkin']
                checkout = pricing_data['fourteenNights']['checkout']
                url = self.build_airbnb_url(base_url, checkin, checkout)
                price = self.fetch_price_from_python_api(url)
                if price is not None:
                    pricing_data['fourteenNights']['price'] = price
                    total_fetched += 1
                    collection.update_one(
                        {'_id': ObjectId(search_id)},
                        {'$set': {'pricingData': pricing_data}}
                    )
                    print(f"  ✓ 14-night {checkin} → {checkout}: {price}")
            
            # 30-night price
            if pricing_data.get('thirtyNights') and pricing_data['thirtyNights'].get('checkin'):
                print(f"📅 [Scheduler] Fetching 30-night price")
                checkin = pricing_data['thirtyNights']['checkin']
                checkout = pricing_data['thirtyNights']['checkout']
                url = self.build_airbnb_url(base_url, checkin, checkout)
                price = self.fetch_price_from_python_api(url)
                if price is not None:
                    pricing_data['thirtyNights']['price'] = price
                    total_fetched += 1
                    collection.update_one(
                        {'_id': ObjectId(search_id)},
                        {'$set': {'pricingData': pricing_data}}
                    )
                    print(f"  ✓ 30-night {checkin} → {checkout}: {price}")
            
            # Update status to completed (checkinDate already set in step 2)
            collection.update_one(
                {'_id': ObjectId(search_id)},
                {
                    '$set': {
                        'status': 'completed',
                        'pricingData': pricing_data
                    }
                }
            )
            print(f"✅ [Scheduler] Completed search: {search_name} (fetched {total_fetched} prices)")
            return True
            
        except Exception as e:
            print(f"❌ [Scheduler] Error running search {search_name}: {e}")
            import traceback
            traceback.print_exc()
            # Update status to error
            if collection:
                try:
                    collection.update_one(
                        {'_id': ObjectId(search_id)},
                        {'$set': {'status': 'error'}}
                    )
                except:
                    pass
            return False
    
    def wait_for_available_slot(self):
        """Wait until there's an available slot in the thread pool"""
        while len(self.running_tasks) >= MAX_WORKERS:
            # Check if any tasks have completed
            completed_tasks = []
            for search_id, future in self.running_tasks.items():
                if future.done():
                    completed_tasks.append(search_id)
            
            # Remove completed tasks
            with self.lock:
                for search_id in completed_tasks:
                    del self.running_tasks[search_id]
            
            if len(self.running_tasks) >= MAX_WORKERS:
                time.sleep(1)  # Wait 1 second before checking again
    
    def submit_task(self, search_id: str, search_name: str):
        """Submit a search task to the thread pool"""
        # Wait for available slot if pool is full
        if len(self.running_tasks) >= MAX_WORKERS:
            print(f"⏳ [Scheduler] Thread pool full ({MAX_WORKERS} tasks), waiting for slot...")
            self.wait_for_available_slot()
        
        # Submit task to thread pool
        future = self.executor.submit(self.run_search, search_id, search_name)
        
        with self.lock:
            self.running_tasks[search_id] = future
        print(f"📤 [Scheduler] Task submitted: {search_name} (Active threads: {len(self.running_tasks)}/{MAX_WORKERS})")
    
    def check_and_run_schedules(self):
        """Check for scheduled tasks and run them"""
        try:
            # Use local timezone (system default or configured TZ)
            if TZ:
                current_time = datetime.now(TZ)
            else:
                current_time = datetime.now()
            
            current_time_str = current_time.strftime('%H:%M:%S')
            timezone_info = current_time.strftime('%Z') if TZ else 'local'
            print(f"⏰ [Scheduler] Checking schedules at {current_time_str} ({timezone_info})")
            
            searches = self.get_scheduled_searches()
            
            # Check if searches is None or empty list
            if searches is None:
                print("⚠️ [Scheduler] No searches returned (None)")
                return
            if not isinstance(searches, list):
                print(f"⚠️ [Scheduler] Invalid searches type: {type(searches)}")
                return
            if len(searches) == 0:
                print("ℹ️ [Scheduler] No scheduled searches found")
                return
            
            tasks_to_run = []
            current_hour_minute = current_time.strftime('%H:%M')
            
            for search in searches:
                search_id = str(search.get('_id'))
                search_name = search.get('name', 'Unknown')
                schedule = search.get('schedule', {})
                last_run = search.get('lastRun', 'Never')
                status = search.get('status', 'idle')
                times = schedule.get('times', [])
                
                # Log schedule details
                enabled_times = [t.get('time') for t in times if t.get('enabled')]
                if enabled_times:
                    print(f"🔍 [Scheduler] Checking '{search_name}': scheduled at {enabled_times}, current: {current_hour_minute}, status: {status}, last run: {last_run}")
                
                # Skip if already running
                if status == 'running':
                    print(f"⏸️ [Scheduler] Skipping '{search_name}' - already running")
                    continue
                
                # Check if should run now
                if self.should_run_now(schedule, last_run):
                    tasks_to_run.append((search_id, search_name))
            
            # Run tasks (will queue if pool is full)
            if len(tasks_to_run) > 0:
                print(f"📋 [Scheduler] Found {len(tasks_to_run)} task(s) to run")
                for search_id, search_name in tasks_to_run:
                    self.submit_task(search_id, search_name)
            else:
                print("ℹ️ [Scheduler] No tasks to run at this time")
        except Exception as e:
            print(f"❌ [Scheduler] Error in check_and_run_schedules: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup_completed_tasks(self):
        """Remove completed tasks from tracking"""
        completed = []
        with self.lock:
            for search_id, future in self.running_tasks.items():
                if future.done():
                    completed.append(search_id)
            for search_id in completed:
                del self.running_tasks[search_id]
                print(f"✅ [Scheduler] Task completed and removed: {search_id[:8]}... (Active: {len(self.running_tasks)}/{MAX_WORKERS})")
    
    def start(self):
        """Start the scheduler loop"""
        self.running = True
        print(f"🚀 [Scheduler] Started with max {MAX_WORKERS} concurrent threads")
        print(f"⏱️ [Scheduler] Checking for scheduled tasks every {CHECK_INTERVAL} seconds")
        
        while self.running:
            try:
                self.check_and_run_schedules()
                self.cleanup_completed_tasks()
            except Exception as e:
                print(f"❌ [Scheduler] Error in scheduler loop: {e}")
                import traceback
                traceback.print_exc()
            
            # Sleep until next check
            time.sleep(CHECK_INTERVAL)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        
        # Wait for all running tasks to complete
        with self.lock:
            futures = list(self.running_tasks.values())
        
        if futures:
            for future in as_completed(futures):
                pass
        
        self.executor.shutdown(wait=True)

# Global scheduler instance
scheduler = Scheduler()

def start_scheduler():
    """Start the scheduler in a background thread"""
    print("🔄 [Scheduler] Starting scheduler in background thread...")
    scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
    scheduler_thread.start()
    print("✅ [Scheduler] Scheduler started in background thread")
    return scheduler_thread

