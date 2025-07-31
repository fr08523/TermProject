#!/bin/bash

# Sports Management System - Backend Start Script
# This script sets up and runs the Flask backend server

echo "🏈 Sports Management System - Backend Setup"
echo "==========================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Create instance directory if it doesn't exist
mkdir -p instance

# Check if database exists, if not initialize it
if [ ! -f "instance/sports_management.db" ]; then
    echo "🗄️ Initializing database with sample data..."
    python init_db.py
else
    echo "✅ Database already exists"
fi

# Start the Flask development server
echo "🚀 Starting Flask backend server..."
echo "📍 Backend will be available at: http://127.0.0.1:5000"
echo "🔗 API endpoints:"
echo "   - Auth: http://127.0.0.1:5000/auth"
echo "   - API: http://127.0.0.1:5000/api"  
echo "   - Analytics: http://127.0.0.1:5000/analytics"
echo ""
echo "👤 Default login credentials:"
echo "   Username: admin"
echo "   Password: password123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==========================================="

python run.py