from abc import ABC, abstractmethod

class MetricPlugin(ABC):
    @abstractmethod
    def get_metric_value(self, config: dict) -> float:
        # Reads current value from the metric source (Prometheus, Redis, PubSub, etc.)
        pass

