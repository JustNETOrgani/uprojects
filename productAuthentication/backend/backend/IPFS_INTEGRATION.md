# IPFS Integration for Anti-Counterfeit System

This document describes the IPFS (InterPlanetary File System) integration for decentralized product data storage in the anti-counterfeit system.

## Overview

The system now uses IPFS for decentralized storage of product data, providing:
- **Decentralized Storage**: Product data is stored across the IPFS network
- **Data Integrity**: Content-addressed storage ensures data authenticity
- **Resilience**: Data remains available even if individual nodes go offline
- **Transparency**: Public access to product data via IPFS hashes

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   IPFS Node     │    │   Blockchain    │
│                 │    │                 │    │                 │
│ 1. Create       │───▶│ 2. Store Data   │    │ 3. Register     │
│    Product      │    │    in IPFS      │    │    Hash         │
│                 │    │                 │    │                 │
│ 4. Retrieve     │◀───│ 5. Serve Data   │    │ 6. Verify       │
│    from IPFS    │    │    from IPFS    │    │    Authenticity │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Setup Instructions

### 1. Install IPFS

#### macOS (with Homebrew)
```bash
brew install ipfs
```

#### Linux
```bash
wget https://dist.ipfs.io/go-ipfs/v0.17.0/go-ipfs_v0.17.0_linux-amd64.tar.gz
tar -xzf go-ipfs_v0.17.0_linux-amd64.tar.gz
sudo mv go-ipfs/ipfs /usr/local/bin/
```

#### Windows
Download from: https://dist.ipfs.io/#go-ipfs

### 2. Initialize IPFS
```bash
ipfs init
```

### 3. Start IPFS Daemon
```bash
ipfs daemon
```

### 4. Run Setup Script (Optional)
```bash
cd backend
python setup_ipfs.py
```

**Note**: If IPFS is not available or not running, the system will automatically fall back to a mock IPFS service that simulates IPFS behavior for development and testing purposes.

### 5. Run Database Migration
```bash
python migration_add_ipfs_columns.py
```

### 6. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

Update your `.env` file or environment variables:

```env
# IPFS Configuration
IPFS_GATEWAY=http://127.0.0.1:5001
IPFS_PUBLIC_GATEWAY=https://ipfs.io/ipfs/

# Legacy Swarm Configuration (for backward compatibility)
SWARM_GATEWAY=http://localhost:1633
SWARM_PUBLIC_GATEWAY=https://swarm-gateways.net/bzz:/
```

## API Endpoints

### Product Creation with IPFS Storage

**POST** `/api/v1/products/`

Creates a new product and stores data in IPFS:

```json
{
  "product_name": "Sample Product",
  "product_description": "A sample product for testing",
  "manufacturing_date": "2024-01-01T00:00:00Z",
  "batch_number": "BATCH001",
  "category": "electronics"
}
```

