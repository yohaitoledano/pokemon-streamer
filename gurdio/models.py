from typing import List, Optional
from pydantic import BaseModel
from google.protobuf.json_format import Parse, MessageToDict
from .pokemon_pb2 import Pokemon as ProtoPokemon

class Rule(BaseModel):
    url: str
    reason: str
    match: List[str]

class Config(BaseModel):
    rules: List[Rule]

def parse_proto_pokemon(data: bytes) -> dict:
    """Parse Pokemon data from protobuf bytes to dict."""
    pokemon = ProtoPokemon()
    pokemon.ParseFromString(data)
    return MessageToDict(pokemon, preserving_proto_field_name=True) 