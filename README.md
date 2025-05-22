# Location-Based News API (Agno + OpenAI)

A production-ready FastAPI application that delivers comprehensive news coverage for any location using the Agno agent framework, OpenAI GPT-4o, and advanced reverse geocoding. The app coordinates a team of specialized AI agents to search, analyze, and synthesize news articles into professional-quality reports.

**🆕 Latest Update**: Fixed structured response parsing and removed raw content for clean UI integration!

---

## 🚀 Features

- **🌍 Location-based news**: Get comprehensive news for any coordinates (lat/lon) with automatic location detection
- **🤖 AI-powered team coordination**: Uses Agno's team/coordinate mode with OpenAI GPT-4o for multi-step reasoning
- **📍 Smart reverse geocoding**: Automatically converts coordinates to city/region names for accurate news search
- **🔍 Multi-source aggregation**: Combines DuckDuckGo and Newspaper4k tools for real-time news and deep article analysis
- **📰 Professional output**: Generates NYT-style articles with proper structure, attribution, and analysis
- **🏗️ Structured responses**: **FIXED!** UI-ready JSON with individual article objects, metadata, and easy filtering
- **🛡️ Production-ready**: Comprehensive error handling, logging, health checks, and monitoring
- **📊 Dual output formats**: Choose between markdown (human-readable) or structured JSON (UI-ready)
- **🔧 Development tools**: Test endpoints, debug mode, and comprehensive documentation
- **🔄 Backward compatible**: Original endpoints preserved while adding new structured functionality
- **✨ Clean API responses**: No raw content in structured endpoints - pure UI-ready data

---

## 🏗️ Architecture

The application uses a **team-based AI architecture** with specialized agents:

- **Searcher Agent**: Expert news researcher finding high-quality, recent articles from reputable sources
- **StructuredWriter Agent**: Specialized writer creating parseable, structured content for UI consumption
- **Writer Agent**: Professional journalist synthesizing multiple sources into coherent narratives
- **Editor Teams**: Senior coordinators ensuring quality, accuracy, and professional standards

---

## 📋 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/NewsApp_Agno.git
cd NewsApp_Agno
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**⚠️ Important**: You need a valid OpenAI API key with GPT-4o access. Get one from [OpenAI Platform](https://platform.openai.com/api-keys).

### 5. Run the application
```bash
# Development mode (with auto-reload)
uvicorn main:app --reload

# Or simply run the Python file
python main.py
```

### 6. Validate setup (Optional but recommended)
```bash
# Run validation script to ensure all dependencies are working
python validate_setup.py
```

### 7. Test the API
Open your browser and go to:
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Test Endpoint**: [http://127.0.0.1:8000/test-news/structured](http://127.0.0.1:8000/test-news/structured)

---

## 📚 API Endpoints

### 🏗️ POST `/news/structured` - Get Structured News (Recommended)

**✨ FIXED & IMPROVED!** Get news in a structured format optimized for frontend integration. Returns clean, individual article objects with metadata.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/news/structured" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius": 10,
    "max_results": 5,
    "categories": ["Politics", "Sports", "Local News"]
  }'
```

**Response:**
```json
{
  "location_name": "New York City",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius": 10
  },
  "news_articles": [
    {
      "id": "1",
      "title": "Major Political Development in NYC",
      "summary": "Brief summary of the political news article in 1-2 sentences.",
      "category": "Politics",
      "source": "New York Times",
      "url": "https://nytimes.com/article1",
      "published_date": "May 22, 2025",
      "relevance_score": 0.9
    },
    {
      "id": "2", 
      "title": "Sports Championship Update",
      "summary": "Summary of the sports news article.",
      "category": "Sports",
      "source": "ESPN",
      "url": "https://espn.com/article2",
      "published_date": "May 21, 2025",
      "relevance_score": 0.8
    }
  ],
  "categories": {
    "Politics": 3,
    "Sports": 2,
    "Local News": 1
  },
  "total_articles": 6,
  "generated_at": "2025-05-22T14:25:50.315822",
  "status": "success"
}
```

**✅ Benefits:**
- **No parsing required** - Individual article objects ready for UI
- **Rich metadata** - Source, date, relevance score for each article
- **Category organization** - Easy filtering and grouping
- **Frontend-friendly** - Direct integration with React, Vue, Angular
- **Clean response** - No raw markdown content cluttering the response

### 🌍 POST `/news` - Get Markdown News

Get comprehensive news coverage in traditional markdown format.

**Request Body:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius": 10,
  "max_results": 5,
  "categories": ["politics", "technology", "business"]
}
```

