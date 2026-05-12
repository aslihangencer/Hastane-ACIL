@echo off
TITLE Hospital ERP - Production Auto Recovery System

set PROJECT_DIR=C:\Users\Handan Gencer\Desktop\Acil_Servis_App
set PORT=8501
set MAX_RETRIES=5
set RETRY_COUNT=0

echo ==========================================
echo 🏥 HOSPITAL ERP - AUTO RECOVERY SYSTEM
echo ==========================================
echo.

cd /d "%PROJECT_DIR%"

:CHECK_APP
echo [CHECK] Application health kontrol ediliyor...

:: Python check
python --version >nul 2>&1
if errorlevel 1 (
    echo [CRITICAL] Python bulunamadi!
    pause
    exit
)

:: Streamlit check
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [CRITICAL] Streamlit eksik! (Lutfen 'pip install streamlit' calistirin)
    pause
    exit
)

:: App file check
if not exist "app.py" (
    echo [CRITICAL] app.py bulunamadi!
    pause
    exit
)

echo [OK] Sistem hazir

:START_APP
echo [START] Hospital ERP baslatiliyor...
echo [INFO] http://localhost:%PORT%

:: Start app in separate process (Minimized or background if possible, but separate window is good for visibility)
start "Hospital ERP Engine" cmd /c ^
py -m streamlit run app.py --server.port %PORT% --logger.level=error --server.headless=true

timeout /t 8 >nul

:: Health check loop
:HEALTH_CHECK
echo [HEALTH] Sistem kontrol ediliyor...

powershell -Command "try { Invoke-WebRequest http://localhost:%PORT% -UseBasicParsing -TimeoutSec 5 } catch { exit 1 }"

if errorlevel 1 (
    echo [FAIL] Sistem cevap vermiyor (Port %PORT% erisilemez)
    set /a RETRY_COUNT+=1
    echo [RETRY] Deneme: %RETRY_COUNT% / %MAX_RETRIES%

    if %RETRY_COUNT% GEQ %MAX_RETRIES% (
        echo [CRITICAL] Sistem otomatik olarak baslatilamadi. Lutfen terminaldeki Python hatalarini kontrol edin.
        pause
        exit
    )

    echo [RECOVERY] Sistem donmus olabilir. Yeniden baslatiliyor...
    :: Taskkill only the python instances related to this app might be tricky, but we'll try basic
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq Hospital ERP Engine" >nul 2>&1
    timeout /t 3 >nul
    goto START_APP
)

echo [OK] Sistem aktif ve calisiyor. Izleme devam ediyor...

:: Continuous monitoring (every 15 seconds)
timeout /t 15 >nul
goto HEALTH_CHECK
