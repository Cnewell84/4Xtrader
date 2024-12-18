from flask import Flask, render_template, jsonify, Response
from flask_socketio import SocketIO
import pandas as pd
import json
import os
import time
from utils.secrets import read_secret
from websocket_server import init_socketio, start_market_data_stream
from market_simulator import MarketDataSimulator
from trade_executor import execute_trade, close_trade, adjust_risk_parameters, calculate_position_size
from performance_tracker import PerformanceTracker

app = Flask(__name__)
socketio = init_socketio(app)
start_market_data_stream(socketio)

# Path to the data directory
DATA_DIR = 'data'
STATUS_FILE = os.path.join(DATA_DIR, 'status.json')
TRADES_FILE = os.path.join(DATA_DIR, 'trades.csv')
MARKET_DATA_FILE = os.path.join(DATA_DIR, 'market_data.csv')

def main():
    simulator = MarketDataSimulator()
    entry_price, stop_loss, take_profit = None, None, None
    account_balance = 10000  # Example starting balance
    max_drawdown = 0.2  # 20% maximum drawdown
    performance_tracker = PerformanceTracker()

    for market_data in simulator.generate_tick():
        if account_balance < 10000 * (1 - max_drawdown):
            print("Maximum drawdown reached. Stopping trading.")
            break

        if entry_price is None:
            risk_percentage = adjust_risk_parameters(performance_tracker.calculate_metrics())
            position_size = calculate_position_size(account_balance, risk_percentage, 10)
            entry_price, stop_loss, take_profit = execute_trade(market_data, account_balance, risk_percentage)
        else:
            trade_closed, account_balance = close_trade(market_data, entry_price, stop_loss, take_profit, account_balance)
            if trade_closed:
                profit = market_data['bid'] - entry_price
                performance_tracker.log_trade(profit)
                entry_price, stop_loss, take_profit = None, None, None

        # Log performance metrics periodically
        if len(performance_tracker.trades) % 10 == 0:
            metrics = performance_tracker.calculate_metrics()
            print("Live Performance Metrics:", metrics)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint to get current account status."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status = json.load(f)
        return jsonify(status)
    else:
        return jsonify({"error": "Status file not found"}), 404

@app.route('/api/trades')
def api_trades():
    """API endpoint to get open trades."""
    if os.path.exists(TRADES_FILE):
        trades = pd.read_csv(TRADES_FILE).to_dict(orient='records')
        return jsonify(trades)
    else:
        return jsonify({"error": "Trades file not found"}), 404

@app.route('/api/market_data')
def api_market_data():
    """API endpoint to get recent market data."""
    if os.path.exists(MARKET_DATA_FILE):
        data = pd.read_csv(MARKET_DATA_FILE, parse_dates=['time'])
        data = data.tail(100).to_dict(orient='records')  # Fetch last 100 data points
        return jsonify(data)
    else:
        return jsonify({"error": "Market data file not found"}), 404

@app.route('/api/stream/market_data')
def stream_market_data():
    def generate():
        last_modified = 0
        while True:
            try:
                if os.path.exists(MARKET_DATA_FILE):
                    current_modified = os.path.getmtime(MARKET_DATA_FILE)
                    if current_modified > last_modified:
                        data = pd.read_csv(MARKET_DATA_FILE, parse_dates=['time'])
                        latest_data = data.tail(1).to_dict(orient='records')[0]
                        yield f"data: {json.dumps(latest_data)}\n\n"
                        last_modified = current_modified
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Error in stream: {e}")
                time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    main()
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)