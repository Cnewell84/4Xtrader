import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

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
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            logger.info(f"Telegram notification sent successfully")
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