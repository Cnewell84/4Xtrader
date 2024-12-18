import random
import time

class MarketDataSimulator:
    def generate_tick(self):
        # Simulate market data
        instruments = ['EUR_USD', 'GBP_USD', 'USD_JPY']
        while True:
            for instrument in instruments:
                yield {
                    'instrument': instrument,
                    'time': time.time(),
                    'bid': random.uniform(1.1, 1.2),
                    'ask': random.uniform(1.1, 1.2)
                }
            time.sleep(1)