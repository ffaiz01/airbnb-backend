"""
Scheduler service for running scheduled Airbnb price searches
Uses thread pool with maximum 3 concurrent threads
"""
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo import MongoClient
import requests
import os
from typing import List, Dict, Optional

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/')
NEXTJS_API_URL = os.getenv('NEXTJS_API_URL', 'http://localhost:3000')
PYTHON_API_URL = os.getenv('PYTHON_API_URL', 'http://127.0.0.1:5000')
MAX_WORKERS = 3  # Maximum concurrent threads
CHECK_INTERVAL = 60  # Check for scheduled tasks every 60 seconds

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
            return None
    
    def get_scheduled_searches(self) -> List[Dict]:
        """Get all searches with enabled schedules"""
        try:
            collection = self.connect_db()
            if collection is None:
                return []
            
            searches = collection.find({
                'schedule.enabled': True
            })
            return list(searches)
        except Exception as e:
            print(f"❌ Error fetching scheduled searches: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def should_run_now(self, schedule: Dict, last_run: str) -> bool:
        """Check if a search should run now based on its schedule"""
        if not schedule or not schedule.get('enabled'):
            return False
        
        times = schedule.get('times', [])
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
                            return False
                    except:
                        pass
                return True
        
        return False
    
    def run_search(self, search_id: str, search_name: str) -> bool:
        """Run a single search by calling Next.js API"""
        try:
            url = f"{NEXTJS_API_URL}/api/searches/{search_id}/run"
            response = requests.post(url, timeout=5)
            
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
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
            self.wait_for_available_slot()
        
        # Submit task to thread pool
        future = self.executor.submit(self.run_search, search_id, search_name)
        
        with self.lock:
            self.running_tasks[search_id] = future
    
    def check_and_run_schedules(self):
        """Check for scheduled tasks and run them"""
        try:
            searches = self.get_scheduled_searches()
            
            # Check if searches is None or empty list
            if searches is None:
                return
            if not isinstance(searches, list):
                return
            if len(searches) == 0:
                return
            
            tasks_to_run = []
            
            for search in searches:
                search_id = str(search.get('_id'))
                search_name = search.get('name', 'Unknown')
                schedule = search.get('schedule', {})
                last_run = search.get('lastRun', 'Never')
                status = search.get('status', 'idle')
                
                # Skip if already running
                if status == 'running':
                    continue
                
                # Check if should run now
                if self.should_run_now(schedule, last_run):
                    tasks_to_run.append((search_id, search_name))
            
            # Run tasks (will queue if pool is full)
            for search_id, search_name in tasks_to_run:
                self.submit_task(search_id, search_name)
        except Exception as e:
            pass
    
    def cleanup_completed_tasks(self):
        """Remove completed tasks from tracking"""
        completed = []
        with self.lock:
            for search_id, future in self.running_tasks.items():
                if future.done():
                    completed.append(search_id)
            for search_id in completed:
                del self.running_tasks[search_id]
    
    def start(self):
        """Start the scheduler loop"""
        self.running = True
        
        while self.running:
            try:
                self.check_and_run_schedules()
                self.cleanup_completed_tasks()
            except Exception as e:
                pass  # Silently handle errors
            
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
    scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
    scheduler_thread.start()
    return scheduler_thread

