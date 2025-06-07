import os
import sys

os.environ['POKEPROXY_CONFIG'] = r'C:\Users\yohai\pokemon-streamer\pokemon-streamer\gurdio\POKEPROXY_CONFIG.json'

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 