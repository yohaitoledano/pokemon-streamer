import pytest
import time
from ..stats import Stats

def test_stats_initialization():
    stats = Stats()
    assert stats.request_count == 0
    assert stats.error_count == 0
    assert stats.incoming_bytes == 0
    assert stats.outgoing_bytes == 0
    assert stats.total_response_time == 0
    assert stats.start_time > 0

def test_stats_add_request():
    stats = Stats()
    
    # Test successful request
    stats.add_request(100, 200, 0.5)
    assert stats.request_count == 1
    assert stats.error_count == 0
    assert stats.incoming_bytes == 100
    assert stats.outgoing_bytes == 200
    assert stats.total_response_time == 0.5
    
    # Test error request
    stats.add_request(50, 0, 0.2, is_error=True)
    assert stats.request_count == 2
    assert stats.error_count == 1
    assert stats.incoming_bytes == 150
    assert stats.outgoing_bytes == 200
    assert stats.total_response_time == 0.7

def test_stats_properties():
    stats = Stats()
    
    # Test with no requests
    assert stats.error_rate == 0
    assert stats.avg_response_time == 0
    
    # Test with requests
    stats.add_request(100, 200, 0.5)
    stats.add_request(100, 200, 1.5)
    assert stats.error_rate == 0
    assert stats.avg_response_time == 1.0
    
    # Test with errors
    stats.add_request(100, 0, 0.5, is_error=True)
    assert stats.error_rate == 1/3

def test_stats_uptime():
    stats = Stats()
    time.sleep(0.1)  # Wait a bit
    uptime = stats.uptime
    assert uptime >= 0.1  # Should be at least 0.1 seconds 