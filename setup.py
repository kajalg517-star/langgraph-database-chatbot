#!/usr/bin/env python3
"""
Setup script for the Python Database Chatbot.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up Python Database Chatbot with Google ADK")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Warning: Not running in a virtual environment")
        print("   It's recommended to create a virtual environment:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print()
        
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            sys.exit(0)
    else:
        print("✅ Running in virtual environment")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ .env file created")
            print("⚠️  Please edit .env file with your actual configuration values")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    else:
        print("✅ .env file already exists")
    
    # Run tests
    print("\n🧪 Running tests...")
    if run_command("python -m pytest tests/ -v", "Running tests"):
        print("✅ All tests passed")
    else:
        print("⚠️  Some tests failed, but setup can continue")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit the .env file with your configuration:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    print("   - SUPABASE_SCHEMA")
    print("   - GEMINI_API_KEY")
    print()
    print("2. Test the database connection:")
    print("   python main.py test")
    print()
    print("3. Start the interactive chatbot:")
    print("   python main.py chat")
    print()
    print("4. Or run a single query:")
    print('   python main.py query "How many students are in the database?"')
    print()
    print("For more information, see README.md")


if __name__ == "__main__":
    main()
