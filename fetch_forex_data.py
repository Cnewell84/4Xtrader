import os
from datetime import datetime
import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
from azure.storage.blob import BlobServiceClient

# Define the output CSV path
OUTPUT_CSV = "data/processed_forex_data.csv"  # Ensure this variable is defined

def fetch_data():
    """
    Fetch raw Forex data from OANDA API.
    
    Returns:
    - list: List of candle data.
    """
    access_token = os.getenv("OANDA_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("OANDA_ACCESS_TOKEN environment variable not set.")
    
    client = API(access_token=access_token)
    params = {
        "granularity": "M1",
        "count": 5000  # Number of data points
    }
    
    r = instruments.InstrumentsCandles(instrument="EUR_USD", params=params)
    client.request(r)
    raw_data = r.response.get('candles', [])
    
    return raw_data

def process_data(raw_data):
    """
    Process raw Forex data into a pandas DataFrame.
    
    Parameters:
    - raw_data (list): Raw candle data from OANDA API.
    
    Returns:
    - pd.DataFrame: Processed Forex data.
    """
    frames = []
    for candle in raw_data:
        frames.append({
            'time': candle['time'],
            'open': float(candle['mid']['o']),
            'high': float(candle['mid']['h']),
            'low': float(candle['mid']['l']),
            'close': float(candle['mid']['c']),
            'volume': candle['volume']
        })
    
    df = pd.DataFrame(frames)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    
    return df

def save_processed_data(df, output_path):
    """
    Append the new processed data to the existing CSV file.

    Parameters:
    - df (pd.DataFrame): Processed market data.
    - output_path (str): Path to the CSV file.
    """
    if os.path.exists(output_path):
        df.to_csv(output_path, mode='a', header=False)
    else:
        df.to_csv(output_path, mode='w', header=True)
    print(f"Processed data saved to {output_path}.")

def main():
    # Fetch and process data
    raw_data = fetch_data()
    df_processed = process_data(raw_data)

    # Save the processed data by appending
    save_processed_data(df_processed, OUTPUT_CSV)
    
    # Upload to Azure Blob Storage
    try:
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        container_name = "forex-data"
        container_client = blob_service_client.get_container_client(container_name)
        
        blob_name = f"forex_data_{datetime.now().strftime('%Y%m%d')}.csv"
        blob_client = container_client.get_blob_client(blob_name)
        
        with open(OUTPUT_CSV, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"Successfully uploaded {blob_name} to Azure Blob Storage")
    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: {str(e)}")

if __name__ == "__main__":
    main()