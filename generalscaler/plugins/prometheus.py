import requests
from .base import MetricPlugin

class PrometheusPlugin(MetricPlugin):
    def __init__(self, url="http://prometheus:9090"):
        self.url = url

    def get_metric_value(self, config):
        query = config.get("query")
        response = requests.get(
            f"{self.url}/api/v1/query",
            params={"query": query}
        )
        result = response.json()
        try:
            return float(result["data"]["result"][0]["value"][1])
        except Exception:
            return 0.0
    
    def validate_config(self, config: dict) -> bool:
        """Validate that config has required 'query' field"""
        return "query" in config

