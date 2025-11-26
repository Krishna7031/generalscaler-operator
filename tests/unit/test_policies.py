import pytest
from generalscaler.policies.slo_policy import SLOPolicy
from generalscaler.policies.cost_policy import CostPolicy

# Test SLO Policy
class TestSLOPolicy:
    def test_scale_up(self):
        """When metric > target, should scale up"""
        policy = SLOPolicy()
        desired = policy.should_scale(
            current_value=200,      # 2x target
            target_value=100,
            current_replicas=3,
            min_replicas=1,
            max_replicas=10
        )
        assert desired > 3, "Should scale up when metric is high"
    
    def test_scale_down(self):
        """When metric < target, should scale down"""
        policy = SLOPolicy()
        desired = policy.should_scale(
            current_value=50,       # 0.5x target
            target_value=100,
            current_replicas=6,
            min_replicas=1,
            max_replicas=10
        )
        assert desired < 6, "Should scale down when metric is low"
    
    def test_no_scale(self):
        """When metric near target, should not change"""
        policy = SLOPolicy()
        desired = policy.should_scale(
            current_value=100,      # Exactly at target
            target_value=100,
            current_replicas=5,
            min_replicas=1,
            max_replicas=10
        )
        assert desired == 5, "Should not scale when metric is at target"
    
    def test_respects_min_replicas(self):
        """Should never go below min_replicas"""
        policy = SLOPolicy()
        desired = policy.should_scale(
            current_value=10,       # Very low
            target_value=100,
            current_replicas=1,
            min_replicas=2,         # Min is 2
            max_replicas=10
        )
        assert desired >= 2, "Should respect min_replicas"
    
    def test_respects_max_replicas(self):
        """Should never go above max_replicas"""
        policy = SLOPolicy()
        desired = policy.should_scale(
            current_value=1000,     # Very high
            target_value=100,
            current_replicas=10,
            min_replicas=1,
            max_replicas=8          # Max is 8
        )
        assert desired <= 8, "Should respect max_replicas"

# Test Cost Policy
class TestCostPolicy:
    def test_respects_budget(self):
        """Should not exceed budget even if metric demands it"""
        policy = CostPolicy(max_cost_per_hour=50, cost_per_pod=1.0)
        desired = policy.should_scale(
            current_value=200,      # Wants to scale up a lot
            target_value=100,
            current_replicas=10,
            min_replicas=1,
            max_replicas=100
        )
        # Budget: $50/hour, Cost per pod: $1
        # Max affordable: 50 pods
        assert desired <= 50, "Should not exceed budget"
    
    def test_allows_scaling_within_budget(self):
        """Should allow scaling when within budget"""
        policy = CostPolicy(max_cost_per_hour=100, cost_per_pod=1.0)
        desired = policy.should_scale(
            current_value=200,
            target_value=100,
            current_replicas=10,
            min_replicas=1,
            max_replicas=200
        )
        # Budget: $100, Cost: $1 per pod
        # Should allow scaling up to ~20 pods (policy wants 2x replicas)
        assert desired > 10, "Should scale up when within budget"

