import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import talib
import stable_baselines3
import tensorflow as tf
import torch
import ccxt
import oandapyV20
from azure.storage.blob import BlobServiceClient

def test_libraries():
    # Test NumPy
    print("\n1. Testing NumPy:")
    arr = np.array([1, 2, 3, 4, 5])
    print(f"NumPy array created: {arr}")
    print(f"NumPy version: {np.__version__}")

    # Test Pandas
    print("\n2. Testing Pandas:")
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    print(f"Pandas DataFrame created:\n{df}")
    print(f"Pandas version: {pd.__version__}")

    # Test Matplotlib
    print("\n3. Testing Matplotlib:")
    plt.plot([1, 2, 3], [1, 2, 3])
    plt.close()
    print(f"Matplotlib version: {plt.__version__}")
    print("Matplotlib plot created and closed successfully")

    # Test TA-Lib
    print("\n4. Testing TA-Lib:")
    close_prices = np.array([10.0, 11.0, 12.0, 11.0, 10.0])
    sma = talib.SMA(close_prices, timeperiod=3)
    print(f"TA-Lib SMA calculated: {sma}")
    print("TA-Lib working correctly")

    # Test Stable-Baselines3
    print("\n5. Testing Stable-Baselines3:")
    print(f"Stable-Baselines3 version: {stable_baselines3.__version__}")

    # Test TensorFlow
    print("\n6. Testing TensorFlow:")
    print(f"TensorFlow version: {tf.__version__}")
    print("GPU available:", tf.test.is_built_with_cuda())

    # Test PyTorch
    print("\n7. Testing PyTorch:")
    print(f"PyTorch version: {torch.__version__}")
    print("CUDA available:", torch.cuda.is_available())

    # Test CCXT
    print("\n8. Testing CCXT:")
    print(f"CCXT version: {ccxt.__version__}")
    exchanges = ccxt.exchanges
    print(f"Available exchanges: {len(exchanges)}")

    # Test oandapyV20
    print("\n9. Testing oandapyV20:")
    print(f"oandapyV20 version: {oandapyV20.__version__}")
    print("oandapyV20 imported successfully")

    # Test azure-storage-blob
    print("\n10. Testing azure-storage-blob:")
    print(f"azure-storage-blob version: {BlobServiceClient.__module__}")
    print("azure-storage-blob imported successfully")

def calculate_position_size(account_balance, profit_pool, scaling_factor, risk_percentage=0.02):
    """
    Calculate the position size based on account balance, profit pool, and scaling factor,
    ensuring that the risk per trade does not exceed a predefined percentage of account equity.

    Parameters:
    - account_balance (float): The total balance of the trading account.
    - profit_pool (float): The cumulative realized profits.
    - scaling_factor (float): A factor to scale the position size based on strategy requirements.
    - risk_percentage (float, optional): The maximum risk per trade as a percentage of account equity.
                                         Defaults to 0.02 (2%).

    Returns:
    - float: The calculated position size.
    """

    # Calculate account equity
    account_equity = account_balance + profit_pool

    # Define the maximum risk per trade
    max_risk = account_equity * risk_percentage

    # Calculate the base position size using the scaling factor
    # (You may need to adjust this formula based on your specific trading strategy)
    position_size = account_balance * scaling_factor

    # Ensure that the position size does not exceed the maximum risk
    if position_size > max_risk:
        position_size = max_risk

    return position_size

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("\nTesting all libraries...")
    
    try:
        test_libraries()
        print("\nAll libraries tested successfully!")
    except Exception as e:
        print(f"\nError during testing: {str(e)}") 