import pytest
import time
from ..stats import Stats

@pytest.fixture(autouse=True)
def reset_stats():
    """Reset the Stats singleton before each test."""
    Stats._instance = None
    yield
    Stats._instance = None

def test_stats_initialization():
    stats = Stats()
    stream_stats = stats.get_stats('stream')
    assert stream_stats['request_count'] == 0
    assert stream_stats['error_rate'] == 0
    assert stream_stats['incoming_bytes'] == 0
    assert stream_stats['outgoing_bytes'] == 0
    assert stream_stats['average_response_time'] == 0
    assert stream_stats['uptime_seconds'] >= 0

def test_stats_add_request():
    stats = Stats()
    
    # Test successful request
    stats.add_request('stream', 100, 200, 0.5)
    stream_stats = stats.get_stats('stream')
    assert stream_stats['request_count'] == 1
    assert stream_stats['error_rate'] == 0
    assert stream_stats['incoming_bytes'] == 100
    assert stream_stats['outgoing_bytes'] == 200
    assert stream_stats['average_response_time'] == 0.5
    
    # Test error request
    stats.add_request('stream', 50, 0, 0.2, is_error=True)
    stream_stats = stats.get_stats('stream')
    assert stream_stats['request_count'] == 2
    assert stream_stats['error_rate'] == 0.5  # 1 error out of 2 requests
    assert stream_stats['incoming_bytes'] == 150
    assert stream_stats['outgoing_bytes'] == 200
    assert stream_stats['average_response_time'] == 0.35  # (0.5 + 0.2) / 2

def test_stats_singleton():
    stats1 = Stats()
    stats2 = Stats()
    assert stats1 is stats2  # Should be the same instance
    
    # Test that stats are shared between instances
    stats1.add_request('stream', 100, 200, 0.5)
    stream_stats = stats2.get_stats('stream')
    assert stream_stats['request_count'] == 1
    assert stream_stats['incoming_bytes'] == 100

def test_stats_multiple_endpoints():
    stats = Stats()
    
    # Add requests to different endpoints
    stats.add_request('stream', 100, 200, 0.5)
    stats.add_request('other', 50, 100, 0.3)
    
    all_stats = stats.get_all_stats()
    assert 'stream' in all_stats
    assert 'other' in all_stats
    
    stream_stats = all_stats['stream']
    assert stream_stats['request_count'] == 1
    assert stream_stats['incoming_bytes'] == 100
    
    other_stats = all_stats['other']
    assert other_stats['request_count'] == 1
    assert other_stats['incoming_bytes'] == 50

def test_stats_uptime():
    stats = Stats()
    time.sleep(0.1)  # Wait a bit
    stream_stats = stats.get_stats('stream')
    assert stream_stats['uptime_seconds'] >= 0.1  # Should be at least 0.1 seconds 