@echo off
echo Building Docker image...
docker build -t airbnb-python-api .
if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b %errorlevel%
)
echo.
echo Starting container...
docker run -d --name airbnb-python-api -p 5000:5000 -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" -e NEXTJS_API_URL="http://localhost:3000" airbnb-python-api
if %errorlevel% neq 0 (
    echo Container start failed!
    pause
    exit /b %errorlevel%
)
echo.
echo Container started successfully!
echo API is running at http://localhost:5000
pause

