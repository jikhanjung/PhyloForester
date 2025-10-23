@echo off
REM PhyloForester Build Script (Windows)
REM Usage: build.bat

echo ======================================
echo Building PhyloForester...
echo ======================================
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Error: PyInstaller is not installed.
    echo Install it with: pip install pyinstaller
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Run PyInstaller
echo Running PyInstaller...
pyinstaller --clean PhyloForester.spec
echo.

REM Check if build was successful
if exist "dist\PhyloForester" (
    echo ======================================
    echo Build complete!
    echo ======================================
    echo.
    echo Output directory: dist\PhyloForester\
    echo.
    echo To run the application:
    echo   cd dist\PhyloForester
    echo   PhyloForester.exe
    echo.
) else (
    echo ======================================
    echo Build failed!
    echo ======================================
    pause
    exit /b 1
)

pause
