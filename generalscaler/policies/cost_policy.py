class CostPolicy:
    """
    Cost-aware scaling policy
    Scales based on performance BUT respects budget limits
    """
    
    def __init__(self, max_cost_per_hour=50, cost_per_pod=0.5):
        """
        Args:
            max_cost_per_hour: Maximum budget per hour (e.g., $50)
            cost_per_pod: Cost per pod per hour (e.g., $0.50)
        """
        self.max_cost_per_hour = max_cost_per_hour
        self.cost_per_pod = cost_per_pod
    
    def should_scale(self, current_value, target_value, current_replicas, min_replicas, max_replicas):
        """
        First calculate desired replicas like SLO policy,
        then check if it fits budget
        """
        
        # Step 1: Calculate desired replicas (same as SLO)
        if current_value > target_value * 1.2:
            ratio = current_value / target_value
            desired = int(current_replicas * ratio)
            print(f"📈 Want to scale UP to {desired} pods")
            
        elif current_value < target_value * 0.8:
            ratio = current_value / target_value
            desired = int(current_replicas * ratio)
            print(f"📉 Want to scale DOWN to {desired} pods")
            
        else:
            desired = current_replicas
            print(f"✅ No scaling needed")
        
        # Step 2: Check cost constraint
        projected_cost = desired * self.cost_per_pod
        
        if projected_cost > self.max_cost_per_hour:
            # Budget exceeded! Cap at maximum affordable pods
            max_affordable = int(self.max_cost_per_hour / self.cost_per_pod)
            print(f"💰 Cost limit reached! Capping at {max_affordable} pods (budget: ${self.max_cost_per_hour}/hour)")
            desired = max_affordable
        else:
            print(f"💰 Within budget: {desired} pods = ${projected_cost:.2f}/hour")
        
        # Enforce min/max limits
        desired = max(min_replicas, min(desired, max_replicas))
        
        return desired

