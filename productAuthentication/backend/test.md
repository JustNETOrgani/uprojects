
## Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL
- MetaMask browser extension
- hardhat (for local blockchain development)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Smart Contract Setup
```bash
cd smart-contracts
npm install
npx hardhat compile
npx hardhat test
npx hardhat node
```

## Configuration

1. **Environment Variables**: Copy `.env.example` to `.env` and configure:
   - Database connection
   - Blockchain network settings
   - API keys
   - JWT secrets

2. **MetaMask Configuration**: Connect to local Ganache network or testnet

3. **Database Setup**: Run migrations to create necessary tables

## Usage

### For Manufacturers
1. Connect MetaMask wallet
2. Register products through the manufacturer dashboard
3. Generate QR codes for each product
4. Track product verification status

### For Consumers/Retailers
1. Scan QR codes using the mobile-responsive scanner
2. View real-time verification results
3. Access complete product information
4. Report counterfeit products

### For Administrators
1. Manage user roles and permissions
2. Monitor system performance
3. View analytics and counterfeit alerts
4. Manage blockchain network status

## Security Features

- Data encryption for sensitive information
- Input validation and sanitization
- Rate limiting to prevent abuse
- Role-based access control
- Secure blockchain transactions
- HTTPS communication








