#!/usr/bin/env python3
"""
Setup script for the Dynasty Baseball Farm System Django backend.
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def clean_project():
    """Clean the project by removing database and migrations"""
    print("🧹 Cleaning project...")
    
    # Remove database
    db_file = Path("db.sqlite3")
    if db_file.exists():
        db_file.unlink()
        print("✓ Removed db.sqlite3")
    else:
        print("ℹ️  No db.sqlite3 found")
    
    # Remove migration files (except __init__.py)
    migration_files_removed = 0
    for migration_file in Path(".").rglob("*/migrations/*.py"):
        if migration_file.name != "__init__.py":
            migration_file.unlink()
            migration_files_removed += 1
            print(f"✓ Removed {migration_file}")
    
    if migration_files_removed == 0:
        print("ℹ️  No migration files found to remove")
    else:
        print(f"✓ Removed {migration_files_removed} migration files")
    
    # Remove venv 
    venv_path = Path("venv")
    if venv_path.exists():
        shutil.rmtree(venv_path)
        print("✓ Removed venv")
    else:
        print("ℹ️  No venv found")
    
    print("🧹 Clean completed!")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup script for Dynasty Baseball Farm System Backend")
    parser.add_argument("--clean", action="store_true", help="Clean the project before setup (removes db.sqlite3 and migrations)")
    args = parser.parse_args()
    
    print("Setting up Dynasty Baseball Farm System Backend")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Clean if requested
    if args.clean:
        clean_project()
        print()
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Create virtual environment"):
            sys.exit(1)
    
    # Determine the correct pip and python paths
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Install dependencies
    if not run_command(f"{pip_path} install -r requirements.txt", "Install dependencies"):
        sys.exit(1)
    
    # Run migrations
    if not run_command(f"{python_path} manage.py makemigrations", "Create migrations"):
        sys.exit(1)
    
    if not run_command(f"{python_path} manage.py migrate", "Apply migrations"):
        sys.exit(1)
    
    if not run_command(f"{python_path} manage.py create_test_data", "Create test data"):
        sys.exit(1)
    
    # Create superuser
    if args.clean:
        print("\nCreating superuser account...")
        print("Please enter the following information for the admin account:")
        try:
            subprocess.run(f"{python_path} manage.py createsuperuser", shell=True, check=True)
            print("✓ Superuser created successfully")
        except subprocess.CalledProcessError:
            print("✗ Superuser creation failed or was cancelled")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo start the development server:")
    print(f"  {python_path} manage.py runserver")
    print("\nTo access the admin interface:")
    print("  http://localhost:8000/admin")
    print("\nAPI endpoints will be available at:")
    print("  http://localhost:8000/api/")

if __name__ == "__main__":
    main() 