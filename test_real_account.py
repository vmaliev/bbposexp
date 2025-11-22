#!/usr/bin/env python3
"""
Test script to fetch and analyze real data from Bybit API.
"""

import json
import bybit_api
import analyzer
import ai_analysis
from config import Config

def test_real_account():
    """Fetch real data and run analysis."""
    print("🚀 Connecting to Bybit API...\n")
    
    try:
        # 1. Fetch Data
        print("📡 Fetching positions...")
        positions = bybit_api.get_positions()
        print(f"   ✅ Found {len(positions)} positions")
        
        print("📡 Fetching open orders...")
        orders = bybit_api.get_open_orders()
        print(f"   ✅ Found {len(orders)} orders")
        
        # 2. Run Analysis
        print("\n🔍 Running Analysis...")
        analysis = analyzer.analyze_positions(positions, orders)
        
        # 3. Print Analysis Results
        print("\n📊 Portfolio Summary:")
        print(f"  - Total Equity: ${analysis['portfolio']['total_long_exposure'] + analysis['portfolio']['total_short_exposure']:,.2f} (Exposure)")
        print(f"  - Net Exposure: ${analysis['portfolio']['net_exposure']:,.2f}")
        print(f"  - Bias: {analysis['portfolio']['bias'].upper()}")
        print(f"  - Total PnL: ${analysis['portfolio']['total_unrealized_pnl']:,.2f}")
        
        print("\n⚠️ Risk Metrics:")
        print(f"  - High Leverage Positions: {analysis['risks']['high_leverage_count']}")
        print(f"  - Close to Liquidation: {analysis['risks']['close_liquidation_count']}")
        print(f"  - Positions without Stop Loss: {analysis['risks'].get('no_stop_loss_count', 0)}")
        print(f"  - Non-Hedged No-SL Positions: {len(analysis['risks'].get('risky_positions', []))}")
        print(f"  - Hedged Symbols: {analysis['risks'].get('hedged_symbols', [])}")
        
        # 4. Print Positions
        if analysis['positions']:
            print("\n📋 Open Positions:")
            for pos in analysis['positions']:
                sl_status = "✅" if pos['stop_loss'] > 0 else "❌ NO SL"
                print(f"  - {pos['symbol']} ({pos['side'].upper()}) {pos['leverage']}x")
                print(f"    PnL: ${pos['unrealized_pnl']:.2f} | Liq Dist: {pos['liquidation_distance_pct']:.2f}%")
                print(f"    SL: {sl_status} | Risk: {pos['leverage_risk'].upper()}")
                print("-" * 40)
        else:
            print("\nℹ️ No open positions.")

        # 5. Get AI/Fallback Recommendations
        print("\n💡 Generating Recommendations...")
        suggestions = ai_analysis.analyze_with_ai(analysis)
        
        print("-" * 40)
        if suggestions.get('urgent'):
            print("\n🔴 URGENT:")
            for s in suggestions['urgent']:
                print(f"  • {s}")
                
        if suggestions.get('recommended'):
            print("\n🟡 RECOMMENDED:")
            for s in suggestions['recommended']:
                print(f"  • {s}")
                
        if suggestions.get('optional'):
            print("\n🟢 OPTIONAL:")
            for s in suggestions['optional']:
                print(f"  • {s}")
                
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_real_account()
