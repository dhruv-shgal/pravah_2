@echo off
echo ========================================
echo   Eco-Connect Platform - Quick Start
echo ========================================
echo.

echo Installing required dependencies...
pip install -r requirements_simple.txt
echo.
echo Note: Face recognition is optional. To enable advanced face verification:
echo   1. Install Visual Studio Build Tools
echo   2. Install CMake  
echo   3. Run: pip install dlib face-recognition
echo.

echo Starting Eco-Connect Platform...
echo.

echo Starting Integrated Eco-Connect App (Port 3000)...
cd flask_eco
python app.py

echo.
echo ========================================
echo   Eco-Connect Platform Started!
echo ========================================
echo.
echo Main Application: http://localhost:3000
echo.
echo Features Available:
echo   - User Authentication (Login/Signup)
echo   - Face Recognition Registration  
echo   - Guest Mode Access
echo   - Profile Management
echo   - Eco-Coins System
echo.
echo Note: AI verification requires the full service stack
echo Run 'run_all_services.bat' for complete functionality
echo.
pause