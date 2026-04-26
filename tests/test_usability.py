import pytest
from unittest.mock import patch
from app import create_app
from config import TestingConfig

#Create test client 
@pytest.fixture
def client():
    app = create_app(TestingConfig)
    app.config["TESTING"] = True
    return app.test_client()

#Test for missing parameters 
def test_shortterm_missing_params(client):
    response = client.get("/api/shortterm_model")
    assert response.status_code == 400
    assert "error" in response.get_json()

#Test for invalid station ID
@patch("app.main.routes.get_stations_from_db")
def test_invalid_station(mock_db, client):
    mock_db.return_value = []

    response = client.get("/api/shortterm_model?station_id=999&minutes=10")
    assert response.status_code == 404

#Test for missing parameters in long-term model endpoint
def test_longterm_missing_inputs(client):
    response = client.get("/api/longterm_model")
    assert response.status_code == 400

#Search functionality test with mocked API response
@patch("app.main.routes.fetch_bike_api")
def test_search_function(mock_api, client):
    mock_api.return_value = [
        {"name": "Dame Street", "address": "Dublin"}
    ]

    response = client.get("/api/search?q=dame")
    data = response.get_json()

    assert len(data) > 0