@echo off
REM 🐼 Chinese Learning Web App Setup Script for Windows
REM This script sets up the virtual environment and installs dependencies

echo 🚀 Setting up Chinese Learning Web App...
echo ==================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.7+ first.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created!
) else (
    echo ✅ Virtual environment already exists!
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🎉 Setup completed successfully!
echo ==================================
echo.
echo 🚀 To run the app:
echo    1. Activate virtual environment: venv\Scripts\activate
echo    2. Run the app: python app.py
echo    3. Open browser: http://localhost:5000
echo    4. When done: deactivate
echo.
echo 📱 Or use the quick start script: run.bat
echo.
pause