Response includes IPFS hash and URL:
```json
{
  "id": 1,
  "product_name": "Sample Product",
  "ipfs_hash": "QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx",
  "ipfs_url": "https://ipfs.io/ipfs/QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx",
  "blockchain_id": 1,
  "qr_code_hash": "abc123...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Retrieve Product Data from IPFS

**GET** `/api/v1/products/{product_id}/ipfs-data`

Retrieves complete product data from IPFS:

```json
{
  "product_id": 1,
  "ipfs_hash": "QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx",
  "ipfs_url": "https://ipfs.io/ipfs/QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx",
  "product_data": {
    "id": 1,
    "product_name": "Sample Product",
    "product_description": "A sample product for testing",
    "manufacturing_date": "2024-01-01T00:00:00Z",
    "batch_number": "BATCH001",
    "category": "electronics",
    "qr_code_hash": "abc123...",
    "manufacturer_id": 1,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "metadata": {
    "version": "1.0",
    "timestamp": "2024-01-01T00:00:00Z",
    "type": "product"
  },
  "retrieved_at": "2024-01-01T00:00:00Z"
}
```

## Enhanced Counterfeit Detection

The system now includes an advanced counterfeit detection algorithm with multiple validation layers:

### Detection Layers

1. **QR Code Validation**
   - Format validation (SHA-256 hash)
   - Duplicate detection across products
   - Hash matching verification

2. **IPFS Data Integrity**
   - Data retrieval verification
   - Content consistency checks
   - Metadata validation

3. **Blockchain Verification**
   - Registration status check
   - Transaction history validation

4. **Duplicate Detection**
   - Batch number uniqueness
   - Manufacturer verification

5. **Pattern Analysis**
   - Verification frequency analysis
   - Suspicious activity detection

6. **Manufacturer Validation**
   - Account status verification
   - Credential validation

7. **Data Consistency**
   - Cross-source validation
   - Temporal consistency checks

### Detection Results

```json
{
  "is_authentic": true,
  "detection_reasons": [
    "QR code hash format is valid",
    "QR code is unique - no duplicates found",
    "IPFS data integrity verified",
    "Product registered on blockchain",
    "No duplicate products found with same batch number",
    "Normal verification pattern: 2 in 30 days",
    "Manufacturer account is valid and verified",
    "Product information is complete",
    "Manufacturing date is reasonable"
  ],
  "confidence_score": 0.95,
  "risk_level": "low",
  "risk_factors": [],
  "validation_summary": {
    "qr_valid": true,
    "ipfs_valid": true,
    "blockchain_valid": true,
    "no_duplicates": true,
    "normal_pattern": true,
    "manufacturer_valid": true,
    "data_consistent": true
  }
}
```

## Database Schema Changes

New columns added to the `products` table:

```sql
ALTER TABLE products ADD COLUMN ipfs_hash VARCHAR UNIQUE;
ALTER TABLE products ADD COLUMN ipfs_url VARCHAR;
CREATE INDEX idx_products_ipfs_hash ON products(ipfs_hash);
```

## Security Considerations

1. **Data Privacy**: Product data stored in IPFS is publicly accessible
2. **Content Addressing**: IPFS hashes ensure data integrity
3. **Pinning**: Important data should be pinned to prevent garbage collection
4. **Access Control**: API endpoints still require authentication

## Monitoring and Maintenance

### IPFS Node Health
```bash
# Check node status
ipfs id

# Check connected peers
ipfs swarm peers

# Check repository size
ipfs repo stat
```

### Data Pinning
```bash
# Pin important data
ipfs pin add <ipfs_hash>

# List pinned data
ipfs pin ls

# Unpin data
ipfs pin rm <ipfs_hash>
```

## Troubleshooting

### Common Issues

1. **IPFS Daemon Not Starting**
   ```bash
   # Check if port 5001 is available
   lsof -i :5001
   
   # Kill existing processes
   pkill ipfs
   
   # Restart daemon
   ipfs daemon
   ```

2. **Connection Timeout**
   - Check IPFS_GATEWAY configuration
   - Verify daemon is running
   - Check firewall settings

3. **Data Not Found**
   - Verify IPFS hash is correct
   - Check if data is pinned
   - Ensure IPFS node is connected to network

### Logs and Debugging

Enable debug logging in your application:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

1. **Local IPFS Node**: Run IPFS node locally for better performance
2. **Pinning Strategy**: Pin frequently accessed data
3. **Caching**: Implement caching for frequently retrieved data
4. **Load Balancing**: Use multiple IPFS gateways for redundancy

## Future Enhancements

1. **IPFS Cluster**: Implement IPFS cluster for high availability
2. **Encryption**: Add client-side encryption for sensitive data
3. **Compression**: Implement data compression for storage efficiency
4. **CDN Integration**: Use IPFS-compatible CDNs for faster access

## Support

For issues related to IPFS integration:
1. Check IPFS node status
2. Verify network connectivity
3. Review application logs
4. Consult IPFS documentation: https://docs.ipfs.io/
