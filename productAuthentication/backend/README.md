# Barcode-Based Blockchain Anti-Counterfeit Application

A comprehensive web-based application that combines blockchain technology with barcode/QR code scanning to identify and prevent counterfeit products. The system leverages Ethereum blockchain for immutable product records and provides real-time verification capabilities.

###  Project Structure
```
root/
├── README.md                    # Complete documentation
├── setup.sh                     # Automated setup script
├── smart-contracts/             # Ethereum smart contracts
│   ├── contracts/              
│   │   └── AntiCounterfeit.sol # Main smart contract
│   ├── scripts/
│   │   └── deploy.js           # Deployment script
│   ├── test/
│   │   └── AntiCounterfeit.test.js  # Test suite
│   └── package.json            # Dependencies
├── backend/                    # Python FastAPI backend
│   ├── app/                    # Application code
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── api/               # API routes and endpoints
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── products.py
│   │   │       │   ├── users.py
│   │   │       │   └── verifications.py
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/            # Database models
│   │   │   ├── product.py
│   │   │   ├── user.py
│   │   │   └── verification.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── product.py
│   │   │   ├── user.py
│   │   │   └── verification.py
│   │   └── services/          # Business logic
│   │       ├── blockchain_service.py
│   │       └── qr_service.py
│   ├── static/                # Static files
│   │   └── qr_codes/         # Generated QR codes
│   ├── uploads/              # File uploads
│   ├── .env                  # Environment variables
│   ├── .env.example         # Example environment template
│   ├── requirements.txt     # Python dependencies
│   └── anticounterfeit.db  # SQLite database
```

### Technical Stack
- **Blockchain**: Ethereum (Solidity), Hardhat, Web3.js
- **Backend**: Python FastAPI, SQLAlchemy, SQLite (development)
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Authentication**: JWT tokens with role-based access
- **QR Codes**: react-qr-code, qr-scanner
- **Database**: SQLite for development (easily switchable to PostgreSQL)


## Next Steps to Run the Application

### 1. Start the Blockchain Network
```bash
cd smart-contracts
npx hardhat node
```
This will start a local Ethereum network on `http://127.0.0.1:8545`
// npx hardhat run scripts/deploy.js --network localhost

### 2. Deploy Smart Contracts
In a new terminal:
```bash
cd smart-contracts
npx hardhat run scripts/deploy.js --network localhost
```
Copy the deployed contract address and update it in `backend/.env`

### 3. Start the Backend Server
In a new terminal:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### 4. Start the Frontend
In a new terminal:
```bash
cd frontend
npm run dev
```
The application will be available at `http://localhost:3000`

##  Application Features

###  Authentication System
- User registration and login
- JWT token-based authentication
- Role-based access control (Admin, Manufacturer, Retailer, Distributor, Consumer)

###  Product Management
- Product registration with QR code generation
- Product verification and tracking
- Supply chain location updates
- Product history and analytics

###  Blockchain Integration
- Immutable product records on Ethereum
- Smart contract-based verification
- Real-time blockchain status monitoring
- Gas fee optimization

###  QR Code System
- Automatic QR code generation for products
- Mobile-responsive QR code scanning
- Real-time verification against blockchain
- QR code validation and security

### Dashboard & Analytics
- Real-time statistics and metrics
- Product verification history
- Blockchain network status
- User activity monitoring

##  Configuration Files

### Backend Configuration (`backend/.env`)
```env
DATABASE_URL=sqlite:///./anticounterfeit.db
SECRET_KEY=your-secret-key-here-change-in-production
ETHEREUM_NETWORK=localhost
CONTRACT_ADDRESS=your-deployed-contract-address
```

##  Testing the Application

### 1. Create a Test User
- Visit `http://localhost:3000/login`
- Click "Create a new account"
- Register with your email and password

### 2. Register a Product (Manufacturer Role)
- Login to the application
- Navigate to Products section
- Click "Register New Product"
- Fill in product details
- Generate QR code

### 3. Verify a Product
- Use the QR scanner in the app
- Scan the generated QR code
- View verification results

### 4. Check Blockchain Status
- Monitor blockchain connection in the top bar
- View transaction history
- Check network status

##  Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Different permissions for different user types
- **Input Validation**: Comprehensive validation for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **CORS Configuration**: Proper cross-origin resource sharing
- **Environment Variables**: Secure configuration management

## Production Deployment

### For Production Use:
1. **Database**: Switch to PostgreSQL
2. **Blockchain**: Deploy to Ethereum mainnet or testnet
3. **Environment**: Update all environment variables
4. **Security**: Change default secret keys
5. **SSL**: Enable HTTPS
6. **Monitoring**: Add logging and monitoring

### Recommended Cloud Services:
- **Frontend**: Vercel, Netlify, or AWS S3
- **Backend**: AWS EC2, Google Cloud Run, or Heroku
- **Database**: AWS RDS, Google Cloud SQL, or managed PostgreSQL
- **Blockchain**: Infura, Alchemy, or your own Ethereum node


### Common Issues:
1. **Port Already in Use**: Change ports in the startup commands
2. **Database Connection**: Check DATABASE_URL in backend/.env
3. **Blockchain Connection**: Ensure Hardhat node is running
4. **Frontend Build Errors**: Run `npm install` in frontend directory
5. **Backend Import Errors**: Activate virtual environment and check dependencies

### follww these:
- Check the API documentation at `http://localhost:8000/docs`
- Review the README.md file for detailed information
- Check console logs for error messages
- Ensure all services are running on correct ports 

