from flask_socketio import SocketIO, emit
import json
import pandas as pd
from datetime import datetime
import os
from market_simulator import MarketDataSimulator
import threading
import time
from utils.telegram_notifications import TelegramNotifier

# Initialize the notifier
notifier = TelegramNotifier()

def init_socketio(app):
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('status', {'data': 'Connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('place_trade')
    def handle_trade(data):
        # Process trade request
        trade = {
            'trade_id': data.get('trade_id'),
            'instrument': data.get('instrument'),
            'units': data.get('units'),
            'type': data.get('type'),
            'price': data.get('price'),
            'timestamp': datetime.now().isoformat()
        }
        # Save trade to CSV
        df = pd.DataFrame([trade])
        df.to_csv('data/trades.csv', mode='a', 
                 header=not os.path.exists('data/trades.csv'),
                 index=False)
        # Emit trade confirmation
        emit('trade_confirmed', trade)
    
    return socketio 

def start_market_data_stream(socketio):
    simulator = MarketDataSimulator()
    
    def stream_data():
        while True:
            for tick in simulator.generate_tick():
                socketio.emit('market_data', tick)
            time.sleep(1)  # Update every second
    
    thread = threading.Thread(target=stream_data)
    thread.daemon = True
    thread.start()

def handle_trade_close(trade_data):
    # Example trade data processing
    profit = trade_data.get('profit')
    symbol = trade_data.get('instrument')

    if profit > 0:
        notifier.send_profit_notification(symbol, profit)