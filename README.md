# Airbnb Price Spy - Python API Server

Flask API server for fetching Airbnb listing prices using the `pyairbnb` library.

## Features

- 🔍 Search Airbnb listings and extract lowest prices
- ⏰ Automatic scheduled price fetching with thread pool (max 3 concurrent)
- 🗄️ MongoDB integration for storing search schedules
- 📊 Google Sheets integration for data export
- 🐳 Docker support for easy deployment
- ☁️ GCP VM deployment ready

## API Endpoints

### Health Check
```
GET /api/health
```

### Search Airbnb (Full Options)
```
POST /api/search
Body: {
  "url": "https://www.airbnb.co.uk/s/...",
  "currency": "GBP",  // optional
  "language": "en",   // optional
  "proxy_url": ""     // optional
}
```

### Search Airbnb (Simple)
```
POST /api/search/simple
Body: {
  "url": "https://www.airbnb.co.uk/s/..."
}
Returns: {
  "success": true,
  "lowest_price": 109.0,
  "lowest_price_currency": "GBP",
  "prices_found": 50,
  "results_count": 50
}
```

### Scheduler Status
```
GET /api/scheduler/status
```

### Start Scheduler
```
POST /api/scheduler/start
```

### Stop Scheduler
```
POST /api/scheduler/stop
```

## Installation

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

### Using Docker

```bash
# Build image
docker build -t airbnb-python-api .

# Run container
docker run -d \
  --name airbnb-python-api \
  -p 5000:5000 \
  -e MONGODB_URI="your-mongodb-uri" \
  -e NEXTJS_API_URL="http://localhost:3000" \
  airbnb-python-api
```

## Environment Variables

- `MONGODB_URI`: MongoDB connection string (required)
- `NEXTJS_API_URL`: Next.js API URL for triggering price fetches (required)
- `PYTHON_API_URL`: Self-reference URL (optional, defaults to http://127.0.0.1:5000)
- `HOST`: Host to bind to (optional, defaults to 0.0.0.0)
- `PORT`: Port to listen on (optional, defaults to 5000)
- `DEBUG`: Enable debug mode (optional, defaults to False)
- `GOOGLE_CREDENTIALS_FILE`: Path to Google service account credentials JSON (optional, defaults to credentials.json)
- `GOOGLE_SPREADSHEET_ID`: Google Sheets spreadsheet ID (optional, required for Google Sheets integration)
- `GOOGLE_WORKSHEET_NAME`: Name of the worksheet to write to (optional, defaults to "Price Data")

## Scheduler

The scheduler automatically runs scheduled searches from MongoDB:
- Checks every 60 seconds for scheduled tasks
- Maximum 3 concurrent threads
- Queues tasks when thread pool is full
- Runs searches at specified times (HH:MM format)
- Automatically writes pricing data to Google Sheets after each run (if configured)

## Google Sheets Integration

The scheduler can automatically export pricing data to Google Sheets after each search run.

### Setup

1. **Create a Google Service Account:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API and Google Drive API
   - Create a Service Account
   - Download the JSON credentials file
   - Save it as `credentials.json` in the `python server` folder

2. **Create/Share Google Sheet:**
   - Create a new Google Sheet
   - Copy the Spreadsheet ID from the URL (the long string between `/d/` and `/edit`)
   - Share the sheet with the service account email (found in credentials.json)
   - Set `GOOGLE_SPREADSHEET_ID` environment variable

3. **Configure Environment Variables:**
   ```bash
   export GOOGLE_SPREADSHEET_ID="your-spreadsheet-id"
   export GOOGLE_WORKSHEET_NAME="Price Data"  # Optional, defaults to "Price Data"
   ```

### Data Format

The data is written in the following format:

| Timestamp | Search Name | URL | Checkin Date | Checkout Date | Nights | Price | Price Per Night | Cleaning Fee | Total |
|-----------|-------------|-----|--------------|---------------|--------|-------|-----------------|--------------|-------|

- Each row represents one price entry
- All pricing data (1N, 2N, 3N, 14N, 30N) is written after each search run
- New rows are appended (historical data is preserved)

## Project Structure

```
python server/
├── app.py              # Flask application
├── scheduler.py        # Background scheduler service
├── utils.py            # Utility functions (price extraction)
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md          # This file
```

## Deployment

See `DEPLOY_CLOUD_SHELL.md` for GCP VM deployment instructions.

## License

MIT
