import json
import hashlib
from typing import Dict, Any, Optional, Tuple
import aiohttp
import asyncio
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SwarmService:
    """
    Ethereum Swarm service for decentralized storage of product data
    """
    
    def __init__(self):
        self.swarm_gateway = getattr(settings, 'SWARM_GATEWAY', 'http://localhost:1633')
        self.swarm_api_url = f"{self.swarm_gateway}/bzz"
        self.public_gateway = getattr(settings, 'SWARM_PUBLIC_GATEWAY', 'https://swarm-gateways.net/bzz:/')
        self.use_mock = False
        self._check_swarm_availability()
    
    def _check_swarm_availability(self):
        """Check if Swarm is available and ready, fallback to mock if not"""
        try:
            import requests
            # Check if Swarm node is accessible
            response = requests.get(f"{self.swarm_gateway}/", timeout=2)
            if response.status_code != 200:
                self.use_mock = True
                logger.warning("Swarm not available, using mock service")
                return
            
            # Check if Swarm node is synced and ready
            stamps_response = requests.get(f"{self.swarm_gateway}/stamps", timeout=2)
            if stamps_response.status_code == 503:
                # Node is syncing
                self.use_mock = True
                logger.warning("Swarm node is syncing, using mock service")
            elif stamps_response.status_code == 200:
                stamps_data = stamps_response.json()
                if not stamps_data.get("stamps") or len(stamps_data.get("stamps", [])) == 0:
                    # No postage batches available
                    self.use_mock = True
                    logger.warning("No postage batches available, using mock service")
            else:
                # Other error
                self.use_mock = True
                logger.warning("Swarm stamps endpoint error, using mock service")
                
        except Exception as e:
            self.use_mock = True
            logger.warning(f"Swarm not available ({e}), using mock service")
    
    def _get_mock_service(self):
        """Get mock service instance"""
        if not hasattr(self, '_mock_service'):
            from app.services.mock_swarm_service import MockSwarmService
            self._mock_service = MockSwarmService()
        return self._mock_service
        
    async def _make_request(self, endpoint: str, method: str = 'POST', data: Dict = None, files: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to Swarm API"""
        try:
            # For Swarm Bee v2.6.0, use the correct API endpoints
            if endpoint == "add":
                url = f"{self.swarm_gateway}/bzz"
            elif endpoint.startswith("get/"):
                url = f"{self.swarm_gateway}/bzz/{endpoint[4:]}"  # Remove "get/" prefix
            else:
                url = f"{self.swarm_gateway}/bzz/{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method == 'POST':
                    if files:
                        # For file uploads
                        form_data = aiohttp.FormData()
                        for key, value in files.items():
                            form_data.add_field(key, value[0], filename=value[1])
                        async with session.post(url, data=form_data) as response:
                            result = await response.text()
                    else:
                        # For JSON data - use raw endpoint for Swarm Bee
                        if endpoint == "add":
                            raw_url = f"{self.swarm_gateway}/bzz/raw"
                            json_data = json.dumps(data) if data else ""
                            async with session.post(raw_url, data=json_data, headers={'Content-Type': 'application/json'}) as response:
                                result = await response.text()
                        else:
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
            logger.error(f"Swarm request error: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_data(self, data: Dict[str, Any], filename: str = "product_data.json") -> Dict[str, Any]:
        """
        Add product data to Swarm
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
            
            # For Swarm Bee v2.6.0, we need to check if postage batches are available
            # First, let's check if the node is synced and has postage batches
            import aiohttp
            
            # Check stamps endpoint
            stamps_url = f"{self.swarm_gateway}/stamps"
            async with aiohttp.ClientSession() as session:
                async with session.get(stamps_url) as response:
                    if response.status == 503:
                        stamps_data = await response.json()
                        if "syncing in progress" in stamps_data.get("message", ""):
                            return {"success": False, "error": "Swarm node is still syncing. Please wait for sync to complete before uploading data."}
                    
                    # Try to get available stamps
                    if response.status == 200:
                        stamps = await response.json()
                        if not stamps.get("stamps") or len(stamps.get("stamps", [])) == 0:
                            return {"success": False, "error": "No postage batches available. Please create a postage batch first."}
                        
                        # Use the first available stamp
                        stamp_id = stamps["stamps"][0]["batchID"]
                        
                        # Upload data with postage batch
                        upload_url = f"{self.swarm_gateway}/bzz"
                        headers = {
                            'Content-Type': 'application/json',
                            'Swarm-Postage-Batch-Id': stamp_id
                        }
                        
                        async with session.post(upload_url, data=json_data, headers=headers) as upload_response:
                            if upload_response.status == 200:
                                swarm_hash = await upload_response.text()
                                swarm_hash = swarm_hash.strip()
                                
                                # Pin the data to ensure it's not garbage collected
                                await self.pin_data(swarm_hash)
                                
                                return {
                                    "success": True,
                                    "hash": swarm_hash,
                                    "size": len(json_data),
                                    "name": filename,
                                    "public_url": self.get_public_url(swarm_hash)
                                }
                            else:
                                error_text = await upload_response.text()
                                return {"success": False, "error": f"HTTP {upload_response.status}: {error_text}"}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"Failed to check stamps: HTTP {response.status}: {error_text}"}
                
        except Exception as e:
            logger.error(f"Error adding data to Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from Swarm
        Returns: Dict with 'success' and 'data' or 'error'
        """
        try:
            # For Swarm Bee v2.6.0, use the correct endpoint
            import aiohttp
            url = f"{self.swarm_gateway}/bzz/{swarm_hash}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data_text = await response.text()
                        try:
                            data = json.loads(data_text)
                            return {"success": True, "data": data}
                        except json.JSONDecodeError:
                            return {"success": True, "data": data_text}  # Return raw data if not JSON
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                
        except Exception as e:
            logger.error(f"Error getting data from Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def pin_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Pin data to Swarm to ensure it's not garbage collected
        """
        try:
            # For Swarm Bee v2.6.0, use the correct pinning endpoint
            import aiohttp
            url = f"{self.swarm_gateway}/pins/{swarm_hash}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    if response.status == 200:
                        return {"success": True, "message": "Data pinned successfully"}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"Error pinning data to Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def unpin_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Unpin data from Swarm
        """
        try:
            result = await self._make_request(f'unpin/{swarm_hash}', method='POST')
            return result
        except Exception as e:
            logger.error(f"Error unpinning data from Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    def get_public_url(self, swarm_hash: str) -> str:
        """
        Get public URL for accessing Swarm data
        """
        return f"{self.public_gateway}{swarm_hash}"
    
    async def store_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store complete product data in Swarm
        """
        if self.use_mock:
            mock_service = self._get_mock_service()
            return await mock_service.store_product_data(product_data)
        
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
                # Pin the data to ensure persistence
                pin_result = await self.pin_data(result["hash"])
                if not pin_result["success"]:
                    logger.warning(f"Failed to pin data: {pin_result.get('error')}")
                
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
            logger.error(f"Error storing product data in Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def retrieve_product_data(self, swarm_hash: str) -> Dict[str, Any]:
        """
        Retrieve product data from Swarm
        """
        if self.use_mock:
            mock_service = self._get_mock_service()
            return await mock_service.retrieve_product_data(swarm_hash)
        
        try:
            result = await self.get_data(swarm_hash)
            
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
            logger.error(f"Error retrieving product data from Swarm: {e}")
            return {"success": False, "error": str(e)}
    
    async def is_connected(self) -> bool:
        """
        Check if Swarm node is accessible
        """
        try:
            import aiohttp
            url = f"{self.swarm_gateway}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return response.status == 200
        except:
            return False
    
    async def get_node_info(self) -> Dict[str, Any]:
        """
        Get Swarm node information
        """
        try:
            import aiohttp
            url = f"{self.swarm_gateway}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return {"success": True, "node_info": health_data}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current Swarm service status
        """
        return {
            "use_mock": self.use_mock,
            "swarm_gateway": self.swarm_gateway,
            "public_gateway": self.public_gateway,
            "status": "mock" if self.use_mock else "real"
        }
