import os
import time
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx

from gurdio.utils import ensure_data_integrity, evaluate_rule, load_config, parse_pokemon
from gurdio.models import Rule
from gurdio.stats import stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pokemon Stream Proxy")
config = load_config()

@app.post("/stream")
async def stream_endpoint(
    request: Request,
    x_grd_signature: Optional[str] = Header(None)
) -> JSONResponse:
    """
    Handle incoming Pokemon stream requests.
    
    Args:
        request (Request): The incoming request
        x_grd_signature (Optional[str]): HMAC-SHA256 signature of the request body
        
    Returns:
        JSONResponse: The response from the matched service
        
    Raises:
        HTTPException: If signature is missing, invalid, or no matching rule is found
    """
    if not x_grd_signature:
        raise HTTPException(status_code=401, detail="Missing signature header")

    body = await request.body()
    start_time = time.time()
    
    stats['stream'].incoming_bytes += len(body)

    try:
        # Check if HMAC_SECRET is set
        hmac_secret = os.getenv('HMAC_SECRET')
        if not hmac_secret:
            logger.error("HMAC_SECRET environment variable not set")
            raise HTTPException(status_code=500, detail="HMAC_SECRET environment variable not set")

        # Validate signature
        if not ensure_data_integrity(body, x_grd_signature, hmac_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")

        pokemon = parse_pokemon(body)
        
        # Find matching rule
        matched_rule = None
        for rule in config.rules:
            if evaluate_rule(pokemon, rule):
                matched_rule = rule
                break

        if not matched_rule:
            raise HTTPException(status_code=404, detail="No matching rule found")

        # Forward request
        async with httpx.AsyncClient() as client:
            headers = dict(request.headers)
            headers.pop('x-grd-signature', None)
            headers['X-Grd-Reason'] = matched_rule.reason

            response = await client.post(
                matched_rule.url,
                json=pokemon,
                headers=headers
            )

            # Update stats
            response_time = time.time() - start_time
            stats['stream'].add_request(
                incoming_bytes=len(body),
                outgoing_bytes=len(response.content),
                response_time=response_time,
                is_error=response.status_code >= 400
            )

            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        stats['stream'].add_request(incoming_bytes=len(body), 
                                    outgoing_bytes=0, 
                                    response_time=time.time() - start_time, 
                                    is_error=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def stats_endpoint() -> Dict[str, Dict[str, Any]]:
    """
    Return statistics for the proxy service.
    
    Returns:
        Dict[str, Dict[str, Any]]: Statistics for each endpoint
    """
    return {
        endpoint: {
            "request_count": stat.request_count,
            "error_rate": stat.error_rate,
            "incoming_bytes": stat.incoming_bytes,
            "outgoing_bytes": stat.outgoing_bytes,
            "average_response_time": stat.avg_response_time,
            "uptime_seconds": stat.uptime
        }
        for endpoint, stat in stats.items()
    } 