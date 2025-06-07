from typing import List
from pydantic import BaseModel

class Rule(BaseModel):
    url: str
    reason: str
    match: List[str]

class Config(BaseModel):
    rules: List[Rule] 