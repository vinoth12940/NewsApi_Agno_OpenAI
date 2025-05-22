#!/usr/bin/env python3
"""
Demo script for the new structured news API endpoints.
Shows the difference between markdown and structured responses.
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def demo_structured_response():
    """Demonstrate the new structured news endpoint."""
    
    print("🚀 NewsApp Structured Response Demo")
    print("=" * 50)
    
    # Sample request
    request_data = {
        "latitude": 11.75,
        "longitude": 75.79,
        "radius": 10,
        "max_results": 5,
        "categories": ["Politics", "Sports", "Local News"]
    }
    
    print(f"📍 Request: {json.dumps(request_data, indent=2)}")
    print("\n" + "=" * 50)
    
    try:
        # Test structured endpoint
        print("🔄 Testing /news/structured endpoint...")
        response = requests.post(f"{BASE_URL}/news/structured", json=request_data, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Structured Response Received!")
            print(f"📍 Location: {data['location_name']}")
            print(f"📊 Total Articles: {data['total_articles']}")
            print(f"📂 Categories: {data['categories']}")
            
            print("\n📰 Individual Articles:")
            print("-" * 30)
            
            for i, article in enumerate(data['news_articles'][:3], 1):  # Show first 3
                print(f"{i}. 🏷️  Category: {article['category']}")
                print(f"   📰 Title: {article['title']}")
                print(f"   📝 Summary: {article['summary'][:100]}...")
                print(f"   🔗 Source: {article['source']}")
                print(f"   📅 Date: {article['published_date']}")
                print(f"   ⭐ Relevance: {article['relevance_score']}")
                print(f"   🌐 URL: {article['url'][:50]}...")
                print()
            
            # Show how easy it is to filter by category
            print("🔍 Easy Category Filtering:")
            politics_articles = [a for a in data['news_articles'] if a['category'] == 'Politics']
            print(f"   Politics articles: {len(politics_articles)}")
            
            sports_articles = [a for a in data['news_articles'] if a['category'] == 'Sports']
            print(f"   Sports articles: {len(sports_articles)}")
            
            print("\n💻 Frontend Integration Example:")
            print("```javascript")
            print("// React component example")
            print("const NewsCard = ({ article }) => (")
            print("  <div className='news-card'>")
            print("    <h3>{article.title}</h3>")
            print("    <p>{article.summary}</p>")
            print("    <span className='category'>{article.category}</span>")
            print("    <span className='source'>{article.source}</span>")
            print("    <a href={article.url}>Read More</a>")
            print("  </div>")
            print(");")
            print("```")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on localhost:8000")
        print("   Start with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def compare_responses():
    """Compare markdown vs structured responses."""
    
    print("\n" + "=" * 50)
    print("📊 Response Format Comparison")
    print("=" * 50)
    
    request_data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius": 10,
        "max_results": 3
    }
    
    try:
        # Test both endpoints
        print("🔄 Testing both endpoints...")
        
        # Original endpoint
        markdown_response = requests.post(f"{BASE_URL}/news", json=request_data, timeout=30)
        
        # Structured endpoint  
        structured_response = requests.post(f"{BASE_URL}/news/structured", json=request_data, timeout=30)
        
        if markdown_response.status_code == 200 and structured_response.status_code == 200:
            md_data = markdown_response.json()
            struct_data = structured_response.json()
            
            print("📝 Original Markdown Response:")
            print(f"   Type: {type(md_data['article'])}")
            print(f"   Length: {len(md_data['article'])} characters")
            print(f"   Sample: {md_data['article'][:100]}...")
            
            print("\n🏗️  Structured Response:")
            print(f"   Type: {type(struct_data['news_articles'])}")
            print(f"   Articles: {len(struct_data['news_articles'])} individual objects")
            print(f"   Categories: {struct_data['categories']}")
            print(f"   Easy to parse: ✅")
            print(f"   UI-ready: ✅")
            
        else:
            print("❌ One or both endpoints failed")
            
    except Exception as e:
        print(f"❌ Comparison failed: {e}")

def show_benefits():
    """Show the benefits of structured responses."""
    
    print("\n" + "=" * 50)
    print("🎯 Benefits of Structured Response")
    print("=" * 50)
    
    benefits = [
        "✅ No markdown parsing needed on frontend",
        "✅ Individual article objects for easy mapping",
        "✅ Built-in category filtering and organization", 
        "✅ Rich metadata (source, date, relevance score)",
        "✅ Easy sorting and filtering capabilities",
        "✅ Direct integration with UI components",
        "✅ Backward compatibility maintained",
        "✅ Raw markdown still available for debugging"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print("\n🔧 Use Cases:")
    use_cases = [
        "📱 Mobile apps with news cards",
        "🌐 Web dashboards with category filters", 
        "📊 Analytics and data visualization",
        "🔍 Search and filtering interfaces",
        "📰 News aggregation platforms",
        "🎨 Custom UI components"
    ]
    
    for use_case in use_cases:
        print(f"   {use_case}")

if __name__ == "__main__":
    demo_structured_response()
    compare_responses()
    show_benefits()
    
    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print("💡 Try the new endpoints:")
    print("   POST /news/structured - For UI integration")
    print("   GET /test-news/structured - For testing")
    print("   GET /docs - For full API documentation")
    print("=" * 50) 