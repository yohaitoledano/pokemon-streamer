import os
os.environ['POKEPROXY_CONFIG'] = r'C:\Users\yohai\pokemon-streamer\pokemon-streamer\gurdio\POKEPROXY_CONFIG.json'

import uvicorn
from gurdio.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 