#!/usr/bin/env python3
"""
ProfileGPT Setup Script
Helps you configure and test the system step by step
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def print_step(step_num, title, description):
    print(f"\n🚀 Step {step_num}: {title}")
    print("=" * 50)
    print(description)
    print()

def check_file_exists(filepath):
    return Path(filepath).exists()

def main():
    print("🎯 ProfileGPT Setup Assistant")
    print("=============================")
    print("This script will help you set up ProfileGPT step by step.\n")

    # Step 1: Check if we're in the right directory
    if not check_file_exists("backend/main.py"):
        print("❌ Please run this script from the ProfileGPT root directory")
        sys.exit(1)

    print_step(1, "Supabase Setup",
        """Please complete these steps:
        1. Go to https://supabase.com and create a new project
        2. Wait for the database to be ready (2-3 minutes)
        3. Go to Settings > API to get your keys
        4. Go to SQL Editor and run the contents of 'backend/setup_database.sql'
        5. Verify the tables were created in the Table Editor
        """)

    input("Press Enter when you've completed the Supabase setup...")

    print_step(2, "Environment Configuration",
        """Now let's configure your environment variables:
        1. Edit 'backend/.env' with your actual values:
           - SUPABASE_URL (from your project settings)
           - SUPABASE_ANON_KEY (from API settings)
           - SUPABASE_SERVICE_KEY (from API settings)
           - OPENAI_API_KEY (from OpenAI dashboard)
        """)

    input("Press Enter when you've updated the .env file...")

    # Step 3: Install dependencies
    print_step(3, "Installing Dependencies", "Installing Python packages...")

    try:
        os.chdir("backend")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Python dependencies installed successfully")
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return
    finally:
        os.chdir("..")

    print_step(4, "Testing Database Connection", "Let's test your database connection...")

    # Create a simple test script
    test_script = """
import sys
sys.path.append('.')
from app.services.supabase_client import supabase_service
from app.core.config import settings

try:
    # Test connection
    result = supabase_service.client.table('tenants').select('id, name').limit(1).execute()
    print("✅ Database connection successful!")
    print(f"Found {len(result.data)} tenant(s)")

    if len(result.data) > 0:
        print(f"Default tenant: {result.data[0]['name']}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("Please check your Supabase credentials in .env file")
"""

    with open("backend/test_connection.py", "w") as f:
        f.write(test_script)

    try:
        os.chdir("backend")
        result = subprocess.run([sys.executable, "test_connection.py"],
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    finally:
        os.chdir("..")
        # Cleanup
        if os.path.exists("backend/test_connection.py"):
            os.remove("backend/test_connection.py")

    print_step(5, "Starting Local Server", "Ready to start the development server!")

    print("You can now start the backend server:")
    print("cd backend && uvicorn main:app --reload")
    print("\nThen test the API at: http://localhost:8000/health")

    start_server = input("\nWould you like to start the server now? (y/n): ").lower().strip()

    if start_server == 'y':
        try:
            os.chdir("backend")
            print("\n🚀 Starting ProfileGPT API server...")
            print("Visit http://localhost:8000/docs for the API documentation")
            print("Press Ctrl+C to stop the server")
            subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload"])
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Thanks for using ProfileGPT!")
        finally:
            os.chdir("..")
    else:
        print("\n✅ Setup complete! You can start the server anytime with:")
        print("cd backend && uvicorn main:app --reload")

if __name__ == "__main__":
    main()