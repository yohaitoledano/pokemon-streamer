import pytest
import base64
import hmac
import hashlib
import json
from ..utils import ensure_data_integrity, evaluate_rule, parse_pokemon
from ..models import Rule, Pokemon

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

def test_parse_pokemon():
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
    
    # Parse and verify
    result = parse_pokemon(data_bytes)
    assert result == pokemon_data
    
    # Test with invalid data
    with pytest.raises(Exception):
        parse_pokemon(b"invalid json") 