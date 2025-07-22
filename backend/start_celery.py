#!/usr/bin/env python
"""
Helper script to start Celery workers and beat scheduler for development.
Run this script to start both the Celery worker and beat scheduler.
"""

import subprocess
import sys
import os
import signal
import time

def start_celery():
    """Start Celery worker and beat scheduler"""
    print("🚀 Starting Celery worker and beat scheduler...")
    
    # Start Celery worker
    worker_process = subprocess.Popen([
        'celery', '-A', 'farm_system', 'worker', 
        '--loglevel=info', '--beat'
    ])
    
    # Start Celery beat scheduler
    # beat_process = subprocess.Popen([
    #     'celery', '-A', 'farm_system', 'beat', 
    #     '--loglevel=info'
    # ])
    
    print("✅ Celery worker and beat scheduler started!")
    print("📝 Worker PID:", worker_process.pid)
    # print("📝 Beat PID:", beat_process.pid)
    print("🛑 Press Ctrl+C to stop both processes")
    
    try:
        # Wait for processes
        worker_process.wait()
        # beat_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping Celery processes...")
        worker_process.terminate()
        # beat_process.terminate()
        
        # Wait for graceful shutdown
        try:
            worker_process.wait(timeout=5)
            # beat_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("⚠️  Force killing processes...")
            worker_process.kill()
            # beat_process.kill()
        
        print("✅ Celery processes stopped")

if __name__ == '__main__':
    start_celery() 