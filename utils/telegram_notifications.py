import os
import requests
import logging
from typing import Optional
from utils.secrets import read_secret
import time

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = read_secret('telegram_bot_token')
        self.chat_id = read_secret('telegram_chat_id')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_sent = 0
        self.min_interval = 1  # Minimum 1 second between messages

        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram credentials not properly configured")

    def send_message(self, message: str, parse_mode: Optional[str] = 'HTML') -> bool:
        """
        Send a message through Telegram.
        
        Args:
            message: The message to send
            parse_mode: Message format ('HTML' or 'Markdown')
        
        Returns:
            bool: True if message was sent successfully
        """
        # Ensure we don't exceed rate limits
        current_time = time.time()
        if current_time - self.last_sent < self.min_interval:
            time.sleep(self.min_interval)
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 429:  # Too Many Requests
                retry_after = int(response.headers.get('Retry-After', 30))
                time.sleep(retry_after)
                return self.send_message(message)  # Retry after waiting
            
            self.last_sent = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return False

    def send_trade_alert(self, trade_type: str, symbol: str, price: float, 
                        stop_loss: float, take_profit: float) -> bool:
        """
        Send a formatted trade alert.
        
        Args:
            trade_type: 'BUY' or 'SELL'
            symbol: Trading pair (e.g., 'EUR_USD')
            price: Entry price
            stop_loss: Stop loss level
            take_profit: Take profit level
        """
        message = (
            f"🤖 <b>Trade Alert</b>\n\n"
            f"{'🟢' if trade_type == 'BUY' else '🔴'} <b>{trade_type}</b> {symbol}\n"
            f"💰 Entry: {price:.5f}\n"
            f"🛑 Stop Loss: {stop_loss:.5f}\n"
            f"🎯 Take Profit: {take_profit:.5f}"
        )
        return self.send_message(message)

    def send_trade_result(self, trade_type: str, symbol: str, 
                         entry_price: float, exit_price: float, 
                         profit_loss: float, pips: float) -> bool:
        """
        Send a formatted trade result notification.
        
        Args:
            trade_type: 'BUY' or 'SELL'
            symbol: Trading pair
            entry_price: Entry price
            exit_price: Exit price
            profit_loss: Profit/loss amount
            pips: Number of pips gained/lost
        """
        emoji = "✅" if profit_loss > 0 else "❌"
        message = (
            f"🤖 <b>Trade Closed</b> {emoji}\n\n"
            f"{'🟢' if trade_type == 'BUY' else '🔴'} <b>{trade_type}</b> {symbol}\n"
            f"📈 Entry: {entry_price:.5f}\n"
            f"📉 Exit: {exit_price:.5f}\n"
            f"💵 P/L: {profit_loss:.2f}\n"
            f"📊 Pips: {pips:.1f}"
        )
        return self.send_message(message)

    def send_error_alert(self, error_message: str) -> bool:
        """
        Send an error notification.
        
        Args:
            error_message: Description of the error
        """
        message = (
            f"⚠️ <b>Error Alert</b>\n\n"
            f"❌ {error_message}"
        )
        return self.send_message(message)

    def send_profit_notification(self, symbol: str, profit: float):
        """
        Send a profit notification.
        
        Args:
            symbol: Trading pair (e.g., 'EUR_USD')
            profit: Profit amount
        """
        message = (
            f"💰 <b>Profit Alert</b>\n\n"
            f"📈 {symbol}\n"
            f"💵 Profit: {profit:.2f}"
        )
        return self.send_message(message) 