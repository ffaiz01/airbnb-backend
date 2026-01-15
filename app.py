from flask import Flask, request, jsonify
from flask_cors import CORS
import pyairbnb
import json
import os
from datetime import datetime
from utils import extract_lowest_price
from scheduler import start_scheduler

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Start scheduler when app starts
scheduler_thread = None

@app.route('/api/search', methods=['POST'])
def search_airbnb():
    """
    Search Airbnb listings from a URL
    
    Expected JSON body:
    {
        "url": "https://www.airbnb.co.uk/s/...",
        "currency": "GBP",  # optional, defaults to GBP
        "language": "en",   # optional, defaults to en
        "proxy_url": ""     # optional, defaults to empty
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'URL is required',
                'message': 'Please provide an Airbnb URL in the request body'
            }), 400
        
        url = data['url']
        currency = data.get('currency', 'GBP')
        language = data.get('language', 'en')
        proxy_url = data.get('proxy_url', '')
        
        # Fetch the live StaysSearch hash first so
        # the persisted query id matches airbnb website.
        dynamic_hash = pyairbnb.fetch_stays_search_hash()
        
        # Use the URL wrapper to search
        results = pyairbnb.search_all_from_url(
            url,
            currency=currency,
            language=language,
            proxy_url=proxy_url,
            # hash=dynamic_hash,  # optional, fallbacks to predefined hash
        )

        print(results)
        input('g')
        
        # Extract lowest price using utility function
        price_info = extract_lowest_price(results)
        
        # Add metadata
        response_data = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'currency': currency,
            'language': language,
            'results_count': price_info['results_count'],
            'lowest_price': price_info['lowest_price'],
            'lowest_price_currency': currency if price_info['lowest_price'] else None,
            'prices_found': price_info['prices_found'],
            'data': results
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while fetching Airbnb data'
        }), 500

@app.route('/api/search/simple', methods=['POST'])
def search_airbnb_simple():
    """
    Simplified search endpoint that only requires URL
    
    Expected JSON body:
    {
        "url": "https://www.airbnb.co.uk/s/..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'URL is required'
            }), 400
        
        url = data['url']
        
        # Fetch the live StaysSearch hash
        dynamic_hash = pyairbnb.fetch_stays_search_hash()
        
        # Search with default settings
        results = pyairbnb.search_all_from_url(
            url,
            currency="GBP",
            language="en",
            proxy_url="",
        )
        
        # Extract lowest price using utility function
        price_info = extract_lowest_price(results)
        
        return jsonify({
            'success': True,
            'lowest_price': price_info['lowest_price'],
            'lowest_price_currency': 'GBP' if price_info['lowest_price'] else None,
            'prices_found': price_info['prices_found'],
            'results_count': price_info['results_count'],
            'data': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'service': 'Airbnb Search API',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API information endpoint"""
    return jsonify({
        'service': 'Airbnb Search API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/search': 'Search Airbnb listings with full options',
            'POST /api/search/simple': 'Search Airbnb listings (simplified)',
            'GET /api/health': 'Health check'
        }
    }), 200

@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get scheduler status"""
    from scheduler import scheduler
    return jsonify({
        "running": scheduler.running,
        "active_threads": len(scheduler.running_tasks),
        "max_threads": 3,
        "running_tasks": list(scheduler.running_tasks.keys())
    })

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler_endpoint():
    """Stop the scheduler"""
    from scheduler import scheduler
    scheduler.stop()
    return jsonify({"message": "Scheduler stopped"})

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler_endpoint():
    """Start the scheduler"""
    global scheduler_thread
    from scheduler import scheduler
    
    if not scheduler.running:
        scheduler_thread = start_scheduler()
        return jsonify({"message": "Scheduler started"})
    else:
        return jsonify({"message": "Scheduler already running"})

@app.route('/api/searches/<search_id>/run', methods=['POST'])
def run_search_endpoint(search_id):
    """Trigger a search to run immediately using the scheduler"""
    try:
        from scheduler import scheduler
        
        # Get search name from MongoDB for logging
        from pymongo import MongoClient
        from bson import ObjectId
        import os
        
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb+srv://wasif833:00123333@cluster0.6b8txmd.mongodb.net/')
        client = MongoClient(mongodb_uri, tls=True, tlsAllowInvalidCertificates=False)
        
        # Extract database name
        uri_parts = mongodb_uri.rstrip('/').split('/')
        if len(uri_parts) > 3 and uri_parts[-1] and uri_parts[-1] != '':
            db_name = uri_parts[-1].split('?')[0]
        else:
            db_name = 'airbnb-price-spy'
        
        if db_name == '' or db_name == mongodb_uri or db_name is None:
            db_name = 'airbnb-price-spy'
        
        db = client[db_name]
        collection = db.searches
        
        # Get search to verify it exists and get name
        search = collection.find_one({'_id': ObjectId(search_id)})
        if not search:
            return jsonify({"error": "Search not found"}), 404
        
        search_name = search.get('name', 'Unknown')
        
        # Submit task to scheduler
        scheduler.submit_task(search_id, search_name)
        
        return jsonify({
            "success": True,
            "message": f"Search '{search_name}' has been queued to run",
            "search_id": search_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Start scheduler in background
    scheduler_thread = start_scheduler()
    
    # Get host and port from environment variables (for Docker/GCP)
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)

