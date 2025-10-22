@echo off
echo ========================================
echo   Eco-Connect Integrated Platform
echo ========================================
echo.
echo Features:
echo   - User Authentication (Login/Signup)
echo   - Face Recognition Registration
echo   - Guest Mode Access
echo   - AI-Powered Activity Verification
echo   - Eco-Coins Reward System
echo.

echo Installing required dependencies...
pip install -r requirements_simple.txt
echo.
echo Note: Face recognition is optional. To enable advanced face verification:
echo   1. Install Visual Studio Build Tools
echo   2. Install CMake
echo   3. Run: pip install dlib face-recognition
echo.

echo Starting all services...
echo.

echo [1/4] Starting Plantation API (Port 8001)...
start "Plantation API" cmd /k "python plantation_api.py"
timeout /t 3 /nobreak >nul

echo [2/4] Starting Waste Collection API (Port 8002)...
start "Waste API" cmd /k "python waste_api.py"
timeout /t 3 /nobreak >nul

echo [3/4] Starting Animal Feeding API (Port 8003)...
start "Animal Feeding API" cmd /k "python animal_feeding_api.py"
timeout /t 3 /nobreak >nul

echo [4/4] Starting Integrated Eco-Connect App (Port 3000)...
start "Eco-Connect Platform" cmd /k "cd flask_eco && python app.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    All Services Started Successfully!
echo ========================================
echo.
echo AI Verification APIs:
echo   - Tree Plantation: http://localhost:8001
echo   - Waste Collection: http://localhost:8002  
echo   - Animal Feeding: http://localhost:8003
echo.
echo Main Application:
echo   - Eco-Connect Platform: http://localhost:3000
echo.
echo Authentication Features:
echo   - Login/Signup with face recognition
echo   - Guest mode for quick access
echo   - Profile management with eco-coins
echo   - Activity tracking and rewards
echo.
echo Note: Make sure you have a webcam connected for face registration
echo.
echo Press any key to close this window...
pause >nul