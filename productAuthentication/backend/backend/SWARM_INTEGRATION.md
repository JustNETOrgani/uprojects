# Ethereum Swarm Integration for Anti-Counterfeit System

This document describes the Ethereum Swarm integration for decentralized product data storage in the anti-counterfeit system.

## Overview

The system now uses **Ethereum Swarm** for decentralized storage of product data, providing:
- **Decentralized Storage**: Product data is stored across the Swarm network
- **Ethereum Integration**: Native integration with Ethereum ecosystem
- **Data Integrity**: Content-addressed storage ensures data authenticity
- **Resilience**: Data remains available even if individual nodes go offline
- **Transparency**: Public access to product data via Swarm hashes

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Swarm Node    │    │   Blockchain    │
│                 │    │                 │    │                 │
│ 1. Create       │───▶│ 2. Store Data   │    │ 3. Register     │
│    Product      │    │    in Swarm     │    │    Hash         │
│                 │    │                 │    │                 │
│ 4. Retrieve     │◀───│ 5. Serve Data   │    │ 6. Verify       │
│    from Swarm   │    │    from Swarm   │    │    Authenticity │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Setup Instructions

### Option 1: Full Swarm Setup (Recommended for Production)

#### 1. Install Go (Required for Swarm)
```bash
# macOS
brew install go

# Linux
sudo apt-get install golang-go
```

#### 2. Install Swarm
```bash
go install github.com/ethersphere/swarm@latest
```

#### 3. Start Swarm Daemon
```bash
swarm --httpaddr 127.0.0.1:8500
```

#### 4. Run Setup Script
```bash
cd backend
python setup_swarm.py
```

### Option 2: Development Mode (Mock Swarm)

The system automatically falls back to a **Mock Swarm Service** when the real Swarm is not available. This allows you to:

- ✅ **Develop and test** without setting up Swarm
- ✅ **Use all features** with simulated Swarm behavior
- ✅ **Generate realistic Swarm hashes** (0x format)
- ✅ **Test the complete workflow** end-to-end

**No additional setup required** - the mock service is automatically used when Swarm is not running.

### 5. Run Database Migration
```bash
python migration_add_swarm_columns.py
```

### 6. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 7. Start Your Application
```bash
uvicorn app.main:app --reload
```

The system will automatically detect whether Swarm is available and use the appropriate service (real Swarm or mock).

## Configuration

Update your `.env` file or environment variables:

```env
# Swarm Configuration
SWARM_GATEWAY=http://127.0.0.1:8500
SWARM_PUBLIC_GATEWAY=https://swarm-gateways.net/bzz:/
```

## API Endpoints

### Product Creation with Swarm Storage

**POST** `/api/v1/products/`

Creates a new product and stores data in Swarm:

```json
{
  "product_name": "Sample Product",
  "product_description": "A sample product for testing",
  "manufacturing_date": "2024-01-01T00:00:00Z",
  "batch_number": "BATCH001",
  "category": "electronics"
}
```

Response includes Swarm hash and URL:
```json
{
  "id": 1,
  "product_name": "Sample Product",
  "swarm_hash": "0x1234567890abcdef1234567890abcdef12345678",
  "swarm_url": "https://swarm-gateways.net/bzz:/0x1234567890abcdef1234567890abcdef12345678",
  "blockchain_id": 1,
  "qr_code_hash": "abc123...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Retrieve Product Data from Swarm

**GET** `/api/v1/products/{product_id}/swarm-data`

Retrieves complete product data from Swarm:

```json
{
  "product_id": 1,
  "swarm_hash": "0x1234567890abcdef1234567890abcdef12345678",
  "swarm_url": "https://swarm-gateways.net/bzz:/0x1234567890abcdef1234567890abcdef12345678",
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

The system includes an advanced counterfeit detection algorithm with multiple validation layers:

### Detection Layers

1. **QR Code Validation**
   - Format validation (SHA-256 hash)
   - Duplicate detection across products
   - Hash matching verification

2. **Swarm Data Integrity**
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
    "Swarm data integrity verified",
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
    "swarm_valid": true,
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
ALTER TABLE products ADD COLUMN swarm_hash VARCHAR UNIQUE;
ALTER TABLE products ADD COLUMN swarm_url VARCHAR;
CREATE INDEX idx_products_swarm_hash ON products(swarm_hash);
```

## Security Considerations

1. **Data Privacy**: Product data stored in Swarm is publicly accessible
2. **Content Addressing**: Swarm hashes ensure data integrity
3. **Pinning**: Important data should be pinned to prevent garbage collection
4. **Access Control**: API endpoints still require authentication
5. **Ethereum Integration**: Native blockchain integration for enhanced security

## Monitoring and Maintenance

### Swarm Node Health
```bash
# Check node status
swarm --version

# Check connected peers
curl http://localhost:8500/

# Check repository size
curl http://localhost:8500/bzz
```

### Data Pinning
```bash
# Pin important data
curl -X POST http://localhost:8500/bzz/pin/0x<swarm_hash>

# List pinned data
curl http://localhost:8500/bzz/pin

# Unpin data
curl -X POST http://localhost:8500/bzz/unpin/0x<swarm_hash>
```

## Troubleshooting

### Common Issues

1. **Swarm Daemon Not Starting**
   ```bash
   # Check if port 8500 is available
   lsof -i :8500
   
   # Kill existing processes
   pkill swarm
   
   # Restart daemon
   swarm --httpaddr 127.0.0.1:8500
   ```

2. **Connection Timeout**
   - Check SWARM_GATEWAY configuration
   - Verify daemon is running
   - Check firewall settings

3. **Data Not Found**
   - Verify Swarm hash is correct
   - Check if data is pinned
   - Ensure Swarm node is connected to network

### Logs and Debugging

Enable debug logging in your application:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

1. **Local Swarm Node**: Run Swarm node locally for better performance
2. **Pinning Strategy**: Pin frequently accessed data
3. **Caching**: Implement caching for frequently retrieved data
4. **Load Balancing**: Use multiple Swarm gateways for redundancy

## Future Enhancements

1. **Swarm Cluster**: Implement Swarm cluster for high availability
2. **Encryption**: Add client-side encryption for sensitive data
3. **Compression**: Implement data compression for storage efficiency
4. **CDN Integration**: Use Swarm-compatible CDNs for faster access

## Support

For issues related to Swarm integration:
1. Check Swarm node status
2. Verify network connectivity
3. Review application logs
4. Consult Swarm documentation: https://docs.ethswarm.org/

## Key Differences from IPFS

| Feature | IPFS | Swarm |
|---------|------|-------|
| Hash Format | `Qm...` | `0x...` |
| Gateway | `ipfs.io` | `swarm-gateways.net` |
| Ethereum Integration | Limited | Native |
| API Endpoint | `/api/v0/` | `/bzz/` |
| Content Addressing | DAG-based | Chunk-based |
| Network | Global IPFS | Ethereum Swarm |
