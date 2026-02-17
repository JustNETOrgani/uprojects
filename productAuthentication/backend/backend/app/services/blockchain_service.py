from web3 import Web3

try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
from typing import Optional, Dict, Any
import json
import os
from app.core.config import settings


class BlockchainService:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.contract_address = None
        self.contract_abi = None

    async def initialize(self):
        """Initializing Web3 connection and contract."""
        try:
            print(f"DEBUG: Initializing blockchain service...")
            print(f"DEBUG: Settings ETHEREUM_NETWORK: {settings.ETHEREUM_NETWORK}")
            print(f"DEBUG: Settings CONTRACT_ADDRESS: {settings.CONTRACT_ADDRESS}")

            if settings.ETHEREUM_NETWORK == "localhost":
                self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
                # self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            elif settings.ETHEREUM_NETWORK == "sepolia":
                if not settings.INFURA_URL:
                    raise ValueError("INFURA_URL is required for Sepolia network")
                self.w3 = Web3(Web3.HTTPProvider(settings.INFURA_URL))
            else:
                raise ValueError(f"Unsupported network: {settings.ETHEREUM_NETWORK}")

            self.contract_abi = self._load_contract_abi()

            self.contract_address = settings.CONTRACT_ADDRESS
            print(f"DEBUG: Contract address from settings: {self.contract_address}")
            if self.contract_address:
                self.contract = self.w3.eth.contract(
                    address=self.contract_address, abi=self.contract_abi
                )

            print(
                f"Blockchain service initialized for network: {settings.ETHEREUM_NETWORK}"
            )
            print(f"DEBUG: Final contract address: {self.contract_address}")

        except Exception as e:
            print(f"Error initializing blockchain service: {e}")
            raise

    def _load_contract_abi(self) -> list:
        """Loading contract ABI from file."""
        try:
            abi_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "smart-contracts",
                "artifacts",
                "contracts",
                "AntiCounterfeit.sol",
                "AntiCounterfeit.json",
            )

            if os.path.exists(abi_path):
                with open(abi_path, "r") as f:
                    contract_json = json.load(f)
                    return contract_json["abi"]
            else:
                return self._get_basic_abi()

        except Exception as e:
            print(f"Error loading contract ABI: {e}")
            return self._get_basic_abi()

    def _get_basic_abi(self) -> list:
        """ABI structure for development."""
        return [
            {
                "inputs": [],
                "name": "getTotalProducts",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"type": "string", "name": "productName"},
                    {"type": "string", "name": "productDescription"},
                    {"type": "uint256", "name": "manufacturingDate"},
                    {"type": "string", "name": "batchNumber"},
                    {"type": "string", "name": "category"},
                    {"type": "string", "name": "qrCodeHash"},
                ],
                "name": "registerProduct",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [
                    {"type": "uint256", "name": "productId"},
                    {"type": "string", "name": "location"},
                    {"type": "string", "name": "notes"},
                    {"type": "string", "name": "qrCodeHash"},
                ],
                "name": "verifyProduct",
                "outputs": [{"type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [{"type": "uint256", "name": "productId"}],
                "name": "getProduct",
                "outputs": [
                    {
                        "components": [
                            {"type": "uint256", "name": "productId"},
                            {"type": "string", "name": "productName"},
                            {"type": "string", "name": "productDescription"},
                            {"type": "uint256", "name": "manufacturingDate"},
                            {"type": "string", "name": "batchNumber"},
                            {"type": "address", "name": "manufacturer"},
                            {"type": "string", "name": "category"},
                            {"type": "bool", "name": "isActive"},
                            {"type": "uint256", "name": "registrationDate"},
                            {"type": "string", "name": "qrCodeHash"},
                        ],
                        "type": "tuple",
                    }
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [{"type": "string", "name": "qrCodeHash"}],
                "name": "getProductByQRCode",
                "outputs": [
                    {
                        "components": [
                            {"type": "uint256", "name": "productId"},
                            {"type": "string", "name": "productName"},
                            {"type": "string", "name": "productDescription"},
                            {"type": "uint256", "name": "manufacturingDate"},
                            {"type": "string", "name": "batchNumber"},
                            {"type": "address", "name": "manufacturer"},
                            {"type": "string", "name": "category"},
                            {"type": "bool", "name": "isActive"},
                            {"type": "uint256", "name": "registrationDate"},
                            {"type": "string", "name": "qrCodeHash"},
                        ],
                        "type": "tuple",
                    }
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "type": "uint256", "name": "productId"},
                    {"indexed": True, "type": "address", "name": "verifier"},
                    {"indexed": False, "type": "bool", "name": "isAuthentic"},
                    {"indexed": False, "type": "string", "name": "location"},
                    {"indexed": False, "type": "uint256", "name": "timestamp"},
                ],
                "name": "ProductVerified",
                "type": "event",
            },
        ]

    async def register_product(
        self,
        product_name: str,
        product_description: str,
        manufacturing_date: int,
        batch_number: str,
        category: str,
        qr_code_hash: str,
        wallet_address: str,
        private_key: str,
    ) -> Dict[str, Any]:
        """Registering a product on the blockchain."""
        try:
            if not self.contract:
                raise ValueError("Contract not initialized")

            # Preparing transaction
            print(f"wallet address {wallet_address}")
            # Convert to checksum address
            wallet_address = self.w3.to_checksum_address(wallet_address)
            nonce = self.w3.eth.get_transaction_count(wallet_address)
          
            print({'nonce----->': nonce})
            
            # Build transaction
            transaction = self.contract.functions.registerProduct(
                product_name,
                product_description,
                manufacturing_date,
                batch_number,
                category,
                qr_code_hash,
            ).build_transaction(
                {
                    "chainId": self.w3.eth.chain_id,
                    "gas": 500000,  # Increased gas limit for smart contract
                    "gasPrice": self.w3.eth.gas_price,
                    "nonce": nonce,
                }
            )

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

            # Send transaction - Fix: Use raw_transaction (snake_case)
            try:
                # Use the correct attribute name
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            except AttributeError:
                # Fallback to camelCase if snake_case doesn't work
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Extract product ID from the ProductRegistered event
            product_id = None
            if tx_receipt.logs:
                for log in tx_receipt.logs:
                    if log.address == self.contract_address:
                        # The first topic is the event signature, second topic is the product ID
                        if len(log.topics) > 1:
                            product_id = int(log.topics[1].hex(), 16)
                            break

            return {
                "success": True,
                "blockchain_id": product_id,
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
            }

        except Exception as e:
            print(f"BLOCKCHAIN REGISTRATION ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    async def verify_product(
        self,
        product_id: int,
        location: str,
        notes: str,
        wallet_address: str,
        private_key: str,
        qr_code_hash: str = None,
    ) -> Dict[str, Any]:
        """Verify a product on the blockchain with counterfeit detection."""
        try:
            if not self.contract:
                raise ValueError("Contract not initialized")

            # Get product details to validate QR code hash
            product_details = await self.get_product(product_id)
            if not product_details:
                return {"success": False, "error": "Product not found on blockchain"}

            # Use provided QR code hash or get from product details
            if not qr_code_hash:
                qr_code_hash = product_details.get("qrCodeHash", "")

            # Preparing transaction
            # Convert to checksum address
            wallet_address = self.w3.to_checksum_address(wallet_address)
            nonce = self.w3.eth.get_transaction_count(wallet_address)

            # Building transaction with QR code hash for counterfeit detection
            transaction = self.contract.functions.verifyProduct(
                product_id, location, notes, qr_code_hash
            ).build_transaction(
                {
                    "chainId": self.w3.eth.chain_id,
                    "gas": 400000,  # Increased gas limit for verification
                    "gasPrice": self.w3.eth.gas_price,
                    "nonce": nonce,
                }
            )

            # Signing transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

            # Sending transaction
            try:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            except AttributeError:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Waiting for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Extract verification result from transaction receipt
            verification_result = True  # Default to True
            if tx_receipt.logs:
                for log in tx_receipt.logs:
                    if log.address == self.contract_address and len(log.topics) > 3:
                        # Check if this is a ProductVerified event
                        # The isAuthentic value is in the event data
                        try:
                            # Decode the event data to get the isAuthentic value
                            event_data = self.contract.events.ProductVerified().process_log(log)
                            if event_data and len(event_data) > 0:
                                verification_result = event_data[0]['args']['isAuthentic']
                        except Exception as e:
                            print(f"Error decoding verification event: {e}")
                            # If we can't decode, assume success if transaction completed
                            pass

            return {
                "success": True,
                "verification_result": verification_result,
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product details from blockchain."""
        try:
            if not self.contract:
                return None

            product = self.contract.functions.getProduct(product_id).call()

            return {
                "productId": product[0],
                "productName": product[1],
                "productDescription": product[2],
                "manufacturingDate": product[3],
                "batchNumber": product[4],
                "manufacturer": product[5],
                "category": product[6],
                "isActive": product[7],
                "registrationDate": product[8],
                "qrCodeHash": product[9],
            }

        except Exception as e:
            print(f"Error getting product from blockchain: {e}")
            return None

    async def get_product_by_qr_code(
        self, qr_code_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Get product details by QR code hash."""
        try:
            if not self.contract:
                return None

            product = self.contract.functions.getProductByQRCode(qr_code_hash).call()

            return {
                "productId": product[0],
                "productName": product[1],
                "productDescription": product[2],
                "manufacturingDate": product[3],
                "batchNumber": product[4],
                "manufacturer": product[5],
                "category": product[6],
                "isActive": product[7],
                "registrationDate": product[8],
                "qrCodeHash": product[9],
            }

        except Exception as e:
            print(f"Error getting product by QR code from blockchain: {e}")
            return None

    async def _ensure_initialized(self):
        """Ensuring the service is initialized before use."""
        if not hasattr(self, "w3") or not self.w3:
            await self.initialize()

    async def get_network_info(self) -> Dict[str, Any]:
        """Getting blockchain network information."""
        try:
            await self._ensure_initialized()
            return {
                "network": settings.ETHEREUM_NETWORK,
                "connected": await self.is_connected(),
                "chain_id": self.w3.eth.chain_id if self.w3 else None,
                "latest_block": self.w3.eth.block_number if self.w3 else None,
                "contract_address": self.contract_address,
            }
        except Exception as e:
            return {
                "network": settings.ETHEREUM_NETWORK,
                "connected": False,
                "error": str(e),
            }

    async def get_total_products(self) -> int:
        """Getting total number of products on blockchain."""
        try:
            await self._ensure_initialized()
            if not self.contract:
                return 0

            return self.contract.functions.getTotalProducts().call()

        except Exception as e:
            print(f"Error getting total products from blockchain: {e}")
            return 0

    async def is_connected(self) -> bool:
        """Checking  if its connected to blockchain network."""
        try:
            await self._ensure_initialized()
            return self.w3.is_connected()
        except:
            return False