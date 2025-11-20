"""
Bybit API v5 client with signed request support.
Handles authentication and position data retrieval.
"""

import hmac
import hashlib
import time
import requests
from typing import Dict, Any, Optional, List
from config import Config


def generate_signature(params: str, timestamp: str, api_secret: str, recv_window: str) -> str:
    """
    Generate HMAC SHA256 signature for Bybit API v5.
    
    Args:
        params: Query string parameters
        timestamp: Request timestamp in milliseconds
        api_secret: Bybit API secret key
        recv_window: Receive window in milliseconds
    
    Returns:
        Hex-encoded signature string
    """
    param_str = f"{timestamp}{Config.BYBIT_API_KEY}{recv_window}{params}"
    return hmac.new(
        api_secret.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def signed_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make a signed request to Bybit API v5.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path (e.g., '/v5/position/list')
        params: Query parameters or request body
    
    Returns:
        API response as dictionary
    
    Raises:
        Exception: If API request fails
    """
    if params is None:
        params = {}
    
    # Generate timestamp
    timestamp = str(int(time.time() * 1000))
    recv_window = str(Config.RECV_WINDOW)
    
    # Build query string for GET requests
    if method.upper() == 'GET':
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    else:
        query_string = ''
    
    # Generate signature
    signature = generate_signature(query_string, timestamp, Config.BYBIT_API_SECRET, recv_window)
    
    # Build headers
    headers = {
        'X-BAPI-API-KEY': Config.BYBIT_API_KEY,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    
    # Make request
    url = f"{Config.BYBIT_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=params, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        data = response.json()
        
        # Check Bybit API response code
        if data.get('retCode') != 0:
            error_msg = data.get('retMsg', 'Unknown error')
            raise Exception(f"Bybit API error: {error_msg} (code: {data.get('retCode')})")
        
        return data
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


def get_positions(category: str = 'linear', settle_coin: str = 'USDT') -> List[Dict[str, Any]]:
    """
    Fetch all open positions from Bybit.
    
    Args:
        category: Product type ('linear' for USDT perpetuals)
        settle_coin: Settlement coin (USDT, USDC, etc.)
    
    Returns:
        List of position dictionaries
    
    Raises:
        Exception: If API request fails
    """
    endpoint = '/v5/position/list'
    params = {
        'category': category,
        'settleCoin': settle_coin
    }
    
    try:
        response = signed_request('GET', endpoint, params)
        
        # Extract positions from response
        result = response.get('result', {})
        positions = result.get('list', [])
        
        # Filter only positions with non-zero size
        open_positions = [
            pos for pos in positions
            if float(pos.get('size', 0)) > 0
        ]
        
        return open_positions
    
    except Exception as e:
        raise Exception(f"Failed to fetch positions: {str(e)}")


def test_connection() -> bool:
    """
    Test API connection and credentials.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        get_positions()
        return True
    except Exception:
        return False
