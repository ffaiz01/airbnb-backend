# Scheduler Service

The scheduler service automatically runs scheduled Airbnb price searches using a thread pool with a maximum of 3 concurrent threads.

## Features

- **Thread Pool Management**: Maximum 3 concurrent threads
- **Queue System**: Tasks wait for available slots if pool is full
- **Automatic Scheduling**: Checks for scheduled tasks every 60 seconds
- **MongoDB Integration**: Reads schedule data from MongoDB
- **Next.js API Integration**: Triggers price fetching via Next.js API

## How It Works

1. **Scheduler Loop**: Runs every 60 seconds, checking for scheduled tasks
2. **Time Matching**: Compares current time (HH:MM) with scheduled times
3. **Thread Pool**: Uses `ThreadPoolExecutor` with max 3 workers
4. **Queue Management**: If all 3 threads are busy, new tasks wait until a slot is available
5. **Task Tracking**: Tracks running tasks to avoid duplicate runs

## Configuration

Environment variables (set in `.env` or system):

- `MONGODB_URI`: MongoDB connection string
- `NEXTJS_API_URL`: Next.js API URL (default: http://localhost:3000)
- `PYTHON_API_URL`: Python API URL (default: http://127.0.0.1:5000)

## API Endpoints

### GET `/api/scheduler/status`
Get current scheduler status:
```json
{
  "running": true,
  "active_threads": 2,
  "max_threads": 3,
  "running_tasks": ["search_id_1", "search_id_2"]
}
```

### POST `/api/scheduler/start`
Start the scheduler (if not already running)

### POST `/api/scheduler/stop`
Stop the scheduler and wait for running tasks to complete

## Usage

The scheduler starts automatically when the Flask app starts. It runs in a background daemon thread.

To manually control:
```python
from scheduler import scheduler

# Start scheduler
scheduler.start()

# Stop scheduler
scheduler.stop()
```

## Thread Pool Behavior

- **Maximum 3 threads**: Only 3 searches can run simultaneously
- **Queue when full**: If 3 threads are busy, new tasks wait
- **Automatic cleanup**: Completed tasks are removed from tracking
- **Wait for completion**: When stopping, scheduler waits for all tasks to finish

## Example Schedule

A search with schedule:
```json
{
  "schedule": {
    "enabled": true,
    "times": [
      {"time": "07:00", "enabled": true},
      {"time": "14:00", "enabled": true},
      {"time": "21:00", "enabled": false}
    ]
  }
}
```

Will run at:
- 07:00 every day
- 14:00 every day
- 21:00 is disabled, so won't run

## Notes

- The scheduler checks every 60 seconds, so tasks may run up to 60 seconds after their scheduled time
- Duplicate prevention: Won't run the same task twice within 30 seconds
- Status tracking: Skips searches that are already in "running" status