**Response:**
```json
{
  "location_name": "New York City",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius": 10
  },
  "article": "# Breaking News from New York City\n\n## Executive Summary...",
  "generated_at": "2025-05-21T16:00:00.000Z",
  "status": "success"
}
```

### 🧪 Test Endpoints

- **GET `/test-news/structured`** - Test structured endpoint with NYC data
- **GET `/test-news`** - Test markdown endpoint with NYC data
- **GET `/health`** - Health check and system status
- **GET `/`** - API information and available endpoints

---

## 🎨 Frontend Integration

### React Example
```javascript
import React, { useState, useEffect } from 'react';

const NewsApp = () => {
  const [news, setNews] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchNews = async (coordinates) => {
    setLoading(true);
    try {
      const response = await fetch('/news/structured', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(coordinates)
      });
      const data = await response.json();
      setNews(data);
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
    }
  };

  const NewsCard = ({ article }) => (
    <div className="news-card">
      <span className="category-badge">{article.category}</span>
      <h3>{article.title}</h3>
      <p>{article.summary}</p>
      <div className="meta">
        <span className="source">{article.source}</span>
        <span className="date">{article.published_date}</span>
        <span className="score">★ {article.relevance_score.toFixed(1)}</span>
      </div>
      <a href={article.url} target="_blank" rel="noopener noreferrer">
        Read Full Article
      </a>
    </div>
  );

  return (
    <div className="news-app">
      {loading && <div>Loading news...</div>}
      
      {news && (
        <div>
          <h1>News for {news.location_name}</h1>
          <div className="stats">
            <span>Total Articles: {news.total_articles}</span>
            <div className="categories">
              {Object.entries(news.categories).map(([cat, count]) => (
                <span key={cat} className="category-count">
                  {cat}: {count}
                </span>
              ))}
            </div>
          </div>
          
          <div className="news-grid">
            {news.news_articles.map(article => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsApp;
```

### JavaScript/Vanilla Example
```javascript
// Fetch news for specific coordinates
async function getNews(lat, lng, categories = ['Politics', 'Sports', 'Local News']) {
  const response = await fetch('/news/structured', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      latitude: lat,
      longitude: lng,
      radius: 10,
      max_results: 10,
      categories: categories
    })
  });
  
  return await response.json();
}

// Filter articles by category
function filterByCategory(articles, category) {
  return articles.filter(article => article.category === category);
}

// Sort articles by relevance
function sortByRelevance(articles) {
  return articles.sort((a, b) => b.relevance_score - a.relevance_score);
}

// Usage example
getNews(40.7128, -74.0060)
  .then(data => {
    console.log(`Found ${data.total_articles} articles for ${data.location_name}`);
    
    // Get politics articles sorted by relevance
    const politicsNews = sortByRelevance(
      filterByCategory(data.news_articles, 'Politics')
    );
    
    console.log('Top political news:', politicsNews[0]);
  });
```

---

## 🔧 Configuration

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latitude` | float | required | Latitude (-90 to 90) |
| `longitude` | float | required | Longitude (-180 to 180) |
| `radius` | float | 10 | Search radius in km (1-1000) |
| `max_results` | int | 5 | Maximum articles (1-20) |
| `categories` | array | null | News categories to focus on |

### Available Categories
- Politics
- Sports
- Local News
- Business
- Technology
- Health
- Entertainment
- Science
- World News

### Environment Variables
```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional
LOG_LEVEL=INFO
MAX_WORKERS=4
TIMEOUT_SECONDS=30
```

---

## 🐳 Docker Deployment

### Prerequisites
- Docker Desktop installed and running
- OpenAI API key set in your environment

### Quick Start with Docker

#### Option 1: Using Docker Compose (Recommended)
```bash
# Build and run in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop the application
docker compose down
```

#### Option 2: Manual Docker Build
```bash
# Build the image
docker build -t newsapp-agno .

# Run the container
docker run -d -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY --name newsapp newsapp-agno

# Check container status
docker ps

