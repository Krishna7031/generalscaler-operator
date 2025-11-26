class SLOPolicy:
    """
    Simple SLO-based scaling policy
    Scales up when metric is above target, scales down when below
    """
    
    def should_scale(self, current_value, target_value, current_replicas, min_replicas, max_replicas):
        """
        Decide how many replicas we need
        
        Args:
            current_value: Current metric value (e.g., 150 messages in queue)
            target_value: Desired metric value (e.g., 100 messages)
            current_replicas: How many pods running now (e.g., 3)
            min_replicas: Minimum allowed pods (e.g., 2)
            max_replicas: Maximum allowed pods (e.g., 10)
        
        Returns:
            desired_replicas: How many pods we should have
        """
        
        # If current is much higher than target, we need more pods
        if current_value > target_value * 1.2:  # 20% above target
            # Calculate proportionally
            # If metric is 2x target, we need 2x pods
            ratio = current_value / target_value
            desired = int(current_replicas * ratio)
            
            print(f"📈 Scaling UP: metric {current_value} > target {target_value}")
            
        # If current is much lower than target, we can reduce pods
        elif current_value < target_value * 0.8:  # 20% below target
            ratio = current_value / target_value
            desired = int(current_replicas * ratio)
            
            print(f"📉 Scaling DOWN: metric {current_value} < target {target_value}")
            
        # Metric is in acceptable range, don't change
        else:
            desired = current_replicas
            print(f"✅ No scaling needed: metric {current_value} is near target {target_value}")
        
        # Enforce min/max limits
        desired = max(min_replicas, min(desired, max_replicas))
        
        return desired

