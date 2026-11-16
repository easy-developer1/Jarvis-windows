@echo off
setlocal EnableExtensions

title JARVIS - Windows EXE Builder
cd /d "%~dp0"

echo.
echo ==========================================
echo          J.A.R.V.I.S. BUILD SYSTEM
echo ==========================================
echo.

echo [1/6] Checking Python 3.12...
py -3.12 --version
if errorlevel 1 (
    echo Python 3.12 was not found.
    echo Install Python 3.12 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/6] Creating virtual environment...
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 goto error
)

set "PYTHON=%CD%\.venv\Scripts\python.exe"

echo.
echo [3/6] Updating pip...
"%PYTHON%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto error

echo.
echo [4/6] Installing dependencies...
"%PYTHON%" -m pip install customtkinter pyttsx3 SpeechRecognition pyaudio psutil pyautogui requests pyinstaller
if errorlevel 1 goto error

echo.
echo [5/6] Compiling JARVIS...
"%PYTHON%" -m PyInstaller ^
 --noconfirm ^
 --onefile ^
 --windowed ^
 --collect-all customtkinter ^
 --hidden-import=pyttsx3.drivers ^
 --hidden-import=pyttsx3.drivers.sapi5 ^
 --hidden-import=speech_recognition ^
 --hidden-import=pyaudio ^
 --hidden-import=psutil ^
 --hidden-import=pyautogui ^
 --name "JARVIS" ^
 jarvis.py

if errorlevel 1 goto error

echo.
echo [6/6] Verifying executable...
if not exist "dist\JARVIS.exe" (
    echo ERROR: dist\JARVIS.exe was not created.
    goto error
)

echo.
echo ==========================================
echo          BUILD COMPLETED
echo ==========================================
echo Executable: %CD%\dist\JARVIS.exe
echo.
pause
exit /b 0

:error
echo.
echo ==========================================
echo             BUILD FAILED
echo ==========================================
echo Review the error messages above.
pause
exit /b 1
