#!/usr/bin/env python3
"""
Kubernetes Test Automation Deployment Script

This script deploys and manages the Test Automation infrastructure on Kubernetes:
- Deploys Chrome Node Pods based on node_count parameter (min=1, max=5)
- Deploys Test Controller Pod
- Checks Chrome Node readiness before running tests
- Handles inter-pod communication
- Implements error handling and retry logic
"""

import sys
import time
import argparse
import subprocess
import json
from typing import Optional, Dict, List

# Configuration
NAMESPACE = "test-automation"
MAX_RETRIES = 5
RETRY_DELAY = 10  # seconds
DEPLOYMENT_TIMEOUT = 300  # 5 minutes


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class KubernetesDeployer:
    """Manages Kubernetes deployment for test automation"""

    def __init__(self, node_count: int, manifests_dir: str = "k8s/manifests"):
        """
        Initialize deployer

        Args:
            node_count: Number of Chrome Node pods (1-5)
            manifests_dir: Directory containing Kubernetes YAML files
        """
        if not 1 <= node_count <= 5:
            raise ValueError("node_count must be between 1 and 5")

        self.node_count = node_count
        self.manifests_dir = manifests_dir
        self.namespace = NAMESPACE

    def log(self, message: str, level: str = "INFO"):
        """Print colored log message"""
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED
        }
        color = colors.get(level, Colors.END)
        print(f"{color}[{level}]{Colors.END} {message}")

    def run_command(self, command: List[str], check: bool = True) -> Optional[subprocess.CompletedProcess]:
        """
        Execute shell command with error handling

        Args:
            command: Command and arguments as list
            check: Raise exception on non-zero exit code

        Returns:
            CompletedProcess or None on error
        """
        try:
            self.log(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e.stderr}", "ERROR")
            if check:
                raise
            return None

    def check_kubectl(self) -> bool:
        """Verify kubectl is installed and configured"""
        self.log("Checking kubectl installation...")
        result = self.run_command(["kubectl", "version", "--client"], check=False)

        if result and result.returncode == 0:
            self.log("kubectl is installed", "SUCCESS")
            return True
        else:
            self.log("kubectl not found or not configured", "ERROR")
            return False

    def check_cluster_connection(self) -> bool:
        """Verify connection to Kubernetes cluster"""
        self.log("Checking cluster connection...")
        result = self.run_command(["kubectl", "cluster-info"], check=False)

        if result and result.returncode == 0:
            self.log("Connected to cluster", "SUCCESS")
            return True
        else:
            self.log("Cannot connect to cluster", "ERROR")
            return False

    def create_namespace(self) -> bool:
        """Create namespace if it doesn't exist"""
        self.log(f"Creating namespace: {self.namespace}")

        # Check if namespace exists
        result = self.run_command(
            ["kubectl", "get", "namespace", self.namespace],
            check=False
        )

        if result and result.returncode == 0:
            self.log(f"Namespace {self.namespace} already exists", "WARNING")
            return True

        # Create namespace
        result = self.run_command(
            ["kubectl", "apply", "-f", f"{self.manifests_dir}/01-namespace.yaml"],
            check=False
        )

        if result and result.returncode == 0:
            self.log(f"Namespace {self.namespace} created", "SUCCESS")
            return True
        else:
            self.log("Failed to create namespace", "ERROR")
            return False

    def deploy_configmap(self) -> bool:
        """Deploy ConfigMap with node_count parameter"""
        self.log(f"Deploying ConfigMap with node_count={self.node_count}")

        # Try to create ConfigMap imperatively
        try:
            # Generate YAML
            create_result = subprocess.run([
                "kubectl", "create", "configmap", "test-automation-config",
                f"--from-literal=node_count={self.node_count}",
                "--from-literal=max_retries=5",
                "--from-literal=retry_delay=10",
                "--from-literal=chrome_node_service=http://chrome-node-service:4444",
                "-n", self.namespace,
                "--dry-run=client",
                "-o", "yaml"
            ], capture_output=True, text=True)

            if create_result.returncode == 0:
                # Apply the YAML
                apply_result = subprocess.run(
                    ["kubectl", "apply", "-f", "-"],
                    input=create_result.stdout,
                    capture_output=True,
                    text=True
                )

                if apply_result.returncode == 0:
                    self.log("ConfigMap deployed", "SUCCESS")
                    return True
                else:
                    self.log(f"Failed to apply ConfigMap: {apply_result.stderr}", "WARNING")
        except Exception as e:
            self.log(f"Failed to create ConfigMap imperatively: {e}", "WARNING")

        # Fallback: apply from file
        self.log("Using ConfigMap from file", "WARNING")
        result = self.run_command([
            "kubectl", "apply", "-f", f"{self.manifests_dir}/02-configmap.yaml"
        ], check=False)

        return result and result.returncode == 0

    def scale_chrome_nodes(self) -> bool:
        """
        Scale Chrome Node deployment to specified node_count

        Returns:
            True if scaling succeeded
        """
        self.log(f"Scaling Chrome Nodes to {self.node_count} replicas...")

        # First, ensure deployment exists
        result = self.run_command([
            "kubectl", "apply", "-f", f"{self.manifests_dir}/03-chrome-node-deployment.yaml"
        ], check=False)

        if not result or result.returncode != 0:
            self.log("Failed to create/update Chrome Node deployment", "ERROR")
            return False

        # Scale to desired replica count
        result = self.run_command([
            "kubectl", "scale", "deployment", "chrome-node",
            f"--replicas={self.node_count}",
            "-n", self.namespace
        ], check=False)

        if result and result.returncode == 0:
            self.log(f"Chrome Nodes scaled to {self.node_count}", "SUCCESS")
            return True
        else:
            self.log("Failed to scale Chrome Nodes", "ERROR")
            return False

    def deploy_chrome_node_service(self) -> bool:
        """Deploy Chrome Node Service for inter-pod communication"""
        self.log("Deploying Chrome Node Service...")

        result = self.run_command([
            "kubectl", "apply", "-f", f"{self.manifests_dir}/04-chrome-node-service.yaml"
        ], check=False)

        if result and result.returncode == 0:
            self.log("Chrome Node Service deployed", "SUCCESS")
            return True
        else:
            self.log("Failed to deploy Chrome Node Service", "ERROR")
            return False

    def wait_for_chrome_nodes_ready(self, timeout: int = DEPLOYMENT_TIMEOUT) -> bool:
        """
        Wait for all Chrome Node pods to be ready

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if all pods are ready
        """
        self.log(f"Waiting for {self.node_count} Chrome Node pods to be ready...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Get pod status
            result = self.run_command([
                "kubectl", "get", "pods",
                "-n", self.namespace,
                "-l", "component=chrome-node",
                "-o", "json"
            ], check=False)

            if not result or result.returncode != 0:
                self.log("Failed to get pod status", "ERROR")
                time.sleep(5)
                continue

            try:
                pods_data = json.loads(result.stdout)
                pods = pods_data.get("items", [])

                if len(pods) != self.node_count:
                    self.log(f"Found {len(pods)}/{self.node_count} pods, waiting...", "WARNING")
                    time.sleep(5)
                    continue

                # Check if all pods are ready
                ready_count = 0
                for pod in pods:
                    pod_name = pod["metadata"]["name"]
                    status = pod.get("status", {})
                    conditions = status.get("conditions", [])

                    # Check Ready condition
                    for condition in conditions:
                        if condition["type"] == "Ready" and condition["status"] == "True":
                            ready_count += 1
                            break

                self.log(f"Ready: {ready_count}/{self.node_count} Chrome Nodes")

                if ready_count == self.node_count:
                    self.log("All Chrome Nodes are ready!", "SUCCESS")
                    return True

            except json.JSONDecodeError as e:
                self.log(f"Failed to parse pod status: {e}", "ERROR")

            time.sleep(5)

        self.log(f"Timeout waiting for Chrome Nodes (>{timeout}s)", "ERROR")
        return False

    def verify_chrome_node_service(self) -> bool:
        """
        Verify Chrome Node Service has endpoints

        Returns:
            True if service has endpoints
        """
        self.log("Verifying Chrome Node Service endpoints...")

        for attempt in range(MAX_RETRIES):
            result = self.run_command([
                "kubectl", "get", "endpoints", "chrome-node-service",
                "-n", self.namespace,
                "-o", "json"
            ], check=False)

            if result and result.returncode == 0:
                try:
                    endpoints_data = json.loads(result.stdout)
                    subsets = endpoints_data.get("subsets", [])

                    if subsets and any(s.get("addresses") for s in subsets):
                        endpoint_count = sum(len(s.get("addresses", [])) for s in subsets)
                        self.log(f"Service has {endpoint_count} endpoints", "SUCCESS")
                        return True
                    else:
                        self.log(f"Service has no endpoints (attempt {attempt + 1}/{MAX_RETRIES})", "WARNING")
                except json.JSONDecodeError:
                    self.log("Failed to parse endpoints", "ERROR")

            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

        self.log("Service has no endpoints after max retries", "ERROR")
        return False

    def deploy_test_controller(self) -> bool:
        """Deploy Test Controller Pod"""
        self.log("Deploying Test Controller...")

        result = self.run_command([
            "kubectl", "apply", "-f", f"{self.manifests_dir}/05-test-controller-deployment.yaml"
        ], check=False)

        if result and result.returncode == 0:
            self.log("Test Controller deployed", "SUCCESS")
            return True
        else:
            self.log("Failed to deploy Test Controller", "ERROR")
            return False

    def monitor_test_execution(self, timeout: int = 600) -> bool:
        """
        Monitor Test Controller pod and display logs

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if tests completed successfully
        """
        self.log("Monitoring test execution...")

        start_time = time.time()

        # Wait for Test Controller pod to start
        while time.time() - start_time < 60:
            result = self.run_command([
                "kubectl", "get", "pods",
                "-n", self.namespace,
                "-l", "component=test-controller",
                "-o", "json"
            ], check=False)

            if result and result.returncode == 0:
                try:
                    pods_data = json.loads(result.stdout)
                    pods = pods_data.get("items", [])

                    if pods:
                        pod_name = pods[0]["metadata"]["name"]
                        self.log(f"Test Controller pod: {pod_name}", "SUCCESS")
                        break
                except json.JSONDecodeError:
                    pass

            time.sleep(2)
        else:
            self.log("Test Controller pod not found", "ERROR")
            return False

        # Follow logs
        self.log("=" * 60)
        self.log("TEST CONTROLLER LOGS:", "INFO")
        self.log("=" * 60)

        try:
            subprocess.run([
                "kubectl", "logs", "-f",
                "-n", self.namespace,
                "-l", "component=test-controller"
            ])
        except KeyboardInterrupt:
            self.log("\nLog streaming interrupted", "WARNING")

        # Check final status
        result = self.run_command([
            "kubectl", "get", "pods",
            "-n", self.namespace,
            "-l", "component=test-controller",
            "-o", "json"
        ], check=False)

        if result and result.returncode == 0:
            try:
                pods_data = json.loads(result.stdout)
                pods = pods_data.get("items", [])

                if pods:
                    status = pods[0].get("status", {})
                    phase = status.get("phase")

                    if phase == "Succeeded":
                        self.log("Tests completed successfully!", "SUCCESS")
                        return True
                    elif phase == "Running":
                        self.log("Tests are still running", "WARNING")
                        return True
                    else:
                        self.log(f"Tests failed (status: {phase})", "ERROR")
                        return False
            except json.JSONDecodeError:
                pass

        return False

    def deploy_all(self) -> bool:
        """
        Execute complete deployment workflow

        Returns:
            True if deployment succeeded
        """
        self.log("=" * 60)
        self.log(f"{Colors.BOLD}KUBERNETES TEST AUTOMATION DEPLOYMENT{Colors.END}")
        self.log(f"Node Count: {self.node_count}")
        self.log("=" * 60)

        # Step 1: Pre-flight checks
        if not self.check_kubectl():
            return False

        if not self.check_cluster_connection():
            return False

        # Step 2: Create namespace
        if not self.create_namespace():
            return False

        # Step 3: Deploy ConfigMap
        if not self.deploy_configmap():
            return False

        # Step 4: Deploy Chrome Nodes
        if not self.scale_chrome_nodes():
            return False

        # Step 5: Deploy Chrome Node Service
        if not self.deploy_chrome_node_service():
            return False

        # Step 6: Wait for Chrome Nodes to be ready
        if not self.wait_for_chrome_nodes_ready():
            return False

        # Step 7: Verify Service endpoints
        if not self.verify_chrome_node_service():
            return False

        # Step 8: Deploy Test Controller
        if not self.deploy_test_controller():
            return False

        # Step 9: Monitor test execution
        self.monitor_test_execution()

        self.log("=" * 60)
        self.log("DEPLOYMENT COMPLETED", "SUCCESS")
        self.log("=" * 60)

        return True

    def cleanup(self) -> bool:
        """Clean up all deployed resources"""
        self.log("Cleaning up resources...")

        result = self.run_command([
            "kubectl", "delete", "namespace", self.namespace
        ], check=False)

        if result and result.returncode == 0:
            self.log("Resources cleaned up", "SUCCESS")
            return True
        else:
            self.log("Failed to clean up resources", "ERROR")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Deploy and manage Kubernetes test automation infrastructure"
    )
    parser.add_argument(
        "--node-count",
        type=int,
        default=2,
        help="Number of Chrome Node pods (1-5, default: 2)"
    )
    parser.add_argument(
        "--manifests-dir",
        default="k8s/manifests",
        help="Directory containing Kubernetes YAML files"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up all deployed resources"
    )

    args = parser.parse_args()

    try:
        deployer = KubernetesDeployer(
            node_count=args.node_count,
            manifests_dir=args.manifests_dir
        )

        if args.cleanup:
            success = deployer.cleanup()
        else:
            success = deployer.deploy_all()

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.END} {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
