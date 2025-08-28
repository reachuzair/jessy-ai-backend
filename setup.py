#!/usr/bin/env python3
"""
Setup script for Jessy AI Backend
Helps with initial project setup and database initialization
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr.strip()}")
        return False

def check_file_exists(file_path, description=""):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description} - Found")
        return True
    else:
        print(f"❌ {description} - Not found")
        return False

def main():
    print("🚀 Jessy AI Backend Setup Script")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️  Warning: You don't appear to be in a virtual environment")
        print("It's recommended to create and activate a virtual environment first:")
        print("  python -m venv venv")
        print("  venv\\Scripts\\activate  # Windows")
        print("  source venv/bin/activate  # macOS/Linux")
        proceed = input("\nProceed anyway? (y/N): ")
        if proceed.lower() != 'y':
            print("Setup cancelled.")
            return 1
    
    print(f"\n1️⃣  Checking required files...")
    
    # Check for important files
    files_to_check = [
        ("requirements.txt", "Requirements file"),
        ("src/app.py", "Main application file"),
        ("src/database_init.py", "Database initialization script"),
    ]
    
    all_files_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some required files are missing. Please check your project structure.")
        return 1
    
    print(f"\n2️⃣  Installing dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("\n⚠️  Failed to install dependencies. You may need to:")
        print("  - Check your internet connection")
        print("  - Upgrade pip: python -m pip install --upgrade pip")
        print("  - Install packages manually")
        return 1
    
    print(f"\n3️⃣  Testing imports...")
    if not run_command("python test_imports.py", "Testing application imports"):
        print("\n⚠️  Import test failed. Please check the error messages above.")
        return 1
    
    print(f"\n4️⃣  Checking environment configuration...")
    if not check_file_exists(".env", "Environment configuration"):
        print("⚠️  .env file not found. Please create one with required environment variables.")
        print("See README.md for the list of required variables.")
        create_env = input("Create a basic .env template? (y/N): ")
        if create_env.lower() == 'y':
            env_template = '''# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/jessy_db

# JWT Configuration
JWT_SECRET=change_this_to_a_secure_secret_key

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com

# AI Services Configuration
GEMINI_API_KEY=your_gemini_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# CORS Configuration
ENVIRONMENT=development
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
'''
            with open('.env', 'w') as f:
                f.write(env_template)
            print("✅ Basic .env template created. Please edit it with your actual values.")
    
    print(f"\n5️⃣  Database setup...")
    print("Note: Make sure PostgreSQL is running and accessible before proceeding.")
    setup_db = input("Initialize database tables now? (y/N): ")
    if setup_db.lower() == 'y':
        if not run_command("python src/database_init.py", "Creating database tables"):
            print("⚠️  Database initialization failed. Please check:")
            print("  - PostgreSQL is running")
            print("  - Database connection string in .env is correct")
            print("  - Database exists and is accessible")
    
    print(f"\n{'='*50}")
    print("🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Edit the .env file with your actual configuration values")
    print("2. Ensure PostgreSQL and Redis (optional) are running")
    print("3. Run the application: python run.py")
    print("4. Access the API docs at: http://localhost:8003/docs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
