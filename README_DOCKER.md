# Docker Setup

## Local Development with Docker

### Build the image
```bash
docker build -t airbnb-python-api .
```

### Run the container
```bash
docker run -d \
  --name airbnb-python-api \
  -p 5000:5000 \
  -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" \
  -e NEXTJS_API_URL="http://localhost:3000" \
  -e PYTHON_API_URL="http://127.0.0.1:5000" \
  airbnb-python-api
```

### Using Docker Compose
```bash
# Create .env file with your environment variables
cp .env.example .env
# Edit .env with your values

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Environment Variables

- `MONGODB_URI`: MongoDB connection string (required)
- `NEXTJS_API_URL`: URL of your Next.js application (required)
- `PYTHON_API_URL`: Self-reference URL (optional, defaults to http://127.0.0.1:5000)
- `HOST`: Host to bind to (optional, defaults to 0.0.0.0)
- `PORT`: Port to listen on (optional, defaults to 5000)
- `DEBUG`: Enable debug mode (optional, defaults to False)

## Health Check

The container includes a health check endpoint:
```bash
curl http://localhost:5000/api/health
```

## Viewing Logs

```bash
# Docker logs
docker logs airbnb-python-api

# Docker Compose logs
docker-compose logs -f python-api
```

