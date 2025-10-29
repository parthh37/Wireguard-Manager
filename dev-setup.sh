#!/bin/bash

# Development Setup Script for WireGuard Manager
# This script sets up a local development environment

echo "=================================="
echo "WireGuard Manager - Dev Setup"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate secret key
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    
    # Update .env with generated secret
    sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env 2>/dev/null || \
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    
    echo "✓ .env file created with random SECRET_KEY"
else
    echo ""
    echo ".env file already exists"
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/clients data/profiles data/usage data/audit
mkdir -p backups logs

echo "✓ Data directories created"

# Check if Redis is installed
echo ""
echo "Checking Redis..."
if command -v redis-server &> /dev/null; then
    echo "✓ Redis is installed"
    
    # Check if Redis is running
    if redis-cli ping &> /dev/null; then
        echo "✓ Redis is running"
    else
        echo "⚠ Redis is not running. Start it with: redis-server"
    fi
else
    echo "⚠ Redis is not installed"
    echo "Install Redis:"
    echo "  macOS: brew install redis"
    echo "  Linux: sudo apt install redis-server"
fi

echo ""
echo "=================================="
echo "Development Environment Ready!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start Redis (if not running):"
echo "   redis-server"
echo ""
echo "2. Review and update .env file:"
echo "   nano .env"
echo ""
echo "3. Run the development server:"
echo "   python3 app.py"
echo ""
echo "4. Access the application:"
echo "   http://127.0.0.1:5000"
echo ""
echo "Note: WireGuard features will not work without WireGuard installed"
echo "      and proper sudo permissions configured."
echo ""
echo "For production deployment, see DEPLOYMENT.md"
echo ""
