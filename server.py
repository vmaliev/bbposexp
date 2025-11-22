import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
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
            "analysis": ai_suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
