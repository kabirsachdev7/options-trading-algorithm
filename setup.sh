#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define paths
VENV_DIR="venv"  # Adjust if your virtual environment has a different name
REQUIREMENTS="requirements.txt"
DATA_COLLECTION_SCRIPT="data/data_collection.py"
PREPROCESSING_SCRIPT="data/preprocessing.py"
FEATURE_ENGINEERING_SCRIPT="features/feature_engineering.py"
LSTM_MODEL_SCRIPT="models/lstm_model.py"

# Function to display messages
function echo_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

function echo_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo_info "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
    echo_info "Virtual environment '$VENV_DIR' created."
fi

# Activate the virtual environment
echo_info "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
echo_info "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo_info "Installing Python dependencies from '$REQUIREMENTS'..."
pip install -r $REQUIREMENTS

# Navigate to Frontend Directory
FRONTEND_DIR="ui/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo_error "Frontend directory '$FRONTEND_DIR' does not exist."
    exit 1
fi

cd $FRONTEND_DIR

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo_error "package.json not found in '$FRONTEND_DIR'. Ensure you have initialized the React app correctly."
    exit 1
fi

# Install Frontend Dependencies
echo_info "Installing frontend dependencies using npm..."
npm install

# Build Frontend Application
echo_info "Building frontend application..."
npm run build

# Return to Project Root Directory
cd ../../

# Build and Start Docker Containers
echo_info "Building and starting Docker containers using docker-compose..."
docker-compose up --build -d

# Run Data Collection Script
echo_info "Running data collection script..."
python $DATA_COLLECTION_SCRIPT

# Run Preprocessing Script
echo_info "Running preprocessing script..."
python $PREPROCESSING_SCRIPT

# Run Feature Engineering Script
echo_info "Running feature engineering script..."
python $FEATURE_ENGINEERING_SCRIPT

# Run LSTM Model Training Script
echo_info "Running LSTM model training script..."
python $LSTM_MODEL_SCRIPT

echo_info "Setup and model training completed successfully."

# Deactivate the virtual environment
deactivate

echo_info "Virtual environment deactivated."
