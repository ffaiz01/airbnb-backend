# Quick Docker Commands

## Build and Run (Complete Setup)

### Option 1: Use the batch file (Easiest)
```cmd
build-and-run.bat
```

### Option 2: Manual commands

**Step 1: Build the image**
```cmd
docker build -t airbnb-python-api .
```

**Step 2: Run the container**
```cmd
docker run -d --name airbnb-python-api -p 5000:5000 -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" -e NEXTJS_API_URL="http://localhost:3000" airbnb-python-api
```

### Option 3: Single line (build + run)
```cmd
docker build -t airbnb-python-api . && docker run -d --name airbnb-python-api -p 5000:5000 -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" -e NEXTJS_API_URL="http://localhost:3000" airbnb-python-api
```

## Windows Command Prompt (Single Line - Run Only)

```cmd
docker run -d --name airbnb-python-api -p 5000:5000 -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" -e NEXTJS_API_URL="http://localhost:3000" airbnb-python-api
```

## PowerShell (Single Line)

```powershell
docker run -d --name airbnb-python-api -p 5000:5000 -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" -e NEXTJS_API_URL="http://localhost:3000" airbnb-python-api
```

## Using the Batch File

Simply double-click `run-docker.bat` or run:
```cmd
run-docker.bat
```

## Other Useful Commands

### Stop the container
```cmd
docker stop airbnb-python-api
```

### Start the container
```cmd
docker start airbnb-python-api
```

### Remove the container
```cmd
docker rm airbnb-python-api
```

### View logs
```cmd
docker logs airbnb-python-api
```

### View logs (follow)
```cmd
docker logs -f airbnb-python-api
```

### Rebuild and run (stop, remove, build, run)
```cmd
docker stop airbnb-python-api && docker rm airbnb-python-api && docker build -t airbnb-python-api . && docker run -d --name airbnb-python-api -p 5000:5000 -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" -e NEXTJS_API_URL="http://localhost:3000" airbnb-python-api
```

