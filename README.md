# Pokemon Stream Proxy

A high-performance proxy service for handling Pokemon stream data with rule-based routing and statistics tracking.

## Features

- Protocol Buffers for efficient serialization
- Configurable routing rules
- HTTPS support with SSL verification
- Real-time statistics tracking
- Interactive API documentation with Swagger UI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pokemon-streamer.git
cd pokemon-streamer
```

2. Install dependencies:
```bash
pip install -e .
```

## Configuration

Create a `POKEPROXY_CONFIG.json` file in your project root:

```json
{
    "rules": [
        {
            "name": "legendary_pokemon",
            "condition": "pokemon.legendary == true",
            "url": "https://my-special-awesome-pokemon-service.com/legendary",
            "reason": "Legendary Pokemon detected"
        },
        {
            "name": "high_stats",
            "condition": "pokemon.total >= 600",
            "url": "https://my-special-awesome-pokemon-service.com/powerful",
            "reason": "High total stats detected"
        }
    ]
}
```

## Usage

1. Set the HMAC secret for request validation:
```bash
export HMAC_SECRET="your-secret-key"
```

2. Generate SSL certificates (if you don't have them):
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

3. Start the service with HTTPS:
```bash
uvicorn gurdio.api:app --reload --ssl-keyfile key.pem --ssl-certfile cert.pem
```

4. Access the API:
- Main endpoint: `https://localhost:8000/stream`
- Statistics: `https://localhost:8000/stats`
- API Documentation: `http://localhost:8000/docs`

## API Documentation

The service provides interactive API documentation using Swagger UI. You can access it at:
```
http://localhost:8000/docs
```

This interface allows you to:
- View detailed API documentation
- Test API endpoints directly from the browser
- See request/response schemas
- View example requests and responses
- Understand authentication requirements

## Project Structure

```
pokemon-streamer/
├── gurdio/
│   ├── __init__.py
│   ├── api.py              # FastAPI application
│   ├── models.py           # Data models
│   ├── utils.py            # Utility functions
│   ├── stats.py            # Statistics tracking
│   ├── pokemon.proto       # Protocol Buffer definition
│   └── pokemon_pb2.py      # Generated Protocol Buffer code
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_models.py
│   └── test_utils.py
├── setup.py
└── README.md
```

## Dependencies

- FastAPI
- Protocol Buffers
- httpx
- pydantic
- grpcio-tools

## License

MIT 
