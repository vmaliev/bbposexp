#!/usr/bin/env python3
"""
Test script to validate analyzer logic with mock data.
"""

import json
from analyzer import analyze_positions

# Mock position data (simulating Bybit API response)
mock_positions = [
    {
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'size': '0.5',
        'avgPrice': '42150.00',
        'markPrice': '43200.00',
        'liqPrice': '39800.00',
        'leverage': '12.5',
        'unrealisedPnl': '525.00'
    },
    {
        'symbol': 'ETHUSDT',
        'side': 'Sell',
        'size': '5.0',
        'avgPrice': '2250.00',
        'markPrice': '2180.00',
        'liqPrice': '2420.00',
        'leverage': '8.0',
        'unrealisedPnl': '350.00'
    },
    {
        'symbol': 'ARBUSDT',
        'side': 'Buy',
        'size': '1000',
        'avgPrice': '1.85',
        'markPrice': '1.92',
        'liqPrice': '1.65',
        'leverage': '5.0',
        'unrealisedPnl': '70.00'
    },
    {
        'symbol': 'DOGEUSDT',
        'side': 'Buy',
        'size': '10000',
        'avgPrice': '0.085',
        'markPrice': '0.088',
        'liqPrice': '0.075',
        'leverage': '3.0',
        'unrealisedPnl': '30.00'
    }
]

def test_analyzer():
    """Test the analyzer with mock data."""
    print("🧪 Testing Analyzer with Mock Data\n")
    print("=" * 60)
    
    # Run analysis
    analysis = analyze_positions(mock_positions)
    
    # Print results
    print("\n📊 Analysis Results:\n")
    print(json.dumps(analysis, indent=2))
    
    # Validate key metrics
    print("\n✅ Validation:")
    print(f"  - Total positions: {analysis['portfolio']['total_positions']}")
    print(f"  - Portfolio bias: {analysis['portfolio']['bias']}")
    print(f"  - High leverage positions: {analysis['risks']['high_leverage_count']}")
    print(f"  - Close to liquidation: {analysis['risks']['close_liquidation_count']}")
    
    # Check position analysis
    print("\n📋 Position Details:")
    for pos in analysis['positions']:
        print(f"  - {pos['symbol']}: {pos['leverage_risk']} risk, "
              f"{pos['liquidation_distance_pct']:.2f}% from liq, "
              f"cluster: {pos['cluster']}")
    
    print("\n✅ Test completed successfully!")

if __name__ == '__main__':
    test_analyzer()
