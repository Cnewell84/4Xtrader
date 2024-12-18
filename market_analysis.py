def analyze_market_conditions(market_data):
    # Example: Use moving averages to determine market trend
    short_term_ma = sum(market_data['bid'][-5:]) / 5
    long_term_ma = sum(market_data['bid'][-20:]) / 20
    return short_term_ma > long_term_ma  # Bullish if short-term MA is above long-term MA 