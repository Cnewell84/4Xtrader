class PerformanceTracker:
    def __init__(self):
        self.trades = []
        self.total_profit = 0
        self.total_loss = 0

    def log_trade(self, profit):
        self.trades.append(profit)
        if profit > 0:
            self.total_profit += profit
        else:
            self.total_loss += profit

    def calculate_metrics(self):
        win_rate = sum(1 for p in self.trades if p > 0) / len(self.trades) if self.trades else 0
        average_profit = self.total_profit / len(self.trades) if self.trades else 0
        average_loss = self.total_loss / len(self.trades) if self.trades else 0
        return {
            "win_rate": win_rate,
            "average_profit": average_profit,
            "average_loss": average_loss
        } 