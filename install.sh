#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Starting installation..."
echo "Step 1: Checking system dependencies..."

# Check for Python 3 and pip3
if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null; then
    echo "Error: Python 3 or pip3 is not installed. Please install them first."
    echo "On Debian/Ubuntu, run: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

# Check for Node.js and npm
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "Error: Node.js or npm is not installed. Please install them first."
    exit 1
fi

echo "All system dependencies are met."
echo "Step 2: Setting up Python virtual environment using 'virtualenv'..."

# Install virtualenv if it's not installed
if ! command -v virtualenv &> /dev/null; then
    echo "'virtualenv' command not found. Installing it via pip..."
    pip3 install --user virtualenv
    # Add user's local bin to PATH if it's not already there
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtual environment using virtualenv
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment with 'virtualenv'..."
    virtualenv venv
fi

# Verify that the virtual environment was created successfully
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Failed to create Python virtual environment even with 'virtualenv'."
    echo "Your Python installation is severely broken. Please reinstall Python completely."
    exit 1
fi

source venv/bin/activate
echo "Virtual environment activated."

echo "Step 3: Installing Python packages..."
pip install -r backend/requirements.txt

echo "Step 4: Installing Node.js packages..."
cd frontend
npm install

echo "Step 5: Building frontend application..."
npm run build
cd ..

echo "Step 6: Creating .env file..."
if [ ! -f ".env" ]; then
    echo "BACKEND_PORT=5235" > .env
fi

echo "Installation complete!"
echo "Starting the application..."
echo "You can access it at http://localhost:5235"

# Start the application
python3 -m backend.app.main