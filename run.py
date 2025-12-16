#!/usr/bin/env python3
"""
Simple script to run the Flask server
"""
from app import app

if __name__ == '__main__':
    print("🚀 Starting Airbnb Search API Server...")
    print("📍 Server running on http://localhost:5000")
    print("📡 API endpoints available at:")
    print("   - POST /api/search")
    print("   - POST /api/search/simple")
    print("   - GET  /api/health")
    print("\nPress CTRL+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

