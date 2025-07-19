#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Starting installation..."
echo "Step 1: Checking system dependencies..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it first."
    exit 1
fi

# Check for python3-venv on Debian/Ubuntu
if command -v apt-get &> /dev/null; then
    if ! dpkg -l | grep -q python3-venv; then
        echo "Error: python3-venv is not installed. Please run 'sudo apt-get install python3-venv' first."
        exit 1
    fi
fi

# Check for Node.js and npm
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "Error: Node.js or npm is not installed. Please install them first."
    echo "We recommend using nvm (Node Version Manager) for installation."
    exit 1
fi

echo "All system dependencies are met."
echo "Step 2: Setting up Python virtual environment..."

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "Step 3: Installing Python packages..."
pip install -r backend/requirements.txt

echo "Step 4: Installing Node.js packages..."
cd frontend
npm install

echo "Step 5: Building frontend application..."
npm run build
cd ..

echo "Step 6: Creating .env file..."
# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "BACKEND_PORT=5235" > .env
fi

echo "Installation complete!"
echo "Starting the application..."
echo "You can access it at http://localhost:5235"

# Start the application
python3 -m backend.app.main