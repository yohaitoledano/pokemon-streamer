import pytest
import base64
import hmac
import hashlib
import json
from ..utils import ensure_data_integrity, evaluate_rule, parse_pokemon
from ..models import Rule
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
    
    # Create protobuf message
    proto_pokemon = ProtoPokemon()
    proto_pokemon.number = pokemon_data["number"]
    proto_pokemon.name = pokemon_data["name"]
    proto_pokemon.type_one = pokemon_data["type_one"]
    proto_pokemon.type_two = pokemon_data["type_two"]
    proto_pokemon.total = pokemon_data["total"]
    proto_pokemon.hit_points = pokemon_data["hit_points"]
    proto_pokemon.attack = pokemon_data["attack"]
    proto_pokemon.defense = pokemon_data["defense"]
    proto_pokemon.special_attack = pokemon_data["special_attack"]
    proto_pokemon.special_defense = pokemon_data["special_defense"]
    proto_pokemon.speed = pokemon_data["speed"]
    proto_pokemon.generation = pokemon_data["generation"]
    proto_pokemon.legendary = pokemon_data["legendary"]
    
    # Convert to bytes
    data_bytes = proto_pokemon.SerializeToString()
    
    # Parse and verify
    result = parse_pokemon(data_bytes)
    proto_dict = MessageToDict(proto_pokemon, preserving_proto_field_name=True)
    
    assert result == proto_dict
    
    # Test with invalid data
    with pytest.raises(Exception):
        parse_pokemon(b"invalid protobuf data") 