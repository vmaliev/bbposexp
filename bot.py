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
    
    if command == 'analyze':
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
