"""
Quick setup script to install all required dependencies for AIWAF website
"""
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all required packages"""
    packages = [
        "python-dotenv",
        "Flask-SQLAlchemy",
        "PyMySQL",
        "sshtunnel",
        "paramiko<4.0.0,>=2.7.2"
    ]
    
    print("Installing required packages for AIWAF website...")
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nInstallation complete: {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("🎉 All packages installed! You can now run: python run_tunnel.py")
    else:
        print("⚠️ Some packages failed to install. Please check the errors above.")

if __name__ == "__main__":
    main()