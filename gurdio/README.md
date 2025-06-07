# Pokemon Stream Proxy

A FastAPI-based proxy service for handling Pokemon stream data with rule-based routing and statistics tracking.

## Features

- HMAC-SHA256 signature validation
- Rule-based request routing
- Real-time statistics tracking
- Protobuf message handling
- Configurable routing rules

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a configuration file (e.g., `config.json`):
```json
{
    "rules": [
        {
            "url": "http://my-special-awesome-pokemon-service.com",
            "reason": "awesome pokemon",
            "match": [
                "hit_points==20",
                "type_two!=word",
                "special_defense > 10",
                "generation < 20"
            ]
        }
    ]
}
```

## Environment Variables

- `POKEPROXY_CONFIG`: Path to the configuration file
- `HMAC_SECRET`: Base64-encoded HMAC secret for signature validation

## Running the Service

```bash
python -m demo_app.gurdio.main
```

The service will start on `http://localhost:8000`

## API Endpoints

### POST /stream
Handles incoming Pokemon stream requests.

Headers:
- `X-Grd-Signature`: HMAC-SHA256 signature of the request body

### GET /stats
Returns statistics for the proxy service.

Response:
```json
{
    "stream": {
        "request_count": 0,
        "error_rate": 0.0,
        "incoming_bytes": 0,
        "outgoing_bytes": 0,
        "average_response_time": 0.0,
        "uptime_seconds": 0.0
    }
}
```

## Running Tests

```bash
pytest demo_app/gurdio/tests/
```

## Project Structure

```
demo_app/gurdio/
├── __init__.py
├── api.py           # FastAPI endpoints
├── models.py        # Data models
├── stats.py         # Statistics tracking
├── utils.py         # Helper functions
├── main.py          # Application entry point
└── tests/           # Unit tests
    ├── __init__.py
    ├── test_api.py
    ├── test_stats.py
    └── test_utils.py
```

## Dependencies

- FastAPI
- uvicorn
- httpx
- protobuf
- pydantic
- pytest (for testing) 