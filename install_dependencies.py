import subprocess
import sys

def install_offline_dependencies():
    """Install all required dependencies for offline speech recognition"""
    
    dependencies = [
        "pocketsphinx",
        "pyaudio",
        "pyttsx3",
        "pillow"
    ]
    
    print("Installing offline speech recognition dependencies...")
    
    for package in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
    
    print("\nInstallation complete!")
    print("\nNote: PocketSphinx might require additional system dependencies:")
    print("Ubuntu/Debian: sudo apt-get install libasound2-dev")
    print("macOS: brew install portaudio")
    print("Windows: Dependencies should be handled automatically")

if __name__ == "__main__":
    install_offline_dependencies()
