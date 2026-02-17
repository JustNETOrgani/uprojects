import json
import hashlib
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MockIPFSService:
    """
    Mock IPFS service for development and testing
    Simulates IPFS behavior without requiring actual IPFS installation
    """
    
    def __init__(self):
        self.storage = {}  # In-memory storage for development
        self.public_gateway = "https://ipfs.io/ipfs/"
        
    def _generate_ipfs_hash(self, data: str) -> str:
        """Generate a mock IPFS hash (Qm format)"""
        # Create a deterministic hash that looks like an IPFS hash
        hash_input = f"ipfs_mock_{data}_{datetime.now().isoformat()}"
        hash_bytes = hashlib.sha256(hash_input.encode()).digest()
        # IPFS hashes typically start with Qm for SHA-256
        return "Qm" + hash_bytes.hex()[:44]  # Qm + 44 hex chars
    
    async def add_data(self, data: Dict[str, Any], filename: str = "product_data.json") -> Dict[str, Any]:
        """
        Add product data to mock IPFS storage
        Returns: Dict with 'success', 'hash', 'size'
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2, default=str)
            
            # Generate mock IPFS hash
            ipfs_hash = self._generate_ipfs_hash(json_data)
            
            # Store in memory
            self.storage[ipfs_hash] = {
                'data': json_data,
                'filename': filename,
                'size': len(json_data),
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "hash": ipfs_hash,
                "size": len(json_data),
                "name": filename
            }
                
        except Exception as e:
            logger.error(f"Error adding data to mock IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from mock IPFS storage
        Returns: Dict with 'success' and 'data' or 'error'
        """
        try:
            if ipfs_hash in self.storage:
                return {
                    "success": True,
                    "data": self.storage[ipfs_hash]['data']
                }
            else:
                return {"success": False, "error": "Data not found"}
                
        except Exception as e:
            logger.error(f"Error getting data from mock IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def pin_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Pin data to mock IPFS (no-op for mock)
        """
        return {"success": True, "message": "Data pinned (mock)"}
    
    async def unpin_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Unpin data from mock IPFS (no-op for mock)
        """
        return {"success": True, "message": "Data unpinned (mock)"}
    
    def get_public_url(self, ipfs_hash: str) -> str:
        """
        Get public URL for accessing mock IPFS data
        """
        return f"{self.public_gateway}{ipfs_hash}"
    
    async def store_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store complete product data in mock IPFS
        """
        try:
            # Add metadata
            ipfs_data = {
                "type": "product",
                "version": "1.0",
                "timestamp": product_data.get("created_at"),
                "product": product_data
            }
            
            # Generate filename based on product info
            filename = f"product_{product_data.get('id', 'unknown')}_{product_data.get('product_name', 'unnamed').replace(' ', '_')}.json"
            
            result = await self.add_data(ipfs_data, filename)
            
            if result["success"]:
                # Pin the data (mock)
                await self.pin_data(result["hash"])
                
                return {
                    "success": True,
                    "ipfs_hash": result["hash"],
                    "size": result["size"],
                    "public_url": self.get_public_url(result["hash"]),
                    "filename": filename
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error storing product data in mock IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def retrieve_product_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from mock IPFS
        """
        try:
            result = await self.get_data(ipfs_hash)
            
            if result["success"]:
                data = json.loads(result["data"])
                
                # Validate data structure
                if isinstance(data, dict) and data.get("type") == "product":
                    return {
                        "success": True,
                        "product_data": data.get("product", {}),
                        "metadata": {
                            "version": data.get("version"),
                            "timestamp": data.get("timestamp"),
                            "type": data.get("type")
                        }
                    }
                else:
                    return {"success": False, "error": "Invalid data format"}
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving product data from mock IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def is_connected(self) -> bool:
        """
        Check if mock IPFS is accessible (always true for mock)
        """
        return True
    
    async def get_node_info(self) -> Dict[str, Any]:
        """
        Get mock IPFS node information
        """
        return {
            "success": True, 
            "node_info": {
                "version": "mock-ipfs-1.0.0",
                "status": "connected",
                "type": "mock",
                "storage_count": len(self.storage)
            }
        }
