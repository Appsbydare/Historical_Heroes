#!/usr/bin/env python3
"""
Startup script for Wikipedia Extraction Manager
Runs both backend API server and frontend development server
"""

import subprocess
import sys
import os
import time
import signal
import threading
import shutil
from pathlib import Path

def find_npm():
    """Find npm executable"""
    # Try to find npm in PATH
    npm_path = shutil.which('npm')
    if npm_path:
        return npm_path
    
    # Common npm locations on Windows
    possible_paths = [
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        os.path.expanduser(r"~\AppData\Roaming\npm\npm.cmd"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def run_backend():
    """Run the Flask backend API server"""
    print("🚀 Starting backend API server...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Install Flask dependencies if needed
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"], check=True)
    except subprocess.CalledProcessError:
        print("⚠️  Warning: Could not install Flask dependencies")
    
    # Start the API server
    try:
        subprocess.run([sys.executable, "api/app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend server failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Backend server stopped")

def run_frontend():
    """Run the React frontend development server"""
    print("🚀 Starting frontend development server...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Find npm
    npm_path = find_npm()
    if not npm_path:
        print("❌ Error: npm not found!")
        print("Please install Node.js from https://nodejs.org/")
        print("Make sure to check 'Add to PATH' during installation")
        return
    
    print(f"📦 Using npm at: {npm_path}")
    
    # Install npm dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run([npm_path, "install"], check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            print("Try running 'npm install' manually in the frontend directory")
            return
    
    # Start the development server
    try:
        subprocess.run([npm_path, "run", "dev"], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend server failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Frontend server stopped")

def main():
    """Main function to start both servers"""
    print("🌟 Wikipedia Extraction Manager")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not (Path(__file__).parent / "backend").exists():
        print("❌ Error: Backend directory not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    if not (Path(__file__).parent / "frontend").exists():
        print("❌ Error: Frontend directory not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check for npm
    npm_path = find_npm()
    if not npm_path:
        print("❌ Error: npm not found!")
        print("Please install Node.js from https://nodejs.org/")
        print("Make sure to check 'Add to PATH' during installation")
        sys.exit(1)
    
    # Start both servers in separate threads
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    try:
        backend_thread.start()
        time.sleep(2)  # Give backend time to start
        frontend_thread.start()
        
        print("\n✅ Both servers are starting...")
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:5000")
        print("\nPress Ctrl+C to stop both servers")
        
        # Wait for both threads
        backend_thread.join()
        frontend_thread.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main() 