#!/usr/bin/env python3
"""
Telegram Bot for Bybit Position Analysis
Provides a Telegram interface to interact with the Bybit analysis bot.
"""

import asyncio
import logging
import html
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
        
        # Row 1: Balance and PnL
        row1 = []
        if exclude != 'balance':
            row1.append(InlineKeyboardButton("💰 Balance", callback_data='balance'))
        if exclude != 'pnl':
            row1.append(InlineKeyboardButton("📈 PnL Today", callback_data='pnl'))
        if row1:
            buttons.append(row1)
        
        # Row 2: Positions and Orders
        row2 = []
        if exclude != 'list':
            row2.append(InlineKeyboardButton("📊 Positions", callback_data='list'))
        if exclude != 'orders':
            row2.append(InlineKeyboardButton("📋 Orders", callback_data='orders'))
        if row2:
            buttons.append(row2)
            
        # Row 3: Trades and Analyze
        row3 = []
        if exclude != 'trades':
            row3.append(InlineKeyboardButton("🤝 Trades", callback_data='trades'))
        if exclude != 'analyze':
            row3.append(InlineKeyboardButton("🔍 Analyze", callback_data='analyze'))
        if row3:
            buttons.append(row3)
        
        # Row 4: Refresh current view
        if exclude:
            buttons.append([InlineKeyboardButton("🔄 Refresh", callback_data=exclude)])
        
        return InlineKeyboardMarkup(buttons)
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        # Web App URL (Updated with ngrok)
        web_app_url = Config.WEB_APP_URL or "https://example.com"
        
        keyboard = [
            [
                InlineKeyboardButton("🚀 Open Dashboard", web_app={"url": web_app_url}),
            ],
            [
                InlineKeyboardButton("💰 Balance", callback_data='balance'),
                InlineKeyboardButton("📈 PnL Today", callback_data='pnl'),
            ],
            [
                InlineKeyboardButton("📊 Positions", callback_data='list'),
                InlineKeyboardButton("📋 Orders", callback_data='orders'),
            ],
            [
                InlineKeyboardButton("🤝 Trades", callback_data='trades'),
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
            "/pnl - Show today's PnL\n"
            "/list - List all open positions\n"
            "/orders - List all open orders\n"
            "/trades - Show recent trades\n"
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
            "/pnl - Show today's PnL\n"
            "/list - List all open positions\n"
            "/orders - List all open orders (limit, SL, TP)\n"
            "/trades - Show recent trades\n"
            "/analyze - Analyze current positions with AI\n"
            "/help - Show this help message\n\n"
            "<b>Features:</b>\n"
            "• Account balance tracking\n"
            "• Real-time position monitoring\n"
            "• Trade history\n"
            "• Daily PnL calculation\n"
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
            
            # Fetch Tickers for Funding Rates
            try:
                tickers = bybit_api.get_tickers(category='linear')
                tickers_map = {t['symbol']: t for t in tickers}
            except Exception as e:
                logger.warning(f"Failed to fetch tickers: {e}")
                tickers_map = {}
            
            header = f"📋 <b>Bybit Positions List</b>\n"
            header += f"{'='*50}\n\n"
            header += f"✅ Found {len(positions)} open position(s)\n\n"
            
            total_value = 0
            total_pnl = 0
            
            current_message = header
            is_first_message = True
            
            for pos in positions:
                symbol = html.escape(str(pos.get('symbol', 'N/A')))
                side = html.escape(str(pos.get('side', 'N/A')))
                size = float(pos.get('size', 0))
                entry_price = float(pos.get('avgPrice', 0))
                mark_price = float(pos.get('markPrice', 0))
                leverage = float(pos.get('leverage', 0))
                unrealized_pnl = float(pos.get('unrealisedPnl', 0))
                
                position_value = abs(size * mark_price)
                total_value += position_value
                total_pnl += unrealized_pnl
                
                # Default funding info
                pos['fundingRate'] = 0.0
                pos['estFundingFee'] = 0.0
                pos['fundingInfoStr'] = ""
                
                if symbol in tickers_map:
                    ticker = tickers_map[symbol]
                    funding_rate = float(ticker.get('fundingRate', 0))
                    est_fee = position_value * funding_rate
                    
                    # Store for sorting and display
                    pos['fundingRate'] = funding_rate
                    pos['estFundingFee'] = est_fee
                    
                    # Determine Pay/Receive
                    is_long = (side == 'Buy')
                    is_pay = (is_long and funding_rate > 0) or (not is_long and funding_rate < 0)
                    
                    action_str = "🔴 Pay" if is_pay else "🟢 Receive"
                    rate_pct = funding_rate * 100
                    
                    # Get next funding time and format it
                    next_funding_time_ms = int(ticker.get('nextFundingTime', 0))
                    funding_time_str = "N/A"
                    funding_countdown_str = ""
                    if next_funding_time_ms > 0:
                        import datetime
                        # Convert milliseconds to seconds, then to datetime object in UTC
                        dt_object = datetime.datetime.fromtimestamp(next_funding_time_ms / 1000, tz=datetime.timezone.utc)
                        funding_time_str = dt_object.strftime('%H:%M UTC') # Format as HH:MM UTC
                        
                        # Calculate countdown
                        now_utc = datetime.datetime.now(datetime.timezone.utc)
                        time_until_funding = dt_object - now_utc
                        
                        if time_until_funding.total_seconds() > 0:
                            hours, remainder = divmod(int(time_until_funding.total_seconds()), 3600)
                            minutes, seconds = divmod(remainder, 60)
                            funding_countdown_str = f" ({hours:02d}h {minutes:02d}m)"
                        
                    pos['fundingInfoStr'] = f"  Funding: {rate_pct:.4f}% | {action_str} ${abs(est_fee):.4f}{funding_countdown_str}\n"
                
            # Sort positions by absolute funding rate (lowest rate first)
            positions.sort(key=lambda p: abs(p.get('fundingRate', 0.0)), reverse=False)
            
            for pos in positions:
                symbol = html.escape(str(pos.get('symbol', 'N/A')))
                side = html.escape(str(pos.get('side', 'N/A')))
                size = float(pos.get('size', 0))
                entry_price = float(pos.get('avgPrice', 0))
                mark_price = float(pos.get('markPrice', 0))
                leverage = float(pos.get('leverage', 0))
                unrealized_pnl = float(pos.get('unrealisedPnl', 0))
                
                pnl_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
                side_emoji = "📈" if side == "Buy" else "📉"
                
                pos_str = f"{side_emoji} <b>{symbol}</b> ({side})\n"
                pos_str += f"  Size: {size:.4f} | Entry: ${entry_price:.4f}\n"
                pos_str += f"  Mark: ${mark_price:.4f} | Lev: {leverage}x\n"
                pos_str += f"  {pnl_emoji} PnL: ${unrealized_pnl:.2f}\n"
                pos_str += pos['fundingInfoStr']
                pos_str += "\n"
                
                if len(current_message) + len(pos_str) > 4000:
                    if is_first_message:
                        await message.edit_text(current_message, parse_mode='HTML')
                        is_first_message = False
                    else:
                        await update.effective_chat.send_message(current_message, parse_mode='HTML')
                    current_message = pos_str
                else:
                    current_message += pos_str
            
            
            footer = f"{'='*50}\n"
            footer += f"💰 Total Value: ${total_value:.2f} USDT\n"
            footer += f"💰 Total PnL: ${total_pnl:.2f} USDT\n\n"
            
            # Add balance info
            try:
                balance = bybit_api.get_wallet_balance()
                available = float(balance.get('totalAvailableBalance', 0))
                equity = float(balance.get('totalEquity', 0))
                footer += f"<b>Account Balance:</b>\n"
                footer += f"Available: ${available:,.2f} USDT\n"
                footer += f"Total Equity: ${equity:,.2f} USDT\n"
            except:
                pass  # Silently fail if balance fetch fails
            
            if len(current_message) + len(footer) > 4000:
                if is_first_message:
                    await message.edit_text(current_message, parse_mode='HTML')
                    is_first_message = False
                else:
                    await update.effective_chat.send_message(current_message, parse_mode='HTML')
                current_message = footer
            else:
                current_message += footer
            
            
            # Add navigation buttons
            keyboard = self.get_navigation_keyboard(exclude='list')
            
            if is_first_message:
                await message.edit_text(current_message, parse_mode='HTML', reply_markup=keyboard)
            else:
                await update.effective_chat.send_message(current_message, parse_mode='HTML', reply_markup=keyboard)
                
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
            
            header = f"📋 <b>Bybit Open Orders</b>\n"
            header += f"{'='*50}\n\n"
            header += f"✅ Found {len(orders)} open order(s)\n\n"
            
            
            current_message = header
            is_first_message = True
            
            for order in orders:
                symbol = html.escape(str(order.get('symbol', 'N/A')))
                side = html.escape(str(order.get('side', 'N/A')))
                order_type = html.escape(str(order.get('orderType', 'N/A')))
                price = float(order.get('price', 0))
                qty = float(order.get('qty', 0))
                order_id = html.escape(str(order.get('orderId', 'N/A')))
                
                side_emoji = "📈" if side == "Buy" else "📉"
                
                order_str = f"{side_emoji} <b>{symbol}</b> ({side})\n"
                order_str += f"  Type: {order_type}\n"
                order_str += f"  Price: ${price:.4f} | Qty: {qty:.4f}\n"
                order_str += f"  Order ID: {order_id}\n\n"
                
                if len(current_message) + len(order_str) > 4000:
                    if is_first_message:
                        await message.edit_text(current_message, parse_mode='HTML')
                        is_first_message = False
                    else:
                        await update.effective_chat.send_message(current_message, parse_mode='HTML')
                    current_message = order_str
                else:
                    current_message += order_str
            
            keyboard = self.get_navigation_keyboard(exclude='orders')
            if is_first_message:
                await message.edit_text(current_message, parse_mode='HTML', reply_markup=keyboard)
            else:
                await update.effective_chat.send_message(current_message, parse_mode='HTML', reply_markup=keyboard)
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            keyboard = self.get_navigation_keyboard()
            try:
                await message.edit_text(error_msg, reply_markup=keyboard)
            except:
                await update.effective_chat.send_message(error_msg, reply_markup=keyboard)
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
            
            # Risk Metrics
            risks = analysis['risks']
            response += f"<b>⚠️ Risk Metrics</b>\n"
            response += f"High Leverage: {risks['high_leverage_count']}\n"
            response += f"Close to Liq: {risks['close_liquidation_count']}\n"
            response += f"No Stop Loss: {risks.get('no_stop_loss_count', 0)}\n"
            
            risky_pos_count = len(risks.get('risky_positions', []))
            if risky_pos_count > 0:
                response += f"🔴 <b>Unhedged & No SL: {risky_pos_count}</b>\n"
            else:
                response += f"Unhedged & No SL: 0\n"
                
            hedged_count = len(risks.get('hedged_symbols', []))
            response += f"Hedged Symbols: {hedged_count}\n\n"

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
                        response += f"• {html.escape(sug)}\n"
                    response += "\n"
                
                if suggestions.get('recommended'):
                    response += f"🟡 <b>RECOMMENDED:</b>\n"
                    for sug in suggestions['recommended'][:3]:
                        response += f"• {html.escape(sug)}\n"
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

    async def show_recent_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show recent trade history (last 24h)."""
        if update.callback_query:
            await update.callback_query.answer()
            message = await update.callback_query.edit_message_text("📡 Fetching recent trades...")
        else:
            message = await update.message.reply_text("📡 Fetching recent trades...")
            
        try:
            # Calculate start time (24 hours ago)
            import datetime
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            start_time_dt = now_utc - datetime.timedelta(hours=24)
            start_time_ms = int(start_time_dt.timestamp() * 1000)
            
            logger.info(f"Fetching trades for last 24h. Start time: {start_time_ms} ({start_time_dt})")

            # Fetch recent closed PnL records
            # We fetch a bit more than usual to ensure we cover the 24h window if there are many trades
            trades = bybit_api.get_closed_pnl(start_time=start_time_ms, limit=50)
            logger.info(f"Fetched {len(trades)} trades from API")
            
            # Filter trades to ensure they are within last 24h
            filtered_trades = []
            for t in trades:
                try:
                    updated_time = float(t.get('updatedTime', 0))
                    if updated_time >= start_time_ms:
                        filtered_trades.append(t)
                    else:
                        logger.info(f"Filtering out trade: {t.get('symbol')} time={updated_time} < {start_time_ms}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid updatedTime for trade: {t}")
            
            trades = filtered_trades
            logger.info(f"Trades after filtering: {len(trades)}")
            
            # Sort trades by update time (newest first) to get the most recent ones
            trades.sort(key=lambda x: float(x.get('updatedTime', 0)), reverse=True)
            
            if not trades:
                keyboard = self.get_navigation_keyboard(exclude='trades')
                await message.edit_text("ℹ️ No recent trades found in the last 24h.", reply_markup=keyboard)
                return
                
            response = f"📈 <b>Last 24h Trades</b>\n"
            response += f"{'='*30}\n\n"
            
            display_count = min(len(trades), 20)
            trades_to_show = trades[:display_count]
            
            # Sort ascending (oldest to newest) so newest is at the bottom
            trades_to_show.sort(key=lambda x: float(x.get('updatedTime', 0)))
            
            for trade in trades_to_show:  # Show top 20 sorted chronologically
                symbol = html.escape(str(trade.get('symbol', 'N/A')))
                side = html.escape(str(trade.get('side', 'N/A')))
                price = float(trade.get('avgExitPrice', 0))
                qty = float(trade.get('qty', 0))
                time_ms = float(trade.get('updatedTime', 0))
                pnl = float(trade.get('closedPnl', 0))
                
                # Format time (simple MM-DD HH:MM:SS)
                dt = datetime.datetime.fromtimestamp(time_ms / 1000, tz=datetime.timezone.utc)
                time_str = dt.strftime('%m-%d %H:%M:%S')
                
                side_emoji = "🟢" if side == "Buy" else "🔴"
                pnl_emoji = "🟢" if pnl >= 0 else "🔴"
                
                response += f"{side_emoji} <b>{symbol}</b> ({side})\n"
                response += f"  Price: ${price:.4f} | Qty: {qty}\n"
                response += f"  Time: {time_str} (UTC)\n"
                response += f"  {pnl_emoji} PnL: <b>${pnl:.2f}</b>\n\n"
                
            if len(trades) > display_count:
                response += f"<i>Showing last {display_count} of {len(trades)} trades for last 24h</i>"
            else:
                response += f"<i>Total {len(trades)} trades fetched for last 24h</i>"
            
            keyboard = self.get_navigation_keyboard(exclude='trades')
            await message.edit_text(response, parse_mode='HTML', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error in show_recent_trades: {e}", exc_info=True)
            error_msg = f"❌ Error: {str(e)}"
            keyboard = self.get_navigation_keyboard()
            await message.edit_text(error_msg, reply_markup=keyboard)


    async def show_daily_pnl(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show Profit & Loss for the last 24 hours."""
        if update.callback_query:
            await update.callback_query.answer()
            message = await update.callback_query.edit_message_text("💰 Calculating 24h PnL...")
        else:
            message = await update.message.reply_text("💰 Calculating 24h PnL...")
            
        try:
            # Calculate start time (24 hours ago)
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            start_time_dt = now - datetime.timedelta(hours=24)
            start_time = int(start_time_dt.timestamp() * 1000)

            # Fetch data
            closed_pnl_list = bybit_api.get_closed_pnl(start_time=start_time)
            positions = bybit_api.get_positions()
            
            # Calculate Realized PnL (24h)
            realized_pnl = sum(float(item.get('closedPnl', 0)) for item in closed_pnl_list)
            trade_count = len(closed_pnl_list)
            
            # Calculate Unrealized PnL (Current Open)
            unrealized_pnl = sum(float(pos.get('unrealisedPnl', 0)) for pos in positions)
            
            # Total PnL
            total_daily_pnl = realized_pnl + unrealized_pnl
            
            # Formatting
            r_emoji = "🟢" if realized_pnl >= 0 else "🔴"
            u_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
            t_emoji = "🟢" if total_daily_pnl >= 0 else "🔴"
            
            response = f"📊 <b>Rolling 24h Profit & Loss</b>\n"
            response += f"{'='*30}\n\n"
            
            response += f"<b>💵 Realized PnL (24h)</b>\n"
            response += f"{r_emoji} <b>${realized_pnl:,.2f}</b> ({trade_count} trades)\n\n"
            
            response += f"<b>🔓 Unrealized PnL (Open)</b>\n"
            response += f"{u_emoji} <b>${unrealized_pnl:,.2f}</b>\n\n"
            
            response += f"{'='*30}\n"
            response += f"<b>💰 Total PnL: {t_emoji} ${total_daily_pnl:,.2f}</b>\n"
            
            keyboard = self.get_navigation_keyboard(exclude='pnl')
            await message.edit_text(response, parse_mode='HTML', reply_markup=keyboard)
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            keyboard = self.get_navigation_keyboard()
            await message.edit_text(error_msg, reply_markup=keyboard)
            logger.error(f"Error calculating PnL: {e}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks."""
        query = update.callback_query
        
        if query.data == 'balance':
            await self.show_balance(update, context)
        elif query.data == 'pnl':
            await self.show_daily_pnl(update, context)
        elif query.data == 'list':
            await self.list_positions(update, context)
        elif query.data == 'orders':
            await self.list_orders(update, context)
        elif query.data == 'trades':
            await self.show_recent_trades(update, context)
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
        application.add_handler(CommandHandler("pnl", self.show_daily_pnl))
        application.add_handler(CommandHandler("list", self.list_positions))
        application.add_handler(CommandHandler("orders", self.list_orders))
        application.add_handler(CommandHandler("trades", self.show_recent_trades))
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
