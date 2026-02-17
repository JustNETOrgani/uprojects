#!/usr/bin/env python3
"""
IPFS setup script for the anti-counterfeit system.
This script helps set up IPFS for decentralized product data storage.
"""

import subprocess
import sys
import os
import platform
import requests
import time
from pathlib import Path

def check_ipfs_installed():
    """Check if IPFS is installed"""
    try:
        result = subprocess.run(['ipfs', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ IPFS is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ IPFS is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ IPFS is not installed or not in PATH")
        return False

def install_ipfs():
    """Install IPFS based on the operating system"""
    system = platform.system().lower()
    
    print(f"🔧 Installing IPFS for {system}...")
    
    if system == "darwin":  # macOS
        try:
            # Check if Homebrew is available
            subprocess.run(['brew', '--version'], check=True, capture_output=True)
            print("📦 Installing IPFS via Homebrew...")
            subprocess.run(['brew', 'install', 'ipfs'], check=True)
            print("✅ IPFS installed successfully via Homebrew")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Homebrew not found. Please install IPFS manually:")
            print("   1. Download from: https://dist.ipfs.io/#kubo")
            print("   2. Extract and add to PATH")
            return False
    
    elif system == "linux":
        print("📦 Installing IPFS for Linux...")
        try:
            # Download and install IPFS
            version = "v0.17.0"  # Latest stable version
            url = f"https://dist.ipfs.io/kubo/{version}/kubo_{version}_linux-amd64.tar.gz"
            
            print(f"   Downloading IPFS {version}...")
            response = requests.get(url)
            response.raise_for_status()
            
            # Save and extract
            with open("kubo.tar.gz", "wb") as f:
                f.write(response.content)
            
            subprocess.run(['tar', '-xzf', 'kubo.tar.gz'], check=True)
            subprocess.run(['sudo', 'mv', 'kubo/ipfs', '/usr/local/bin/'], check=True)
            subprocess.run(['rm', '-rf', 'kubo', 'kubo.tar.gz'], check=True)
            
            print("✅ IPFS installed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install IPFS: {e}")
            print("   Please install IPFS manually:")
            print("   1. Download from: https://dist.ipfs.io/#kubo")
            print("   2. Extract and add to PATH")
            return False
    
    elif system == "windows":
        print("📦 Installing IPFS for Windows...")
        print("   Please install IPFS manually:")
        print("   1. Download from: https://dist.ipfs.io/#kubo")
        print("   2. Extract and add to PATH")
        print("   3. Or use: winget install ipfs")
        return False
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def initialize_ipfs():
    """Initialize IPFS repository"""
    try:
        print("🔧 Initializing IPFS repository...")
        result = subprocess.run(['ipfs', 'init'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ IPFS repository initialized successfully")
            return True
        else:
            print(f"❌ Failed to initialize IPFS: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error initializing IPFS: {e}")
        return False

def start_ipfs_daemon():
    """Start IPFS daemon"""
    try:
        print("🚀 Starting IPFS daemon...")
        print("   This will start IPFS in the background.")
        print("   The daemon will be accessible at http://127.0.0.1:5001")
        
        # Start daemon in background
        process = subprocess.Popen(['ipfs', 'daemon'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for daemon to start
        time.sleep(3)
        
        # Check if daemon is running
        try:
            response = requests.get('http://127.0.0.1:5001/api/v0/version', timeout=5)
            if response.status_code == 200:
                print("✅ IPFS daemon started successfully")
                print(f"   Version: {response.text.strip()}")
                return True
            else:
                print("❌ IPFS daemon failed to start properly")
                return False
        except requests.exceptions.RequestException:
            print("❌ IPFS daemon is not responding")
            return False
            
    except Exception as e:
        print(f"❌ Error starting IPFS daemon: {e}")
        return False

def test_ipfs_connection():
    """Test IPFS connection"""
    try:
        print("🧪 Testing IPFS connection...")
        response = requests.get('http://127.0.0.1:5001/api/v0/version', timeout=5)
        if response.status_code == 200:
            print("✅ IPFS connection successful")
            print(f"   Version: {response.text.strip()}")
            return True
        else:
            print(f"❌ IPFS connection failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ IPFS connection failed: {e}")
        return False

def setup_ipfs():
    """Main setup function"""
    print("🌐 IPFS Setup for Anti-Counterfeit System")
    print("=" * 50)
    
    # Check if IPFS is installed
    if not check_ipfs_installed():
        print("\n📦 Installing IPFS...")
        if not install_ipfs():
            print("\n❌ IPFS installation failed. Please install manually.")
            return False
        print()
    
    # Initialize IPFS if needed
    ipfs_path = Path.home() / ".ipfs"
    if not ipfs_path.exists():
        print("\n🔧 Initializing IPFS...")
        if not initialize_ipfs():
            print("\n❌ IPFS initialization failed.")
            return False
        print()
    else:
        print("✅ IPFS repository already exists")
    
    # Test connection
    if not test_ipfs_connection():
        print("\n🚀 Starting IPFS daemon...")
        if not start_ipfs_daemon():
            print("\n❌ Failed to start IPFS daemon.")
            print("   Please start it manually with: ipfs daemon")
            return False
        print()
    
    print("\n🎉 IPFS setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run the database migration: python migration_add_ipfs_columns.py")
    print("   2. Start your FastAPI application")
    print("   3. Create products - they will be stored in IPFS automatically")
    
    print("\n🔗 Useful IPFS commands:")
    print("   - Check status: ipfs id")
    print("   - View peers: ipfs swarm peers")
    print("   - Add file: ipfs add <file>")
    print("   - View file: ipfs cat <hash>")
    print("   - Pin file: ipfs pin add <hash>")
    
    return True

if __name__ == "__main__":
    success = setup_ipfs()
    if not success:
        sys.exit(1)
