#!/usr/bin/env python3
"""
Validation script to ensure all dependencies are properly installed
and the NewsApp_Agno project is ready to run.
"""

import sys
import importlib
from typing import List, Tuple

def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {package_name or module_name}"
    except ImportError as e:
        return False, f"❌ {package_name or module_name}: {str(e)}"

def main():
    """Run validation tests."""
    print("🔍 Validating NewsApp_Agno Dependencies...")
    print("=" * 50)
    
    # Core dependencies
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("agno", "Agno"),
        ("openai", "OpenAI"),
        ("pydantic", "Pydantic"),
        ("dotenv", "python-dotenv"),
        ("newspaper", "newspaper4k"),
        ("duckduckgo_search", "duckduckgo-search"),
        ("geopy", "geopy"),
        ("httpx", "httpx"),
        ("requests", "requests"),
        ("lxml", "lxml"),
        ("lxml_html_clean", "lxml_html_clean"),
        ("bs4", "beautifulsoup4"),
        ("nltk", "nltk"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("pytest", "pytest"),
    ]
    
    results = []
    for module, package in dependencies:
        success, message = test_import(module, package)
        results.append((success, message))
        print(message)
    
    print("\n" + "=" * 50)
    
    # Test main application import
    print("🚀 Testing main application...")
    try:
        from main import app
        print("✅ Main application imports successfully!")
        main_app_success = True
    except Exception as e:
        print(f"❌ Main application import failed: {str(e)}")
        main_app_success = False
    
    # Summary
    successful = sum(1 for success, _ in results if success)
    total = len(results)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Dependencies: {successful}/{total} successful")
    print(f"Main app: {'✅ Ready' if main_app_success else '❌ Failed'}")
    
    if successful == total and main_app_success:
        print("\n🎉 All validations passed! Your NewsApp_Agno is ready to run!")
        print("\n🚀 To start the application:")
        print("   uvicorn main:app --reload")
        print("   or")
        print("   python main.py")
        return 0
    else:
        print("\n⚠️  Some validations failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 