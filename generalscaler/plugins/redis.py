import redis
from .base import MetricPlugin

class RedisPlugin(MetricPlugin):
    def get_metric_value(self, config):
        r = redis.Redis(
            host=config.get("host", "redis"),
            port=config.get("port", 6379)
        )
        key = config["queue_key"]
        return float(r.llen(key))
    
    def validate_config(self, config: dict) -> bool:
        """Validate that config has required 'queue_key' field"""
        return "queue_key" in config

