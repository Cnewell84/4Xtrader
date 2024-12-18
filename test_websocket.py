import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('market_data')
def on_market_data(data):
    print(f"Received: {data['pair']} - Bid: {data['bid']}, Ask: {data['ask']}")

try:
    sio.connect('http://localhost:5001')
    sio.wait()
except Exception as e:
    print(f'Error: {e}') 