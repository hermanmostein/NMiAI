"""
Local testing script for Tripletex AI Agent
"""

import requests
import json
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
SANDBOX_BASE_URL = os.getenv("SANDBOX_BASE_URL", "")
SANDBOX_TOKEN = os.getenv("SANDBOX_SESSION_TOKEN", "")


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_solve_simple():
    """Test simple employee creation task"""
    print("\nTesting simple task (create employee)...")
    
    if not SANDBOX_BASE_URL or not SANDBOX_TOKEN:
        print("⚠️  Sandbox credentials not configured. Set SANDBOX_BASE_URL and SANDBOX_SESSION_TOKEN in .env")
        return False
    
    payload = {
        "prompt": "Create an employee named John Doe with email john.doe@example.com",
        "files": [],
        "tripletex_credentials": {
            "base_url": SANDBOX_BASE_URL,
            "session_token": SANDBOX_TOKEN
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/solve",
            json=payload,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_solve_norwegian():
    """Test Norwegian language task"""
    print("\nTesting Norwegian language task...")
    
    if not SANDBOX_BASE_URL or not SANDBOX_TOKEN:
        print("⚠️  Sandbox credentials not configured")
        return False
    
    payload = {
        "prompt": "Opprett en ansatt med navn Ola Nordmann, epost ola@example.no. Han skal være kontoadministrator.",
        "files": [],
        "tripletex_credentials": {
            "base_url": SANDBOX_BASE_URL,
            "session_token": SANDBOX_TOKEN
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/solve",
            json=payload,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_solve_customer():
    """Test customer creation task"""
    print("\nTesting customer creation task...")
    
    if not SANDBOX_BASE_URL or not SANDBOX_TOKEN:
        print("⚠️  Sandbox credentials not configured")
        return False
    
    payload = {
        "prompt": "Create a customer named Acme Corporation with email contact@acme.com",
        "files": [],
        "tripletex_credentials": {
            "base_url": SANDBOX_BASE_URL,
            "session_token": SANDBOX_TOKEN
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/solve",
            json=payload,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Tripletex AI Agent - Local Testing")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Sandbox configured: {'Yes' if SANDBOX_BASE_URL and SANDBOX_TOKEN else 'No'}")
    print("=" * 60)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test solve endpoints (only if sandbox is configured)
    if SANDBOX_BASE_URL and SANDBOX_TOKEN:
        results.append(("Simple Task (English)", test_solve_simple()))
        results.append(("Norwegian Task", test_solve_norwegian()))
        results.append(("Customer Creation", test_solve_customer()))
    else:
        print("\n⚠️  Skipping solve tests - sandbox not configured")
        print("To test solve endpoint, add to .env:")
        print("  SANDBOX_BASE_URL=https://your-sandbox.tripletex.dev/v2")
        print("  SANDBOX_SESSION_TOKEN=your-token")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
