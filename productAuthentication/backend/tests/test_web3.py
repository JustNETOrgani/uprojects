#!/usr/bin/env python3
"""
Simple Web3 test script
"""

from web3 import Web3
import json

def test_web3_connection():
    """Test Web3 connection to local Hardhat node"""
    
    print("🔍 Testing Web3 Connection...")
    print("-" * 50)
    
    try:
        # Test connection to Hardhat
        print("1. Connecting to Hardhat node...")
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
        if w3.is_connected():
            print("✅ Web3 connected successfully!")
            
            # Get network info
            chain_id = w3.eth.chain_id
            latest_block = w3.eth.block_number
            accounts = w3.eth.accounts
            
            print(f"   Chain ID: {chain_id}")
            print(f"   Latest Block: {latest_block}")
            print(f"   Available Accounts: {len(accounts)}")
            if accounts:
                print(f"   First Account: {accounts[0]}")
                balance = w3.eth.get_balance(accounts[0])
                print(f"   Balance: {w3.from_wei(balance, 'ether')} ETH")
        else:
            print("❌ Web3 connection failed")
            return
        
        # Test contract interaction
        print("\n2. Testing contract interaction...")
        contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
        
        # Basic ABI for testing
        basic_abi = [
            {
                "inputs": [],
                "name": "getTotalProducts",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        contract = w3.eth.contract(address=contract_address, abi=basic_abi)
        print(f"✅ Contract initialized at {contract_address}")
        
        # Test calling a function
        try:
            total_products = contract.functions.getTotalProducts().call()
            print(f"✅ Total products: {total_products}")
        except Exception as e:
            print(f"❌ Contract call failed: {e}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_web3_connection()
