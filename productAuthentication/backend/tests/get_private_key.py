#!/usr/bin/env python3
"""
Get private key for Hardhat Account 0
"""

# Hardhats privates
HARDHAT_PRIVATE_KEYS = [
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",  # Account 0
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",  # Account 1
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",  # Account 2
]

def get_private_key():
    """Get private key for Hardhat Account 0"""
    
    print("🔑 Getting Hardhat Private Keys...")
    print("-" * 50)
    
    print("Hardhat Default Private Keys(dev):")
    for i, key in enumerate(HARDHAT_PRIVATE_KEYS):
        print(f"   Account {i}: {key}")
    
    print(f"\n  testing: {HARDHAT_PRIVATE_KEYS[0]}")
    print("WARNING: These are public keys for development only!")

    
    return HARDHAT_PRIVATE_KEYS[0]

if __name__ == "__main__":
    get_private_key()
