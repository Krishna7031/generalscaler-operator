import pytest
from generalscaler.plugins.prometheus import PrometheusPlugin
from generalscaler.plugins.redis import RedisPlugin
from generalscaler.plugins.pubsub import PubSubPlugin

# Test Prometheus Plugin
class TestPrometheusPlugin:
    def test_validate_config_valid(self):
        """Config with 'query' should be valid"""
        plugin = PrometheusPlugin()
        config = {"query": "up"}
        assert plugin.validate_config(config) == True
    
    def test_validate_config_invalid(self):
        """Config without 'query' should be invalid"""
        plugin = PrometheusPlugin()
        config = {}
        assert plugin.validate_config(config) == False

# Test Redis Plugin
class TestRedisPlugin:
    def test_validate_config_valid(self):
        """Config with 'queue_key' should be valid"""
        plugin = RedisPlugin()
        config = {"queue_key": "jobs"}
        assert plugin.validate_config(config) == True
    
    def test_validate_config_invalid(self):
        """Config without 'queue_key' should be invalid"""
        plugin = RedisPlugin()
        config = {}
        assert plugin.validate_config(config) == False

# Test Pub/Sub Plugin
class TestPubSubPlugin:
    def test_validate_config_valid(self):
        """Config with project_id and subscription should be valid"""
        plugin = PubSubPlugin()
        config = {"project_id": "my-project", "subscription": "my-sub"}
        assert plugin.validate_config(config) == True
    
    def test_validate_config_invalid_missing_project(self):
        """Config without project_id should be invalid"""
        plugin = PubSubPlugin()
        config = {"subscription": "my-sub"}
        assert plugin.validate_config(config) == False

