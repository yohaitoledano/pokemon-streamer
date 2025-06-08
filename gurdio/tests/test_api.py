import pytest
from fastapi.testclient import TestClient
import base64
import hmac
import hashlib
import json
import os
from ..api import app
from ..stats import Stats
from collections import defaultdict

@pytest.fixture(autouse=True)
def setup_environment():
    """Set up test environment variables."""
    secret = base64.b64encode(b"test secret").decode()
    os.environ['HMAC_SECRET'] = secret
    yield
    if 'HMAC_SECRET' in os.environ:
        del os.environ['HMAC_SECRET']

@pytest.fixture(autouse=True)
def reset_stats():
    """Reset the Stats singleton before each test."""
    from ..stats import stats
    Stats._instance = None
    stats._initialized = False
    stats.stats = defaultdict(stats._create_stats)
    stats.stats['stream'] = stats._create_stats()
    yield
    Stats._instance = None
    stats._initialized = False
    stats.stats = defaultdict(stats._create_stats)
    stats.stats['stream'] = stats._create_stats()

client = TestClient(app)

def generate_signature(data: bytes, secret: str) -> str:
    secret_bytes = base64.b64decode(secret)
    return hmac.new(
        secret_bytes,
        data,
        hashlib.sha256
    ).hexdigest()

def test_stream_endpoint_missing_signature():
    pokemon_data = {
        "number": 1,
        "name": "Bulbasaur",
        "type_one": "Grass",
        "type_two": "Poison",
        "total": 318,
        "hit_points": 20,
        "attack": 49,
        "defense": 49,
        "special_attack": 65,
        "special_defense": 65,
        "speed": 45,
        "generation": 1,
        "legendary": False
    }
    data_bytes = json.dumps(pokemon_data).encode('utf-8')
    
    response = client.post(
        "/stream",
        data=data_bytes,
        # headers={"X-Grd-Signature": signature}
    )
    assert response.status_code == 422

    response = client.post(
        "/stream",
        data=data_bytes,
        headers={"X-Grd-Signature": "invalid_signature"}
    )
    assert response.status_code == 401
    
    # Verify stats were updated
    stats_response = client.get("/stats")
    stats = stats_response.json()["stream"]
    assert stats["request_count"] == 1 # first request doesn't reach to the endpoint
    assert stats["error_rate"] == 1.0  # 100% error rate
    assert stats["incoming_bytes"] > 0
    assert stats["outgoing_bytes"] == 0  # No response content for errors

def test_stream_endpoint_invalid_signature():
    # Test data
    pokemon_data = {
        "number": 1,
        "name": "Bulbasaur",
        "type_one": "Grass",
        "type_two": "Poison",
        "total": 318,
        "hit_points": 45,
        "attack": 49,
        "defense": 49,
        "special_attack": 65,
        "special_defense": 65,
        "speed": 45,
        "generation": 1,
        "legendary": False
    }
    data_bytes = json.dumps(pokemon_data).encode('utf-8')
    
    response = client.post(
        "/stream",
        data=data_bytes,
        headers={"X-Grd-Signature": "invalid"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"
    
    # Verify stats were updated
    stats_response = client.get("/stats")
    stats = stats_response.json()["stream"]
    assert stats["request_count"] == 1
    assert stats["error_rate"] == 1.0  # 100% error rate
    assert stats["incoming_bytes"] > 0
    assert stats["outgoing_bytes"] == 0  # No response content for errors

def test_stream_endpoint_valid_data():
    # Test data
    pokemon_data = {
        "number": 1,
        "name": "Bulbasaur",
        "type_one": "Grass",
        "type_two": "Poison",
        "total": 318,
        "hit_points": 45,
        "attack": 49,
        "defense": 49,
        "special_attack": 65,
        "special_defense": 65,
        "speed": 45,
        "generation": 1,
        "legendary": False
    }
    data_bytes = json.dumps(pokemon_data).encode('utf-8')
    secret = base64.b64encode(b"test secret").decode()
    signature = generate_signature(data_bytes, secret)
    
    response = client.post(
        "/stream",
        data=data_bytes,
        headers={"X-Grd-Signature": signature}
    )
    
    # Since we don't have a mock for the downstream service,
    # we expect a 404 (no matching rule) or 500 (downstream error)
    assert response.status_code in [404, 500]
    
    # Verify stats were updated
    stats_response = client.get("/stats")
    stats = stats_response.json()["stream"]
    assert stats["request_count"] == 1
    assert stats["error_rate"] == 1.0  # 100% error rate since no matching rule
    assert stats["incoming_bytes"] > 0
    assert stats["outgoing_bytes"] == 0  # Should have response content even for errors

def test_stats_endpoint():
    # Make a request first to ensure stats are populated
    pokemon_data = {
        "number": 1,
        "name": "Bulbasaur",
        "type_one": "Grass",
        "type_two": "Poison",
        "total": 318,
        "hit_points": 45,
        "attack": 49,
        "defense": 49,
        "special_attack": 65,
        "special_defense": 65,
        "speed": 45,
        "generation": 1,
        "legendary": False
    }
    data_bytes = json.dumps(pokemon_data).encode('utf-8')
    secret = base64.b64encode(b"test secret").decode()
    signature = generate_signature(data_bytes, secret)
    
    client.post(
        "/stream",
        data=data_bytes,
        headers={"X-Grd-Signature": signature}
    )
    
    # Check stats
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stream" in data
    stats = data["stream"]
    assert stats["request_count"] == 1
    assert stats["error_rate"] == 1.0  # 100% error rate since no matching rule
    assert stats["incoming_bytes"] > 0
    assert stats["outgoing_bytes"] == 0
    assert stats["average_response_time"] >= 0
    assert stats["uptime_seconds"] >= 0 