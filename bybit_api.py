"""
Bybit API v5 client with signed request support.
Handles authentication and position data retrieval.
"""

import hmac
import hashlib
import time
import requests
import urllib.parse
from datetime import datetime, timezone
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
    
    # Build query string for GET requests (use raw values for signature)
    if method.upper() == 'GET':
        # Build query string with proper encoding
        # Sort parameters alphabetically
        sorted_params = sorted(params.items())
        query_parts = []
        for k, v in sorted_params:
            # Don't URL-encode for signature - use raw values
            query_parts.append(f"{k}={v}")
        query_string = '&'.join(query_parts)
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
            # Build URL manually with query string to avoid double-encoding
            if query_string:
                url = f"{url}?{query_string}"
            response = requests.get(url, headers=headers, timeout=10)
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
    Fetch all open positions from Bybit with pagination support.
    
    Args:
        category: Product type ('linear' for USDT perpetuals)
        settle_coin: Settlement coin (USDT, USDC, etc.)
    
    Returns:
        List of position dictionaries
    
    Raises:
        Exception: If API request fails
    """
    endpoint = '/v5/position/list'
    all_positions = []
    cursor = None
    
    try:
        # Loop through all pages
        while True:
            params = {
                'category': category,
                'settleCoin': settle_coin
            }
            
            # Add cursor for pagination (if not first request)
            if cursor:
                params['cursor'] = cursor
            
            response = signed_request('GET', endpoint, params)
            
            # Extract positions from response
            result = response.get('result', {})
            positions = result.get('list', [])
            
            # Add positions to our list
            all_positions.extend(positions)
            
            # Check if there are more pages
            cursor = result.get('nextPageCursor')
            if not cursor:
                break
        
        # Filter only positions with non-zero size
        open_positions = [
            pos for pos in all_positions
            if float(pos.get('size', 0)) > 0
        ]
        
        return open_positions
    
    except Exception as e:
        raise Exception(f"Failed to fetch positions: {str(e)}")


def get_open_orders(category: str = 'linear', settle_coin: str = 'USDT') -> List[Dict[str, Any]]:
    """
    Fetch all open orders from Bybit (limit, market, conditional orders).
    
    Args:
        category: Product type ('linear' for USDT perpetuals)
        settle_coin: Settlement coin (USDT, USDC, etc.)
    
    Returns:
        List of order dictionaries
    
    Raises:
        Exception: If API request fails
    """
    endpoint = '/v5/order/realtime'
    all_orders = []
    cursor = None
    
    try:
        # Loop through all pages
        while True:
            params = {
                'category': category,
                'settleCoin': settle_coin
            }
            
            # Add cursor for pagination (if not first request)
            if cursor:
                params['cursor'] = cursor
            
            response = signed_request('GET', endpoint, params)
            
            # Extract orders from response
            result = response.get('result', {})
            orders = result.get('list', [])
            
            # Add orders to our list
            all_orders.extend(orders)
            
            # Check if there are more pages
            cursor = result.get('nextPageCursor')
            if not cursor:
                break
        
        return all_orders
    
    except Exception as e:
        raise Exception(f"Failed to fetch open orders: {str(e)}")


def get_conditional_orders(category: str = 'linear', settle_coin: str = 'USDT') -> List[Dict[str, Any]]:
    """
    Fetch all conditional orders (stop loss, take profit triggers).
    
    Args:
        category: Product type ('linear' for USDT perpetuals)
        settle_coin: Settlement coin (USDT, USDC, etc.)
    
    Returns:
        List of conditional order dictionaries
    
    Raises:
        Exception: If API request fails
    """
    endpoint = '/v5/order/realtime'
    all_orders = []
    cursor = None
    
    try:
        # Loop through all pages
        while True:
            params = {
                'category': category,
                'settleCoin': settle_coin,
                'orderFilter': 'StopOrder'  # Filter for conditional orders
            }
            
            # Add cursor for pagination (if not first request)
            if cursor:
                params['cursor'] = cursor
            
            response = signed_request('GET', endpoint, params)
            
            # Extract orders from response
            result = response.get('result', {})
            orders = result.get('list', [])
            
            # Add orders to our list
            all_orders.extend(orders)
            
            # Check if there are more pages
            cursor = result.get('nextPageCursor')
            if not cursor:
                break
        
        return all_orders
    
    except Exception as e:
        raise Exception(f"Failed to fetch conditional orders: {str(e)}")


def get_recent_trades(category: str = 'linear', limit: int = 100, settle_coin: str = 'USDT') -> List[Dict[str, Any]]:
    """
    Fetch recent trade executions (excluding Funding fees).
    
    Args:
        category: Product type ('linear' for USDT perpetuals)
        limit: Number of trades to fetch (max 100)
        settle_coin: Settlement coin
    
    Returns:
        List of execution dictionaries
    """
    endpoint = '/v5/execution/list'
    
    try:
        params = {
            'category': category,
            'limit': limit,
            'settleCoin': settle_coin
        }
        
        response = signed_request('GET', endpoint, params)
        result = response.get('result', {})
        all_executions = result.get('list', [])
        
        # Filter out Funding executions to show only actual trades
        trades = [
            exc for exc in all_executions 
            if exc.get('execType') != 'Funding'
        ]
        
        return trades
        
    except Exception as e:
        raise Exception(f"Failed to fetch recent trades: {str(e)}")


def get_todays_trades(category: str = 'linear', settle_coin: str = 'USDT') -> List[Dict[str, Any]]:
    """
    Fetch all trade executions for the current day (UTC).
    
    Args:
        category: Product type ('linear' for USDT perpetuals)
        settle_coin: Settlement coin
    
    Returns:
        List of execution dictionaries for today
    """
    endpoint = '/v5/execution/list'
    all_executions = []
    cursor = None
    
    # Calculate start of day (UTC)
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = int(start_of_day.timestamp() * 1000)
    
    try:
        while True:
            params = {
                'category': category,
                'limit': 50,  # Fetch 50 at a time
                'settleCoin': settle_coin,
                'startTime': start_time
            }
            
            if cursor:
                params['cursor'] = cursor
            
            response = signed_request('GET', endpoint, params)
            result = response.get('result', {})
            executions = result.get('list', [])
            
            all_executions.extend(executions)
            
            cursor = result.get('nextPageCursor')
            if not cursor:
                break
                
            # Safety limit to prevent excessive API calls
            if len(all_executions) > 1000:
                break
        
        # Filter out Funding executions and sort by time (newest first)
        trades = [
            exc for exc in all_executions 
            if exc.get('execType') != 'Funding'
        ]
        trades.sort(key=lambda x: int(x.get('execTime', 0)), reverse=True)
        
        return trades
        
    except Exception as e:
        raise Exception(f"Failed to fetch today's trades: {str(e)}")


def get_closed_pnl(category: str = 'linear', limit: int = 50, start_time: int = None) -> List[Dict[str, Any]]:
    """
    Fetch closed Profit and Loss (Realized PnL).
    
    Args:
        category: Product type ('linear', 'inverse')
        limit: Number of records to fetch
        start_time: Start timestamp in milliseconds (default: Start of today UTC)
    
    Returns:
        List of closed PnL records
    """
    endpoint = '/v5/position/closed-pnl'
    
    try:
        # Default to start of day UTC if no start_time provided
        if start_time is None:
            now = datetime.now(timezone.utc)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = int(start_of_day.timestamp() * 1000)
            
        params = {
            'category': category,
            'limit': limit,
            'startTime': start_time
        }
        
        response = signed_request('GET', endpoint, params)
        result = response.get('result', {})
        return result.get('list', [])
        
    except Exception as e:
        raise Exception(f"Failed to fetch closed PnL: {str(e)}")


def get_wallet_balance(account_type: str = 'UNIFIED', coin: str = 'USDT') -> Dict[str, Any]:
    """
    Fetch wallet balance information from Bybit.
    
    Args:
        account_type: Account type ('UNIFIED', 'CONTRACT', etc.)
        coin: Coin to get balance for (default: USDT)
    
    Returns:
        Dictionary with balance information including:
        - totalEquity: Total account equity
        - totalAvailableBalance: Available balance for trading
        - totalMarginBalance: Total margin balance
        - totalInitialMargin: Total initial margin
        - totalMaintenanceMargin: Total maintenance margin
    
    Raises:
        Exception: If API request fails
    """
    endpoint = '/v5/account/wallet-balance'
    
    try:
        params = {
            'accountType': account_type
        }
        
        response = signed_request('GET', endpoint, params)
        
        # Extract wallet data from response
        result = response.get('result', {})
        accounts = result.get('list', [])
        
        if not accounts:
            return {
                'totalEquity': '0',
                'totalAvailableBalance': '0',
                'totalMarginBalance': '0',
                'totalInitialMargin': '0',
                'totalMaintenanceMargin': '0',
                'coin': []
            }
        
        # Get the first account (usually there's only one for UNIFIED)
        account = accounts[0]
        
        # Find USDT coin data
        coins = account.get('coin', [])
        usdt_data = None
        for c in coins:
            if c.get('coin') == coin:
                usdt_data = c
                break
        
        return {
            'totalEquity': account.get('totalEquity', '0'),
            'totalAvailableBalance': account.get('totalAvailableBalance', '0'),
            'totalMarginBalance': account.get('totalMarginBalance', '0'),
            'totalInitialMargin': account.get('totalInitialMargin', '0'),
            'totalMaintenanceMargin': account.get('totalMaintenanceMargin', '0'),
            'accountIMRate': account.get('accountIMRate', '0'),
            'accountMMRate': account.get('accountMMRate', '0'),
            'coin_data': usdt_data if usdt_data else {}
        }
    
    except Exception as e:
        raise Exception(f"Failed to fetch wallet balance: {str(e)}")


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
