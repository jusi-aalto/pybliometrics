@echo off
echo ==========================================
echo Verifying pybliometrics-mcp Installation
echo ==========================================
echo.

echo [1/6] Checking current directory...
cd
echo.

echo [2/6] Listing files in current directory...
dir /B
echo.

echo [3/6] Checking src folder...
if exist src\pybliometrics_mcp (
    echo ✓ src\pybliometrics_mcp folder exists
    dir /B src\pybliometrics_mcp
) else (
    echo ✗ src\pybliometrics_mcp folder NOT found
)
echo.

echo [4/6] Testing Python import...
python -c "import pybliometrics_mcp; print('✓ Import successful!')" 2>nul && (
    echo Python can import the package
) || (
    echo ✗ Import failed - package may not be installed
    echo Run: pip install -e .
)
echo.

echo [5/6] Checking if pybliometrics-mcp command exists...
where pybliometrics-mcp 2>nul && (
    echo ✓ Command found
) || (
    echo ✗ Command not found in PATH
    echo You may need to use: python -m pybliometrics_mcp.server
)
echo.

echo [6/6] Running test script...
if exist test_server.py (
    python test_server.py
) else (
    echo ✗ test_server.py not found
)
echo.

echo ==========================================
echo Verification Complete!
echo ==========================================
pause
