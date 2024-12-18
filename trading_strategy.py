def should_enter_trade(market_data):
    # Example strategy: Enter trade if bid price is below a threshold
    return market_data['bid'] < 1.15

def should_exit_trade(market_data, entry_price):
    # Example strategy: Exit trade if bid price is above entry price + profit margin
    return market_data['bid'] > entry_price + 0.001 