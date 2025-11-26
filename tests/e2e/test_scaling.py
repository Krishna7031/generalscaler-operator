import subprocess
import time
import pytest

def run_kubectl(cmd):
    """Helper to run kubectl commands"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

class TestHTTPAppScaling:
    def test_http_app_deploys(self, install_operator):
        """Test that HTTP app deploys successfully"""
        print("\n📱 Deploying HTTP app...")
        subprocess.run(
            ["kubectl", "apply", "-f", "examples/http-app/"],
            check=True
        )
        
        # Wait for deployment to be ready
        time.sleep(15)
        
        # Check deployment exists
        result = run_kubectl(
            "kubectl get deployment http-app -o jsonpath='{.metadata.name}'"
        )
        assert result == "http-app", "HTTP app deployment should exist"
    
    def test_http_app_generalscaler_created(self, install_operator):
        """Test that GeneralScaler is created"""
        print("\n📊 Checking GeneralScaler...")
        result = run_kubectl(
            "kubectl get generalscaler http-app-scaler -o jsonpath='{.metadata.name}'"
        )
        assert result == "http-app-scaler", "GeneralScaler should be created"
    
    def test_http_app_has_replicas(self, install_operator):
        """Test that HTTP app has correct replicas"""
        print("\n🔢 Checking replica count...")
        # Deploy app
        subprocess.run(
            ["kubectl", "apply", "-f", "examples/http-app/"],
            check=True
        )
        time.sleep(15)
        
        # Check initial replicas
        replicas = run_kubectl(
            "kubectl get deployment http-app -o jsonpath='{.spec.replicas}'"
        )
        assert replicas == "2", f"Should have 2 replicas, got {replicas}"

class TestWorkerAppScaling:
    def test_worker_app_deploys(self, install_operator):
        """Test that Worker app deploys successfully"""
        print("\n🔄 Deploying Worker app...")
        subprocess.run(
            ["kubectl", "apply", "-f", "examples/worker-app/"],
            check=True
        )
        
        time.sleep(15)
        
        result = run_kubectl(
            "kubectl get deployment worker-app -o jsonpath='{.metadata.name}'"
        )
        assert result == "worker-app", "Worker app deployment should exist"
    
    def test_worker_app_generalscaler_created(self, install_operator):
        """Test that Worker GeneralScaler is created"""
        print("\n📊 Checking Worker GeneralScaler...")
        result = run_kubectl(
            "kubectl get generalscaler worker-app-scaler -o jsonpath='{.metadata.name}'"
        )
        assert result == "worker-app-scaler", "Worker GeneralScaler should exist"

class TestQueueAppScaling:
    def test_queue_app_deploys(self, install_operator):
        """Test that Queue app deploys successfully"""
        print("\n📨 Deploying Queue app...")
        subprocess.run(
            ["kubectl", "apply", "-f", "examples/queue-app/"],
            check=True
        )
        
        time.sleep(15)
        
        result = run_kubectl(
            "kubectl get deployment queue-app -o jsonpath='{.metadata.name}'"
        )
        assert result == "queue-app", "Queue app deployment should exist"
    
    def test_queue_app_generalscaler_created(self, install_operator):
        """Test that Queue GeneralScaler is created"""
        print("\n📊 Checking Queue GeneralScaler...")
        result = run_kubectl(
            "kubectl get generalscaler queue-app-scaler -o jsonpath='{.metadata.name}'"
        )
        assert result == "queue-app-scaler", "Queue GeneralScaler should exist"

