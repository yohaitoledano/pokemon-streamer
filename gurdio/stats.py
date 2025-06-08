import time
from collections import defaultdict

class Stats:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Stats, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.stats = defaultdict(self._create_stats)
        # Initialize stream endpoint stats
        self.stats['stream'] = self._create_stats()
        self._initialized = True
    
    def _create_stats(self):
        return {
            'request_count': 0,
            'error_count': 0,
            'incoming_bytes': 0,
            'outgoing_bytes': 0,
            'total_response_time': 0,
            'start_time': time.time()
        }
    
    def add_request(self, endpoint: str, incoming_bytes: int, 
                    outgoing_bytes: int, 
                    response_time: float, 
                    is_error: bool = False):
        if endpoint not in self.stats:
            self.stats[endpoint] = self._create_stats()
            
        stat = self.stats[endpoint]
        stat['request_count'] += 1
        stat['incoming_bytes'] += incoming_bytes
        stat['outgoing_bytes'] += outgoing_bytes
        stat['total_response_time'] += response_time
        if is_error:
            stat['error_count'] += 1
    
    def get_stats(self, endpoint: str) -> dict:
        if endpoint not in self.stats:
            self.stats[endpoint] = self._create_stats()
            
        stat = self.stats[endpoint]
        return {
            'request_count': stat['request_count'],
            'error_rate': stat['error_count'] / stat['request_count'] if stat['request_count'] > 0 else 0,
            'incoming_bytes': stat['incoming_bytes'],
            'outgoing_bytes': stat['outgoing_bytes'],
            'average_response_time': stat['total_response_time'] / stat['request_count'] if stat['request_count'] > 0 else 0,
            'uptime_seconds': time.time() - stat['start_time']
        }
    
    def get_all_stats(self) -> dict:
        all_stats = {endpoint: self.get_stats(endpoint) for endpoint in self.stats}
        return all_stats

#ToDO - use persistent DB in thread safe manner 
stats = Stats() 