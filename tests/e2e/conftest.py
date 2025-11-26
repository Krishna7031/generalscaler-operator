import subprocess
import time
import pytest

@pytest.fixture(scope="session")
def kind_cluster():
    """Create and destroy kind cluster for testing"""
    print("\n🔧 Creating kind cluster...")
    subprocess.run(["kind", "create", "cluster", "--name", "test-cluster"], check=True)
    
    yield  # Tests run here
    
    print("\n🧹 Deleting kind cluster...")
    subprocess.run(["kind", "delete", "cluster", "--name", "test-cluster"], check=True)

@pytest.fixture(scope="session")
def install_operator(kind_cluster):
    """Install CRD and operator into cluster"""
    print("\n📦 Installing CRD...")
    subprocess.run(["kubectl", "apply", "-f", "deploy/crd.yaml"], check=True)
    
    print("🚀 Installing operator...")
    subprocess.run(["kubectl", "apply", "-f", "deploy/operator.yaml"], check=True)
    
    # Wait for operator to be ready
    time.sleep(10)
    yield

