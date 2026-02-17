import json
import hashlib
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MockSwarmService:
    """
    Mock Swarm service for development and testing
    Simulates Swarm behavior without requiring actual Swarm installation
    """
    
    def __init__(self):
        self.storage = {}  # In-memory storage for development
        self.public_gateway = "https://swarm-gateways.net/bzz:/"
        
    def _generate_swarm_hash(self, data: str) -> str:
        """Generate a mock Swarm hash (0x format)"""
        # Create a deterministic hash that looks like a Swarm hash
        hash_input = f"swarm_mock_{data}_{datetime.now().isoformat()}"
        hash_bytes = hashlib.sha256(hash_input.encode()).digest()
        return "0x" + hash_bytes.hex()[:40]  # 0x + 40 hex chars
    
    async def add_data(self, data: Dict[str, Any], filename: str = "product_data.json") -> Dict[str, Any]:
        """
        Add product data to mock Swarm storage
        Returns: Dict with 'success', 'hash', 'size'
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2, default=str)
            
            # Generate mock Swarm hash
            swarm_hash = self._generate_swarm_hash(json_data)
            
            # Store in memory
            self.storage[swarm_hash] = {
                'data': json_data,
                'filename': filename,
                'size': len(json_data),
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "hash": swarm_hash,
                "size": len(json_data),
                "name": filename
            }
                
        except Exception as e:
            logger.error(f"Error adding data to mock Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from mock Swarm storage
        Returns: Dict with 'success' and 'data' or 'error'
        """
        try:
            if swarm_hash in self.storage:
                return {
                    "success": True,
                    "data": self.storage[swarm_hash]['data']
                }
            else:
                return {"success": False, "error": "Data not found"}
                
        except Exception as e:
            logger.error(f"Error getting data from mock Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def pin_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Pin data to mock Swarm (no-op for mock)
        """
        return {"success": True, "message": "Data pinned (mock)"}
    
    async def unpin_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Unpin data from mock Swarm (no-op for mock)
        """
        return {"success": True, "message": "Data unpinned (mock)"}
    
    def get_public_url(self, swarm_hash: str) -> str:
        """
        Get public URL for accessing mock Swarm data
        """
        return f"{self.public_gateway}{swarm_hash}"
    
    async def store_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store complete product data in mock Swarm
        """
        try:
            # Add metadata
            swarm_data = {
                "type": "product",
                "version": "1.0",
                "timestamp": product_data.get("created_at"),
                "product": product_data
            }
            
            # Generate filename based on product info
            filename = f"product_{product_data.get('id', 'unknown')}_{product_data.get('product_name', 'unnamed').replace(' ', '_')}.json"
            
            result = await self.add_data(swarm_data, filename)
            
            if result["success"]:
                # Pin the data (mock)
                await self.pin_data(result["hash"])
                
                return {
                    "success": True,
                    "swarm_hash": result["hash"],
                    "size": result["size"],
                    "public_url": self.get_public_url(result["hash"]),
                    "filename": filename
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error storing product data in mock Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def retrieve_product_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from mock Swarm
        """
        try:
            result = await self.get_data(swarm_hash)
            
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
            logger.error(f"Error retrieving product data from mock Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def is_connected(self) -> bool:
        """
        Check if mock Swarm is accessible (always true for mock)
        """
        return True
    
    async def get_node_info(self) -> Dict[str, Any]:
        """
        Get mock Swarm node information
        """
        return {
            "success": True, 
            "node_info": {
                "status": "connected",
                "type": "mock",
                "storage_count": len(self.storage)
            }
        }
