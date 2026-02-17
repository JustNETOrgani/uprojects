import json
import hashlib
from typing import Dict, Any, Optional, Tuple
import aiohttp
import asyncio
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class IPFSService:
    """
    IPFS service for decentralized storage of product data
    Uses the current IPFS HTTP API (api/v0)
    """
    
    def __init__(self):
        self.ipfs_gateway = getattr(settings, 'IPFS_GATEWAY', 'http://127.0.0.1:5001')
        self.public_gateway = getattr(settings, 'IPFS_PUBLIC_GATEWAY', 'https://ipfs.io/ipfs/')
        self.use_mock = False
        self._check_ipfs_availability()
    
    def _check_ipfs_availability(self):
        """Check if IPFS is available and ready, fallback to mock if not"""
        try:
            import requests
            # Check if IPFS node is accessible (POST request for IPFS API)
            response = requests.post(f"{self.ipfs_gateway}/api/v0/version", timeout=2)
            if response.status_code != 200:
                self.use_mock = True
                logger.warning("IPFS not available, using mock service")
            else:
                logger.info("IPFS node is available and ready")
        except Exception as e:
            self.use_mock = True
            logger.warning(f"IPFS not available ({e}), using mock service")
    
    def _get_mock_service(self):
        """Get mock service instance"""
        if not hasattr(self, '_mock_service'):
            from app.services.mock_ipfs_service import MockIPFSService
            self._mock_service = MockIPFSService()
        return self._mock_service
    
    async def _make_request(self, endpoint: str, method: str = 'POST', data: Dict = None, files: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to IPFS API"""
        try:
            url = f"{self.ipfs_gateway}/api/v0/{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method == 'POST':
                    if files:
                        # For file uploads using multipart/form-data
                        form_data = aiohttp.FormData()
                        for key, value in files.items():
                            form_data.add_field(key, value[0], filename=value[1])
                        async with session.post(url, data=form_data) as response:
                            result = await response.text()
                    else:
                        # For JSON data
                        async with session.post(url, json=data) as response:
                            result = await response.text()
                else:
                    async with session.get(url) as response:
                        result = await response.text()
                
                if response.status == 200:
                    return {"success": True, "data": result.strip()}
                else:
                    return {"success": False, "error": f"HTTP {response.status}: {result}"}
                    
        except Exception as e:
            logger.error(f"IPFS request error: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_data(self, data: Dict[str, Any], filename: str = "product_data.json") -> Dict[str, Any]:
        """
        Add product data to IPFS
        Returns: Dict with 'success', 'hash', 'size'
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2, default=str)
            
            # Create file-like object
            import io
            file_obj = io.BytesIO(json_data.encode('utf-8'))
            
            # Prepare files for upload
            files = {
                'file': (file_obj, filename)
            }
            
            result = await self._make_request("add", method='POST', files=files)
            
            if result["success"]:
                # Parse the JSON response from IPFS
                try:
                    response_data = json.loads(result["data"])
                    ipfs_hash = response_data.get("Hash")
                    size = response_data.get("Size", len(json_data))
                    name = response_data.get("Name", filename)
                    
                    if ipfs_hash:
                        # Pin the data to ensure it's not garbage collected
                        await self.pin_data(ipfs_hash)
                        
                        return {
                            "success": True,
                            "hash": ipfs_hash,
                            "size": size,
                            "name": name,
                            "public_url": self.get_public_url(ipfs_hash)
                        }
                    else:
                        return {"success": False, "error": "No hash in IPFS response"}
                except json.JSONDecodeError:
                    return {"success": False, "error": "Invalid JSON response from IPFS"}
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error adding data to IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from IPFS
        Returns: Dict with 'success' and 'data' or 'error'
        """
        try:
            result = await self._make_request(f"cat?arg={ipfs_hash}", method='POST')
            
            if result["success"]:
                try:
                    data = json.loads(result["data"])
                    return {"success": True, "data": data}
                except json.JSONDecodeError:
                    return {"success": True, "data": result["data"]}  # Return raw data if not JSON
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error getting data from IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def pin_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Pin data to IPFS to ensure it's not garbage collected
        """
        try:
            result = await self._make_request(f"pin/add?arg={ipfs_hash}", method='POST')
            if result["success"]:
                return {"success": True, "message": "Data pinned successfully"}
            else:
                return result
        except Exception as e:
            logger.error(f"Error pinning data to IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def unpin_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Unpin data from IPFS
        """
        try:
            result = await self._make_request(f"pin/rm?arg={ipfs_hash}", method='POST')
            return result
        except Exception as e:
            logger.error(f"Error unpinning data from IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    def get_public_url(self, ipfs_hash: str) -> str:
        """
        Get public URL for accessing IPFS data
        """
        return f"{self.public_gateway}{ipfs_hash}"
    
    async def store_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store complete product data in IPFS
        """
        if self.use_mock:
            mock_service = self._get_mock_service()
            return await mock_service.store_product_data(product_data)
        
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
                # Pin the data to ensure persistence
                pin_result = await self.pin_data(result["hash"])
                if not pin_result["success"]:
                    logger.warning(f"Failed to pin data: {pin_result.get('error')}")
                
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
            logger.error(f"Error storing product data in IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def retrieve_product_data(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from IPFS
        """
        if self.use_mock:
            mock_service = self._get_mock_service()
            return await mock_service.retrieve_product_data(ipfs_hash)
        
        try:
            result = await self.get_data(ipfs_hash)
            
            if result["success"]:
                data = result["data"]
                
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
            logger.error(f"Error retrieving product data from IPFS: {e}")
            return {"success": False, "error": str(e)}
    
    async def is_connected(self) -> bool:
        """
        Check if IPFS node is accessible
        """
        try:
            import aiohttp
            url = f"{self.ipfs_gateway}/api/v0/version"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    return response.status == 200
        except:
            return False
    
    async def get_node_info(self) -> Dict[str, Any]:
        """
        Get IPFS node information
        """
        try:
            import aiohttp
            url = f"{self.ipfs_gateway}/api/v0/version"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    if response.status == 200:
                        version_data = await response.text()
                        return {"success": True, "node_info": {"version": version_data.strip()}}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current IPFS service status
        """
        return {
            "use_mock": self.use_mock,
            "ipfs_gateway": self.ipfs_gateway,
            "public_gateway": self.public_gateway,
            "status": "mock" if self.use_mock else "real"
        }
