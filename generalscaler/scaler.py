from kubernetes import client
import time

class SafeScaler:
    """
    Handles safe scaling operations with cooldown and rate limits
    """
    
    def __init__(self):
        # Track last scaling time for each deployment
        # Example: {"default/my-app": 1732612345.67}
        self.last_scale_time = {}
        
        # Kubernetes API client for scaling deployments
        self.apps_v1 = client.AppsV1Api()
    
    def scale_deployment(self, namespace, deployment_name, desired_replicas, safety_config):
        """
        Safely scale a deployment with cooldown and rate limits
        
        Args:
            namespace: Kubernetes namespace (e.g., "default")
            deployment_name: Name of deployment (e.g., "http-app")
            desired_replicas: How many pods we want (e.g., 5)
            safety_config: Safety settings from CRD
                {
                    "cooldownSeconds": 300,
                    "maxScaleUpRate": 2,
                    "maxScaleDownRate": 1
                }
        
        Returns:
            True if scaling happened, False if blocked by safety
        """
        
        # Create unique key for this deployment
        key = f"{namespace}/{deployment_name}"
        
        # Get safety settings (with defaults)
        cooldown = safety_config.get("cooldownSeconds", 300)  # 5 minutes default
        max_scale_up = safety_config.get("maxScaleUpRate", 2)
        max_scale_down = safety_config.get("maxScaleDownRate", 1)
        
        # ============================================
        # SAFETY CHECK 1: Cooldown Period
        # ============================================
        if key in self.last_scale_time:
            elapsed = time.time() - self.last_scale_time[key]
            if elapsed < cooldown:
                remaining = int(cooldown - elapsed)
                print(f"⏸️  COOLDOWN ACTIVE for {key}")
                print(f"   Wait {remaining} more seconds before next scaling")
                return False
        
        # ============================================
        # Get current state from Kubernetes
        # ============================================
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            current_replicas = deployment.spec.replicas
        except Exception as e:
            print(f"❌ Error reading deployment {key}: {e}")
            return False
        
        # ============================================
        # SAFETY CHECK 2: Rate Limiting
        # ============================================
        original_desired = desired_replicas
        
        if desired_replicas > current_replicas:
            # Scaling UP
            max_allowed = current_replicas + max_scale_up
            if desired_replicas > max_allowed:
                print(f"🚦 RATE LIMIT: Want {desired_replicas}, but capping at {max_allowed}")
                print(f"   (Can only add {max_scale_up} pods at a time)")
                desired_replicas = max_allowed
        
        elif desired_replicas < current_replicas:
            # Scaling DOWN
            min_allowed = current_replicas - max_scale_down
            if desired_replicas < min_allowed:
                print(f"🚦 RATE LIMIT: Want {desired_replicas}, but capping at {min_allowed}")
                print(f"   (Can only remove {max_scale_down} pods at a time)")
                desired_replicas = min_allowed
        
        # ============================================
        # Check if any change is needed
        # ============================================
        if desired_replicas == current_replicas:
            print(f"✅ No scaling needed for {key} (already at {current_replicas} replicas)")
            return False
        
        # ============================================
        # Perform the scaling operation
        # ============================================
        try:
            # Update the deployment
            deployment.spec.replicas = desired_replicas
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            # Record the scaling time
            self.last_scale_time[key] = time.time()
            
            # Log the action
            if desired_replicas > current_replicas:
                print(f"📈 SCALED UP: {key}")
            else:
                print(f"📉 SCALED DOWN: {key}")
            print(f"   {current_replicas} → {desired_replicas} replicas")
            
            if original_desired != desired_replicas:
                print(f"   (Policy wanted {original_desired}, but safety limited it)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error scaling {key}: {e}")
            return False

