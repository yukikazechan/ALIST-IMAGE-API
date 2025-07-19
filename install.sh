#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- Helper Functions ---
install_dependencies() {
    echo "Updating package list..."
    sudo apt-get update -y

    # Install python3-venv if not present
    if ! dpkg -l | grep -q python3-venv; then
        echo "python3-venv not found. Attempting to install..."
        sudo apt-get install -y python3-venv
    fi

    # Install Node.js and npm using nvm if not present
    if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
        echo "Node.js or npm not found. Attempting to install using nvm..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        nvm install --lts
        # Source nvm again to use it in the current script
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi
}

# --- Main Script ---
echo "Starting installation..."

# Check for sudo permissions at the beginning
if [ "$EUID" -ne 0 ]; then
    echo "This script needs to install system packages. Please run with sudo or enter your password."
    sudo -v
    if [ $? -ne 0 ]; then
        echo "Sudo permission denied. Exiting."
        exit 1
    fi
fi

# Check for essential tools
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it first."
    exit 1
fi
if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed. Please run 'sudo apt-get install curl' first."
    exit 1
fi

# Install system dependencies if needed
install_dependencies

echo "All system dependencies are installed."
echo "Setting up Python virtual environment..."

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "Installing Python packages..."
pip install -r backend/requirements.txt

echo "Installing Node.js packages..."
cd frontend
npm install

echo "Building frontend application..."
npm run build
cd ..

echo "Creating .env file..."
if [ ! -f ".env" ]; then
    echo "BACKEND_PORT=5235" > .env
fi

echo "Installation complete!"
echo "Starting the application..."
echo "You can access it at http://localhost:5235"

# Start the application
python3 -m backend.app.main