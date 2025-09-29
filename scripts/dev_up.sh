#!/bin/bash
# Heystive MVP Development Startup Script
# Linux/macOS version

set -e

echo "🚀 Heystive MVP Development Environment"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "heystive_professional/backend_min.py" ]; then
    print_error "Please run this script from the Heystive project root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate
print_success "Virtual environment activated"

# Install backend dependencies
print_status "Installing backend dependencies..."
pip install -r heystive_professional/requirements-core.txt
print_success "Backend dependencies installed"

# Install web UI dependencies
print_status "Installing web UI dependencies..."
pip install -r ui_modern_web/requirements-web.txt
print_success "Web UI dependencies installed"

# Install desktop UI dependencies (optional)
print_status "Installing desktop UI dependencies..."
pip install -r ui_modern_desktop/requirements-desktop.txt
print_success "Desktop UI dependencies installed"

print_success "All dependencies installed successfully!"

echo ""
echo "🎯 Starting Heystive MVP Services"
echo "================================="

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    cd heystive_professional
    python backend_min.py &
    BACKEND_PID=$!
    cd ..
    print_success "Backend started (PID: $BACKEND_PID)"
    echo $BACKEND_PID > .backend.pid
}

# Function to start web UI
start_web_ui() {
    print_status "Starting web UI..."
    cd ui_modern_web
    python app.py &
    WEB_PID=$!
    cd ..
    print_success "Web UI started (PID: $WEB_PID)"
    echo $WEB_PID > .web.pid
}

# Start services
start_backend
sleep 2
start_web_ui

echo ""
echo "✅ Heystive MVP is now running!"
echo "==============================="
echo "Backend API: http://127.0.0.1:8000"
echo "Web Interface: http://127.0.0.1:5174"
echo "Health Check: http://127.0.0.1:8000/ping"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    print_status "Stopping services..."
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend stopped"
        fi
        rm -f .backend.pid
    fi
    
    if [ -f ".web.pid" ]; then
        WEB_PID=$(cat .web.pid)
        if kill -0 $WEB_PID 2>/dev/null; then
            kill $WEB_PID
            print_success "Web UI stopped"
        fi
        rm -f .web.pid
    fi
    
    print_success "All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
