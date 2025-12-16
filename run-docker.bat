@echo off
docker run -d --name airbnb-python-api -p 5000:5000 -e MONGODB_URI="mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/airbnb-price-spy" -e NEXTJS_API_URL="http://localhost:3000" airbnb-python-api

