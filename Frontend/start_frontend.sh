#!/bin/bash

# Sports Management System - Frontend Start Script  
# This script sets up and runs the React frontend

echo "⚛️ Sports Management System - Frontend Setup"
echo "============================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Node.js version: $(node --version)"
echo "📦 npm version: $(npm --version)"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing React dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Create .env file for frontend if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating frontend environment configuration..."
    echo "REACT_APP_API_URL=http://127.0.0.1:5000" > .env
fi

# Start the React development server
echo "🚀 Starting React frontend server..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo "🔗 Make sure backend is running at: http://127.0.0.1:5000"
echo ""
echo "👤 Default login credentials:"
echo "   Username: admin"
echo "   Password: password123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"

npm start