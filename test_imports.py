#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
Run this to check if the application will start without errors.
"""

import sys
import traceback

def test_import(module_name, description=""):
    """Test importing a module and print result"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - {description}: {e}")
        return False

def main():
    print("Testing core application imports...\n")
    
    success_count = 0
    total_tests = 0
    
    # Test core FastAPI imports
    tests = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
        ("passlib", "Password hashing"),
        ("jwt", "JWT tokens"),
        ("redis", "Redis client"),
        ("aiohttp", "Async HTTP client"),
        ("google.generativeai", "Gemini AI"),
        ("dotenv", "Environment variables"),
    ]
    
    for module, desc in tests:
        total_tests += 1
        if test_import(module, desc):
            success_count += 1
    
    print(f"\n--- Core Dependencies Test Results ---")
    print(f"Passed: {success_count}/{total_tests}")
    
    # Test application modules
    print(f"\nTesting application modules...\n")
    
    app_tests = [
        ("src.config.database", "Database configuration"),
        ("src.config.cors", "CORS configuration"),
        ("src.models.user", "User model"),
        ("src.models.token_blacklist", "Token blacklist model"),
        ("src.controllers.auth_controller", "Authentication controller"),
        ("src.routes.auth", "Authentication routes"),
        ("src.utils.jwt", "JWT utilities"),
        ("src.utils.otp_service", "OTP service"),
        ("src.middlewares.rate_limit", "Rate limiting"),
        ("src.middlewares.error_handler", "Error handling"),
    ]
    
    app_success = 0
    app_total = len(app_tests)
    
    for module, desc in app_tests:
        if test_import(module, desc):
            app_success += 1
    
    print(f"\n--- Application Modules Test Results ---")
    print(f"Passed: {app_success}/{app_total}")
    
    # Test main application import
    print(f"\nTesting main application...")
    try:
        from src.app import app
        print("✅ Main application imports successfully")
        print("✅ FastAPI app created successfully")
        main_app_success = True
    except Exception as e:
        print(f"❌ Main application import failed: {e}")
        traceback.print_exc()
        main_app_success = False
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"Core Dependencies: {success_count}/{total_tests}")
    print(f"Application Modules: {app_success}/{app_total}")
    print(f"Main Application: {'✅ SUCCESS' if main_app_success else '❌ FAILED'}")
    
    overall_success = (success_count == total_tests and 
                      app_success == app_total and 
                      main_app_success)
    
    if overall_success:
        print(f"\n🎉 ALL TESTS PASSED! The application should run without import errors.")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Please install missing dependencies.")
        print(f"Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
