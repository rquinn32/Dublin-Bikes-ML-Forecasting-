import pytest
from unittest.mock import patch
from app import create_app
from config import TestingConfig

#Create test client fixture for API testing
@pytest.fixture
def client():
    app = create_app(TestingConfig)
    app.config["TESTING"] = True
    return app.test_client()

#Test home page loads 
@patch("app.main.routes.get_reviews_from_db", return_value=[])
def test_home_page(mock_reviews, client):
    response = client.get("/")
    assert response.status_code == 200

#Test stations API route 
@patch("app.main.routes.get_stations_from_db", return_value=[])
def test_api_stations_route(mock_stations, client):
    response = client.get("/api/stations")
    assert response.status_code in [200, 500]

#Invalid route handling 
def test_invalid_route(client):
    response = client.get("/not-a-real-page")
    assert response.status_code == 404