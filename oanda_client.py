import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.endpoints.trades import TradeClose
from oandapyV20.endpoints.accounts import AccountDetails

class OandaAPI:
    def __init__(self, access_token, account_id):
        self.client = API(access_token=access_token)
        self.account_id = account_id

    def place_order(self, order_request):
        r = OrderCreate(accountID=self.account_id, data=order_request)
        try:
            response = self.client.request(r)
            return response
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def get_open_trades(self):
        r = AccountDetails(accountID=self.account_id)
        try:
            response = self.client.request(r)
            return response.get('trades', [])
        except Exception as e:
            print(f"Error getting open trades: {e}")
            return []

    def close_trade(self, trade_id):
        r = TradeClose(accountID=self.account_id, tradeID=trade_id)
        try:
            response = self.client.request(r)
            return response
        except Exception as e:
            print(f"Error closing trade: {e}")
            return None 