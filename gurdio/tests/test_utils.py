import pytest
import base64
import hmac
import hashlib
import json
import time
from ..utils import ensure_data_integrity, evaluate_rule, parse_pokemon
from ..models import Rule, get_cached_pokemon_message
from ..pokemon_pb2 import Pokemon as ProtoPokemon
from google.protobuf.json_format import MessageToDict

def test_ensure_data_integrity():
    # Test data
    data = b"test data"
    secret = base64.b64encode(data).decode()
    
    # Generate valid signature
    secret_bytes = base64.b64decode(secret)
    valid_signature = hmac.new(
        secret_bytes,
        data,
        hashlib.sha256
    ).hexdigest()
    
    # Test valid signature
    assert ensure_data_integrity(data, valid_signature, secret) is True
    
    # Test invalid signature
    assert ensure_data_integrity(data, "invalid", secret) is False
    
    # Test invalid secret
    assert ensure_data_integrity(data, valid_signature, "invalid") is False

def test_evaluate_rule():
    # Test data
    pokemon = {
        "hit_points": 20,
        "type_two": "fire",
        "special_defense": 15,
        "generation": 1,
        "legendary": True
    }
    
    # Test rule
    rule = Rule(
        url="http://test.com",
        reason="test rule",
        match=[
            "hit_points==20",
            "type_two!=water",
            "special_defense > 10",
            "generation < 20",
            "legendary==True"
        ]
    )
    
    # Test matching rule
    assert evaluate_rule(pokemon, rule) is True
    
    # Test non-matching rule
    non_matching_rule = Rule(
        url="http://test.com",
        reason="test rule",
        match=["hit_points==30"]
    )
    assert evaluate_rule(pokemon, non_matching_rule) is False
    
    # Test invalid field
    invalid_field_rule = Rule(
        url="http://test.com",
        reason="test rule",
        match=["invalid_field==20"]
    )
    assert evaluate_rule(pokemon, invalid_field_rule) is False

def test_parse_empty_protobuf():
    """Test parsing an empty protobuf message."""
    # Create empty protobuf message
    proto_pokemon = ProtoPokemon()
    data_bytes = proto_pokemon.SerializeToString()
    
    # Parse and verify
    result = parse_pokemon(data_bytes)
    
    # All fields should be empty or have default values
    assert result == {
        "number": 0,
        "name": "",
        "type_one": "",
        "type_two": "",
        "total": 0,
        "hit_points": 0,
        "attack": 0,
        "defense": 0,
        "special_attack": 0,
        "special_defense": 0,
        "speed": 0,
        "generation": 0,
        "legendary": False
    }

def test_protobuf_creation_benchmark():
    """Benchmark the performance difference between cached and non-cached protobuf creation."""
    iterations = 100000
    
    # Benchmark non-cached creation
    start_time = time.time()
    for _ in range(iterations):
        pokemon = ProtoPokemon()
        pokemon.number = 1
        pokemon.name = "Test"
    non_cached_time = time.time() - start_time
    
    # Benchmark cached creation
    start_time = time.time()
    for _ in range(iterations):
        pokemon = get_cached_pokemon_message()
        pokemon.Clear()
        pokemon.number = 1
        pokemon.name = "Test"
    cached_time = time.time() - start_time
    
    # Calculate and print results
    speedup = non_cached_time / cached_time
    print(f"\nProtobuf Creation Benchmark (100,000 iterations):")
    print(f"Non-cached time: {non_cached_time:.3f} seconds")
    print(f"Cached time: {cached_time:.3f} seconds")
    print(f"Speedup: {speedup:.2f}x")
    
    # Verify the benchmark is meaningful
    assert cached_time < non_cached_time, "Cached version should be faster" 