# Stop and remove
docker stop newsapp && docker rm newsapp
```

### Testing Your Docker Deployment

After starting the application, run the included test script:

```bash
# Test the Docker application
python test_docker_app.py
```

**Expected output:**
```
🐳 Testing NewsApp_Agno Docker Application
==================================================

🧪 Testing: Health Check
📍 URL: http://localhost:8000/health
✅ Status: 200 - SUCCESS
   📊 Status: healthy
   🔧 OpenAI Configured: True

🧪 Testing: API Information
📍 URL: http://localhost:8000/
✅ Status: 200 - SUCCESS
   📝 Name: Location-Based News API
   🔢 Version: 1.0.0

🧪 Testing: Structured News Endpoint (Test)
📍 URL: http://localhost:8000/test-news/structured
⏳ This may take 30-60 seconds for AI processing...
✅ Status: 200 - SUCCESS
   📍 Location: New York City
   📰 Total Articles: 16
   📊 Categories: {'Politics': 4, 'Sports': 4, 'Local News': 4, 'Business': 4}
```

### Access Your Application

Once running, access these URLs in your browser:

- **📖 Interactive API Documentation**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:8000/health
- **🏠 API Information**: http://localhost:8000/
- **🧪 Test Endpoint**: http://localhost:8000/test-news/structured

### Docker Configuration Details

**Dockerfile Features:**
- **Python 3.12**: Matches development environment
- **Security**: Non-root user for container security
- **Optimization**: Multi-stage build with dependency caching
- **Health Checks**: Built-in health monitoring
- **System Dependencies**: All required libraries (gcc, libxml2, curl)

**Docker Compose Features:**
- **Environment Variables**: Automatic .env file loading
- **Volume Mounting**: Persistent tmp directory for logs
- **Health Monitoring**: Automatic health checks
- **Network Isolation**: Custom network for security
- **Production Ready**: Restart policies and proper configuration

### Production Docker Compose

For production deployment, use this enhanced configuration:

```yaml
version: '3.8'
services:
  newsapp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
      - MAX_WORKERS=4
    volumes:
      - ./tmp:/app/tmp
      - ./.env:/app/.env:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  # Optional: Add nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - newsapp
    restart: unless-stopped
    profiles:
      - production

networks:
  default:
    name: news-api-network
```

### Docker Management Commands

```bash
# View container logs
docker compose logs -f newsapp

# Restart the application
docker compose restart

# Rebuild and restart
docker compose up --build -d

# Scale the application (multiple instances)
docker compose up -d --scale newsapp=3

# Execute commands in running container
docker compose exec newsapp bash

# Monitor resource usage
docker stats

# Clean up unused images and containers
docker system prune -f
```

### Troubleshooting Docker Issues

**Container won't start:**
```bash
# Check logs
docker compose logs newsapp

# Check if port is in use
lsof -i :8000

# Verify environment variables
docker compose exec newsapp env | grep OPENAI
```

**Health check failing:**
```bash
# Test health endpoint manually
curl http://localhost:8000/health

# Check container health status
docker compose ps
```

**Performance issues:**
```bash
# Monitor resource usage
docker stats newsapp_agno-news-api-1

# Increase memory limits in docker-compose.yml
# Add under deploy.resources.limits.memory: "4G"
```

---

## 🛠️ Development

### Validation and Testing Tools

#### Setup Validation
```bash
# Validate all dependencies are installed correctly
python validate_setup.py
```

**Expected output:**
```
🔍 Validating NewsApp_Agno Dependencies...
==================================================
✅ FastAPI
✅ Uvicorn
✅ Agno
✅ OpenAI
✅ Pydantic
... (all dependencies)

🚀 Testing main application...
✅ Main application imports successfully!

📊 VALIDATION SUMMARY
==================================================
Dependencies: 18/18 successful
Main app: ✅ Ready

🎉 All validations passed! Your NewsApp_Agno is ready to run!
```

#### Docker Application Testing
```bash
# Test Docker deployment (requires running container)
python test_docker_app.py
```

This script tests:
- Health check endpoint
- API information endpoint
- Structured news endpoint with real AI processing
- Provides comprehensive status and next steps

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=main tests/
```

### Development Mode
```bash
# Run with auto-reload
uvicorn main:app --reload --log-level debug

# Or use the built-in development server
python main.py
```

### Development Workflow

1. **Setup Validation**:
   ```bash
   python validate_setup.py
   ```

