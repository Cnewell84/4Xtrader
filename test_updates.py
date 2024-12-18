import pandas as pd
import time
import os

def update_market_data():
    data = {
        'time': pd.Timestamp.now(),
        'instrument': 'EUR_USD',
        'bid': 1.0921,
        'ask': 1.0922
    }
    df = pd.DataFrame([data])
    df.to_csv('data/market_data.csv', mode='a', header=not os.path.exists('data/market_data.csv'))

while True:
    update_market_data()
    time.sleep(2)  # Update every 2 seconds 