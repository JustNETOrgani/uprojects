#!/usr/bin/env python3
"""
Get valid Hardhat addresses and fix wallet address issues
"""

from web3 import Web3

def get_valid_addresses():
    """Get valid Hardhat addresses"""
    
    print("Getting Valid Hardhat Addresses...")
    print("-" * 50)
    
    try:
        # Connect to Hardhat
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
        if w3.is_connected():
            print("Connected to Hardhat network")
            
            # Get accounts
            accounts = w3.eth.accounts
            print(f"📋 Found {len(accounts)} accounts:")
            
            for i, account in enumerate(accounts):
                # Convert to checksum address
                checksum_address = Web3.to_checksum_address(account)
                balance = w3.eth.get_balance(account)
                balance_eth = w3.from_wei(balance, 'ether')
                
                print(f"   Account {i}: {checksum_address}")
                print(f"   Balance: {balance_eth} ETH")
                print()
            
            # Use the first account as the valid address
            valid_address = Web3.to_checksum_address(accounts[0])
            print(f"🎯 Recommended address to use: {valid_address}")
            
            return valid_address
            
        else:
            print("❌ Failed to connect to Hardhat")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    get_valid_addresses()
