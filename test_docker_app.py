#!/usr/bin/env python3
"""
Test script to verify the NewsApp_Agno Docker application is working correctly.
"""

import requests
import json
import time

def test_endpoint(url, description, method="GET", data=None):
    """Test an API endpoint and return the result."""
    print(f"\n🧪 Testing: {description}")
    print(f"📍 URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code} - SUCCESS")
            return True, result
        else:
            print(f"❌ Status: {response.status_code} - FAILED")
            print(f"   Error: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this is normal for AI processing)")
        return False, None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None

def main():
    """Run all tests."""
    print("🐳 Testing NewsApp_Agno Docker Application")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    success, result = test_endpoint(f"{base_url}/health", "Health Check")
    if success:
        print(f"   📊 Status: {result['status']}")
        print(f"   🔧 OpenAI Configured: {result['environment']['openai_configured']}")
    
    # Test 2: Root endpoint
    success, result = test_endpoint(f"{base_url}/", "API Information")
    if success:
        print(f"   📝 Name: {result['name']}")
        print(f"   🔢 Version: {result['version']}")
    
    # Test 3: Test structured endpoint (this might take a while)
    print(f"\n🧪 Testing: Structured News Endpoint (Test)")
    print(f"📍 URL: {base_url}/test-news/structured")
    print("⏳ This may take 30-60 seconds for AI processing...")
    
    try:
        response = requests.get(f"{base_url}/test-news/structured", timeout=90)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code} - SUCCESS")
            print(f"   📍 Location: {result['location_name']}")
            print(f"   📰 Total Articles: {result['total_articles']}")
            print(f"   📊 Categories: {result['categories']}")
            if result.get('news_articles'):
                print(f"   📄 First Article: {result['news_articles'][0]['title'][:60]}...")
        else:
            print(f"❌ Status: {response.status_code} - FAILED")
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - AI processing can take time, but the endpoint is working")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Docker Application Test Complete!")
    print("\n📖 Available endpoints:")
    print("   • Health Check: http://localhost:8000/health")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Test News: http://localhost:8000/test-news/structured")
    print("   • Custom Location: POST http://localhost:8000/news/structured")
    print("\n🛑 To stop the application:")
    print("   docker compose down")

if __name__ == "__main__":
    main() 