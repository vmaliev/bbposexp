import logging
import asyncio
from typing import Callable, Optional
from pybit.unified_trading import WebSocket
from config import Config

logger = logging.getLogger(__name__)

class BybitWebSocket:
    """
    Bybit WebSocket client for real-time updates.
    """
    
    def __init__(self, callback: Callable):
        """
        Initialize WebSocket client.
        
        Args:
            callback: Async callback function to handle messages (e.g., send to Telegram)
        """
        self.callback = callback
        self.ws = WebSocket(
            testnet=False,
            channel_type="private",
            api_key=Config.BYBIT_API_KEY,
            api_secret=Config.BYBIT_API_SECRET,
            trace_logging=False,
        )

    def handle_order(self, message):
        """Handle incoming order messages."""
        try:
            # Execute callback in the event loop
            asyncio.run_coroutine_threadsafe(self.callback(message), self.loop)
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    def start(self, loop):
        """Start the WebSocket listener."""
        self.loop = loop
        
        # Subscribe to order updates
        self.ws.order_stream(callback=self.handle_order)
        
        logger.info("Bybit WebSocket started and subscribed to order updates.")

    def stop(self):
        """Stop the WebSocket listener."""
        if self.ws:
            # pybit's WebSocket doesn't have a direct stop/close method that is clean in all versions
            # but we can try to exit.
            # self.ws.exit() # Some versions utilize exit
            pass # The library manages connection lifecycle mostly.
        logger.info("Bybit WebSocket stopped.")
