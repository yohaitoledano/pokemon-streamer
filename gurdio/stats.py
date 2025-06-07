import time
from collections import defaultdict

class Stats:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.incoming_bytes = 0
        self.outgoing_bytes = 0
        self.total_response_time = 0
        self.start_time = time.time()

    def add_request(self, incoming_bytes: int, outgoing_bytes: int, response_time: float, is_error: bool = False):
        self.request_count += 1
        self.incoming_bytes += incoming_bytes
        self.outgoing_bytes += outgoing_bytes
        self.total_response_time += response_time
        if is_error:
            self.error_count += 1

    @property
    def error_rate(self) -> float:
        return self.error_count / self.request_count if self.request_count > 0 else 0

    @property
    def avg_response_time(self) -> float:
        return self.total_response_time / self.request_count if self.request_count > 0 else 0

    @property
    def uptime(self) -> float:
        return time.time() - self.start_time

# Global stats dictionary
stats = defaultdict(Stats) 