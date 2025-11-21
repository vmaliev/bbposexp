"""
Position and portfolio analysis engine.
Computes risk metrics, leverage scores, and exposure analysis.
"""

from typing import Dict, Any, List, Optional


# Symbol categorization mappings
SYMBOL_CLUSTERS = {
    'BTC': ['BTC'],
    'ETH': ['ETH'],
    'L2': ['ARB', 'OP', 'MATIC', 'AVAX', 'STRK', 'METIS', 'IMX', 'MANTA'],
    'MEME': ['DOGE', 'SHIB', 'PEPE', 'WIF', 'BONK', 'FLOKI', 'BRETT'],
    'AI': ['AGIX', 'FET', 'RNDR', 'GRT', 'OCEAN', 'NMR', 'TAO'],
}


def categorize_symbol(symbol: str) -> str:
    """
    Categorize a trading symbol into a cluster.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
    
    Returns:
        Cluster name (BTC, ETH, L2, MEME, AI, or OTHER)
    """
    symbol_upper = symbol.upper()
    
    for cluster, keywords in SYMBOL_CLUSTERS.items():
        for keyword in keywords:
            if keyword in symbol_upper:
                return cluster
    
    return 'OTHER'


def calculate_leverage_risk(leverage: float) -> str:
    """
    Determine leverage risk level.
    
    Args:
        leverage: Position leverage
    
    Returns:
        Risk level: 'safe', 'medium', or 'high'
    """
    if leverage < 5:
        return 'safe'
    elif leverage <= 10:
        return 'medium'
    else:
        return 'high'


