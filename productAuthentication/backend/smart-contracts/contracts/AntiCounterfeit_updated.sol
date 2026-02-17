// AntiCounterfeit.sol updated to make verification free.

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AntiCounterfeit
 * @dev Smart contract for managing anti-counterfeit product registration and verification
 */
contract AntiCounterfeit is AccessControl, ReentrancyGuard {
    using Counters for Counters.Counter;

    // Role definitions
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    bytes32 public constant RETAILER_ROLE = keccak256("RETAILER_ROLE");
    bytes32 public constant DISTRIBUTOR_ROLE = keccak256("DISTRIBUTOR_ROLE");
    bytes32 public constant CONSUMER_ROLE = keccak256("CONSUMER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    // Product structure
    struct Product {
        uint256 productId;
        string productName;
        string productDescription;
        uint256 manufacturingDate;
        string batchNumber;
        address manufacturer;
        string category;
        bool isActive;
        uint256 registrationDate;
        string qrCodeHash;
    }

    // Verification record structure
    struct VerificationRecord {
        uint256 productId;
        address verifier;
        uint256 timestamp;
        string location;
        bool isAuthentic;
        string notes;
    }

    // Location update structure
    struct LocationUpdate {
        uint256 productId;
        address updater;
        uint256 timestamp;
        string location;
        string notes;
    }

    // State variables
    Counters.Counter private _productIds;
    Counters.Counter private _verificationIds;
    Counters.Counter private _locationUpdateIds;

    mapping(uint256 => Product) public products;
    mapping(uint256 => VerificationRecord) public verifications;
    mapping(uint256 => LocationUpdate[]) public locationHistory;
    mapping(string => uint256) public qrCodeToProductId;
    mapping(address => uint256[]) public manufacturerProducts;

    // Events
    event ProductRegistered(
        uint256 indexed productId,
        string productName,
        address indexed manufacturer,
        string qrCodeHash,
        uint256 timestamp
    );

    event LocationUpdated(
        uint256 indexed productId,
        address indexed updater,
        string location,
        uint256 timestamp
    );

    event ProductDeactivated(
        uint256 indexed productId,
        address indexed deactivator,
        uint256 timestamp
    );

    event RoleGranted(
        address indexed account,
        bytes32 indexed role,
        address indexed granter
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Register a new product
     * @param productName Name of the product
     * @param productDescription Description of the product
     * @param manufacturingDate Manufacturing date (Unix timestamp)
     * @param batchNumber Batch or lot number
     * @param category Product category
     * @param qrCodeHash Hash of the QR code
     */
    function registerProduct(
        string memory productName,
        string memory productDescription,
        uint256 manufacturingDate,
        string memory batchNumber,
        string memory category,
        string memory qrCodeHash
    ) external nonReentrant returns (uint256) {
        require(bytes(productName).length > 0, "Product name cannot be empty");
        require(bytes(qrCodeHash).length > 0, "QR code hash cannot be empty");
        require(qrCodeToProductId[qrCodeHash] == 0, "QR code already exists");

        _productIds.increment();
        uint256 newProductId = _productIds.current();

        Product memory newProduct = Product({
            productId: newProductId,
            productName: productName,
            productDescription: productDescription,
            manufacturingDate: manufacturingDate,
            batchNumber: batchNumber,
            manufacturer: msg.sender,
            category: category,
            isActive: true,
            registrationDate: block.timestamp,
            qrCodeHash: qrCodeHash
        });

        products[newProductId] = newProduct;
        qrCodeToProductId[qrCodeHash] = newProductId;
        manufacturerProducts[msg.sender].push(newProductId);

        emit ProductRegistered(
            newProductId,
            productName,
            msg.sender,
            qrCodeHash,
            block.timestamp
        );

        return newProductId;
    }

    /**
     * @dev Verify a product's authenticity with enhanced counterfeit detection
     * @param productId ID of the product to verify
     * @param location Location where verification is performed
     * @param qrCodeHash QR code hash for validation
     */
    function verifyProduct(
        uint256 productId,
        string memory location,
        string memory qrCodeHash
    ) external nonReentrant returns (bool) {
        require(products[productId].isActive, "Product does not exist or is inactive");
        require(bytes(location).length > 0, "Location cannot be empty");
        return performCounterfeitDetection(productId, qrCodeHash);
    }

    /**
     * @dev Perform comprehensive counterfeit detection
     * @param productId ID of the product to check
     * @param qrCodeHash QR code hash for validation
     * @return bool True if product is authentic, false if counterfeit
     */
    function performCounterfeitDetection(
        uint256 productId,
        string memory qrCodeHash
    ) internal view returns (bool) {
        Product memory product = products[productId];
        
        // 1. QR Code Hash Validation
        if (keccak256(abi.encodePacked(product.qrCodeHash)) != keccak256(abi.encodePacked(qrCodeHash))) {
            return false; // QR code mismatch indicates counterfeit
        }
        
        // 2. Check if QR code is already registered to another product
        uint256 existingProductId = qrCodeToProductId[qrCodeHash];
        if (existingProductId != 0 && existingProductId != productId) {
            return false; // QR code already used by another product
        }
        
        // 3. Verify product is registered by a legitimate manufacturer
        if (!hasRole(MANUFACTURER_ROLE, product.manufacturer)) {
            return false; // Product not registered by authorized manufacturer
        }
        
        // 4. Validate manufacturing date is reasonable
        if (product.manufacturingDate > block.timestamp) {
            return false; // Future manufacturing date is impossible
        }
        
        // 5. Check if product was registered too recently (potential fake)
        if (block.timestamp - product.registrationDate < 3600) { // Less than 1 hour
            // This could indicate a hastily created fake product
            // But don't immediately reject, just flag for review
        }
        
        return true; // Product passes all checks
    }

    /**
     * @dev Update product location
     * @param productId ID of the product
     * @param location New location
     * @param notes Additional notes about the location update
     */
    function updateProductLocation(
        uint256 productId,
        string memory location,
        string memory notes
    ) external onlyRole(DISTRIBUTOR_ROLE) nonReentrant {
        require(products[productId].isActive, "Product does not exist or is inactive");
        require(bytes(location).length > 0, "Location cannot be empty");

        _locationUpdateIds.increment();

        LocationUpdate memory newLocationUpdate = LocationUpdate({
            productId: productId,
            updater: msg.sender,
            timestamp: block.timestamp,
            location: location,
            notes: notes
        });

        locationHistory[productId].push(newLocationUpdate);

        emit LocationUpdated(
            productId,
            msg.sender,
            location,
            block.timestamp
        );
    }

    /**
     * @dev Get product details
     * @param productId ID of the product
     * @return Product details
     */
    function getProduct(uint256 productId) external view returns (Product memory) {
        require(products[productId].isActive, "Product does not exist or is inactive");
        return products[productId];
    }

    /**
     * @dev Get product by QR code hash
     * @param qrCodeHash Hash of the QR code
     * @return Product details
     */
    function getProductByQRCode(string memory qrCodeHash) external view returns (Product memory) {
        uint256 productId = qrCodeToProductId[qrCodeHash];
        require(productId > 0, "Product not found for this QR code");
        require(products[productId].isActive, "Product is inactive");
        return products[productId];
    }

    /**
     * @dev Get product location history
     * @param productId ID of the product
     * @return Array of location updates
     */
    function getProductLocationHistory(uint256 productId) external view returns (LocationUpdate[] memory) {
        require(products[productId].isActive, "Product does not exist or is inactive");
        return locationHistory[productId];
    }

    /**
     * @dev Get products by manufacturer
     * @param manufacturer Address of the manufacturer
     * @return Array of product IDs
     */

    function getProductsByManufacturer(address manufacturer) external view returns (uint256[] memory) {
        return manufacturerProducts[manufacturer];
    }

    /**
     * @dev Deactivate a product (only manufacturer or admin can do this)
     * @param productId ID of the product to deactivate
     */
    function deactivateProduct(uint256 productId) external {
        require(products[productId].isActive, "Product is already inactive");
        require(
            products[productId].manufacturer == msg.sender || hasRole(ADMIN_ROLE, msg.sender),
            "Only manufacturer or admin can deactivate product"
        );

        products[productId].isActive = false;

        emit ProductDeactivated(
            productId,
            msg.sender,
            block.timestamp
        );
    }

    /**
     * @dev Grant role to an address
     * @param role Role to grant
     * @param account Address to grant role to
     */
    function grantUserRole(bytes32 role, address account) external onlyRole(ADMIN_ROLE) {
        _grantRole(role, account);
        emit RoleGranted(role, account, msg.sender);
    }

    /**
     * @dev Get total number of products
     * @return Total product count
     */
    function getTotalProducts() external view returns (uint256) {
        return _productIds.current();
    }

    /**
     * @dev Get total number of verifications
     * @return Total verification count
     */
    function getTotalVerifications() external view returns (uint256) {
        return _verificationIds.current();
    }

    /**
     * @dev Check if an address has a specific role
     * @param role Role to check
     * @param account Address to check
     * @return True if address has the role
     */
    function hasUserRole(bytes32 role, address account) external view returns (bool) {
        return hasRole(role, account);
    }
}
