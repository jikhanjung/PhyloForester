#!/usr/bin/env python3
"""
PhyloForester Build Script
Unified cross-platform build script for Windows, macOS, and Linux
"""

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Import version from centralized version file
try:
    from version import __version__ as VERSION
except ImportError:

    def get_version_from_file():
        """Extract version from version.py if import fails"""
        version_file = Path(__file__).parent / "version.py"
        with open(version_file) as f:
            content = f.read()
            match = re.search(r'__version__ = "(.*?)"', content)
            if match:
                return match.group(1)
        raise RuntimeError("Unable to find version string in version.py")

    VERSION = get_version_from_file()


# Build configuration
APP_NAME = "PhyloForester"
MAIN_SCRIPT = "PhyloForester.py"
ICON_PATH = "icons/PhyloForester.png"
BUILD_DIR = "build"
DIST_DIR = "dist"

# Data files to include
DATA_FILES = [
    ("icons/*.png", "icons"),
    ("data/*.*", "data"),
    ("translations/*.qm", "translations"),
    ("migrations/*", "migrations"),
]


def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def print_step(message):
    """Print a step message"""
    print(f">> {message}")


def run_command(cmd, shell=False, check=True):
    """Run a shell command and return the result"""
    print(f"  Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(
        cmd, shell=shell, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
    return result


def clean_build_dirs():
    """Remove previous build artifacts"""
    print_step("Cleaning previous builds...")
    for directory in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"  Removed: {directory}/")


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    print_step("Checking PyInstaller...")
    try:
        result = subprocess.run(
            ["pyinstaller", "--version"], capture_output=True, text=True, check=True
        )
        version = result.stdout.strip()
        print(f"  Found PyInstaller {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  Error: PyInstaller is not installed.")
        print("  Install it with: pip install pyinstaller")
        return False


def get_pyinstaller_args():
    """Get PyInstaller arguments for the current platform"""
    args = [
        "pyinstaller",
        "--clean",
        "--onedir",
        "--noconsole",
        f"--name={APP_NAME}",
    ]

    # Add data files
    for src_pattern, dest_folder in DATA_FILES:
        separator = ";" if platform.system() == "Windows" else ":"
        args.append(f"--add-data={src_pattern}{separator}{dest_folder}")

    # Add icon (platform-specific path separator)
    if platform.system() == "Windows":
        icon_path = ICON_PATH.replace("/", "\\")
    else:
        icon_path = ICON_PATH
    args.append(f"--icon={icon_path}")

    # Add main script
    args.append(MAIN_SCRIPT)

    return args


def run_pyinstaller():
    """Run PyInstaller with appropriate arguments"""
    print_step("Running PyInstaller...")
    args = get_pyinstaller_args()

    try:
        result = run_command(args)
        if result.returncode == 0:
            print("  [OK] PyInstaller completed successfully")
            return True
        print("  [FAIL] PyInstaller failed")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] PyInstaller failed with error: {e}")
        return False


def verify_build():
    """Verify that the build was successful"""
    print_step("Verifying build...")

    system = platform.system()
    if system == "Windows":
        exe_path = Path(DIST_DIR) / APP_NAME / f"{APP_NAME}.exe"
    elif system == "Darwin":  # macOS
        exe_path = Path(DIST_DIR) / APP_NAME / APP_NAME
    else:  # Linux
        exe_path = Path(DIST_DIR) / APP_NAME / APP_NAME

    if exe_path.exists():
        print(f"  [OK] Build successful: {exe_path}")
        return True
    print(f"  [FAIL] Build failed: {exe_path} not found")
    return False


def create_windows_installer():
    """Create Windows installer using Inno Setup (if available)"""
    print_step("Creating Windows installer...")

    # Check if Inno Setup script exists
    iss_script = Path("InnoSetup") / "phyloforester.iss"
    if not iss_script.exists():
        print(f"  [WARN] Inno Setup script not found: {iss_script}")
        print("  Skipping installer creation")
        return False

    # Check if Inno Setup is installed
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    iscc_exe = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_exe = path
            break

    if not iscc_exe:
        print("  [WARN] Inno Setup not found")
        print("  Skipping installer creation")
        return False

    try:
        # Set version in environment for Inno Setup
        env = os.environ.copy()
        env["PHYLOFORESTER_VERSION"] = VERSION

        result = subprocess.run(
            [iscc_exe, str(iss_script)], env=env, capture_output=True, text=True, check=True
        )
        print("  [OK] Windows installer created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] Installer creation failed: {e}")
        return False


def create_macos_dmg():
    """Create macOS DMG image"""
    print_step("Creating macOS DMG...")
    print("  [WARN] DMG creation not yet implemented")
    print("  Use create-dmg or hdiutil manually")
    return False


def create_linux_appimage():
    """Create Linux AppImage"""
    print_step("Creating Linux AppImage...")
    print("  [WARN] AppImage creation not yet implemented")
    print("  Use linuxdeploy manually")
    return False


def build_windows():
    """Build Windows executable and installer"""
    print_header(f"Building {APP_NAME} {VERSION} for Windows")

    if not check_pyinstaller():
        return False

    clean_build_dirs()

    if not run_pyinstaller():
        return False

    if not verify_build():
        return False

    # Try to create installer (optional)
    create_windows_installer()

    print_header("Windows Build Complete!")
    print(f"Executable: {DIST_DIR}\\{APP_NAME}\\{APP_NAME}.exe")
    return True


def build_macos():
    """Build macOS application bundle"""
    print_header(f"Building {APP_NAME} {VERSION} for macOS")

    if not check_pyinstaller():
        return False

    clean_build_dirs()

    if not run_pyinstaller():
        return False

    if not verify_build():
        return False

    # Try to create DMG (optional)
    create_macos_dmg()

    print_header("macOS Build Complete!")
    print(f"Application: {DIST_DIR}/{APP_NAME}/{APP_NAME}")
    return True


def build_linux():
    """Build Linux executable"""
    print_header(f"Building {APP_NAME} {VERSION} for Linux")

    if not check_pyinstaller():
        return False

    clean_build_dirs()

    if not run_pyinstaller():
        return False

    if not verify_build():
        return False

    # Try to create AppImage (optional)
    create_linux_appimage()

    print_header("Linux Build Complete!")
    print(f"Executable: {DIST_DIR}/{APP_NAME}/{APP_NAME}")
    return True


def main():
    """Main build function"""
    print_header(f"{APP_NAME} Build Script")
    print(f"Version: {VERSION}")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")

    system = platform.system()

    if system == "Windows":
        success = build_windows()
    elif system == "Darwin":
        success = build_macos()
    elif system == "Linux":
        success = build_linux()
    else:
        print(f"Error: Unsupported platform: {system}")
        success = False

    if success:
        print("\n[SUCCESS] Build completed successfully!\n")
        return 0
    print("\n[ERROR] Build failed!\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
