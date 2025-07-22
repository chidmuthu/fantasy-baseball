#!/usr/bin/env python
"""
Development server script that starts Django with Daphne for WebSocket support.
This ensures real-time updates work properly in development.
"""

import subprocess
import sys
import os
import signal
import time

def start_dev_server():
    """Start Django development server with Daphne"""
    print("🚀 Starting Django development server with WebSocket support...")
    
    # Start Daphne server for ASGI support
    # Use python -m daphne to ensure proper Django setup
    daphne_process = subprocess.Popen([
        sys.executable, '-m', 'daphne', '-b', '127.0.0.1', '-p', '8000', 
        'farm_system.asgi:application'
    ])
    
    print("✅ Django server started with WebSocket support!")
    print("📝 Daphne PID:", daphne_process.pid)
    print("🌐 Server running on http://127.0.0.1:8000")
    print("🔌 WebSocket endpoint: ws://127.0.0.1:8000/ws/")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        # Wait for process
        daphne_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping Django server...")
        daphne_process.terminate()
        
        # Wait for graceful shutdown
        try:
            daphne_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("⚠️  Force killing server...")
            daphne_process.kill()
        
        print("✅ Django server stopped")

if __name__ == '__main__':
    start_dev_server() 