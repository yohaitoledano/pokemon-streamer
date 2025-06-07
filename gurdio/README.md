# Pokemon Stream Proxy

A FastAPI-based proxy service for handling Pokemon stream data with rule-based routing and statistics tracking.

## Features

- HMAC-SHA256 signature validation
- Rule-based request routing
- Real-time statistics tracking
- Protocol Buffers for efficient serialization
- Configurable routing rules

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -e .
```

## Configuration

Create a configuration file (e.g., `POKEPROXY_CONFIG.json`):
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
python -m gurdio.main
```

The service will start on `http://localhost:8000`

## API Endpoints

### POST /stream
Handles incoming Pokemon stream requests.

Headers:
- `X-Grd-Signature`: HMAC-SHA256 signature of the request body

Request Body:
- Protocol Buffer serialized Pokemon data

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
pytest gurdio/tests/
```

## Project Structure

```
gurdio/
├── __init__.py
├── api.py           # FastAPI endpoints
├── models.py        # Data models and protobuf handling
├── pokemon.proto    # Protocol Buffer definition
├── pokemon_pb2.py   # Generated protobuf code
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

- FastAPI==0.104.1
- uvicorn==0.24.0
- httpx==0.25.1
- protobuf>=4.25.1,<7.0.0
- pydantic==2.4.2
- pytest==7.4.3 (for testing)
- pytest-asyncio==0.21.1 (for testing)
- grpcio-tools>=1.72.1 (for protobuf generation) 