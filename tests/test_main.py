import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to the path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, get_location_name

client = TestClient(app)

class TestHealthEndpoint:
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "components" in data
        assert "environment" in data

class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Location-Based News API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "powered_by" in data

class TestGeocoding:
    @patch('main.Nominatim')
    def test_get_location_name_success(self, mock_nominatim):
        """Test successful reverse geocoding."""
        # Mock the geocoder
        mock_geolocator = MagicMock()
        mock_nominatim.return_value = mock_geolocator
        
        # Mock the location response
        mock_location = MagicMock()
        mock_location.address = "Test Address"
        mock_location.raw = {
            'address': {
                'city': 'New York City',
                'state': 'New York',
                'country': 'United States'
            }
        }
        mock_geolocator.reverse.return_value = mock_location
        
        result = get_location_name(40.7128, -74.0060)
        assert result == "New York City"
        mock_geolocator.reverse.assert_called_once_with((40.7128, -74.0060), language='en', timeout=10)

    @patch('main.Nominatim')
    def test_get_location_name_no_city(self, mock_nominatim):
        """Test reverse geocoding when no city is found but state is available."""
        mock_geolocator = MagicMock()
        mock_nominatim.return_value = mock_geolocator
        
        mock_location = MagicMock()
        mock_location.address = "Test Address"
        mock_location.raw = {
            'address': {
                'state': 'California',
                'country': 'United States'
            }
        }
        mock_geolocator.reverse.return_value = mock_location
        
        result = get_location_name(37.7749, -122.4194)
        assert result == "California"

    @patch('main.Nominatim')
    def test_get_location_name_failure(self, mock_nominatim):
        """Test reverse geocoding failure."""
        mock_geolocator = MagicMock()
        mock_nominatim.return_value = mock_geolocator
        mock_geolocator.reverse.return_value = None
        
        result = get_location_name(0, 0)
        assert result is None

    @patch('main.Nominatim')
    def test_get_location_name_exception(self, mock_nominatim):
        """Test reverse geocoding with exception."""
        mock_geolocator = MagicMock()
        mock_nominatim.return_value = mock_geolocator
        mock_geolocator.reverse.side_effect = Exception("Network error")
        
        result = get_location_name(40.7128, -74.0060)
        assert result is None

class TestNewsEndpoint:
    @patch('main.run_in_threadpool')
    @patch('main.get_location_name')
    def test_news_endpoint_success(self, mock_get_location, mock_run_threadpool):
        """Test successful news endpoint request."""
        # Mock location name
        mock_get_location.return_value = "New York City"
        
        # Mock AI response
        mock_response = "# Breaking News from New York City\n\nThis is a test article..."
        mock_run_threadpool.return_value = mock_response
        
        request_data = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius": 10,
            "max_results": 5
        }
        
        response = client.post("/news", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["location_name"] == "New York City"
        assert data["coordinates"]["latitude"] == 40.7128
        assert data["coordinates"]["longitude"] == -74.0060
        assert data["article"] == mock_response
        assert data["status"] == "success"
        assert "generated_at" in data

    @patch('main.get_location_name')
    def test_news_endpoint_location_not_found(self, mock_get_location):
        """Test news endpoint when location cannot be determined."""
        mock_get_location.return_value = None
        
        request_data = {
            "latitude": 0,
            "longitude": 0
        }
        
        response = client.post("/news", json=request_data)
        assert response.status_code == 404
        assert "Could not determine location name" in response.json()["detail"]

    @patch('main.run_in_threadpool')
    @patch('main.get_location_name')
    def test_news_endpoint_with_categories(self, mock_get_location, mock_run_threadpool):
        """Test news endpoint with categories."""
        mock_get_location.return_value = "San Francisco"
        mock_response = "# Tech News from San Francisco\n\nLatest tech developments..."
        mock_run_threadpool.return_value = mock_response
        
        request_data = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "radius": 15,
            "max_results": 3,
            "categories": ["technology", "business"]
        }
        
        response = client.post("/news", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["location_name"] == "San Francisco"
        assert data["coordinates"]["radius"] == 15

    @patch('main.run_in_threadpool')
    @patch('main.get_location_name')
    def test_news_endpoint_ai_error(self, mock_get_location, mock_run_threadpool):
        """Test news endpoint when AI processing fails."""
        mock_get_location.return_value = "Test City"
        mock_run_threadpool.side_effect = Exception("AI processing error")
        
        request_data = {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        response = client.post("/news", json=request_data)
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    def test_news_endpoint_invalid_coordinates(self):
        """Test news endpoint with invalid coordinates."""
        request_data = {
            "latitude": 91,  # Invalid latitude (> 90)
            "longitude": -74.0060
        }
        
        response = client.post("/news", json=request_data)
        # Pydantic validation should catch this and return 422
        assert response.status_code == 422
        
    def test_news_endpoint_invalid_longitude(self):
        """Test news endpoint with invalid longitude."""
        request_data = {
            "latitude": 40.7128,
            "longitude": 181  # Invalid longitude (> 180)
        }
        
        response = client.post("/news", json=request_data)
        # Pydantic validation should catch this and return 422
        assert response.status_code == 422

class TestNewsEndpointValidation:
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        response = client.post("/news", json={})
        assert response.status_code == 422

    def test_invalid_data_types(self):
        """Test validation with invalid data types."""
        request_data = {
            "latitude": "invalid",
            "longitude": -74.0060
        }
        
        response = client.post("/news", json=request_data)
        assert response.status_code == 422

    def test_optional_fields_defaults(self):
        """Test that optional fields have proper defaults."""
        with patch('main.get_location_name') as mock_get_location, \
             patch('main.run_in_threadpool') as mock_run_threadpool:
            
            mock_get_location.return_value = "Test City"
            mock_run_threadpool.return_value = "Test article"
            
            request_data = {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
            
            response = client.post("/news", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["coordinates"]["radius"] == 10  # Default value

class TestNewsTestEndpoint:
    @patch('main.run_in_threadpool')
    def test_test_news_endpoint_success(self, mock_run_threadpool):
        """Test the test news endpoint."""
        mock_response = "# Test News from New York City\n\nThis is a test article..."
        mock_run_threadpool.return_value = mock_response
        
        response = client.get("/test-news")
        assert response.status_code == 200
        
        data = response.json()
        assert data["location_name"] == "New York City"
        assert data["article"] == mock_response
        assert data["status"] == "success"
        assert "generated_at" in data

    @patch('main.run_in_threadpool')
    def test_test_news_endpoint_error(self, mock_run_threadpool):
        """Test the test news endpoint with AI error."""
        mock_run_threadpool.side_effect = Exception("AI processing error")
        
        response = client.get("/test-news")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

class TestEnvironmentConfiguration:
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_health_with_api_key(self):
        """Test health endpoint shows API key is configured."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["environment"]["openai_configured"] is True

    @patch.dict(os.environ, {}, clear=True)
    def test_health_without_api_key(self):
        """Test health endpoint shows API key is not configured."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["environment"]["openai_configured"] is False

if __name__ == "__main__":
    pytest.main([__file__]) 