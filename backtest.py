import pandas as pd
from trade_executor import execute_trade, close_trade, adjust_risk_parameters
from performance_tracker import PerformanceTracker

def backtest_strategy(historical_data):
    performance_tracker = PerformanceTracker()
    entry_price, stop_loss, take_profit = None, None, None
    account_balance = 10000  # Example starting balance

    for index, market_data in historical_data.iterrows():
        if entry_price is None:
            risk_percentage = adjust_risk_parameters(performance_tracker.calculate_metrics())
            entry_price, stop_loss, take_profit = execute_trade(market_data, account_balance, risk_percentage)
        else:
            if close_trade(market_data, entry_price, stop_loss, take_profit):
                profit = market_data['bid'] - entry_price
                performance_tracker.log_trade(profit)
                entry_price, stop_loss, take_profit = None, None, None

    return performance_tracker.calculate_metrics()

# Load historical data
historical_data = pd.read_csv('historical_data.csv')
metrics = backtest_strategy(historical_data)
print("Backtest Results:", metrics) 