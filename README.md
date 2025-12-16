# Airbnb Price Spy - Python API Server

Flask API server for fetching Airbnb listing prices using the `pyairbnb` library.

## Features

- 🔍 Search Airbnb listings and extract lowest prices
- ⏰ Automatic scheduled price fetching with thread pool (max 3 concurrent)
- 🗄️ MongoDB integration for storing search schedules
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

## Scheduler

The scheduler automatically runs scheduled searches from MongoDB:
- Checks every 60 seconds for scheduled tasks
- Maximum 3 concurrent threads
- Queues tasks when thread pool is full
- Runs searches at specified times (HH:MM format)

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
