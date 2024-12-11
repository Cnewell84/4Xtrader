from flask import Flask, render_template, jsonify
import pandas as pd
import json
import os

app = Flask(__name__)

# Path to the data directory
DATA_DIR = 'data'
STATUS_FILE = os.path.join(DATA_DIR, 'status.json')
TRADES_FILE = os.path.join(DATA_DIR, 'trades.csv')
MARKET_DATA_FILE = os.path.join(DATA_DIR, 'market_data.csv')

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

if __name__ == '__main__':
    app.run(debug=True) 