2. **Local Development**:
   ```bash
   python main.py
   # or
   uvicorn main:app --reload
   ```

3. **Docker Testing**:
   ```bash
   docker compose up -d
   python test_docker_app.py
   ```

4. **API Testing**:
   - Open http://localhost:8000/docs for interactive testing
   - Use http://localhost:8000/test-news/structured for quick validation

### Debugging
- Set `debug_mode=True` in agent configurations
- Check logs in the `tmp/` directory
- Use the `/health` endpoint to verify system status
- Test with `/test-news/structured` for quick validation
- Monitor Docker logs: `docker compose logs -f`

---

## 🚨 Troubleshooting

### Common Issues & Solutions

**❌ Empty `news_articles` array**
- **Fixed in latest version!** The parsing issue has been resolved
- Ensure you're using the latest code with the `extract_content_from_response` function

**❌ OpenAI API Key errors**
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Verify in health endpoint
curl http://127.0.0.1:8000/health
```

**❌ Geocoding failures**
- Check internet connectivity
- Verify coordinates are valid
- Try nearby major cities for remote locations

**❌ Installation issues**
```bash
# Clean install
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**❌ Port already in use**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

**❌ Module import errors**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Getting Help

1. Check the [API documentation](http://127.0.0.1:8000/docs) when running
2. Use the `/health` endpoint to verify system status
3. Check logs in the `tmp/` directory
4. Test with the `/test-news/structured` endpoint first
5. Ensure your OpenAI API key has sufficient credits

---

## 📦 Dependencies

### Core Requirements
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
agno==0.1.40
openai==1.3.7
pydantic==2.5.0
python-dotenv==1.0.0
geopy==2.4.0
```

### Full Dependencies (requirements.txt)
- **fastapi** - Modern web framework for building APIs
- **uvicorn** - ASGI server for FastAPI
- **agno** - AI agent framework for team coordination
- **openai** - OpenAI API client for GPT-4o integration
- **google-genai** - Google Generative AI SDK (backup model support)
- **newspaper4k** - Article extraction and analysis
- **duckduckgo-search** - Web search capabilities
- **python-dotenv** - Environment variable management
- **pydantic** - Data validation and serialization
- **geopy** - Geocoding and reverse geocoding
- **lxml_html_clean** - HTML processing for article extraction

---

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment variables
export OPENAI_API_KEY=your-production-key
export LOG_LEVEL=INFO
export MAX_WORKERS=4

# Run production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Health Monitoring
```bash
# Health check endpoint
curl http://your-domain.com/health

# Expected response
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "searcher": "active",
    "writer": "active",
    "editor_team": "active",
    "geocoding": "active"
  },
  "environment": {
    "openai_configured": true
  }
}
```

### Performance Optimization
- Use multiple workers for production
- Implement caching for frequently requested locations
- Set up load balancing for high traffic
- Monitor API usage and costs

---

## 📊 Performance Metrics

- **Response Time**: 10-30 seconds for comprehensive reports
- **Accuracy**: High-quality sources with proper attribution
- **Coverage**: Global news coverage with local context
- **Scalability**: Production-ready with multiple workers
- **Reliability**: Comprehensive error handling and fallbacks

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update tests for new features
- Update README for significant changes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Agno Framework](https://docs.agno.com/)** - AI agent coordination and team management
- **[OpenAI GPT-4o](https://platform.openai.com/docs/models/gpt-4o)** - Advanced language model for content generation
- **[DuckDuckGo](https://duckduckgo.com/)** - Privacy-focused search engine
- **[Geopy](https://geopy.readthedocs.io/)** - Geocoding library for location services
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework

---

## 📈 Changelog

### v1.1.0 (Latest)
- ✅ **FIXED**: Structured response parsing issue
- ✅ **REMOVED**: Raw article content from structured endpoints
- ✅ **IMPROVED**: Content extraction from TeamRunResponse objects
- ✅ **ENHANCED**: Error logging and debugging
- ✅ **ADDED**: Comprehensive frontend integration examples

### v1.0.0
- 🎉 Initial release with dual output formats
- 🏗️ Structured response endpoints
- 🤖 AI agent team coordination
- 🌍 Global location-based news coverage

---

**Built with ❤️ using Agno, OpenAI GPT-4o, and FastAPI**

**Ready to clone and run! 🚀** 