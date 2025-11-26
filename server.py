import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import bybit_api
import analyzer
import ai_analysis
import os
from config import Config

app = FastAPI()

# Serve static files
app.mount("/css", StaticFiles(directory="webapp/css"), name="css")
app.mount("/js", StaticFiles(directory="webapp/js"), name="js")

@app.get("/")
async def read_index():
    return FileResponse("webapp/index.html")

@app.get("/api/data")
async def get_data():
    try:
        # Fetch all data in parallel (conceptually, though here sequential is fine for now)
        balance = bybit_api.get_wallet_balance()
        positions = bybit_api.get_positions()
        orders = bybit_api.get_open_orders()
        
        # Calculate start of day for daily PnL
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = int(start_of_day.timestamp() * 1000)
        
        closed_pnl_list = bybit_api.get_closed_pnl(start_time=start_time)
        
        # Calculate PnL metrics
        realized_pnl = sum(float(item.get('closedPnl', 0)) for item in closed_pnl_list)
        unrealized_pnl = sum(float(pos.get('unrealisedPnl', 0)) for pos in positions)
        total_daily_pnl = realized_pnl + unrealized_pnl
        
        pnl_data = {
            "realized": realized_pnl,
            "unrealized": unrealized_pnl,
            "total": total_daily_pnl,
            "trade_count": len(closed_pnl_list)
        }
        
        # Perform analysis
        analysis_data = analyzer.analyze_positions(positions, orders)
        
        # Get AI suggestions (cached or fresh)
        # For now, we'll do a quick rule-based analysis to avoid API costs/latency on every poll
        # Ideally, this should be cached or triggered explicitly
        ai_suggestions = ai_analysis.analyze_with_ai(analysis_data)
        
        return {
            "balance": balance,
            "positions": positions,
            "orders": orders,
            "pnl": pnl_data,
            "analysis": ai_suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
async def get_trades():
    try:
        # Fetch closed PnL records
        # The user wants to see PnL, so we prioritize the closed PnL endpoint which guarantees this data
        closed_pnl_list = bybit_api.get_closed_pnl(limit=50)
        
        trades = []
        for item in closed_pnl_list:
            # Map closed PnL fields to the structure expected by the frontend
            trades.append({
                "symbol": item.get("symbol"),
                "side": item.get("side"),
                "execTime": item.get("updatedTime"), 
                "execPrice": float(item.get("avgExitPrice", 0)),
                "execQty": float(item.get("qty", 0)),
                "execFee": float(item.get("execFee", 0)),  # Try to get fee if available
                "closedPnl": float(item.get("closedPnl", 0)) if item.get("closedPnl") is not None else None,
                "orderId": item.get("orderId")
            })
            
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
