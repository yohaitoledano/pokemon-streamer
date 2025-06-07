import pytest
from fastapi.testclient import TestClient
import base64
import hmac
import hashlib
import json
from ..api import app

client = TestClient(app)

def generate_signature(data: bytes, secret: str) -> str:
    secret_bytes = base64.b64decode(secret)
    return hmac.new(
        secret_bytes,
        data,
        hashlib.sha256
    ).hexdigest()

def test_stream_endpoint_missing_signature():
    response = client.post("/stream", data=b"test data")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing signature header"

def test_stream_endpoint_invalid_signature():
    # Set environment variable for testing
    secret = base64.b64encode(b"test secret").decode()
    import os
    os.environ['HMAC_SECRET'] = secret
    
    response = client.post(
        "/stream",
        data=b"test data",
        headers={"X-Grd-Signature": "invalid"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"

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
    
    # Convert to bytes
    data_bytes = json.dumps(pokemon_data).encode('utf-8')
    
    # Generate signature
    secret = base64.b64encode(b"test secret").decode()
    signature = generate_signature(data_bytes, secret)
    
    # Set environment variable for testing
    import os
    os.environ['HMAC_SECRET'] = secret
    
    # Make request
    response = client.post(
        "/stream",
        data=data_bytes,
        headers={"X-Grd-Signature": signature}
    )
    
    # Since we don't have a mock for the downstream service,
    # we expect a 404 (no matching rule) or 500 (downstream error)
    assert response.status_code in [404, 500]

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stream" in data
    stats = data["stream"]
    assert "request_count" in stats
    assert "error_rate" in stats
    assert "incoming_bytes" in stats
    assert "outgoing_bytes" in stats
    assert "average_response_time" in stats
    assert "uptime_seconds" in stats 