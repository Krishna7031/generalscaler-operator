# GeneralScaler Operator

> A comprehensive, production-ready Kubernetes operator for autoscaling Deployments using pluggable metrics and policies. Designed for flexibility, safety, and extensibility.

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Project Development Phases](#project-development-phases)  
- [Architecture](#architecture)  
- [Features](#features)  
- [Installation](#installation)  
- [Usage and Examples](#usage-and-examples)  
- [Metric Plugins](#metric-plugins)  
- [Scaling Policies](#scaling-policies)  
- [Safety Mechanisms](#safety-mechanisms)  
- [Testing Strategy](#testing-strategy)  
- [CI/CD Integration](#cicd-integration)  
- [Helm Chart Usage](#helm-chart-usage)  
- [Development Workflow](#development-workflow)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Project Overview

GeneralScaler is a Kubernetes custom operator that enables generic autoscaling of any Kubernetes Deployment. It uses a Custom Resource Definition (`GeneralScaler`) to let users specify scalable deployments, metric sources (e.g., Prometheus, Redis, Pub/Sub), scaling policies (target SLOs or cost budgets), and safety parameters (cooldown, rate limits). The operator modularly combines metric plugins, a policy engine, and safe scaling logic, supporting extensibility and safe production use.

---

## Project Development Phases

This section details how the GeneralScaler Operator was built from the ground up, explaining each phase with definitions and step-by-step clarity—perfect to revisit anytime you want to recall your development journey.

---

### Phase 1: Define the Custom Resource Definition (CRD)

**What is a CRD?**  
A Custom Resource Definition (CRD) extends the Kubernetes API by allowing you to define your own resource type with custom schemas, validations, and lifecycle. It acts much like built-in resources (Pods, Deployments) but tailored to your domain.

**How this phase was done:**  
- Designed the `GeneralScaler` CRD to be **generic and flexible**, enabling autoscaling of *any* Deployment by specifying its name.
- The CRD schema follows the OpenAPI v3 specification to enforce type safety and validation.
- Key Spec fields:
  - `targetDeployment`: Name of the Kubernetes Deployment to scale.
  - `metrics`: Array of metric objects with type (prometheus, redis, pubsub), plugin config, and target values.
  - `policy`: Defines scaling policy type and config (SLO or cost-based).
  - `safety`: Controls cooldown period and max scale adjustments for stability.
- Applied strict schema validation in the CRD manifest to avoid invalid configurations, enhancing robustness.

*Outcome:* This created a reusable, extensible API for autoscaling instructions.

---

### Phase 2: Implement Metric Plugins

**What are Metric Plugins?**  
Metric plugins abstract data sources for scaling decisions. Each plugin knows how to query its source and produce a numeric metric value.

**How this phase was done:**  
- Developed three core metric plugins:
  - **Prometheus Plugin:** Queries Prometheus HTTP API to retrieve metric values such as request rates or latencies.
  - **Redis Plugin:** Connects to Redis to measure queue lengths, enabling background workload scaling.
  - **Pub/Sub Plugin:** Checks Google Cloud Pub/Sub subscription backlogs for event-driven scaling.
- Each plugin implements:
  - `validate_config()` for config schema validation ensuring correct plugin usage.
  - `get_metric_value()` to fetch live metric data for the controller logic.

*Outcome:* Modular, pluggable metric sources enable versatile autoscaling triggers.

---

### Phase 3: Develop the Policy Engine

**What is a Policy Engine?**  
The policy engine interprets metric values and decides how many replicas a Deployment should have while respecting business constraints.

**How this phase was done:**  
- Created two primary policies:
  - **SLO Policy:** Compares current metrics with Service Level Objectives (like latency thresholds) and recommends scaling up or down accordingly.
  - **Cost Policy:** Restricts scaling based on monetary budget (cost per pod and max cost per hour), preventing cost overruns.
- Designed for extensibility so new policies (e.g., custom business rules) can be added later.
- Ensured policy evaluation returns target replica counts, which are then passed to the safe scaling module.

*Outcome:* Smart, flexible scaling decisions balancing performance and cost.

---

### Phase 4: Safe Scaling Module (`SafeScaler`)

**Why Safe Scaling?**  
Blind scaling risks system instability due to rapid or excessive replica changes (flapping). Safety mechanisms ensure smooth, predictable scaling behavior.

**How this phase was done:**  
- Implemented cooldown functionality to enforce a wait time between scaling events.
- Added rate limiting to control the maximum number of pods added or removed per operation.
- Ensured that scaling always respects min/max replicas defined in the CRD.
- Integrated logging to audit scaling decisions and facilitate debugging.

*Outcome:* Reliable, production-safe autoscaling behavior reducing risk of outages.

---

### Phase 5: Operator Controller

**What is the Operator Controller?**  
The operator controller is the brain that watches for new or updated `GeneralScaler` resources, executes metric queries, applies policies, and enforces safe scaling by updating Kubernetes Deployments.

**How this phase was done:**  
- Built in Python using the Kopf framework for Kubernetes operator development.
- Watches `GeneralScaler` CR events and triggers reconciliation loops.
- Calls metric plugins, reads values, passes them to policies, then invokes `SafeScaler`.
- Applies pod scale updates to target Deployments using Kubernetes API patches.
- Handles errors gracefully and reports events to Kubernetes for visibility.

*Outcome:* Automated, event-driven scaling management integrated natively into Kubernetes.

---

### Phase 6: Sample Applications and Custom Resources (CRs)

**What are Sample Apps?**  
Demonstration apps prove the operator’s effectiveness by simulating real autoscaling scenarios.

**How this phase was done:**  
- Created three distinct applications covering different metric types:
  - HTTP server (uses Prometheus metrics)
  - Background worker (uses Redis queue length)
  - Event queue app (uses Pub/Sub backlog)
- Provided example `GeneralScaler` instances for each app in the `examples/` folder.
- These samples serve both as testbeds and user documentation samples.

*Outcome:* A robust showcase of operator usage in varied, realistic contexts.

---

### Phase 7: Unit and End-to-End (E2E) Testing

**Why Testing Matters**  
Testing ensures correctness, catches bugs early, and builds confidence for production readiness.

**How this phase was done:**  
- Wrote 13 rigorous unit tests covering metric plugin validation, policy behavior, and controller functionality.
- Developed a simple but comprehensive E2E validation shell script (`simple_e2e.sh`) that:
  - Validates all YAML manifests including the CRD.
  - Checks that plugins and policies import and interact as expected.
  - Verifies controller code loads without error.
- Testing covers both correctness and integration points.

*Outcome:* Reliable, maintainable codebase with automated quality assurance.

---

### Phase 8: Continuous Integration and Continuous Delivery (CI/CD)

**What is CI/CD?**  
Automated pipelines that lint, test, and validate your codebase on every change, ensuring ongoing code quality.

**How this phase was done:**  
- Configured GitHub Actions workflow to run:
  - Python linting with `flake8`.
  - Unit tests with `pytest`.
  - E2E validation script.
- Pipeline triggers on every push and pull request to maintain consistent code standards.
- Builds confidence in production readiness through automation.

*Outcome:* Professional project workflow enabling smooth collaboration and deployment.

---

### Phase 9: Helm Chart Packaging

**What is Helm?**  
Helm is a Kubernetes package manager that simplifies deploying and managing applications using reusable charts.

**How this phase was done:**  
- Created a minimal Helm chart under `charts/generalscaler` that packages:
  - The `GeneralScaler` CRD manifest.
  - The operator Deployment and RBAC manifests.
- Parameterized the Helm chart to allow image and replica customization using `values.yaml`.
- Tested chart rendering locally with `helm template` to ensure correctness.

*Outcome:* Easy installation, upgrade, and configuration of the operator in any Kubernetes cluster using Helm.

---

## Architecture

```
GeneralScaler CRD (Kubernetes)
         ↓
Operator Controller (Python Kopf)
         ↓
 ┌───────────────────────────┐
 │ Metric Plugins Interface  │
 │ ├─ Prometheus             │
 │ ├─ Redis                  │
 │ └─ Pub/Sub                │
 └───────────────────────────┘
         ↓
 ┌───────────────────────────┐
 │ Policy Engine             │
 │ ├─ SLO Policy             │
 │ └─ Cost Policy            │
 └───────────────────────────┘
         ↓
 ┌───────────────────────────┐
 │ SafeScaler Logic          │
 │ - Cooldown & Rate Limit   │
 └───────────────────────────┘
         ↓
   Kubernetes Deployment Patch
```

---

## Features

- Generic autoscaling for **any deployment** using pluggable metric sources.
- Extensible metric plugins interface enabling custom metric addition.
- Policy-driven scaling balancing performance (SLO) and cost constraints.
- Safety mechanisms preventing rapid or excessive scaling.
- Comprehensive, automated testing guarantees code correctness.
- Seamless Helm chart packaging for production use.
  
---

## Installation

### Prerequisites

- Kubernetes cluster v1.19+
- `kubectl` configured to access the cluster
- Helm 3.x installed

---

### Install with Helm (recommended)

```
helm install generalscaler ./charts/generalscaler
```

The chart deploys the CRD, operator deployment, and RBAC resources.

---

### Manual Installation

```
kubectl apply -f deploy/crd.yaml
kubectl apply -f deploy/operator.yaml
```

---

## Usage and Examples

### Create GeneralScaler Resource Example

```
apiVersion: autoscaling.example.com/v1
kind: GeneralScaler
metadata:
  name: http-app-scaler
spec:
  targetDeployment: http-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: prometheus
      config:
        query: "rate(http_requests_total[5m])"
      targetValue: 100
  policy:
    type: slo
  safety:
    cooldownSeconds: 300
    maxScaleUpRate: 3
    maxScaleDownRate: 1
```

Apply with:

```
kubectl apply -f examples/http-app/generalscaler.yaml
kubectl get generalscalers -w
kubectl describe generalscaler http-app-scaler
```

---

## Metric Plugins

- **Prometheus:** Fetches query data from Prometheus for dynamic scaling.
- **Redis:** Monitors Redis queue lengths useful for worker autoscaling.
- **Pub/Sub:** Monitors message backlog in Google Cloud Pub/Sub subscriptions.

Each plugin validates its config and exposes current metric value.

---

## Scaling Policies

- **SLO Policy:** Ensure performance targets by scaling to meet latency or throughput objectives.
- **Cost Policy:** Limit scaling based on cost budget constraints.

---

## Safety Mechanisms

To avoid instability:

- **Cooldown:** Pause between scale operations to prevent flapping.
- **Rate Limiting:** Restrict how many replicas can be added or removed at once.
- **Min/Max Replicas:** Hard limits defined in the custom resource.

---

## Testing Strategy

- **Unit tests:** Test individual metric plugins, policies, and core logic.
- **Simple E2E tests:** Validate resource manifests, imports, and end-to-end integration without real cluster dependency.
- **CI/CD:** Automated GitHub Actions workflow runs lint, unit, and E2E tests on every commit.

---

## CI/CD Integration

- Linting with `flake8` to maintain code style.
- Unit testing with `pytest`.
- E2E validations using the simple validation shell script.
- All fully automated on GitHub Actions workflows.

---

## Helm Chart Usage

- The Helm chart packages CRD and operator.
- Allows configuring image, replica count, and operator settings.
- Use `helm install` or `helm upgrade` for easy deploy and upgrade.

---

## Development Workflow

- **Add Metric Plugin:** Implement plugin class and register.
- **Add Policy:** Extend policy logic and register.
- **Extend CRD:** Update schema as needed.
- Local testing with unit and E2E scripts.
- Push to GitHub with automated CI validation.

---

## Contributing

Issues, bugs, and feature requests are welcome!  
Please ensure code passes all tests and linting before submission.

---

## License

MIT License

---

## Contact and Support

For issues or questions, open a GitHub issue or contact me via LinkedIn.

---

*Thank you for reviewing my GeneralScaler Operator project! This README documents the journey, architecture, design decisions, and how to use and extend the operator effectively.*

---
