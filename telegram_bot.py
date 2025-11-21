#!/usr/bin/env python3
"""
Telegram Bot for Bybit Position Analysis
Provides a Telegram interface to interact with the Bybit analysis bot.
"""

import asyncio
import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import Config
import bybit_api
import analyzer
import ai_analysis

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for Bybit position analysis."""
    
    def __init__(self, token: str):
        """Initialize the bot with a Telegram token."""
        self.token = token
    
    def get_navigation_keyboard(self, exclude: str = None) -> InlineKeyboardMarkup:
        """
        Create navigation keyboard with quick action buttons.
        
        Args:
            exclude: Command to exclude from the keyboard (e.g., 'balance', 'list')
        
        Returns:
            InlineKeyboardMarkup with navigation buttons
        """
        buttons = []
        
        # Row 1: Balance and Positions
        row1 = []
        if exclude != 'balance':
            row1.append(InlineKeyboardButton("💰 Balance", callback_data='balance'))
        if exclude != 'list':
            row1.append(InlineKeyboardButton("📊 Positions", callback_data='list'))
        if row1:
            buttons.append(row1)
        
        # Row 2: Orders and Analyze
        row2 = []
        if exclude != 'orders':
            row2.append(InlineKeyboardButton("📋 Orders", callback_data='orders'))
        if exclude != 'analyze':
            row2.append(InlineKeyboardButton("🔍 Analyze", callback_data='analyze'))
        if row2:
            buttons.append(row2)
        
        # Row 3: Refresh current view
        if exclude:
            buttons.append([InlineKeyboardButton("🔄 Refresh", callback_data=exclude)])
        
        return InlineKeyboardMarkup(buttons)
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        keyboard = [
            [
                InlineKeyboardButton("� Balance", callback_data='balance'),
                InlineKeyboardButton("� Positions", callback_data='list'),
            ],
            [
                InlineKeyboardButton("📋 Orders", callback_data='orders'),
                InlineKeyboardButton("🔍 Analyze", callback_data='analyze'),
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data='help'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            f"👋 Welcome {user.mention_html()}!\n\n"
            "🤖 <b>Bybit Position Analysis Bot</b>\n\n"
            "I can help you monitor and analyze your Bybit positions.\n\n"
            "Choose an option below or use these commands:\n"
            "/balance - Show account balance\n"
            "/list - List all open positions\n"
            "/orders - List all open orders\n"
            "/analyze - Analyze positions with AI\n"
            "/help - Show help message\n"
        )
        
        await update.message.reply_html(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        help_text = (
            "🤖 <b>Bybit Position Analysis Bot</b>\n\n"
            "<b>Available Commands:</b>\n\n"
            "/start - Start the bot and show menu\n"
            "/balance - Show account balance and margin\n"
            "/list - List all open positions\n"
            "/orders - List all open orders (limit, SL, TP)\n"
            "/analyze - Analyze current positions with AI\n"
            "/help - Show this help message\n\n"
            "<b>Features:</b>\n"
            "• Account balance tracking\n"
            "• Real-time position monitoring\n"
            "• Risk analysis and metrics\n"
            "• AI-powered suggestions\n"
            "• Order tracking\n\n"
            "<b>Configuration:</b>\n"
            f"• API URL: {Config.BYBIT_BASE_URL}\n"
            f"• AI Provider: {Config.get_ai_provider() or 'None'}\n"
        )
        
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(help_text, parse_mode='HTML')
        else:
            await update.message.reply_html(help_text)
    
    async def show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show account balance and margin information."""
        if update.callback_query:
            await update.callback_query.answer()
            message = await update.callback_query.edit_message_text("💰 Fetching balance from Bybit...")
        else:
            message = await update.message.reply_text("💰 Fetching balance from Bybit...")
        
        try:
            # Fetch wallet balance
            balance = bybit_api.get_wallet_balance()
            
            # Parse balance values
            total_equity = float(balance.get('totalEquity', 0))
            available_balance = float(balance.get('totalAvailableBalance', 0))
            margin_balance = float(balance.get('totalMarginBalance', 0))
            initial_margin = float(balance.get('totalInitialMargin', 0))
            maintenance_margin = float(balance.get('totalMaintenanceMargin', 0))
            
            # Calculate margin usage percentage
            margin_usage = 0
            if margin_balance > 0:
                margin_usage = (initial_margin / margin_balance) * 100
            
            # Format response
            response = f"💰 <b>Account Balance</b>\n"
            response += f"{'='*50}\n\n"
            
            response += f"<b>💵 Balance Overview</b>\n"
            response += f"Total Equity: <b>${total_equity:,.2f}</b> USDT\n"
            response += f"Available Balance: <b>${available_balance:,.2f}</b> USDT\n"
            response += f"Margin Balance: ${margin_balance:,.2f} USDT\n\n"
            
            response += f"<b>📊 Margin Information</b>\n"
            response += f"Initial Margin: ${initial_margin:,.2f} USDT\n"
            response += f"Maintenance Margin: ${maintenance_margin:,.2f} USDT\n"
            response += f"Margin Usage: <b>{margin_usage:.2f}%</b>\n\n"
            
            # Add margin usage warning
            if margin_usage > 80:
                response += "🔴 <b>WARNING:</b> High margin usage! Consider reducing positions.\n"
            elif margin_usage > 60:
                response += "🟡 <b>CAUTION:</b> Moderate margin usage. Monitor closely.\n"
            else:
                response += "🟢 <b>HEALTHY:</b> Margin usage is within safe limits.\n"
            
            # Add navigation buttons
            keyboard = self.get_navigation_keyboard(exclude='balance')
            await message.edit_text(response, parse_mode='HTML', reply_markup=keyboard)
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            keyboard = self.get_navigation_keyboard()
            await message.edit_text(error_msg, reply_markup=keyboard)
            logger.error(f"Error fetching balance: {e}")
    
    async def list_positions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List all open positions."""
        # Send "processing" message
        if update.callback_query:
            await update.callback_query.answer()
            message = await update.callback_query.edit_message_text("📡 Fetching positions from Bybit...")
        else:
            message = await update.message.reply_text("📡 Fetching positions from Bybit...")
        
        try:
            # Fetch positions
            positions = bybit_api.get_positions()
            
            if not positions:
                await message.edit_text("ℹ️ No open positions found.")
                return
            
            # Format positions
            response = f"📋 <b>Bybit Positions List</b>\n"
            response += f"{'='*50}\n\n"
            response += f"✅ Found {len(positions)} open position(s)\n\n"
            
            total_value = 0
            total_pnl = 0
            
            for pos in positions:
                symbol = pos.get('symbol', 'N/A')
                side = pos.get('side', 'N/A')
                size = float(pos.get('size', 0))
                entry_price = float(pos.get('avgPrice', 0))
                mark_price = float(pos.get('markPrice', 0))
                leverage = float(pos.get('leverage', 0))
                unrealized_pnl = float(pos.get('unrealisedPnl', 0))
                
                position_value = abs(size * mark_price)
                total_value += position_value
                total_pnl += unrealized_pnl
                
                pnl_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
                side_emoji = "📈" if side == "Buy" else "📉"
                
                response += f"{side_emoji} <b>{symbol}</b> ({side})\n"
                response += f"  Size: {size:.4f} | Entry: ${entry_price:.4f}\n"
                response += f"  Mark: ${mark_price:.4f} | Lev: {leverage}x\n"
                response += f"  {pnl_emoji} PnL: ${unrealized_pnl:.2f}\n\n"
            
            
            response += f"{'='*50}\n"
            response += f"💰 Total Value: ${total_value:.2f} USDT\n"
            response += f"💰 Total PnL: ${total_pnl:.2f} USDT\n\n"
            
            # Add balance info
            try:
                balance = bybit_api.get_wallet_balance()
                available = float(balance.get('totalAvailableBalance', 0))
                equity = float(balance.get('totalEquity', 0))
                response += f"<b>Account Balance:</b>\n"
                response += f"Available: ${available:,.2f} USDT\n"
                response += f"Total Equity: ${equity:,.2f} USDT\n"
            except:
                pass  # Silently fail if balance fetch fails
            
            
            # Add navigation buttons
            keyboard = self.get_navigation_keyboard(exclude='list')
            
            # Split message if too long
            if len(response) > 4096:
                for i in range(0, len(response), 4096):
                    if i == 0:
                        await message.edit_text(response[i:i+4096], parse_mode='HTML', reply_markup=keyboard)
                    else:
                        await update.effective_chat.send_message(response[i:i+4096], parse_mode='HTML')
            else:
                await message.edit_text(response, parse_mode='HTML', reply_markup=keyboard)
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            keyboard = self.get_navigation_keyboard()
            await message.edit_text(error_msg, reply_markup=keyboard)
            logger.error(f"Error fetching positions: {e}")
    
    async def list_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List all open orders."""
        if update.callback_query:
            await update.callback_query.answer()
            message = await update.callback_query.edit_message_text("📡 Fetching orders from Bybit...")
        else:
            message = await update.message.reply_text("📡 Fetching orders from Bybit...")
        
        try:
            orders = bybit_api.get_open_orders()
            
            if not orders:
                await message.edit_text("ℹ️ No open orders found.")
                return
            
            response = f"📋 <b>Bybit Open Orders</b>\n"
            response += f"{'='*50}\n\n"
            response += f"✅ Found {len(orders)} open order(s)\n\n"
            
            for order in orders:
                symbol = order.get('symbol', 'N/A')
                side = order.get('side', 'N/A')
                order_type = order.get('orderType', 'N/A')
                price = float(order.get('price', 0))
                qty = float(order.get('qty', 0))
                order_id = order.get('orderId', 'N/A')
                
                side_emoji = "📈" if side == "Buy" else "📉"
                
                response += f"{side_emoji} <b>{symbol}</b> ({side})\n"
                response += f"  Type: {order_type}\n"
                response += f"  Price: ${price:.4f} | Qty: {qty:.4f}\n"
                response += f"  Order ID: <code>{order_id}</code>\n\n"
            
            if len(response) > 4096:
                for i in range(0, len(response), 4096):
                    if i == 0:
                        await message.edit_text(response[i:i+4096], parse_mode='HTML')
                    else:
                        await update.effective_chat.send_message(response[i:i+4096], parse_mode='HTML')
            else:
                keyboard = self.get_navigation_keyboard(exclude='orders')
                await message.edit_text(response, parse_mode='HTML', reply_markup=keyboard)
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            keyboard = self.get_navigation_keyboard()
            await message.edit_text(error_msg, reply_markup=keyboard)
            logger.error(f"Error fetching orders: {e}")
    
    async def analyze_positions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Analyze positions with AI."""
        if update.callback_query:
            await update.callback_query.answer()
            message = await update.callback_query.edit_message_text("🔍 Analyzing positions...")
        else:
            message = await update.message.reply_text("🔍 Analyzing positions...")
        
        try:
            # Fetch positions and orders
            positions = bybit_api.get_positions()
            orders = bybit_api.get_open_orders()
            
            if not positions and not orders:
                await message.edit_text("ℹ️ No open positions or orders to analyze.")
                return
            
            # Analyze positions and orders
            analysis = analyzer.analyze_positions(positions, orders)
            
            # Generate AI suggestions
            suggestions = ai_analysis.analyze_with_ai(analysis)
            
            # Format response
            response = f"🔍 <b>Position Analysis</b>\n"
            response += f"{'='*50}\n"
            response += f"<i>Risk Tolerance: 4% per day</i>\n\n"
            
            # Portfolio summary
            portfolio = analysis['portfolio']
            response += f"<b>📊 Portfolio Summary</b>\n"
            response += f"Long Exposure: ${portfolio['total_long_exposure']:.2f}\n"
            response += f"Short Exposure: ${portfolio['total_short_exposure']:.2f}\n"
            response += f"Net Exposure: ${portfolio['net_exposure']:.2f}\n"
            response += f"Total PnL: ${portfolio['total_unrealized_pnl']:.2f}\n"
            response += f"Bias: {portfolio['bias'].upper()}\n"
            response += f"Positions: {portfolio['total_positions']}\n\n"
            
            # High risk positions
            analyzed_positions = analysis['positions']
            high_risk = [p for p in analyzed_positions if p['leverage_risk'] == 'high']
            if high_risk:
                response += f"<b>⚠️ High Risk Positions ({len(high_risk)})</b>\n"
                for pos in high_risk[:5]:  # Show top 5
                    response += f"• {pos['symbol']} ({pos['side'].upper()})\n"
                    response += f"  Lev: {pos['leverage']}x | Liq: {pos['liquidation_distance_pct']:.2f}%\n"
                response += "\n"
            
            # Suggestions
            if suggestions:
                response += f"<b>💡 Suggestions</b>\n\n"
                
                if suggestions.get('urgent'):
                    response += f"🔴 <b>URGENT:</b>\n"
                    for sug in suggestions['urgent'][:3]:
                        response += f"• {sug}\n"
                    response += "\n"
                
                if suggestions.get('recommended'):
                    response += f"🟡 <b>RECOMMENDED:</b>\n"
                    for sug in suggestions['recommended'][:3]:
                        response += f"• {sug}\n"
                    response += "\n"
            
            # Split message if too long
            
            # Add navigation buttons
            keyboard = self.get_navigation_keyboard(exclude='analyze')
            
            # Split message if too long
            if len(response) > 4096:
                for i in range(0, len(response), 4096):
                    if i == 0:
                        await message.edit_text(response[i:i+4096], parse_mode='HTML', reply_markup=keyboard)
                    else:
                        await update.effective_chat.send_message(response[i:i+4096], parse_mode='HTML')
            else:
                await message.edit_text(response, parse_mode='HTML', reply_markup=keyboard)
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            keyboard = self.get_navigation_keyboard()
            await message.edit_text(error_msg, reply_markup=keyboard)
            logger.error(f"Error analyzing positions: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks."""
        query = update.callback_query
        
        if query.data == 'balance':
            await self.show_balance(update, context)
        elif query.data == 'list':
            await self.list_positions(update, context)
        elif query.data == 'orders':
            await self.list_orders(update, context)
        elif query.data == 'analyze':
            await self.analyze_positions(update, context)
        elif query.data == 'help':
            await self.help_command(update, context)
    
    def run(self):
        """Run the bot."""
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("balance", self.show_balance))
        application.add_handler(CommandHandler("list", self.list_positions))
        application.add_handler(CommandHandler("orders", self.list_orders))
        application.add_handler(CommandHandler("analyze", self.analyze_positions))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Run the bot
        logger.info("Starting Telegram bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    # Validate configuration
    is_valid, error = Config.validate()
    if not is_valid:
        logger.error(f"Configuration error: {error}")
        print(f"❌ Configuration error: {error}")
        return
    
    # Get Telegram token
    telegram_token = Config.TELEGRAM_BOT_TOKEN if hasattr(Config, 'TELEGRAM_BOT_TOKEN') else None
    if not telegram_token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment")
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable is not set")
        print("\nPlease add your Telegram bot token to the .env file:")
        print("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here")
        return
    
    # Create and run bot
    bot = TelegramBot(telegram_token)
    bot.run()


if __name__ == '__main__':
    main()
