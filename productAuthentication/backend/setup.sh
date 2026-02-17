#!/bin/bash

# Anti-Counterfeit Blockchain Application Setup Script
# This script helps you set up the complete application

set -e

echo "Setting up Anti-Counterfeit Blockchain Application"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Checkin if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    #  Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    #  npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    #  Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    #  pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
    
    # PostgreSQL
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL is not installed. You'll need to install it manually."
        print_warning "Visit: https://www.postgresql.org/download/"
    fi
    
    #  Redis
    if ! command -v redis-server &> /dev/null; then
        print_warning "Redis is not installed. You'll need to install it manually."
        print_warning "Visit: https://redis.io/download"
    fi
    
    print_success "System requirements check completed"
}

# Smart Contracts
setup_smart_contracts() {
    print_status "Setting up smart contracts..."
    
    cd smart-contracts
    
    print_status "Installing smart contract dependencies..."
    npm install
    
    print_status "Compiling smart contracts..."
    npx hardhat compile
    
    print_success "Smart contracts setup completed"
    cd ..
}

# Backend
setup_backend() {
    print_status "Setting up Python backend..."
    
    cd backend
    
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit backend/.env with your configuration"
    fi
    
    print_success "Backend setup completed"
    cd ..
}
# Database
setup_database() {
    print_status "Setting up database..."
    
    print_warning "Please ensure PostgreSQL is running and create a database named 'anticounterfeit'"
    print_warning "You can do this by running:"
    print_warning "  createdb anticounterfeit"
    
    read -p "Press Enter when you have created the database..."
    
    print_success "Database setup instructions provided"
}

# Main setup function
main() {
    echo "Starting setup process..."
    
    # requirements
    check_requirements
    
    # smart contracts
    setup_smart_contracts
    
    # backend
    setup_backend
    
    # database
    setup_database
    
    # documentation
    generate_docs
    
    echo ""
    echo "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure your environment variables:"
    echo "   - Edit backend/.env"
    echo "   - Edit frontend/.env.local"
    echo ""
    echo "2. Start the services:"
    echo "   - Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "   - Frontend: cd frontend && npm run dev"
    echo "   - Blockchain: cd smart-contracts && npx hardhat node"
    echo ""
    echo "3. Deploy smart contracts:"
    echo "   - cd smart-contracts && npx hardhat run scripts/deploy.js --network localhost"
    echo ""
    echo "4. Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "For more information, check the README.md file."
}

# Run main function
main "$@"
