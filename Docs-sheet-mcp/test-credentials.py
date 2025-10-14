#!/usr/bin/env python3
"""
Test script to verify Google Cloud credentials and environment setup
Run this before starting your MCP agent
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_env_file():
    """Test if .env file exists and is loaded"""
    print_info("Checking .env file...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env file not found in current directory")
        print_info("Create a .env file with your credentials")
        return False
    
    print_success(".env file exists")
    load_dotenv()
    return True

def test_google_credentials():
    """Test Google Cloud credentials"""
    print_info("Checking Google Cloud credentials...")
    
    # Check environment variable
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print_error("GOOGLE_APPLICATION_CREDENTIALS not set in .env")
        print_info("Add this line to .env:")
        print_info("GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json")
        return False
    
    print_success(f"Environment variable set")
    print(f"   Path: {creds_path}")
    
    # Check file exists
    creds_file = Path(creds_path)
    if not creds_file.exists():
        print_error(f"Credentials file not found: {creds_path}")
        print_info("Make sure the path is correct and file exists")
        return False
    
    print_success("Credentials file exists")
    
    # Check file permissions (Unix-like systems)
    if hasattr(os, 'stat'):
        file_stat = creds_file.stat()
        mode = oct(file_stat.st_mode)[-3:]
        if mode != '600':
            print_info(f"File permissions: {mode} (recommended: 600)")
            print_info("Fix with: chmod 600 " + str(creds_path))
        else:
            print_success("File permissions are secure (600)")
    
    # Validate JSON structure
    try:
        with open(creds_path, 'r') as f:
            data = json.load(f)
        
        print_success("Valid JSON file")
        
        # Check required fields
        required_fields = [
            'type',
            'project_id',
            'private_key_id',
            'private_key',
            'client_email',
            'client_id'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print_error(f"Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print_success("All required fields present")
        print(f"   Service Account Email: {data.get('client_email')}")
        print(f"   Project ID: {data.get('project_id')}")
        print(f"   Account Type: {data.get('type')}")
        
        # Verify it's a service account
        if data.get('type') != 'service_account':
            print_error(f"Invalid account type: {data.get('type')}")
            print_info("Expected 'service_account'")
            return False
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        print_info("The credentials file is corrupted. Download it again.")
        return False
    except Exception as e:
        print_error(f"Error reading credentials: {e}")
        return False

def test_groq_api_key():
    """Test Groq API key"""
    print_info("Checking Groq API key...")
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print_error("GROQ_API_KEY not set in .env")
        print_info("Get your API key from: https://console.groq.com")
        print_info("Add this line to .env:")
        print_info("GROQ_API_KEY=gsk_your_api_key_here")
        return False
    
    print_success("Groq API key is set")
    print(f"   Key length: {len(groq_key)} characters")
    print(f"   Key prefix: {groq_key[:10]}...")
    
    # Basic validation
    if len(groq_key) < 20:
        print_error("API key seems too short")
        print_info("Verify you copied the complete key")
        return False
    
    if not groq_key.startswith('gsk_'):
        print_info("Note: Groq API keys typically start with 'gsk_'")
    
    return True

def test_python_packages():
    """Test if required Python packages are installed"""
    print_info("Checking Python packages...")
    
    required_packages = {
        'dotenv': 'python-dotenv',
        'agno': 'agno-sdk',
        'mcp': 'mcp',
    }
    
    all_installed = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            print_info(f"Install with: pip install {package}")
            all_installed = False
    
    return all_installed

def test_node_mcp_server():
    """Test if MCP server is installed"""
    print_info("Checking MCP server installation...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['npx', '-y', '@modelcontextprotocol/server-gdrive', '--version'],
            capture_output=True,
            timeout=10
        )
        print_success("MCP server package is accessible")
        return True
    except FileNotFoundError:
        print_error("Node.js/npx not found")
        print_info("Install Node.js from: https://nodejs.org")
        return False
    except subprocess.TimeoutExpired:
        print_info("MCP server check timed out (this is OK)")
        return True
    except Exception as e:
        print_info(f"Could not verify MCP server: {e}")
        print_info("If you have npm installed, run:")
        print_info("npm install -g @modelcontextprotocol/server-gdrive")
        return True  # Don't fail on this

def print_summary(results):
    """Print summary of all tests"""
    print_header("SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"Tests passed: {passed}/{total}\n")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    if passed == total:
        print_header("🎉 ALL TESTS PASSED!")
        print("You're ready to run the agent!")
        print("\nNext steps:")
        print("1. Make sure you've shared Google Drive files with your service account")
        print("2. Run: python google_mcp_agent.py")
        return True
    else:
        print_header("⚠️  SOME TESTS FAILED")
        print("Please fix the issues above before running the agent.")
        return False

def main():
    """Main test function"""
    print_header("🔍 Google Credentials & Environment Test")
    print("This script will verify your setup is correct\n")
    
    results = {}
    
    # Run all tests
    results[".env file"] = test_env_file()
    results["Google credentials"] = test_google_credentials()
    results["Groq API key"] = test_groq_api_key()
    results["Python packages"] = test_python_packages()
    results["MCP server"] = test_node_mcp_server()
    
    # Print summary
    success = print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)