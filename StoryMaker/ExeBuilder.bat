@echo off
REM Batch script to lint Python files with flake8 and create an executable with PyInstaller

REM -----------------------------------
REM Configuration
REM -----------------------------------

REM Set the name of your main Python script here
set MAIN_SCRIPT=main.py

REM Set the name of the output executable
set OUTPUT_NAME=JSONBuchEditor

REM -----------------------------------
REM Activate Virtual Environment
REM -----------------------------------

echo Attempting to activate virtual environment...
if exist venv\Scripts\activate (
    call venv\Scripts\activate
    echo Virtual environment activated.
) else (
    echo [Error] Virtual environment not found. Please create it with "python -m venv venv".
    pause
    exit /b 1
)

REM -----------------------------------
REM Verify Activation
REM -----------------------------------

echo.
echo Current Directory: %CD%
echo.
echo [Verification] Checking if virtual environment is active...
python -c "import sys; print('Python executable:', sys.executable)"
echo.
echo Current flake8 executable:
where flake8
echo.
echo Current PyInstaller executable:
where pyinstaller
echo.
echo Current Pillow executable:
python -c "import PIL; print('Pillow version:', PIL.__version__)"
echo.

REM -----------------------------------
REM Check for Required Tools
REM -----------------------------------

REM Check if flake8 is installed
echo Checking if flake8 is installed...
flake8 --version >nul 2>&1
if ERRORLEVEL 1 (
    echo [Error] flake8 is not installed. Please install it by running:
    echo       pip install flake8
    pause
    exit /b 1
) else (
    echo flake8 is installed.
)

REM Check if PyInstaller is installed
echo Checking if PyInstaller is installed...
pyinstaller --version >nul 2>&1
if ERRORLEVEL 1 (
    echo [Error] PyInstaller is not installed. Please install it by running:
    echo       pip install pyinstaller
    pause
    exit /b 1
) else (
    echo PyInstaller is installed.
)

REM Check if Pillow is installed
echo Checking if Pillow is installed...
python -c "import PIL" >nul 2>&1
if ERRORLEVEL 1 (
    echo [Error] Pillow is not installed. Please install it by running:
    echo       pip install pillow
    pause
    exit /b 1
) else (
    echo Pillow is installed.
)

REM -----------------------------------
REM Linting Python Files with flake8
REM -----------------------------------

echo.
echo ===============================================
echo        Starting Code Linting with flake8
echo ===============================================
echo.

REM Initialize error flag
set ERROR_FOUND=0

REM Delete existing buildlog.txt if it exists
if exist buildlog.txt del buildlog.txt

REM Iterate through all .py files in the current directory
for %%f in (*.py) do (
    echo [flake8] Checking %%f...
    flake8 "%%f" >> buildlog.txt
    if ERRORLEVEL 1 (
        echo [flake8] Issues found in %%f
        set ERROR_FOUND=1
    )
)

REM Check if any errors were found
if "%ERROR_FOUND%"=="1" (
    echo.
    echo [Warning] flake8 detected issues in one or more files.
    echo The results have been saved to buildlog.txt.
    echo Do you still want to create the executable? (Y/N)
    set /p USER_INPUT=Your choice: 
    if /I "%USER_INPUT%"=="Y" (
        echo Proceeding to create the executable...
    ) else (
        echo Build aborted.
        pause
        exit /b 1
    )
) else (
    echo.
    echo [Success] All Python files passed flake8 checks.
    echo.
)

REM -----------------------------------
REM Creating Executable with PyInstaller
REM -----------------------------------

REM Verify that the main script exists
if not exist "%MAIN_SCRIPT%" (
    echo [Error] Main script "%MAIN_SCRIPT%" not found in the current directory.
    pause
    exit /b 1
)

echo ===============================================
echo        Building Executable with PyInstaller
echo ===============================================
echo.

REM Run PyInstaller to create a one-file executable
pyinstaller --onefile --name "%OUTPUT_NAME%" "%MAIN_SCRIPT%" >> buildlog.txt 2>&1

REM Check if PyInstaller succeeded
if ERRORLEVEL 1 (
    echo [Error] PyInstaller failed to create the executable.
    echo Überprüfen Sie die buildlog.txt für Details.
    pause
    exit /b 1
) else (
    echo.
    echo [Success] Executable created successfully in the 'dist' folder.
    echo.
)

REM -----------------------------------
REM Optional: Clean up build files generated by PyInstaller
REM -----------------------------------

REM Uncomment the lines below if you want to remove build artifacts
REM echo Cleaning up build artifacts...
REM rmdir /s /q build
REM del /q *.spec
REM echo Cleanup complete.

pause
