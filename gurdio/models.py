from typing import List, Optional
from pydantic import BaseModel

class Rule(BaseModel):
    url: str
    reason: str
    match: List[str]

class Config(BaseModel):
    rules: List[Rule]

class Pokemon(BaseModel):
    number: int
    name: str
    type_one: str
    type_two: Optional[str] = None
    total: int
    hit_points: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    generation: int
    legendary: bool 