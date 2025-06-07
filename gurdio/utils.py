import os
import json
import hmac
import hashlib
import base64
import logging
from typing import Dict, Any
from gurdio.models import Config, Rule, Pokemon

logger = logging.getLogger(__name__)

def load_config() -> Config:
    config_path = os.getenv('POKEPROXY_CONFIG')
    if not config_path:
        logger.exception("Can't find POKEPROXY_CONFIG environment variable. " \
                         "Please set it with path to your config file")
        raise ValueError("POKEPROXY_CONFIG environment variable not set")
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    return Config(**config_data)

def ensure_data_integrity(data: bytes, signature: str, secret: str) -> bool:
    """
    Validates the integrity of incoming data using HMAC-SHA256.
    
    This function performs the following checks:
    1. Verifies that the provided signature matches the HMAC-SHA256 hash of the data
    2. Ensures the secret is properly base64 encoded
    3. Validates that the data hasn't been tampered with during transmission
    
    Args:
        data (bytes): The raw request body data to verify
        signature (str): The HMAC-SHA256 signature provided in the X-Grd-Signature header
        secret (str): The base64-encoded HMAC secret used for verification
    
    Returns:
        bool: True if the data integrity check passes, False otherwise
    
    Raises:
        ValueError: If the secret is not properly base64 encoded
    """
    try:
        secret_bytes = base64.b64decode(secret)
        expected_signature = hmac.new(
            secret_bytes,
            data,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Data integrity check failed: {str(e)}")
        return False

def evaluate_rule(pokemon: Dict[str, Any], rule: Rule) -> bool:
    """Evaluate if a Pokemon matches a rule's conditions."""
    # Validate inputs
    if not isinstance(pokemon, dict):
        logger.error("Invalid pokemon: must be a dictionary")
        return False
        
    if not isinstance(rule, Rule):
        logger.error(f"Invalid rule: must be a Rule instance, got {type(rule)}")
        return False
        
    if not rule.match:
        logger.error("Invalid rule: match conditions are empty")
        return False

    for condition in rule.match:
        try:
            if not isinstance(condition, str):
                logger.error(f"Invalid condition: {condition} must be a string")
                return False
                
            # Split on operators, preserving the operator
            if "==" in condition:
                field, value = condition.split("==")
                op = "=="
            elif "!=" in condition:
                field, value = condition.split("!=")
                op = "!="
            elif ">" in condition:
                field, value = condition.split(">")
                op = ">"
            elif "<" in condition:
                field, value = condition.split("<")
                op = "<"
            else:
                logger.error(f"Invalid condition format: {condition}. Expected 'field operator value'")
                return False
                
            # Strip whitespace
            field = field.strip()
            value = value.strip()
            
            field_value = pokemon.get(field)
            
            if field_value is None:
                logger.error(f"Field {field} not found in pokemon data")
                return False
                
            if op == '==':
                if isinstance(field_value, bool):
                    return field_value == (value.lower() == 'true')
                return str(field_value) == value
            elif op == '!=':
                if isinstance(field_value, bool):
                    return field_value != (value.lower() == 'true')
                return str(field_value) != value
            elif op == '>':
                return float(field_value) > float(value)
            elif op == '<':
                return float(field_value) < float(value)
            else:
                logger.error(f"Invalid operator: {op}. Allowed operators are ==, !=, >, <")
                return False
        except Exception as e:
            logger.error(f"Error evaluating rule condition {condition}: {str(e)}")
            return False
    return True

def parse_pokemon(data: bytes) -> dict:
    # Convert bytes to string and parse as JSON
    pokemon_data = json.loads(data.decode('utf-8'))
    pokemon = Pokemon(**pokemon_data)
    return pokemon.model_dump() 