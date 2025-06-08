import os
import time
import logging
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Header, Body
from fastapi.responses import JSONResponse
import httpx
import ssl
from pydantic import BaseModel

from gurdio.utils import ensure_data_integrity, evaluate_rule, load_config, parse_pokemon
from gurdio.models import Rule
from gurdio.stats import stats


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pokemon Stream Proxy",
    description="A proxy service for handling Pokemon stream data with rule-based routing and statistics tracking.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=[
        {"url": "https://localhost:8000", "description": "Local HTTPS server"}
    ]
)

config = load_config()

class PokemonData(BaseModel):
    """Pokemon data model for the stream endpoint."""
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
    legendary: bool = False

class StatsResponse(BaseModel):
    """Statistics response model."""
    request_count: int
    error_rate: float
    incoming_bytes: int
    outgoing_bytes: int
    average_response_time: float
    uptime_seconds: float

@app.post("/stream", 
    response_model=Dict[str, Any],
    summary="Handle Pokemon stream requests",
    description="Process incoming Pokemon data and forward it based on matching rules. Requires HMAC-SHA256 signature for authentication.",
    responses={
        200: {
            "description": "Successfully processed and forwarded Pokemon data",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Pokemon data forwarded successfully"
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Missing signature header"
                    }
                }
            }
        },
        404: {
            "description": "No matching rule found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No matching rule found"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def stream_endpoint(
    request: Request,
    x_grd_signature: str = Header(..., description="HMAC-SHA256 signature of the request body")
) -> JSONResponse:
    """
    Handle incoming Pokemon stream requests.
    
    Args:
        request: The incoming request
        x_grd_signature: HMAC-SHA256 signature of the request body
        
    Returns:
        JSONResponse: The response from the matched service
        
    Raises:
        HTTPException: If signature is missing, invalid, or no matching rule is found
    """
    start_time = time.time()
    body = await request.body()
    incoming_bytes = len(body)
    outgoing_bytes = 0
    is_error = False

    try:
        # Check if HMAC_SECRET is set
        hmac_secret = os.getenv('HMAC_SECRET')
        if not hmac_secret:
            is_error = True
            logger.error("HMAC_SECRET environment variable not set")
            raise HTTPException(status_code=500, detail="HMAC_SECRET environment variable not set")

        # Validate signature
        if not ensure_data_integrity(body, x_grd_signature, hmac_secret):
            is_error = True
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse and validate Pokemon data
        try:
            pokemon_data = json.loads(body)
            pokemon = PokemonData(**pokemon_data)
        except (json.JSONDecodeError, ValueError) as e:
            is_error = True
            raise HTTPException(status_code=422, detail=f"Invalid Pokemon data: {str(e)}")
        
        # Find matching rule
        matched_rule = None
        for rule in config.rules:
            if evaluate_rule(pokemon.dict(), rule):
                matched_rule = rule
                break

        if not matched_rule:
            is_error = True
            raise HTTPException(status_code=404, detail="No matching rule found")

        # Forward request with SSL verification
        async with httpx.AsyncClient(verify=True) as client:  # Enable SSL verification
            headers = dict(request.headers)
            headers.pop('x-grd-signature', None)
            headers['X-Grd-Reason'] = matched_rule.reason
            url = matched_rule.url

            response = await client.post(
                url,
                json=pokemon.dict(),
                headers=headers
            )
            outgoing_bytes = len(response.content)
            is_error = response.status_code >= 400

            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )

    except HTTPException as e:
        is_error = True
        logger.error(f"Request error: {str(e)}")
        raise
    except httpx.RequestError as e:
        is_error = True
        raise HTTPException(status_code=500, detail="Error forwarding request")
    except Exception as e:
        is_error = True
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Update stats in finally block to ensure they're always updated
        response_time = time.time() - start_time
        logger.info(f"Updating stats - incoming_bytes: {incoming_bytes}, outgoing_bytes: {outgoing_bytes}, response_time: {response_time}")
        stats.add_request(
            endpoint='stream',
            incoming_bytes=incoming_bytes,
            outgoing_bytes=outgoing_bytes,
            response_time=response_time,
            is_error=is_error
        )
        logger.info(f"Current stats: {stats.get_stats('stream')}")

@app.get("/stats", 
    response_model=Dict[str, Dict[str, Any]],
    summary="Get service statistics",
    description="Returns current statistics for the proxy service including request counts, error rates, and performance metrics.",
    responses={
        200: {
            "description": "Successfully retrieved statistics",
            "content": {
                "application/json": {
                    "example": {
                        "stream": {
                            "request_count": 100,
                            "error_rate": 0.05,
                            "incoming_bytes": 10240,
                            "outgoing_bytes": 5120,
                            "average_response_time": 0.15,
                            "uptime_seconds": 3600
                        }
                    }
                }
            }
        }
    }
)
async def stats_endpoint() -> Dict[str, Dict[str, Any]]:
    """
    Return statistics for the proxy service.
    
    Returns:
        Dict[str, Dict[str, Any]]: Statistics for each endpoint including:
            - request_count: Total number of requests
            - error_rate: Rate of failed requests
            - incoming_bytes: Total bytes received
            - outgoing_bytes: Total bytes sent
            - average_response_time: Average request processing time
            - uptime_seconds: Service uptime in seconds
    """
    return stats.get_all_stats() 