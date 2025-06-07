from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from google.protobuf.json_format import Parse, MessageToDict
from .pokemon_pb2 import Pokemon as ProtoPokemon

class Rule(BaseModel):
    url: str
    reason: str
    match: List[str]

class Config(BaseModel):
    rules: List[Rule]

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
    pokemon = ProtoPokemon()
    pokemon.ParseFromString(data)
    return MessageToDict(pokemon, preserving_proto_field_name=True) 