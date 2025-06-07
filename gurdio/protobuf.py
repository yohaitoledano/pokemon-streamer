from google.protobuf.json_format import Parse
from .pokemon_pb2 import Pokemon

def parse_pokemon(data: bytes) -> dict:
    pokemon = Pokemon()
    pokemon.ParseFromString(data)
    return {
        "number": pokemon.number,
        "name": pokemon.name,
        "type_one": pokemon.type_one,
        "type_two": pokemon.type_two,
        "total": pokemon.total,
        "hit_points": pokemon.hit_points,
        "attack": pokemon.attack,
        "defense": pokemon.defense,
        "special_attack": pokemon.special_attack,
        "special_defense": pokemon.special_defense,
        "speed": pokemon.speed,
        "generation": pokemon.generation,
        "legendary": pokemon.legendary
    } 