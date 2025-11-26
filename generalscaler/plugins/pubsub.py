from google.cloud import pubsub_v1
from .base import MetricPlugin

class PubSubPlugin(MetricPlugin):
    def get_metric_value(self, config):
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(
            config["project_id"],
            config["subscription"]
        )
        response = subscriber.get_subscription(subscription=subscription_path)
        return float(getattr(response, "num_undelivered_messages", 0))
    
    def validate_config(self, config: dict) -> bool:
        """Validate that config has required fields"""
        return "project_id" in config and "subscription" in config

