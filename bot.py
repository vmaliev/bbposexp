#!/usr/bin/env python3
"""
Bybit Position Analysis Bot
CLI tool for analyzing USDT perpetual futures positions.

Usage:
    python bot.py analyze
"""

import sys
from typing import Dict, Any
from config import Config
import bybit_api
import analyzer
import ai_analysis


def format_currency(amount: float) -> str:
    """Format currency with thousands separator."""
    return f"{amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format percentage value."""
    return f"{value:.2f}%"


def get_risk_emoji(risk_level: str) -> str:
    """Get emoji for risk level."""
    return {
        'high': '🔴',
        'medium': '🟡',
        'safe': '🟢'
    }.get(risk_level, '⚪')


def print_portfolio_summary(analysis: Dict[str, Any]) -> None:
    """Print portfolio summary section."""
    portfolio = analysis['portfolio']
    
    print("\n" + "=" * 60)
    print("PORTFOLIO SUMMARY".center(60))
    print("=" * 60)
    
    print(f"\nLong Exposure:  ${format_currency(portfolio['total_long_exposure'])} USDT")
    print(f"Short Exposure: ${format_currency(portfolio['total_short_exposure'])} USDT")
    print(f"Net Exposure:   ${format_currency(portfolio['net_exposure'])} USDT")
    print(f"Total PnL:      ${format_currency(portfolio['total_unrealized_pnl'])} USDT")
    print(f"Bias:           {portfolio['bias'].upper()}")
    print(f"Total Positions: {portfolio['total_positions']}")
    
    if portfolio['clusters']:
        print("\nCluster Distribution:")
        sorted_clusters = sorted(
            portfolio['clusters'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for cluster, pct in sorted_clusters:
            print(f"  {cluster:8s} {format_percentage(pct)}")


def print_position_risks(analysis: Dict[str, Any]) -> None:
    """Print individual position risks."""
    positions = analysis['positions']
    
    if not positions:
        print("\nNo open positions found.")
        return
    
    print("\n" + "=" * 60)
    print("POSITION RISKS".center(60))
    print("=" * 60)
    
    # Sort by risk score (leverage * inverse liq distance)
    sorted_positions = sorted(
        positions,
        key=lambda p: (100 / max(p['liquidation_distance_pct'], 0.1)) * p['leverage'],
        reverse=True
    )
    
    for pos in sorted_positions:
        risk_emoji = get_risk_emoji(pos['leverage_risk'])
        side_display = pos['side'].upper()
        pnl_sign = '+' if pos['unrealized_pnl'] >= 0 else ''
        
        print(f"\n{risk_emoji} [{pos['leverage_risk'].upper()} RISK] {pos['symbol']} ({side_display})")
        print(f"  Size: {pos['size']:.4f} | Entry: ${format_currency(pos['entry_price'])} | Mark: ${format_currency(pos['mark_price'])}")
        print(f"  Leverage: {pos['leverage']:.1f}x | Liq Price: ${format_currency(pos['liq_price'])}")
        print(f"  Distance to Liquidation: {format_percentage(pos['liquidation_distance_pct'])}")
        print(f"  PnL: {pnl_sign}${format_currency(pos['unrealized_pnl'])} ({pos['pnl_status']})")
        print(f"  Exposure: ${format_currency(pos['exposure_usdt'])} USDT | Cluster: {pos['cluster']}")
        
        # Add warning for high-risk positions
        if pos['leverage_risk'] == 'high' and pos['liquidation_distance_pct'] < 15:
            print(f"  ⚠️  HIGH RISK: High leverage + close to liquidation!")


def print_suggestions(suggestions: Dict[str, Any]) -> None:
    """Print AI-generated suggestions."""
    print("\n" + "=" * 60)
    print("ACTIONABLE SUGGESTIONS".center(60))
    print("=" * 60)
    
    if suggestions.get('urgent'):
        print("\n🔴 URGENT:")
        for suggestion in suggestions['urgent']:
            print(f"  - {suggestion}")
    
    if suggestions.get('recommended'):
        print("\n🟡 RECOMMENDED:")
        for suggestion in suggestions['recommended']:
            print(f"  - {suggestion}")
    
    if suggestions.get('optional'):
        print("\n🟢 OPTIONAL:")
        for suggestion in suggestions['optional']:
            print(f"  - {suggestion}")


def list_positions_command() -> int:
    """
    List all open positions in a simple table format.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    print("📋 Bybit Positions List")
    print("=" * 60)
    
    # Validate configuration
    is_valid, error_msg = Config.validate()
    if not is_valid:
        print(f"\n❌ Configuration Error: {error_msg}")
        print("\nPlease set the following environment variables:")
        print("  - BYBIT_API_KEY")
        print("  - BYBIT_API_SECRET")
        return 1
    
    print("\n📡 Fetching positions from Bybit...")
    
    try:
        # Fetch positions
        raw_positions = bybit_api.get_positions()
        
        if not raw_positions:
            print("\n✨ No open positions found!")
            return 0
        
        print(f"✅ Found {len(raw_positions)} open position(s)\n")
        
        # Print header
        print("=" * 120)
        print(f"{'SYMBOL':<15} {'SIDE':<6} {'SIZE':<15} {'ENTRY':<12} {'MARK':<12} {'AMOUNT':<15} {'PNL':<15} {'LEV':<5}")
        print("=" * 120)
        
        # Sort by symbol
        sorted_positions = sorted(raw_positions, key=lambda p: p.get('symbol', ''))
        
        total_pnl = 0.0
        total_amount = 0.0
        
        for pos in sorted_positions:
            symbol = pos.get('symbol', 'N/A')
            side = pos.get('side', 'N/A')
            size = float(pos.get('size', 0))
            entry_price = float(pos.get('avgPrice', 0))
            mark_price = float(pos.get('markPrice', 0))
            unrealized_pnl = float(pos.get('unrealisedPnl', 0))
            leverage = float(pos.get('leverage', 0))
            
            # Calculate position value (size * mark price)
            position_value = size * mark_price
            
            total_pnl += unrealized_pnl
            total_amount += position_value
            
            # Format PnL with color indicator
            pnl_sign = '+' if unrealized_pnl >= 0 else ''
            pnl_str = f"{pnl_sign}${unrealized_pnl:,.2f}"
            pnl_indicator = "🟢" if unrealized_pnl >= 0 else "🔴"
            
            print(f"{symbol:<15} {side:<6} {size:<15,.4f} ${entry_price:<11,.4f} ${mark_price:<11,.4f} ${position_value:<14,.2f} {pnl_indicator} {pnl_str:<13} {leverage:.1f}x")
        
        print("=" * 120)
        total_sign = '+' if total_pnl >= 0 else ''
        print(f"\n💰 Total Position Value: ${total_amount:,.2f} USDT")
        print(f"💰 Total Unrealized PnL: {total_sign}${total_pnl:,.2f} USDT")
        print("\n" + "=" * 60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


def orders_command() -> int:
    """
    List all open orders (limit, stop loss, take profit).
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    print("📝 Bybit Open Orders")
    print("=" * 60)
    
    # Validate configuration
    is_valid, error_msg = Config.validate()
    if not is_valid:
        print(f"\n❌ Configuration Error: {error_msg}")
        print("\nPlease set the following environment variables:")
        print("  - BYBIT_API_KEY")
        print("  - BYBIT_API_SECRET")
        return 1
    
    print("\n📡 Fetching orders from Bybit...")
    
    try:
        # Fetch all orders
        all_orders = bybit_api.get_open_orders()
        
        if not all_orders:
            print("\n✨ No open orders found!")
            return 0
        
        print(f"✅ Found {len(all_orders)} open order(s)\n")
        
        # Group orders by type
        limit_orders = []
        stop_orders = []
        
        for order in all_orders:
            order_type = order.get('orderType', '')
            stop_order_type = order.get('stopOrderType', '')
            
            if stop_order_type or order_type in ['Stop', 'StopLimit']:
                stop_orders.append(order)
            else:
                limit_orders.append(order)
        
        # Display Limit Orders
        if limit_orders:
            print("=" * 130)
            print("📊 LIMIT ORDERS".center(130))
            print("=" * 130)
            print(f"{'SYMBOL':<15} {'SIDE':<6} {'TYPE':<12} {'QTY':<15} {'PRICE':<15} {'STATUS':<12} {'TIME CREATED':<20}")
            print("=" * 130)
            
            for order in sorted(limit_orders, key=lambda o: o.get('symbol', '')):
                symbol = order.get('symbol', 'N/A')
                side = order.get('side', 'N/A')
                order_type = order.get('orderType', 'N/A')
                qty = float(order.get('qty', 0))
                price = float(order.get('price', 0))
                status = order.get('orderStatus', 'N/A')
                created_time = order.get('createdTime', 'N/A')
                
                # Convert timestamp to readable format
                if created_time != 'N/A':
                    from datetime import datetime
                    created_time = datetime.fromtimestamp(int(created_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                
                side_emoji = "🟢" if side == "Buy" else "🔴"
                print(f"{symbol:<15} {side_emoji} {side:<4} {order_type:<12} {qty:<15,.4f} ${price:<14,.4f} {status:<12} {created_time:<20}")
        
        # Display Stop/Conditional Orders
        if stop_orders:
            print("\n" + "=" * 130)
            print("🎯 STOP LOSS / TAKE PROFIT ORDERS".center(130))
            print("=" * 130)
            print(f"{'SYMBOL':<15} {'SIDE':<6} {'TYPE':<15} {'QTY':<15} {'TRIGGER':<15} {'PRICE':<15} {'STATUS':<12}")
            print("=" * 130)
            
            for order in sorted(stop_orders, key=lambda o: o.get('symbol', '')):
                symbol = order.get('symbol', 'N/A')
                side = order.get('side', 'N/A')
                stop_order_type = order.get('stopOrderType', order.get('orderType', 'N/A'))
                qty = float(order.get('qty', 0))
                trigger_price = float(order.get('triggerPrice', 0))
                price = float(order.get('price', 0))
                status = order.get('orderStatus', 'N/A')
                
                side_emoji = "🟢" if side == "Buy" else "🔴"
                
                # Determine if it's SL or TP based on side and trigger
                order_label = stop_order_type
                
                print(f"{symbol:<15} {side_emoji} {side:<4} {order_label:<15} {qty:<15,.4f} ${trigger_price:<14,.4f} ${price:<14,.4f} {status:<12}")
        
        print("\n" + "=" * 60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1



def analyze_command() -> int:
    """
    Main analyze command - fetch positions and generate report.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    print("🤖 Bybit Position Analysis Bot")
    print("=" * 60)
    
    # Validate configuration
    is_valid, error_msg = Config.validate()
    if not is_valid:
        print(f"\n❌ Configuration Error: {error_msg}")
        print("\nPlease set the following environment variables:")
        print("  - BYBIT_API_KEY")
        print("  - BYBIT_API_SECRET")
        print("\nExample:")
        print("  export BYBIT_API_KEY='your_key_here'")
        print("  export BYBIT_API_SECRET='your_secret_here'")
        return 1
    
    # Check OpenAI status
    if Config.has_openai():
        print("✅ OpenAI API configured - AI analysis enabled")
    else:
        print("ℹ️  OpenAI API not configured - using rule-based analysis")
    
    print("\n📡 Fetching positions from Bybit...")
    
    try:
        # Fetch positions
        raw_positions = bybit_api.get_positions()
        print(f"✅ Found {len(raw_positions)} open position(s)")
        
        if not raw_positions:
            print("\n✨ No open positions to analyze!")
            return 0
        
        # Analyze positions
        print("🔍 Analyzing positions...")
        analysis = analyzer.analyze_positions(raw_positions)
        
        # Get AI suggestions
        print("🧠 Generating suggestions...")
        suggestions = ai_analysis.analyze_with_ai(analysis)
        
        # Print report
        print_portfolio_summary(analysis)
        print_position_risks(analysis)
        print_suggestions(suggestions)
        
        print("\n" + "=" * 60)
        print("✅ Analysis complete!")
        print("=" * 60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


def print_usage() -> None:
    """Print usage information."""
    print("Bybit Position Analysis Bot")
    print("\nUsage:")
    print("  python bot.py list       List all open positions")
    print("  python bot.py orders     List all open orders (limit, SL, TP)")
    print("  python bot.py analyze    Analyze current positions")
    print("  python bot.py help       Show this help message")
    print("\nConfiguration:")
    print("  Set environment variables:")
    print("    BYBIT_API_KEY      - Your Bybit API key")
    print("    BYBIT_API_SECRET   - Your Bybit API secret")
    print("    OPENAI_API_KEY     - (Optional) OpenAI API key for AI analysis")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return 1
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        return list_positions_command()
    elif command == 'orders':
        return orders_command()
    elif command == 'analyze':
        return analyze_command()
    elif command in ['help', '--help', '-h']:
        print_usage()
        return 0
    else:
        print(f"Unknown command: {command}")
        print_usage()
        return 1


if __name__ == '__main__':
    sys.exit(main())
