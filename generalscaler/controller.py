import kopf
from kubernetes import client, config
# Import your plugin and policy classes
from .plugins.prometheus import PrometheusPlugin
from .plugins.redis import RedisPlugin
from .plugins.pubsub import PubSubPlugin
from .policies.slo_policy import SLOPolicy
from .policies.cost_policy import CostPolicy
from .scaler import SafeScaler

# Register plugin types
PLUGINS = {
    "prometheus": PrometheusPlugin,
    "redis": RedisPlugin,
    "pubsub": PubSubPlugin
}
POLICIES = {
    "slo": SLOPolicy,
    "cost": CostPolicy
}

scaler = SafeScaler()

@kopf.on.create('autoscaling.example.com', 'v1', 'generalscalers')
@kopf.on.update('autoscaling.example.com', 'v1', 'generalscalers')
@kopf.timer('autoscaling.example.com', 'v1', 'generalscalers', interval=30.0)
def reconcile(spec, name, namespace, **kwargs):
    """
    This runs every 30 seconds, and whenever a GeneralScaler object is created or updated.
    """
    # 1. Get GeneralScaler config values
    target_deployment = spec["targetDeployment"]
    min_replicas = int(spec.get("minReplicas", 1))
    max_replicas = int(spec.get("maxReplicas", 10))
    metrics_config = spec.get("metrics", [])
    policy_config = spec.get("policy", {})
    safety_config = spec.get("safety", {})

    # 2. Get current replica count from Kubernetes
    apps_v1 = client.AppsV1Api()
    deployment = apps_v1.read_namespaced_deployment(target_deployment, namespace)
    current_replicas = deployment.spec.replicas

    # 3. Read metrics from plugins
    metric_values = []
    target_values = []
    for metric in metrics_config:
        plugin_type = metric["type"]
        plugin_class = PLUGINS.get(plugin_type)
        if not plugin_class:
            print(f"Unknown metrics plugin: {plugin_type}")
            continue
        plugin = plugin_class()
        value = plugin.get_metric_value(metric["config"])
        metric_values.append(value)
        target_values.append(metric.get("targetValue", 100))
    # Use average if there are multiple metrics
    avg_metric_value = sum(metric_values) / len(metric_values) if metric_values else 0
    avg_target_value = sum(target_values) / len(target_values) if target_values else 1

    # 4. Decide scaling using policy
    policy_type = policy_config.get("type", "slo")
    policy_class = POLICIES.get(policy_type)
    if not policy_class:
        print(f"Unknown policy: {policy_type}")
        return
    # For cost policy, pass settings from 'config' if needed
    if policy_type == "cost":
        max_cost = policy_config.get("config", {}).get("maxCostPerHour", 50)
        cost_per_pod = policy_config.get("config", {}).get("costPerPod", 0.5)
        policy = policy_class(max_cost_per_hour=max_cost, cost_per_pod=cost_per_pod)
    else:
        policy = policy_class()
    desired_replicas = policy.should_scale(
        current_value=avg_metric_value,
        target_value=avg_target_value,
        current_replicas=current_replicas,
        min_replicas=min_replicas,
        max_replicas=max_replicas
    )

    # 5. Call SafeScaler to enact scaling
    scaler.scale_deployment(
        namespace=namespace,
        deployment_name=target_deployment,
        desired_replicas=desired_replicas,
        safety_config=safety_config
    )

    return {'message': f'Reconciled {name}, desired replicas: {desired_replicas}'}

if __name__ == '__main__':
    # This lets you run the operator locally for testing
    config.load_kube_config()
    kopf.run()

