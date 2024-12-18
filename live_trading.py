import time
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from forex_env import ForexEnv  # Ensure ForexEnv is adapted for live trading
import telegram
import os
from utils.secrets import read_secret

# Risk Management Configuration
MAX_DRAWDOWN_PERCENTAGE = 0.10  # 10% drawdown
MAX_VOLATILITY_PERCENTAGE = 0.05  # 5% volatility




TELEGRAM_BOT_TOKEN = read_secret('telegram_bot_token')
TELEGRAM_CHAT_ID = read_secret('telegram_chat_id')
OANDA_ACCESS_TOKEN = read_secret('oanda_access_token')

# Configuration
MODEL_PATH = "ppo_forex_agent.zip"       # Path to your trained RL model
SYMBOL = "USD"                           # Trading symbol
LOT_SIZE = 0.01                          # Trading volume (adjust as needed)
STOP_LOSS = 50                           # Stop loss in pips
TAKE_PROFIT = 50                         # Take profit in pips
CHECK_INTERVAL = 60                      # Time between checks in seconds
RISK_PERCENTAGE = 0.02                   # Risk per trade (2%)

def calculate_position_size(account_balance, profit_pool, scaling_factor=0.01, risk_percentage=0.02):
    """
    Calculate the position size based on account balance, profit pool, and scaling factor,
    ensuring that the risk per trade does not exceed a predefined percentage of account equity.

    Parameters:
    - account_balance (float): The total balance of the trading account.
    - profit_pool (float): The cumulative realized profits.
    - scaling_factor (float): A factor to scale the position size based on strategy requirements.
    - risk_percentage (float, optional): The maximum risk per trade as a percentage of account equity.
                                         Defaults to 0.02 (2%).

    Returns:
    - float: The calculated position size.
    """
    # Calculate account equity
    account_equity = account_balance + profit_pool

    # Define the maximum risk per trade
    max_risk = account_equity * risk_percentage

    # Calculate the base position size using the scaling factor
    position_size = account_balance * scaling_factor

    # Ensure that the position size does not exceed the maximum risk
    if position_size > max_risk:
        position_size = max_risk

    return position_size

def send_telegram_message(message):
    """
    Send a Telegram alert.
    
    Parameters:
    - message (str): Content of the message.
    """
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Telegram message sent.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def main():
    # Load the trained PPO model
    model = PPO.load(MODEL_PATH)

    # Initialize the trading environment (ensure it's adapted for live trading)
    env = ForexEnv()

    # Initial account monitoring
    equity, profit_pool = 10000, 0  # Placeholder values for equity and profit pool

    # Initialize peak equity
    peak_equity = equity

    try:
        while True:
            # Retrieve the latest market data
            data = pd.DataFrame()  # Placeholder for market data retrieval
            if data.empty:
                print("No data retrieved. Retrying...")
                time.sleep(CHECK_INTERVAL)
                continue

            # Preprocess data as required by the environment
            obs = env.process_live_data(data)

            # Predict action using the RL model
            action, _states = model.predict(obs, deterministic=True)

            # Map action to trading commands
            if action == 1:
                # Buy signal
                lot = calculate_position_size(equity, profit_pool, scaling_factor=LOT_SIZE, risk_percentage=RISK_PERCENTAGE)
                print(f"Executing buy order with lot size: {lot}")
            elif action == 2:
                # Sell signal
                lot = calculate_position_size(equity, profit_pool, scaling_factor=LOT_SIZE, risk_percentage=RISK_PERCENTAGE)
                print(f"Executing sell order with lot size: {lot}")
            elif action == 0:
                # Close all positions
                print("Closing all positions")

            # Monitor account status
            equity, profit_pool = 10000, 0  # Placeholder for account monitoring

            # Update peak equity
            if equity > peak_equity:
                peak_equity = equity

            # Calculate drawdown
            drawdown = (peak_equity - equity) / peak_equity if peak_equity != 0 else 0

            # Calculate volatility based on recent market data
            recent_prices = data['close'].tail(30).tolist() if not data.empty else []
            volatility = np.std(np.diff(recent_prices) / recent_prices[:-1]) if len(recent_prices) > 1 else 0

            print(f"Current Equity: {equity:.2f}, Drawdown: {drawdown:.2%}, Volatility: {volatility:.2%}")

            # Check for excessive drawdown
            if drawdown > MAX_DRAWDOWN_PERCENTAGE:
                message = f"Excessive Drawdown Alert! Drawdown: {drawdown:.2%}"
                print(message)
                send_telegram_message(message)
                print("Trading halted due to excessive drawdown.")
                break  # Halt trading

            # Check for high volatility
            if volatility > MAX_VOLATILITY_PERCENTAGE:
                message = f"High Volatility Alert! Volatility: {volatility:.2%}"
                print(message)
                send_telegram_message(message)
                print("Trading halted due to high volatility.")
                break  # Halt trading

            # Wait before next check
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("Live trading stopped by user.")

if __name__ == "__main__":
    main() 