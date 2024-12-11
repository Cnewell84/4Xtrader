import subprocess
import logging
from datetime import datetime
import os
import sys

# Configuration
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'auto_retrain.log'),
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def run_fetch_data():
    try:
        logging.info("Starting data fetching.")
        subprocess.check_call(["python", "fetch_forex_data.py"])
        logging.info("Data fetching completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Data fetching failed: {e}")
        sys.exit(1)

def run_retraining():
    try:
        logging.info("Starting model retraining.")
        subprocess.check_call(["python", "retrain_agent.py"])
        logging.info("Model retraining completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Model retraining failed: {e}")
        sys.exit(1)

def main():
    logging.info("Automated retraining workflow initiated.")
    run_fetch_data()
    run_retraining()
    logging.info("Automated retraining workflow finished successfully.")

if __name__ == "__main__":
    main() 