import pandas as pd
from sklearn.preprocessing import StandardScaler
from joblib import dump
import numpy as np
import os
import logging

def prepare_data(ticker='AAPL'):
    """
    Load merged data, scale features, and save X_scaled.npy and y.npy
    """
    logging.info(f"Preparing data for {ticker}")
    
    # Define project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    
    # Paths to merged data
    merged_data_path = os.path.join(project_root, 'data', f'merged_data_with_features_{ticker}.csv')
    
    if not os.path.exists(merged_data_path):
        raise FileNotFoundError(f"Merged data file not found at {merged_data_path}")
    
    # Load data
    logging.info(f"Loading merged data from {merged_data_path}")
    merged_data = pd.read_csv(merged_data_path)
    
    # Define features and target
    features = ['Close', 'strike', 'T', 'delta', 'gamma', 'theta', 'vega', 'rho', 'impliedVolatility', 'moneyness']
    target = 'lastPrice'
    
    # Verify that all required features are present
    missing_features = [feat for feat in features if feat not in merged_data.columns]
    if missing_features:
        raise KeyError(f"Missing required features in merged data: {missing_features}")
    
    X = merged_data[features]
    y = merged_data[target]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save scaler
    scaler_path = os.path.join(script_dir, 'scaler.joblib')
    dump(scaler, scaler_path)
    logging.info(f"Scaler saved to {scaler_path}")
    
    # Save X_scaled and y
    X_scaled_path = os.path.join(script_dir, 'X_scaled.npy')
    y_path = os.path.join(script_dir, 'y.npy')
    np.save(X_scaled_path, X_scaled)
    np.save(y_path, y)
    logging.info(f"X_scaled saved to {X_scaled_path}")
    logging.info(f"y saved to {y_path}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        ticker = 'AAPL'
        prepare_data(ticker)
        logging.info("Data preparation completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during data preparation: {e}")
