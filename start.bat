@echo off

title Travel Assistant

echo.
echo ==============================================
echo Travel Assistant Startup Script
echo ==============================================
echo.

REM Check Python installation
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python installed

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found. Check Python installation
    pause
    exit /b 1
)

echo [OK] pip installed

REM Check .env file
if not exist ".env" (
    echo.
    echo [WARNING] .env file not found
    echo Please copy .env.example to .env and add your ModelScope token
    echo.
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env file. Please edit it with your token
        echo Example: MODELSCOPE_TOKEN=your_token_here
        echo.
    )
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Check virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
) else (
    echo [OK] Virtual environment exists
)

echo [INFO] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

echo [INFO] Starting application...
echo ==============================================
echo URL: http://localhost:7860
echo ==============================================
echo.
echo Press Ctrl+C to stop
echo.

py travel_assistant.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with error
    pause >nul
)
