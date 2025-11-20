"""
AI-enhanced analysis module.
Provides intelligent insights using OpenAI or rule-based fallback.
"""

import json
from typing import Dict, Any, List
from config import Config


def analyze_with_ai(analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Analyze position data and provide actionable suggestions.
    Uses OpenAI if available, otherwise falls back to rule-based analysis.
    
    Args:
        analysis_data: Complete analysis from analyzer module
    
    Returns:
        Dictionary with categorized suggestions (urgent, recommended, optional)
    """
    if Config.has_openai():
        try:
            return _openai_analysis(analysis_data)
        except Exception as e:
            print(f"⚠️  OpenAI analysis failed ({str(e)}), using fallback...")
            return _fallback_analysis(analysis_data)
    else:
        return _fallback_analysis(analysis_data)


def _openai_analysis(analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Use OpenAI API to generate intelligent suggestions.
    
    Args:
        analysis_data: Complete analysis data
    
    Returns:
        Categorized suggestions
    """
    import requests
    
    # Prepare prompt
    system_prompt = """You are an expert cryptocurrency futures trading risk analyst. 
Analyze the provided portfolio data and provide specific, actionable suggestions.
Focus on: liquidation risks, over-leverage, concentration risk, and hedging opportunities.
Be concise and specific. Provide 2-4 suggestions per category."""
    
    user_prompt = f"""Analyze this futures portfolio and provide actionable suggestions:

Portfolio Summary:
- Long Exposure: ${analysis_data['portfolio']['total_long_exposure']:,.2f}
- Short Exposure: ${analysis_data['portfolio']['total_short_exposure']:,.2f}
- Bias: {analysis_data['portfolio']['bias']}
- Total Positions: {analysis_data['portfolio']['total_positions']}
- Total PnL: ${analysis_data['portfolio']['total_unrealized_pnl']:,.2f}

Risk Metrics:
- High Leverage Positions: {analysis_data['risks']['high_leverage_count']}
- Close to Liquidation: {analysis_data['risks']['close_liquidation_count']}

Top Positions:
{json.dumps([{
    'symbol': p['symbol'],
    'side': p['side'],
    'leverage': p['leverage'],
    'liq_distance': f"{p['liquidation_distance_pct']:.2f}%",
    'pnl': p['unrealized_pnl']
} for p in analysis_data['positions'][:5]], indent=2)}

Provide suggestions in JSON format:
{{
    "urgent": ["suggestion 1", "suggestion 2"],
    "recommended": ["suggestion 1", "suggestion 2"],
    "optional": ["suggestion 1", "suggestion 2"]
}}"""
    
    # Call OpenAI API
    headers = {
        'Authorization': f'Bearer {Config.OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 1000
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    
    # Try to parse JSON from response
    try:
        # Extract JSON if wrapped in markdown code blocks
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        suggestions = json.loads(content)
        return suggestions
    except json.JSONDecodeError:
        # If parsing fails, use fallback
        return _fallback_analysis(analysis_data)


def _fallback_analysis(analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Rule-based analysis when OpenAI is not available.
    
    Args:
        analysis_data: Complete analysis data
    
    Returns:
        Categorized suggestions
    """
    urgent = []
    recommended = []
    optional = []
    
    portfolio = analysis_data['portfolio']
    positions = analysis_data['positions']
    risks = analysis_data['risks']
    
    # URGENT: Close liquidation positions
    close_liq_positions = [
        p for p in positions if p['liquidation_distance_pct'] < 10
    ]
    for pos in close_liq_positions:
        urgent.append(
            f"Add collateral or reduce {pos['symbol']} {pos['side'].upper()} position "
            f"({pos['liquidation_distance_pct']:.2f}% from liquidation)"
        )
    
    # URGENT: High leverage positions
    high_lev_positions = [
        p for p in positions if p['leverage'] > 10
    ]
    for pos in high_lev_positions[:2]:  # Top 2
        urgent.append(
            f"Reduce leverage on {pos['symbol']} (currently {pos['leverage']:.1f}x)"
        )
    
    # RECOMMENDED: Cluster concentration
    if portfolio['clusters']:
        max_cluster = max(portfolio['clusters'].items(), key=lambda x: x[1])
        if max_cluster[1] > 40:
            recommended.append(
                f"Diversify away from {max_cluster[0]} cluster ({max_cluster[1]:.1f}% of portfolio)"
            )
    
    # RECOMMENDED: Take profits
    profitable_positions = [
        p for p in positions 
        if p['pnl_status'] == 'profit' and p['unrealized_pnl'] > 100
    ]
    if profitable_positions:
        recommended.append(
            f"Consider taking partial profits on {len(profitable_positions)} profitable position(s)"
        )
    
    # RECOMMENDED: Portfolio bias
    if portfolio['bias'] in ['long', 'short']:
        opposite = 'short' if portfolio['bias'] == 'long' else 'long'
        recommended.append(
            f"Portfolio is heavily {portfolio['bias'].upper()} biased - consider {opposite} hedges"
        )
    
    # OPTIONAL: Stop losses
    if any(p['leverage_risk'] in ['medium', 'high'] for p in positions):
        optional.append("Set tighter stop losses on high-leverage positions")
    
    # OPTIONAL: Losing positions
    losing_positions = [
        p for p in positions 
        if p['pnl_status'] == 'loss' and p['unrealized_pnl'] < -100
    ]
    if losing_positions:
        optional.append(
            f"Review {len(losing_positions)} losing position(s) for potential exit"
        )
    
    # OPTIONAL: General risk management
    if risks['high_leverage_count'] > 3:
        optional.append("Consider reducing overall portfolio leverage")
    
    # Ensure we have at least some suggestions
    if not urgent and not recommended and not optional:
        optional.append("Portfolio looks relatively balanced - continue monitoring")
    
    return {
        'urgent': urgent[:4],
        'recommended': recommended[:4],
        'optional': optional[:4]
    }
