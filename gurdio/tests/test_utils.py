import pytest
import base64
import hmac
import hashlib
from ..utils import ensure_data_integrity, evaluate_rule
from ..models import Rule

def test_ensure_data_integrity():
    # Test data
    data = b"test data"
    secret = base64.b64encode(b"test secret").decode()
    
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
            "legendary==true"
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