#!/bin/bash
echo "Starting installation..."

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install Python 3."
    exit
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Check for Node.js
if ! command -v node &> /dev/null
then
    echo "Node.js could not be found. Please install Node.js."
    exit
fi

# Install frontend dependencies and build
cd frontend
npm install
npm run build
cd ..

echo "Installation complete."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "BACKEND_PORT=5235" > .env
fi

echo "Starting the application..."
python3 -m backend.app.main