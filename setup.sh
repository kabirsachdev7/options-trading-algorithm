#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define paths
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
VENV_DIR="venv"
REQUIREMENTS="$BACKEND_DIR/requirements.txt"

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
cd $FRONTEND_DIR

# Remove conflicting node_modules and package-lock.json if present
if [ -d "node_modules" ] || [ -f "package-lock.json" ]; then
    echo_info "Removing existing node_modules and package-lock.json to avoid conflicts..."
    rm -rf node_modules package-lock.json
fi

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo_error "package.json not found in '$FRONTEND_DIR'. Ensure you have initialized the React app correctly."
    exit 1
fi

# Remove global babel-jest if exists
echo_info "Checking for globally installed babel-jest..."
npm ls -g babel-jest || echo_info "No global babel-jest found."

echo_info "Uninstalling global babel-jest if present..."
npm uninstall -g babel-jest || echo_info "No global babel-jest to uninstall."

# Clean NPM cache
echo_info "Cleaning npm cache..."
npm cache clean --force

# Install Frontend Dependencies
echo_info "Installing frontend dependencies using npm..."
npm install

# Install Missing Babel Plugin
echo_info "Installing @babel/plugin-proposal-private-property-in-object..."
npm install --save-dev @babel/plugin-proposal-private-property-in-object

# Build Frontend Application
echo_info "Building frontend application..."
npm run build || {
    echo_error "Frontend build failed. Attempting to skip preflight checks..."
    echo "SKIP_PREFLIGHT_CHECK=true" > .env
    npm run build
}

# Return to Project Root Directory
cd ..

# Build and Start Docker Containers
echo_info "Building and starting Docker containers using docker-compose..."
docker-compose up --build -d

# Train Models
echo_info "Training LSTM Option Pricing Model..."
python $BACKEND_DIR/models/train_lstm_option_pricing.py

echo_info "Training FNN Strategy Model..."
python $BACKEND_DIR/models/train_fnn_strategy.py

echo_info "Training LSTM Strategy Model..."
python $BACKEND_DIR/models/train_lstm_strategy.py

# Deactivate the virtual environment
deactivate

echo_info "Virtual environment deactivated."
echo_info "Setup and model training completed successfully."
