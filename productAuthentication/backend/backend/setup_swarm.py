#!/usr/bin/env python3
"""
Ethereum Swarm setup and configuration script
This script helps set up Swarm for the anti-counterfeit system
"""

import subprocess
import sys
import os
import time
import requests
from app.core.config import settings

def check_swarm_installed():
    """Check if Swarm is installed"""
    try:
        result = subprocess.run(['swarm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Swarm is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Swarm is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Swarm is not installed or not in PATH")
        return False

def install_swarm():
    """Install Swarm (macOS/Linux)"""
    print("Installing Swarm...")
    
    # For macOS
    if sys.platform == "darwin":
        try:
            # Try installing via Go (if available)
            print("Attempting to install Swarm via Go...")
            subprocess.run(['go', 'install', 'github.com/ethersphere/swarm@latest'], check=True)
            print("✅ Swarm installed via Go")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Go not available. Please install Swarm manually.")
            print("Options:")
            print("1. Install Go: https://golang.org/dl/")
            print("2. Then run: go install github.com/ethersphere/swarm@latest")
            print("3. Or download from: https://github.com/ethersphere/swarm")
            return False
    
    # For Linux
    elif sys.platform.startswith("linux"):
        try:
            # Try installing via Go (if available)
            print("Attempting to install Swarm via Go...")
            subprocess.run(['go', 'install', 'github.com/ethersphere/swarm@latest'], check=True)
            print("✅ Swarm installed via Go")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Go not available. Please install Swarm manually.")
            print("Options:")
            print("1. Install Go: https://golang.org/dl/")
            print("2. Then run: go install github.com/ethersphere/swarm@latest")
            print("3. Or download from: https://github.com/ethersphere/swarm")
            return False
    
    else:
        print("❌ Unsupported platform. Please install Swarm manually.")
        print("Install Go from: https://golang.org/dl/")
        print("Then run: go install github.com/ethersphere/swarm@latest")
        return False

def initialize_swarm():
    """Initialize Swarm node"""
    try:
        result = subprocess.run(['swarm', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Swarm is ready to use")
            return True
        else:
            print(f"❌ Failed to initialize Swarm: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error initializing Swarm: {e}")
        return False

def start_swarm_daemon():
    """Start Swarm daemon"""
    try:
        # Check if daemon is already running
        try:
            response = requests.get(f"{settings.SWARM_GATEWAY}/", timeout=5)
            if response.status_code == 200:
                print("✅ Swarm daemon is already running")
                return True
        except:
            pass
        
        print("Starting Swarm daemon...")
        # Start daemon in background
        subprocess.Popen(['swarm', '--httpaddr', '127.0.0.1:8500'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for daemon to start
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"{settings.SWARM_GATEWAY}/", timeout=2)
                if response.status_code == 200:
                    print("✅ Swarm daemon started successfully")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Swarm daemon failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Swarm daemon: {e}")
        return False

def test_swarm_connection():
    """Test Swarm connection"""
    try:
        response = requests.get(f"{settings.SWARM_GATEWAY}/", timeout=10)
        if response.status_code == 200:
            print(f"✅ Swarm connection successful")
            print(f"   Gateway: {settings.SWARM_GATEWAY}")
            return True
        else:
            print(f"❌ Swarm connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Swarm connection test failed: {e}")
        return False

def setup_swarm():
    """Main setup function"""
    print("🚀 Setting up Ethereum Swarm for Anti-Counterfeit System")
    print("=" * 60)
    
    # Check if Swarm is installed
    if not check_swarm_installed():
        print("\n📦 Installing Swarm...")
        if not install_swarm():
            print("❌ Setup failed: Could not install Swarm")
            return False
    
    # Initialize Swarm if needed
    print("\n🔧 Initializing Swarm...")
    if not initialize_swarm():
        print("❌ Setup failed: Could not initialize Swarm")
        return False
    
    # Start Swarm daemon
    print("\n🚀 Starting Swarm daemon...")
    if not start_swarm_daemon():
        print("❌ Setup failed: Could not start Swarm daemon")
        return False
    
    # Test connection
    print("\n🧪 Testing Swarm connection...")
    if not test_swarm_connection():
        print("❌ Setup failed: Could not connect to Swarm")
        return False
    
    print("\n✅ Swarm setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the database migration: python migration_add_swarm_columns.py")
    print("2. Start your FastAPI application")
    print("3. Test product creation with Swarm storage")
    
    return True

if __name__ == "__main__":
    setup_swarm()
