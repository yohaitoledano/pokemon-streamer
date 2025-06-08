from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from google.protobuf.json_format import Parse, MessageToDict
from gurdio.pokemon_pb2 import Pokemon as ProtoPokemon
from functools import lru_cache

class Rule(BaseModel):
    url: str
    reason: str
    match: List[str]

class Config(BaseModel):
    rules: List[Rule]

@lru_cache(maxsize=1)
def get_cached_pokemon_message() -> ProtoPokemon:
    """
    Get a cached instance of the Pokemon protobuf message type.
    
    This function uses LRU cache with maxsize=1 because:
    1. We only need one instance of the message type
    2. The message type is immutable and acts as a template
    3. We reuse this instance for all parsing operations
    4. The instance is cleared before each use to prevent data leakage
    
    Returns:
        ProtoPokemon: A cached instance of the Pokemon protobuf message
    """
    return ProtoPokemon()

def parse_proto_pokemon(data: bytes) -> Dict[str, Any]:
    """
    Parse Pokemon data from protobuf bytes to dict.
    
    Args:
        data (bytes): The protobuf serialized data
        
    Returns:
        Dict[str, Any]: Dictionary representation of the Pokemon data
        
    Raises:
        Exception: If the protobuf data is invalid or cannot be parsed
    """
    pokemon = get_cached_pokemon_message()
    pokemon.Clear()  # Clear any previous data
    pokemon.ParseFromString(data)
    
    # Convert to dict with proper types
    result = {}
    for field in pokemon.DESCRIPTOR.fields:
        value = getattr(pokemon, field.name)
        if field.type == field.TYPE_UINT64:
            result[field.name] = int(value)
        elif field.type == field.TYPE_BOOL:
            result[field.name] = bool(value)
        else:
            result[field.name] = str(value)
            
    return result 