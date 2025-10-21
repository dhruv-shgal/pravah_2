@echo off
echo ========================================
echo    Eco-Connect Multi-Service Startup
echo ========================================
echo.

echo Starting all API services...
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

echo [4/4] Starting Flask Web App (Port 3000)...
start "Flask Eco App" cmd /k "cd flask_eco && python app.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo    All Services Started!
echo ========================================
echo.
echo API Endpoints:
echo   - Plantation: http://localhost:8001
echo   - Waste Collection: http://localhost:8002  
echo   - Animal Feeding: http://localhost:8003
echo.
echo Web Application:
echo   - Eco-Connect: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul