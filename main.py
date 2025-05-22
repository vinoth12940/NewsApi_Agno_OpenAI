from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from agno.models.openai.chat import OpenAIChat
from agno.agent import Agent
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
import os
import re
import json
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool
from geopy.geocoders import Nominatim
from datetime import datetime
from textwrap import dedent

# Load environment variables from .env or system
load_dotenv()
# Ensure you have OPENAI_API_KEY set in your .env file or environment
# Example .env line: OPENAI_API_KEY=sk-...

app = FastAPI(
    title="Location-Based News API",
    description="AI-powered news aggregation using Agno framework with OpenAI GPT-4o",
    version="1.0.0"
)

# Create temporary directory for storing URLs and logs
base_dir = Path(__file__).parent
tmp_dir = base_dir.joinpath("tmp")
tmp_dir.mkdir(parents=True, exist_ok=True)

urls_file = tmp_dir.joinpath("urls__{session_id}.md")

def get_location_name(latitude, longitude):
    """Convert coordinates to location name using reverse geocoding."""
    try:
        geolocator = Nominatim(user_agent="news_app_v1.0")
        location = geolocator.reverse((latitude, longitude), language='en', timeout=10)
        if location and location.address:
            address = location.raw.get('address', {})
            # Try to get city, town, village, state, or country
            return (
                address.get('city') or
                address.get('town') or
                address.get('village') or
                address.get('state') or
                address.get('country')
            )
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None

def save_response_to_file(response, location_name):
    """Manually save response to file for logging purposes."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"news_report_{location_name}_{timestamp}.md"
        filepath = tmp_dir.joinpath(filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# News Report for {location_name}\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
            f.write(str(response))
        
        print(f"Response saved to: {filepath}")
    except Exception as e:
        print(f"Error saving response to file: {e}")

def calculate_relevance_score(title: str, summary: str, date: str = None) -> float:
    """Calculate relevance score based on content and recency."""
    score = 0.5  # Base score
    
    # Boost for recent dates
    if date and "2025" in date:
        score += 0.3
    
    # Boost for important keywords
    important_keywords = ["breaking", "urgent", "major", "significant", "important", "latest"]
    text = f"{title} {summary}".lower()
    
    for keyword in important_keywords:
        if keyword in text:
            score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0

def extract_content_from_response(response_obj) -> str:
    """
    Extract actual content from AI response object.
    Handles both string responses and TeamRunResponse objects.
    """
    try:
        # Convert to string first
        response_str = str(response_obj)
        
        # Check if it's a TeamRunResponse wrapper
        if "TeamRunResponse" in response_str and "content=" in response_str:
            # Extract content between quotes after content=
            content_match = re.search(r'content="([^"]*(?:\\.[^"]*)*)"', response_str)
            if content_match:
                # Unescape the content
                content = content_match.group(1)
                content = content.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
                return content
        
        # If not wrapped, return as is
        return response_str
    except Exception as e:
        print(f"Error extracting content: {e}")
        return str(response_obj)

def parse_markdown_to_structured_news(markdown_content: str, requested_categories: List[str] = None) -> Dict[str, Any]:
    """
    Parse markdown news content into structured articles.
    
    Expected markdown format:
    ### Category Name
    1. **Title**
       Summary text
       [Read more](url) (Source, Date)
    """
    articles = []
    categories = {}
    article_id = 1
    
    try:
        # Extract actual content from response wrapper
        content = extract_content_from_response(markdown_content)
        
        # Split by category headers (### Category Name)
        lines = content.split('\n')
        current_category = "General"
        current_article = {}
        
        for line in lines:
            line = line.strip()
            
            # Check for category header
            if line.startswith('### '):
                current_category = line.replace('### ', '').strip()
                categories[current_category] = 0
                continue
            
            # Check for numbered article start
            if re.match(r'^\d+\.\s*\*\*(.+?)\*\*', line):
                # Save previous article if exists
                if current_article.get('title'):
                    articles.append(current_article)
                    categories[current_category] = categories.get(current_category, 0) + 1
                
                # Start new article
                title_match = re.search(r'\*\*(.+?)\*\*', line)
                if title_match:
                    current_article = {
                        'id': str(article_id),
                        'title': title_match.group(1).strip(),
                        'category': current_category,
                        'summary': '',
                        'source': 'Unknown',
                        'url': '',
                        'published_date': None,
                        'relevance_score': 0.5
                    }
                    article_id += 1
                continue
            
            # Check for summary (non-empty line that's not a link)
            if line and not line.startswith('[') and current_article.get('title') and not current_article.get('summary'):
                current_article['summary'] = line
                continue
            
            # Check for source link
            if '[Read more]' in line and current_article.get('title'):
                # Extract URL
                url_match = re.search(r'\[Read more\]\((.+?)\)', line)
                if url_match:
                    current_article['url'] = url_match.group(1).strip()
                
                # Extract source and date
                source_match = re.search(r'\)\s*\((.+?)\)', line)
                if source_match:
                    source_info = source_match.group(1).strip()
                    parts = source_info.split(',')
                    if len(parts) >= 1:
                        current_article['source'] = parts[0].strip()
                    if len(parts) >= 2:
                        current_article['published_date'] = parts[1].strip()
                
                # Calculate relevance score
                current_article['relevance_score'] = calculate_relevance_score(
                    current_article['title'],
                    current_article['summary'],
                    current_article.get('published_date')
                )
        
        # Don't forget the last article
        if current_article.get('title'):
            articles.append(current_article)
            categories[current_category] = categories.get(current_category, 0) + 1
        
        # Convert to NewsArticle objects
        news_articles = []
        for article_data in articles:
            if article_data.get('title'):  # Only add articles with titles
                news_articles.append(NewsArticle(**article_data))
        
        return {
            "articles": news_articles,
            "categories": categories,
            "total_articles": len(news_articles)
        }
    
    except Exception as e:
        print(f"Error parsing markdown: {e}")
        print(f"Content preview: {str(markdown_content)[:500]}...")
        # Return empty structure on error
        return {
            "articles": [],
            "categories": {},
            "total_articles": 0
        }

# Create specialized agents with enhanced instructions
searcher = Agent(
    name="Searcher",
    role="Expert news researcher and URL finder",
    description="You are a senior news researcher specializing in finding high-quality, recent news articles from reputable sources.",
    instructions=[
        "Given a topic or location, generate 3-5 diverse search terms to ensure comprehensive coverage.",
        "For each search term, search both general web and news sources.",
        "Prioritize recent articles (within last 7 days) and reputable news outlets.",
        "Return the 10 most relevant and credible URLs with brief descriptions.",
        "Focus on breaking news, major developments, and stories with significant impact.",
        "Ensure sources are from established news organizations, government sites, or verified outlets.",
    ],
    tools=[DuckDuckGoTools()],
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True,
)

writer = Agent(
    name="Writer",
    role="Professional news writer and content synthesizer",
    description=dedent("""\
        You are a senior journalist and content writer with expertise in creating 
        engaging, accurate, and well-structured news articles. Your specialty is 
        synthesizing multiple sources into coherent, informative narratives.\
    """),
    instructions=[
        "First, carefully read and analyze all provided URLs using the `read_article` tool.",
        "Extract key facts, quotes, and data points from each source.",
        "Create a comprehensive, well-structured news article that synthesizes information from all sources.",
        "Ensure the article is engaging, informative, and follows journalistic standards.",
        "Include proper attribution for all facts and quotes.",
        "Structure the article with: compelling headline, executive summary, main content, and key takeaways.",
        "Maintain objectivity and present multiple perspectives when available.",
        "Focus on accuracy, clarity, and readability for a general audience.",
    ],
    tools=[Newspaper4kTools()],
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True,
    expected_output=dedent("""\
        A professional news article in markdown format:
        
        # {Compelling Headline}
        
        ## Executive Summary
        {Brief overview of the main story and its significance}
        
        ## Main Story
        {Detailed coverage with facts, context, and analysis}
        
        ## Key Developments
        {Important updates and recent developments}
        
        ## Impact & Analysis
        {What this means for the community/region}
        
        ## Key Takeaways
        - {Important point 1}
        - {Important point 2}
        - {Important point 3}
        
        ## Sources
        - {Source 1 with attribution}
        - {Source 2 with attribution}
        
        ---
        Report compiled by AI News Team
        Date: {current_date}\
    """),
)

# Create the coordinating editor team
editor = Team(
    name="Editor",
    mode="coordinate",
    model=OpenAIChat("gpt-4o"),
    members=[searcher, writer],
    description="You are a senior news editor coordinating a team of researchers and writers to produce high-quality, comprehensive news coverage.",
    instructions=[
        "Coordinate the team to produce comprehensive news coverage for the requested location or topic.",
        "First, direct the Searcher to find the most relevant and recent news articles.",
        "Then, have the Writer create a well-structured, engaging news article based on the found sources.",
        "Review the final output for accuracy, completeness, and journalistic quality.",
        "Ensure the article meets professional news standards with proper attribution.",
        "If the initial results are insufficient, direct additional searches or revisions.",
        "Provide clear, actionable feedback to team members to improve output quality.",
    ],
    add_datetime_to_instructions=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
)

# Create a structured writer for parseable output
structured_writer = Agent(
    name="StructuredWriter",
    role="Structured news content creator",
    description="Create structured news content that can be easily parsed into individual articles for UI consumption.",
    instructions=[
        "Create a structured news report with clear categories and individual articles.",
        "Use EXACTLY this format for each article:",
        "1. **Article Title Here**",
        "   Brief summary of the article (1-2 sentences)",
        "   [Read more](full_url_here) (Source Name, Date)",
        "",
        "Group articles under category headers like: ### Politics, ### Sports, ### Local News",
        "Ensure each article has a clear title, summary, source, and URL.",
        "Include publication date when available in format: Month Day, Year",
        "Focus on accuracy and proper attribution.",
        "Do not include any other text or formatting outside of this structure.",
    ],
    tools=[Newspaper4kTools()],
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True,
    expected_output=dedent("""\
        ### Politics
        1. **Political News Title**
           Summary of the political news article in 1-2 sentences.
           [Read more](https://example.com/article1) (Source Name, May 22, 2025)
        
        2. **Another Political News Title**
           Another summary of political news.
           [Read more](https://example.com/article2) (Another Source, May 21, 2025)
        
        ### Sports  
        1. **Sports News Title**
           Summary of the sports news article.
           [Read more](https://example.com/article3) (Sports Source, May 21, 2025)
        
        ### Local News
        1. **Local News Title**
           Summary of the local news article.
           [Read more](https://example.com/article4) (Local Source, May 20, 2025)
    """),
)

# Create structured editor team
structured_editor = Team(
    name="StructuredEditor",
    mode="coordinate",
    model=OpenAIChat("gpt-4o"),
    members=[searcher, structured_writer],
    description="You are a senior news editor coordinating a team to produce structured, parseable news content for UI consumption.",
    instructions=[
        "Coordinate the team to produce structured news coverage for the requested location or topic.",
        "First, direct the Searcher to find the most relevant and recent news articles.",
        "Then, have the StructuredWriter create a properly formatted, structured news report.",
        "Ensure the output follows the exact format required for parsing into individual articles.",
        "Each article must have: title, summary, source, URL, and date.",
        "Group articles by categories as requested.",
        "Review for accuracy and proper formatting.",
    ],
    add_datetime_to_instructions=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
)

class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")
    radius: Optional[float] = Field(10, gt=0, le=1000, description="Search radius in km (1-1000)")
    max_results: Optional[int] = Field(5, ge=1, le=20, description="Maximum number of results (1-20)")
    categories: Optional[List[str]] = None

class NewsResponse(BaseModel):
    location_name: str
    coordinates: dict
    article: str
    sources_count: int
    generated_at: str

# New models for structured responses
class NewsArticle(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    source: str
    url: str
    published_date: Optional[str] = None
    relevance_score: float = 0.0

class StructuredNewsResponse(BaseModel):
    location_name: str
    coordinates: Dict[str, Any]
    news_articles: List[NewsArticle]
    categories: Dict[str, int]  # {"Politics": 5, "Sports": 2}
    total_articles: int
    generated_at: str
    status: str

@app.post("/news", response_model=dict)
async def get_location_news(request: LocationRequest):
    """
    Get the latest news for a given location using coordinates.
    
    Returns a comprehensive news article with sources and analysis.
    """
    try:
        # Reverse geocode coordinates to location name
        location_name = get_location_name(request.latitude, request.longitude)
        if not location_name:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not determine location name from coordinates {request.latitude}, {request.longitude}"
            )
        
        # Build comprehensive prompt
        categories_str = f" focusing on {', '.join(request.categories)}" if request.categories else ""
        prompt = dedent(f"""\
            Create a comprehensive news report for {location_name}{categories_str}.
            
            Requirements:
            - Find the top {request.max_results} most recent and relevant news articles
            - Cover news within approximately {request.radius}km of the area
            - Focus on breaking news, major developments, and significant local events
            - Ensure all information is accurate and properly attributed
            - Create an engaging, professional news article suitable for publication
            
            Location: {location_name} (Coordinates: {request.latitude}, {request.longitude})
            Search radius: {request.radius}km
            Target articles: {request.max_results}
        """)
        
        # Run the news team
        response = await run_in_threadpool(editor.run, prompt)
        
        # Save response to file for logging
        save_response_to_file(response, location_name)
        
        return {
            "location_name": location_name,
            "coordinates": {
                "latitude": request.latitude,
                "longitude": request.longitude,
                "radius": request.radius
            },
            "article": str(response),
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/test-news")
async def test_news():
    """
    Test endpoint using a hardcoded location for development and testing.
    """
    try:
        location_name = "New York City"
        prompt = dedent(f"""\
            Create a comprehensive news report for {location_name}.
            
            Requirements:
            - Find the top 5 most recent and relevant news articles
            - Focus on breaking news, major developments, and significant events
            - Ensure all information is accurate and properly attributed
            - Create an engaging, professional news article suitable for publication
            
            Location: {location_name}
        """)
        
        response = await run_in_threadpool(editor.run, prompt)
        
        # Save response to file for logging
        save_response_to_file(response, location_name)
        
        return {
            "location_name": location_name,
            "article": str(response),
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/news/structured", response_model=dict)
async def get_structured_location_news(request: LocationRequest):
    """
    Get structured news data for easy UI integration.
    
    Returns individual articles with metadata for easy parsing and display.
    This endpoint is optimized for frontend consumption with structured JSON.
    """
    try:
        # Reverse geocode coordinates to location name
        location_name = get_location_name(request.latitude, request.longitude)
        if not location_name:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not determine location name from coordinates {request.latitude}, {request.longitude}"
            )
        
        # Build prompt for structured output
        categories_str = f" focusing on {', '.join(request.categories)}" if request.categories else ""
        default_categories = request.categories if request.categories else ["Politics", "Sports", "Local News", "Business"]
        
        prompt = dedent(f"""\
            Create a structured news report for {location_name}{categories_str}.
            
            Format Requirements:
            - Use category headers: ### Category Name
            - List articles as: 1. **Title** followed by summary and source
            - Include full URLs and source attribution
            - Target {request.max_results} articles total
            - Focus on recent news within {request.radius}km
            - Use EXACTLY this format for each article:
              1. **Article Title Here**
                 Brief summary of the article (1-2 sentences)
                 [Read more](full_url_here) (Source Name, Date)
            
            Categories to include: {', '.join(default_categories)}
            Location: {location_name} (Coordinates: {request.latitude}, {request.longitude})
            Search radius: {request.radius}km
        """)
        
        # Get AI response using structured editor
        raw_response = await run_in_threadpool(structured_editor.run, prompt)
        
        # Parse into structured format
        parsed_data = parse_markdown_to_structured_news(
            str(raw_response), 
            request.categories
        )
        
        # Save for logging
        save_response_to_file(raw_response, f"{location_name}_structured")
        
        # Return structured response
        return {
            "location_name": location_name,
            "coordinates": {
                "latitude": request.latitude,
                "longitude": request.longitude,
                "radius": request.radius
            },
            "news_articles": [article.dict() for article in parsed_data["articles"]],
            "categories": parsed_data["categories"],
            "total_articles": parsed_data["total_articles"],
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/test-news/structured")
async def test_structured_news():
    """
    Test endpoint for structured news using a hardcoded location.
    
    Returns structured news data for UI testing and development.
    """
    try:
        location_name = "New York City"
        prompt = dedent(f"""\
            Create a structured news report for {location_name}.
            
            Format Requirements:
            - Use category headers: ### Category Name
            - List articles as: 1. **Title** followed by summary and source
            - Include full URLs and source attribution
            - Target 8 articles total
            - Use EXACTLY this format for each article:
              1. **Article Title Here**
                 Brief summary of the article (1-2 sentences)
                 [Read more](full_url_here) (Source Name, Date)
            
            Categories to include: Politics, Sports, Local News, Business
            Location: {location_name}
        """)
        
        # Get AI response using structured editor
        raw_response = await run_in_threadpool(structured_editor.run, prompt)
        
        # Parse into structured format
        parsed_data = parse_markdown_to_structured_news(str(raw_response))
        
        # Save for logging
        save_response_to_file(raw_response, f"{location_name}_structured_test")
        
        # Return structured response
        return {
            "location_name": location_name,
            "coordinates": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "radius": 10
            },
            "news_articles": [article.dict() for article in parsed_data["articles"]],
            "categories": parsed_data["categories"],
            "total_articles": parsed_data["total_articles"],
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and deployment."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "searcher": "active",
            "writer": "active",
            "editor_team": "active",
            "geocoding": "active"
        },
        "environment": {
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "tmp_directory": str(tmp_dir),
            "agno_version": "latest"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Location-Based News API",
        "description": "AI-powered news aggregation using Agno framework with OpenAI GPT-4o",
        "version": "1.0.0",
        "endpoints": {
            "POST /news": "Get news for specific coordinates (markdown format)",
            "POST /news/structured": "Get structured news for UI integration (JSON format)",
            "GET /test-news": "Test endpoint with hardcoded location (markdown)",
            "GET /test-news/structured": "Test endpoint with structured output (JSON)",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        },
        "features": {
            "structured_output": "Individual articles with metadata for easy UI parsing",
            "backward_compatibility": "Original markdown endpoints still available",
            "ui_ready": "No frontend parsing required for structured endpoints"
        },
        "powered_by": ["Agno", "OpenAI GPT-4o", "FastAPI"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 