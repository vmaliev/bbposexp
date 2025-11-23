
import bybit_api
import json
import time
from datetime import datetime, timezone

def test_closed_pnl():
    print("Testing Closed PnL fetch...")
    # Get start of day in ms
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = int(start_of_day.timestamp() * 1000)
    
    print(f"Fetching from: {start_of_day} ({start_time})")
    
    endpoint = '/v5/position/closed-pnl'
    params = {
        'category': 'linear',
        'startTime': start_time,
        'limit': 50
    }
    
    try:
        response = bybit_api.signed_request('GET', endpoint, params)
        result = response.get('result', {})
        list_pnl = result.get('list', [])
        
        print(f"Found {len(list_pnl)} closed positions today.")
        print(json.dumps(list_pnl, indent=2))
        
        total_pnl = sum(float(item['closedPnl']) for item in list_pnl)
        print(f"Total Realized PnL Today: {total_pnl}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_closed_pnl()
