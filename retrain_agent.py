import os
import sys
import logging
from datetime import datetime
import pandas as pd
from stable_baselines3 import PPO
from forex_env import ForexEnv  # Ensure ForexEnv can handle incremental training

# Configuration
MODEL_PATH = "ppo_forex_agent.zip"       # Path to the existing trained PPO model
NEW_MODEL_PATH_TEMPLATE = "ppo_forex_agent_{date}.zip"  # Template for saving updated models
DATA_DIR = "data"                         # Directory where new data is stored
TRAINING_DATA_FILE = os.path.join(DATA_DIR, "processed_forex_data.csv")  # Path to training data
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'retrain_agent.log'),
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def load_data(file_path):
    """
    Load and preprocess the training data.

    Parameters:
    - file_path (str): Path to the CSV file containing training data.

    Returns:
    - pd.DataFrame: Preprocessed training data.
    """
    try:
        data = pd.read_csv(file_path, parse_dates=['time'])
        data.set_index('time', inplace=True)
        logging.info(f"Loaded training data from {file_path}.")
        return data
    except Exception as e:
        logging.error(f"Error loading training data: {e}")
        sys.exit(1)

def create_environment(data):
    """
    Create the Forex trading environment using the provided data.

    Parameters:
    - data (pd.DataFrame): Preprocessed market data with technical indicators.

    Returns:
    - ForexEnv: An instance of the custom Forex trading environment.
    """
    try:
        env = ForexEnv(historical_data=data)
        logging.info("Initialized ForexEnv for training.")
        return env
    except Exception as e:
        logging.error(f"Error initializing ForexEnv: {e}")
        sys.exit(1)

def fine_tune_model(model_path, env, total_timesteps=50000):
    """
    Fine-tune the existing PPO model with new data.

    Parameters:
    - model_path (str): Path to the existing trained PPO model.
    - env (ForexEnv): The trading environment for training.
    - total_timesteps (int): Number of timesteps for fine-tuning.

    Returns:
    - PPO: The fine-tuned PPO model.
    """
    try:
        model = PPO.load(model_path, env=env)
        logging.info(f"Loaded existing model from {model_path}.")
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        sys.exit(1)
    
    try:
        logging.info(f"Starting fine-tuning for {total_timesteps} timesteps.")
        model.learn(total_timesteps=total_timesteps)
        logging.info("Fine-tuning completed.")
        return model
    except Exception as e:
        logging.error(f"Error during fine-tuning: {e}")
        sys.exit(1)

def save_model(model, date_str):
    """
    Save the fine-tuned model with a timestamp.

    Parameters:
    - model (PPO): The fine-tuned PPO model.
    - date_str (str): Current date string for versioning.
    """
    try:
        new_model_path = NEW_MODEL_PATH_TEMPLATE.format(date=date_str)
        model.save(new_model_path)
        logging.info(f"Saved fine-tuned model to {new_model_path}.")
    except Exception as e:
        logging.error(f"Error saving model: {e}")
        sys.exit(1)

def main():
    logging.info("Retraining process started.")
    
    # Step 1: Load the latest training data
    if not os.path.exists(TRAINING_DATA_FILE):
        logging.error(f"Training data file {TRAINING_DATA_FILE} does not exist.")
        sys.exit(1)
    
    data = load_data(TRAINING_DATA_FILE)
    
    # Step 2: Initialize the trading environment
    env = create_environment(data)
    
    # Step 3: Fine-tune the existing model
    fine_tuned_model = fine_tune_model(MODEL_PATH, env, total_timesteps=50000)  # Adjust timesteps as needed
    
    # Step 4: Save the updated model with a timestamp
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_model(fine_tuned_model, date_str)
    
    logging.info("Retraining process completed successfully.")

if __name__ == "__main__":
    main() 