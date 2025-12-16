"""
Utility functions for processing Airbnb search results
"""

def extract_lowest_price(results):
    """
    Extract the lowest price from Airbnb search results.
    
    Args:
        results: Results from pyairbnb (can be dict or list)
    
    Returns:
        dict: {
            'lowest_price': float or None,
            'prices': list of all prices found,
            'results_count': int,
            'prices_found': int
        }
    """
    prices = []
    results_list = []
    
    # Handle different result formats
    if isinstance(results, dict):
        results_list = results.get('results', [])
    elif isinstance(results, list):
        results_list = results
    else:
        results_list = []
    
    # Extract prices from price.unit.amount
    for item in results_list:
        try:
            if 'price' in item and 'unit' in item['price'] and 'amount' in item['price']['unit']:
                price_amount = item['price']['unit']['amount']
                if price_amount is not None:
                    prices.append(float(price_amount))
        except (KeyError, TypeError, ValueError):
            # Skip items with invalid price structure
            continue
    
    # Find lowest price
    lowest_price = min(prices) if prices else None
    
    return {
        'lowest_price': lowest_price,
        'prices': prices,
        'results_count': len(results_list),
        'prices_found': len(prices)
    }

