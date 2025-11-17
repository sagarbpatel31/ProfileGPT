#!/usr/bin/env python3
"""
Quick test to verify the ProfileGPT setup
Run this after setting up Supabase and configuring .env
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")

    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        print("❌ FastAPI not installed - run: pip install -r backend/requirements.txt")
        return False

    try:
        import supabase
        print("✅ Supabase client available")
    except ImportError:
        print("❌ Supabase not installed")
        return False

    try:
        import openai
        print("✅ OpenAI client available")
    except ImportError:
        print("❌ OpenAI not installed")
        return False

    return True

def test_env_file():
    """Check if .env file exists and has required keys"""
    print("\n📄 Testing environment configuration...")

    env_path = Path("backend/.env")
    if not env_path.exists():
        print("❌ backend/.env file not found")
        print("   Copy backend/.env.example to backend/.env and fill in your values")
        return False

    with open(env_path) as f:
        content = f.read()

    required_keys = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_KEY",
        "OPENAI_API_KEY"
    ]

    missing_keys = []
    for key in required_keys:
        if key not in content or f"{key}=your_" in content or f"{key}=https://your-" in content:
            missing_keys.append(key)

    if missing_keys:
        print(f"❌ Missing or placeholder values for: {', '.join(missing_keys)}")
        print("   Please update your .env file with actual values")
        return False

    print("✅ Environment file looks good")
    return True

def test_backend_structure():
    """Check if backend files are in place"""
    print("\n📁 Testing backend structure...")

    required_files = [
        "backend/main.py",
        "backend/requirements.txt",
        "backend/app/core/config.py",
        "backend/app/services/supabase_client.py",
        "backend/app/services/rag_engine.py",
        "backend/setup_database.sql"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False

    print("✅ Backend structure complete")
    return True

def main():
    print("🎯 ProfileGPT Setup Verification")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("backend/main.py").exists():
        print("❌ Please run this from the ProfileGPT root directory")
        sys.exit(1)

    success = True
    success &= test_backend_structure()
    success &= test_env_file()
    success &= test_imports()

    print("\n" + "=" * 40)

    if success:
        print("🎉 Setup verification passed!")
        print("\nNext steps:")
        print("1. Create your Supabase project at https://supabase.com")
        print("2. Run the SQL in backend/setup_database.sql in Supabase SQL Editor")
        print("3. Update backend/.env with your actual Supabase and OpenAI credentials")
        print("4. Start the server: cd backend && uvicorn main:app --reload")
        print("5. Test at: http://localhost:8000/health")
    else:
        print("❌ Setup verification failed!")
        print("Please fix the issues above and run this script again.")

if __name__ == "__main__":
    main()