def analyze_position(position: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a single position and compute risk metrics.
    
    Args:
        position: Raw position data from Bybit API
    
    Returns:
        Normalized position analysis
    """
    # Extract fields
    symbol = position.get('symbol', '')
    side = position.get('side', '').lower()
    size = float(position.get('size', 0))
    entry_price = float(position.get('avgPrice', 0))
    mark_price = float(position.get('markPrice', 0))
    liq_price = float(position.get('liqPrice', 0)) if position.get('liqPrice') else 0
    leverage = float(position.get('leverage', 1))
    unrealized_pnl = float(position.get('unrealisedPnl', 0))
    
    # Calculate exposure
    exposure_usdt = abs(size * mark_price)
    
    # Calculate liquidation distance
    if liq_price > 0 and mark_price > 0:
        liquidation_distance_pct = abs(mark_price - liq_price) / mark_price * 100
    else:
        liquidation_distance_pct = 100.0  # No liquidation risk if no liq price
    
    # Determine PnL status
    pnl_status = 'profit' if unrealized_pnl > 0 else 'loss'
    
    # Calculate leverage risk
    leverage_risk = calculate_leverage_risk(leverage)
    
    # Categorize symbol
    cluster = categorize_symbol(symbol)
    
    return {
        'symbol': symbol,
        'side': side,
        'size': size,
        'entry_price': entry_price,
        'mark_price': mark_price,
        'liq_price': liq_price,
        'leverage': leverage,
        'unrealized_pnl': unrealized_pnl,
        'exposure_usdt': exposure_usdt,
        'liquidation_distance_pct': liquidation_distance_pct,
        'pnl_status': pnl_status,
        'leverage_risk': leverage_risk,
        'cluster': cluster
    }


def analyze_orders(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze open orders.
    
    Args:
        orders: Raw order data
    
    Returns:
        Analyzed orders
    """
    analyzed_orders = []
    for order in orders:
        analyzed_orders.append({
            'symbol': order.get('symbol', ''),
            'side': order.get('side', '').lower(),
            'type': order.get('orderType', '').lower(),
            'price': float(order.get('price', 0)),
            'qty': float(order.get('qty', 0)),
            'order_id': order.get('orderId', '')
        })
    return analyzed_orders


def analyze_portfolio(positions: List[Dict[str, Any]], orders: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze entire portfolio and compute aggregate metrics.
    
    Args:
        positions: List of analyzed positions
        orders: List of analyzed orders
    
    Returns:
        Portfolio analysis with metrics and risks
    """
    if orders is None:
        orders = []

    if not positions and not orders:
        return {
            'portfolio': {
                'total_long_exposure': 0,
                'total_short_exposure': 0,
                'net_exposure': 0,
                'bias': 'neutral',
                'clusters': {},
                'total_positions': 0,
                'total_orders': 0,
                'total_unrealized_pnl': 0
            },
            'positions': [],
            'orders': [],
            'risks': {
                'highest_risk_position': None,
                'high_leverage_count': 0,
                'close_liquidation_count': 0,
                'total_risk_score': 0
            }
        }
    
    # Calculate exposures
    total_long_exposure = sum(
        pos['exposure_usdt'] for pos in positions if pos['side'] == 'buy'
    )
    total_short_exposure = sum(
        pos['exposure_usdt'] for pos in positions if pos['side'] == 'sell'
    )
    net_exposure = total_long_exposure - total_short_exposure
    total_exposure = total_long_exposure + total_short_exposure
    
    # Determine bias
    if total_exposure > 0:
        long_pct = total_long_exposure / total_exposure
        if long_pct > 0.6:
            bias = 'long'
        elif long_pct < 0.4:
            bias = 'short'
        else:
            bias = 'neutral'
    else:
        bias = 'neutral'
    
    # Calculate cluster distribution
    cluster_exposure = {}
    for pos in positions:
        cluster = pos['cluster']
        cluster_exposure[cluster] = cluster_exposure.get(cluster, 0) + pos['exposure_usdt']
    
    # Convert to percentages
    cluster_distribution = {}
    if total_exposure > 0:
        for cluster, exposure in cluster_exposure.items():
            cluster_distribution[cluster] = (exposure / total_exposure) * 100
    
    # Calculate total unrealized PnL
    total_unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions)
    
    # Risk analysis
    high_leverage_positions = [
        pos for pos in positions if pos['leverage_risk'] == 'high'
    ]
    close_liquidation_positions = [
        pos for pos in positions if pos['liquidation_distance_pct'] < 10
    ]
    
    # Find highest risk position (combination of high leverage and close liquidation)
    highest_risk_position = None
    highest_risk_score = 0
    
    for pos in positions:
        # Risk score: inverse of liq distance * leverage
        if pos['liquidation_distance_pct'] > 0:
            risk_score = (100 / pos['liquidation_distance_pct']) * pos['leverage']
            if risk_score > highest_risk_score:
                highest_risk_score = risk_score
                highest_risk_position = pos
    
    return {
        'portfolio': {
            'total_long_exposure': total_long_exposure,
            'total_short_exposure': total_short_exposure,
            'net_exposure': net_exposure,
            'bias': bias,
            'clusters': cluster_distribution,
            'total_positions': len(positions),
            'total_orders': len(orders),
            'total_unrealized_pnl': total_unrealized_pnl
        },
        'positions': positions,
        'orders': orders,
        'risks': {
            'highest_risk_position': highest_risk_position,
            'high_leverage_count': len(high_leverage_positions),
            'close_liquidation_count': len(close_liquidation_positions),
            'total_risk_score': highest_risk_score
        }
    }


def analyze_positions(raw_positions: List[Dict[str, Any]], raw_orders: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main analysis function - processes raw positions and returns complete analysis.
    
    Args:
        raw_positions: Raw position data from Bybit API
        raw_orders: Raw order data from Bybit API (optional)
    
    Returns:
        Complete portfolio and position analysis
    """
    # Analyze each position
    analyzed_positions = [analyze_position(pos) for pos in raw_positions]
    
    # Analyze orders if provided
    analyzed_orders = []
    if raw_orders:
        analyzed_orders = analyze_orders(raw_orders)
    
    # Analyze portfolio
    portfolio_analysis = analyze_portfolio(analyzed_positions, analyzed_orders)
    
    return portfolio_analysis
