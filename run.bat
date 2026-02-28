@echo off
REM Run script for Medical AI Backend (Windows)
REM This script starts the FastAPI application

echo 🏥 Starting Medical AI Multi-Agent System...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv venv
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo Please copy .env.example to .env and configure it
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Checking dependencies...
pip install -q -r requirements.txt

echo.
echo ✅ Starting server...
echo 📡 API will be available at: http://localhost:8000
echo 📚 API docs at: http://localhost:8000/docs
echo.

REM Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
