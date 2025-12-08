# Kubernetes Test Automation - Python Deployment Script

## Overview

This Python script automates the deployment and management of Selenium-based test automation on Kubernetes.

## Features

✅ **Dynamic Node Deployment**: Deploy 1-5 Chrome Node pods based on `node_count` parameter
✅ **Readiness Checks**: Wait for Chrome Nodes to be ready before running tests
✅ **Inter-Pod Communication**: Verify service endpoints and connectivity
✅ **Error Handling**: Retry logic and comprehensive error handling
✅ **Test Monitoring**: Real-time log streaming from Test Controller
✅ **Cleanup**: Easy resource cleanup

## Requirements

```bash
# Python 3.7+
python3 --version

# kubectl configured with cluster access
kubectl version --client

# Connected to Kubernetes cluster
kubectl cluster-info
```

## Installation

```bash
# Make script executable
chmod +x deploy.py

# No additional Python packages needed - uses only stdlib!
```

## Usage

### Basic Deployment (2 Chrome Nodes)

```bash
python3 deploy.py
```

### Deploy with Custom Node Count

```bash
# Deploy with 1 Chrome Node (minimum)
python3 deploy.py --node-count 1

# Deploy with 5 Chrome Nodes (maximum)
python3 deploy.py --node-count 5

# Deploy with 3 Chrome Nodes
python3 deploy.py --node-count 3
```

### Cleanup Resources

```bash
python3 deploy.py --cleanup
```

### Custom Manifests Directory

```bash
python3 deploy.py --manifests-dir path/to/manifests --node-count 3
```

## What the Script Does

### 1. Pre-flight Checks
- ✓ Verify kubectl is installed
- ✓ Check cluster connectivity

### 2. Resource Deployment
- ✓ Create namespace (`test-automation`)
- ✓ Deploy ConfigMap with `node_count` parameter
- ✓ Deploy Chrome Node Deployment
- ✓ Scale to specified `node_count` (1-5)
- ✓ Deploy Chrome Node Service (inter-pod communication)

### 3. Readiness Verification
- ✓ Wait for all Chrome Node pods to be Running
- ✓ Check pod Ready status
- ✓ Verify Service has endpoints
- ✓ Implement retry logic (max 5 retries, 10s delay)

### 4. Test Execution
- ✓ Deploy Test Controller
- ✓ Stream logs in real-time
- ✓ Monitor test completion

### 5. Error Handling
- ✓ Retry failed operations
- ✓ Timeout management
- ✓ Detailed error messages

## Script Output Example

```
[INFO] ==============================================================
[INFO] KUBERNETES TEST AUTOMATION DEPLOYMENT
[INFO] Node Count: 3
[INFO] ==============================================================
[INFO] Checking kubectl installation...
[SUCCESS] kubectl is installed
[INFO] Checking cluster connection...
[SUCCESS] Connected to cluster
[INFO] Creating namespace: test-automation
[SUCCESS] Namespace test-automation created
[INFO] Deploying ConfigMap with node_count=3
[SUCCESS] ConfigMap deployed
[INFO] Scaling Chrome Nodes to 3 replicas...
[SUCCESS] Chrome Nodes scaled to 3
[INFO] Deploying Chrome Node Service...
[SUCCESS] Chrome Node Service deployed
[INFO] Waiting for 3 Chrome Node pods to be ready...
[INFO] Ready: 1/3 Chrome Nodes
[INFO] Ready: 2/3 Chrome Nodes
[INFO] Ready: 3/3 Chrome Nodes
[SUCCESS] All Chrome Nodes are ready!
[INFO] Verifying Chrome Node Service endpoints...
[SUCCESS] Service has 3 endpoints
[INFO] Deploying Test Controller...
[SUCCESS] Test Controller deployed
[INFO] Monitoring test execution...
[INFO] ==============================================================
[INFO] TEST CONTROLLER LOGS:
[INFO] ==============================================================
... test output ...
[SUCCESS] DEPLOYMENT COMPLETED
```

## Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--node-count` | int | 2 | Number of Chrome Node pods (1-5) |
| `--manifests-dir` | str | k8s/manifests | Directory with YAML files |
| `--cleanup` | flag | False | Delete all resources |

## Configuration

The script uses the following configuration:

```python
NAMESPACE = "test-automation"     # Kubernetes namespace
MAX_RETRIES = 5                   # Maximum retry attempts
RETRY_DELAY = 10                  # Delay between retries (seconds)
DEPLOYMENT_TIMEOUT = 300          # Max wait time (5 minutes)
```

## Requirements Met

### ✅ Deploy Kubernetes Resources
- Deploys Test Controller Pod
- Deploys Chrome Node Pods based on `node_count` (1-5)

### ✅ Inter-Pod Communication
- Creates Service for Chrome Nodes
- Verifies Service endpoints
- Test Controller connects via `chrome-node-service:4444`

### ✅ Readiness Checks
- Waits for Chrome Node pods to be Ready
- Verifies Service has active endpoints
- Only deploys Test Controller when Chrome Nodes are ready

### ✅ Error Handling & Retries
- Retry logic for all operations
- Timeout management
- Detailed error messages
- Graceful failure handling

### ✅ Selenium Test Execution
- Runs tests in headless Chrome
- Uses Selenium Grid (Chrome Nodes)
- Test Controller passes tests via WebDriver protocol

## Troubleshooting

### Script fails with "kubectl not found"

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/
```

### Script fails with "Cannot connect to cluster"

```bash
# Check kubectl configuration
kubectl config current-context

# For EKS:
aws eks update-kubeconfig --region us-east-1 --name <cluster-name>
```

### Chrome Nodes not becoming ready

```bash
# Check pod status
kubectl get pods -n test-automation

# Check pod logs
kubectl logs -n test-automation -l component=chrome-node

# Check events
kubectl get events -n test-automation --sort-by='.lastTimestamp'
```

### Tests failing

```bash
# View Test Controller logs
kubectl logs -n test-automation -l component=test-controller

# Check service endpoints
kubectl get endpoints chrome-node-service -n test-automation
```

## Advanced Usage

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Deploy Test Automation
  run: |
    python3 deploy.py --node-count 3

- name: Cleanup
  if: always()
  run: |
    python3 deploy.py --cleanup
```

### Programmatic Usage

```python
from deploy import KubernetesDeployer

# Create deployer
deployer = KubernetesDeployer(node_count=3)

# Deploy
success = deployer.deploy_all()

# Cleanup
deployer.cleanup()
```

## Project Structure

```
TestOpsProject/
├── deploy.py                   # Main deployment script
├── k8s/
│   └── manifests/
│       ├── 01-namespace.yaml
│       ├── 02-configmap.yaml
│       ├── 03-chrome-node-deployment.yaml
│       ├── 04-chrome-node-service.yaml
│       └── 05-test-controller-deployment.yaml
├── docker/
│   ├── Dockerfile.chromenode
│   └── Dockerfile.controller
└── TestFiles/
    ├── features/
    ├── pages/
    └── utilities/
```

## License

Copyright © 2024
