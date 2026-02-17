#!/usr/bin/env python3
"""
Script to create admin users for the Anti-Counterfeit system
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"

def create_admin_user(email: str, password: str, full_name: str, wallet_address: str = None):
    """Create an admin user via the API"""
    
    print(f"🔧 Creating admin user: {email}")
    print("-" * 50)
    
    try:
        user_data = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": "admin",
            "wallet_address": wallet_address
        }
        
        print("1. Creating user account...")
        create_response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json=user_data
        )
        
        if create_response.status_code != 200:
            print(f"Failed to create user: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False
        
        user_info = create_response.json()
        print(f"User created successfully! ID: {user_info.get('id')}")
        
        print("\n2. Logging in to verify account...")
        login_response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            data={
                "username": email,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"Failed to login: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        print("Login successful!")
        
        # Verify user info
        print("\n3. Verifying user information...")
        user_response = requests.get(
            f"{API_BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            print(f"Failed to get user info: {user_response.status_code}")
            return False
        
        user_info = user_response.json()
        print(f" User verified:")
        print(f"   - Name: {user_info.get('full_name')}")
        print(f"   - Email: {user_info.get('email')}")
        print(f"   - Role: {user_info.get('role')}")
        print(f"   - Wallet: {user_info.get('wallet_address') or 'Not set'}")
        
        print(f"\n🎉 Admin user '{email}' created successfully!")
        print(f"\n📋 Login Credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: Admin")
        
        if wallet_address:
            print(f"   Wallet: {wallet_address}")
        
        print(f"\n Access URLs:")
        print(f"   Frontend: http://localhost:3000")
        print(f"   Onboarding: http://localhost:3000/onboarding")
        print(f"   Dashboard: http://localhost:3000")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(" Connection Error: Make sure the backend is running")
        print("   Backend: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f" Error: {str(e)}")
        return False

def create_manufacturer_user(email: str, password: str, full_name: str, wallet_address: str = None):
    """Create a manufacturer user via the API"""
    
    print(f" Creating manufacturer user: {email}")
    print("-" * 50)
    
    try:
        # First, create the user
        user_data = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": "manufacturer",
            "wallet_address": wallet_address
        }
        
        print("1. Creating user account...")
        create_response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json=user_data
        )
        
        if create_response.status_code != 200:
            print(f" Failed to create user: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False
        
        user_info = create_response.json()
        print(f" User created successfully! ID: {user_info.get('id')}")
        
        # Now login to verify account
        print("\n2. Logging in to verify account...")
        login_response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            data={
                "username": email,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"Failed to login: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        print("Login successful!")
        
        # Verify user info
        print("\n3. Verifying user information...")
        user_response = requests.get(
            f"{API_BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            print(f"Failed to get user info: {user_response.status_code}")
            return False
        
        user_info = user_response.json()
        print(f"User verified:")
        print(f"   - Name: {user_info.get('full_name')}")
        print(f"   - Email: {user_info.get('email')}")
        print(f"   - Role: {user_info.get('role')}")
        print(f"   - Wallet: {user_info.get('wallet_address') or 'Not set'}")
        
        print(f"\n Manufacturer user '{email}' created successfully!")
        print(f"\n Login Credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: Manufacturer")
        
        if wallet_address:
            print(f"   Wallet: {wallet_address}")
        
        print(f"\n Access URLs:")
        print(f"   Frontend: http://localhost:3000")
        print(f"   Onboarding: http://localhost:3000/onboarding")
        print(f"   Products: http://localhost:3000/products")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("Connection Error: Make sure the backend is running")
        print("   Backend: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function to create users"""
    
    print("🚀 Anti-Counterfeit System - User Creation Tool")
    print("=" * 60)
    
    print("\nChoose user type to create:")
    print("1. Admin User")
    print("2. Manufacturer User")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n" + "="*50)
        print("Creating Admin User")
        print("="*50)
        
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        full_name = input("Full Name: ").strip()
        wallet_address = input("Wallet Address (optional, press Enter to skip): ").strip()
        
        if not email or not password or not full_name:
            print("Email, password, and full name are required!")
            return
        
        if wallet_address == "":
            wallet_address = None
        
        create_admin_user(email, password, full_name, wallet_address)
        
    elif choice == "2":
        print("\n" + "="*50)
        print("Creating Manufacturer User")
        print("="*50)
        
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        full_name = input("Full Name: ").strip()
        wallet_address = input("Wallet Address (optional, press Enter to skip): ").strip()
        
        if not email or not password or not full_name:
            print("Email, password, and full name are required!")
            return
        
        if wallet_address == "":
            wallet_address = None
        
        create_manufacturer_user(email, password, full_name, wallet_address)
        
    elif choice == "3":
        print("👋 Goodbye!")
        return
        
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
