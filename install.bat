@echo off
echo "Starting installation..."

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo "Python not found. Please install Python 3 and add it to your PATH."
    goto :eof
)

REM Create and activate virtual environment
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

REM Install backend dependencies
pip install -r backend/requirements.txt

REM Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo "Node.js not found. Please install Node.js."
    goto :eof
)

REM Install frontend dependencies and build
cd frontend
call npm install
call npm run build
cd ..

echo "Installation complete."

REM Create .env file if it doesn't exist
if not exist .env (
    echo BACKEND_PORT=5235 > .env
)

echo "Starting the application..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 5235 --reload --app-dir .