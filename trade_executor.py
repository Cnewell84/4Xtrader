from trading_strategy import should_enter_trade, should_exit_trade
from utils.telegram_notifications import TelegramNotifier
from utils.secrets import read_secret
from oanda_client import OandaAPI
import logging

logger = logging.getLogger(__name__)

notifier = TelegramNotifier()

# Initialize the OANDA API client
oanda_api = OandaAPI(access_token=read_secret('oanda_access_token'), account_id=read_secret('oanda_account_id'))

def execute_trade(market_data, account_balance, risk_percentage=0.02):
    """
    Execute a trade based on market data and account balance using OANDA API
    """
    if should_enter_trade(market_data):
        entry_price = market_data['bid']
        stop_loss = entry_price - 0.001  # Example stop loss
        take_profit = entry_price + 0.002  # Example take profit
        position_size = calculate_position_size(account_balance, risk_percentage, 10)  # 2% risk, 10 pips stop loss

        logger.info(f"Placing OANDA market order: {market_data['instrument']} at {entry_price}")
        
        # Create order request with stop loss and take profit
        order_request = {
            "instrument": market_data['instrument'],
            "units": position_size,
            "type": "MARKET",
            "stopLossOnFill": {
                "price": str(stop_loss)
            },
            "takeProfitOnFill": {
                "price": str(take_profit)
            }
        }
        
        # Place order through OANDA API
        response = oanda_api.place_order(order_request)
        
        if response and response.get('orderFillTransaction'):
            filled_price = float(response['orderFillTransaction']['price'])
            logger.info(f"Trade executed at {filled_price}")
            notifier.send_trade_alert('BUY', market_data['instrument'], filled_price, stop_loss, take_profit)
            return filled_price, stop_loss, take_profit
        else:
            logger.error(f"Failed to execute trade: {response}")
            return None, None, None
            
    return None, None, None

def close_trade(market_data, entry_price, stop_loss, take_profit, account_balance):
    """
    Close an existing OANDA trade based on stop loss or take profit levels
    """
    if market_data['bid'] <= stop_loss or market_data['bid'] >= take_profit:
        # Get open trade ID from OANDA
        open_trades = oanda_api.get_open_trades()
        if open_trades:
            trade_id = open_trades[0]['id']  # Assuming single trade management
            
            # Close the trade through OANDA API
            response = oanda_api.close_trade(trade_id)
            
            if response and response.get('orderFillTransaction'):
                exit_price = float(response['orderFillTransaction']['price'])
                profit = exit_price - entry_price
                account_balance += profit
                
                logger.info(f"Trade closed at {exit_price} with profit {profit}")
                notifier.send_trade_result('SELL', market_data['instrument'], entry_price, exit_price, profit, 0)
                return True, account_balance
                
        logger.error("Failed to close trade")
    return False, account_balance

def calculate_position_size(account_balance, risk_percentage, stop_loss_pips):
    """
    Calculate position size based on account risk parameters
    """
    risk_amount = account_balance * risk_percentage
    # Convert pips to price for OANDA position sizing
    position_size = int((risk_amount / stop_loss_pips) * 100000)  # Standard lot = 100,000 units
    return position_size

def adjust_risk_parameters(performance_metrics):
    """
    Dynamically adjust risk based on trading performance
    """
    if performance_metrics['win_rate'] > 0.6:
        return 0.03  # Increase risk to 3%
    elif performance_metrics['win_rate'] < 0.4:
        return 0.01  # Decrease risk to 1%
    return 0.02  # Default risk

class TradeExecutor:
    def __init__(self, config):
        # Read secrets from Docker secrets mount point
        try:
            with open('/run/secrets/oanda_token', 'r') as f:
                access_token = f.read().strip()
            with open('/run/secrets/oanda_account', 'r') as f:
                account_id = f.read().strip()
        except FileNotFoundError as e:
            logging.error(f"Failed to read Docker secrets: {e}")
            raise

        self.api = API(access_token=access_token)
        self.account_id = account_id
        
        # Telegram config can stay in config file since it's not sensitive
        self.telegram_bot = None
        if config.get('telegram'):
            self.telegram_bot = TelegramBot(config['telegram']['token'], 
                                          config['telegram']['chat_id'])