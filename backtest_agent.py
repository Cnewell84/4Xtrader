import gym
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from forex_env import ForexEnv  # Replace with the actual path to your custom environment
import matplotlib.pyplot as plt

def calculate_sharpe_ratio(returns, risk_free_rate=0):
    """
    Calculate the Sharpe Ratio of the returns.

    Parameters:
    - returns (pd.Series): Series of returns.
    - risk_free_rate (float, optional): Risk-free rate. Defaults to 0.

    Returns:
    - float: Sharpe Ratio.
    """
    excess_returns = returns - risk_free_rate
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_win_rate(trades):
    """
    Calculate the win rate from a list of trades.

    Parameters:
    - trades (list of float): List of trade profits/losses.

    Returns:
    - float: Win rate as a percentage.
    """
    wins = [trade for trade in trades if trade > 0]
    return len(wins) / len(trades) * 100 if trades else 0

def calculate_max_drawdown(equity_curve):
    """
    Calculate the Maximum Drawdown of the equity curve.

    Parameters:
    - equity_curve (pd.Series): Series representing the equity over time.

    Returns:
    - float: Maximum Drawdown as a percentage.
    """
    cumulative_max = equity_curve.cummax()
    drawdown = (equity_curve - cumulative_max) / cumulative_max
    return drawdown.min() * 100

def backtest(model_path, historical_data_path, output_csv='backtest_results.csv'):
    """
    Backtest the trained agent on historical data and calculate performance metrics.

    Parameters:
    - model_path (str): Path to the trained PPO model.
    - historical_data_path (str): Path to the historical Forex data CSV file.
    - output_csv (str, optional): Path to save the backtest results. Defaults to 'backtest_results.csv'.
    """
    # Load the historical data
    data = pd.read_csv(historical_data_path, parse_dates=['time'], index_col='time')
    
    # Initialize the custom Forex trading environment with historical data
    env = ForexEnv(historical_data=data)
    
    # Load the trained PPO model
    model = PPO.load(model_path, env=env)
    
    obs = env.reset()
    done = False
    trades = []
    equity_curve = []
    
    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        
        # Assuming the environment returns 'trade_profit' in 'info' dict
        trade_profit = info.get('trade_profit', 0)
        trades.append(trade_profit)
        
        # Assuming the environment tracks equity and returns it in 'info'
        current_equity = info.get('current_equity', env.initial_balance)
        equity_curve.append(current_equity)
    
    # Convert equity_curve to pandas Series for calculations
    equity_series = pd.Series(equity_curve, index=data.index[:len(equity_curve)])
    
    # Calculate performance metrics
    returns = equity_series.pct_change().dropna()
    sharpe_ratio = calculate_sharpe_ratio(returns)
    win_rate = calculate_win_rate(trades)
    max_drawdown = calculate_max_drawdown(equity_series)
    
    # Save backtest results
    backtest_results = {
        'Sharpe Ratio': sharpe_ratio,
        'Win Rate (%)': win_rate,
        'Maximum Drawdown (%)': max_drawdown
    }
    
    results_df = pd.DataFrame([backtest_results])
    results_df.to_csv(output_csv, index=False)
    
    # Display the results
    print("\nBacktest Performance Metrics:")
    print(results_df)
    
    # Plot the equity curve
    plt.figure(figsize=(12, 6))
    equity_series.plot(title='Equity Curve')
    plt.xlabel('Time')
    plt.ylabel('Equity')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    MODEL_PATH = "ppo_forex_agent.zip"          # Path to your trained model
    HISTORICAL_DATA_PATH = "historical_data.csv"  # Path to your historical data CSV
    OUTPUT_CSV = "backtest_results.csv"         # Output path for backtest results

    backtest(MODEL_PATH, HISTORICAL_DATA_PATH, OUTPUT_CSV) 