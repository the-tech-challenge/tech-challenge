# DevOps Technical Challenge

Deploy a containerized Flask application to AWS using Terraform and GitHub Actions.

## Architecture

```
User → ALB (Port 80) → EC2 (Port 5000) ← ECR (Docker Image)
```
*   **Infrastructure**: Modular Terraform (split into `tech-challenge-infra`, `terraform-modules`).
*   **CI/CD**: reusable GitHub Actions workflows (`github-actions-library`).
*   **Security**: SSM Session Manager (No SSH port 22 open), Minimal IAM Roles, OIDC Authentication.

## Repositories
This solution is split into three repositories for enterprise modularity:
1.  **[tech-challenge](.)**: Application code & Deploy Workflow.
2.  **[tech-challenge-infra](../tech_challenge_infra)**: Terraform infrastructure code.
3.  **[github-actions-library](../github-actions-library)**: Reusable CI/CD workflows.

## Quick Start

### 1. Prerequisites
*   AWS Account & OIDC Provider configured for GitHub Actions.
*   Terraform installed locally (optional, for manual runs).

### 2. Configure Repositories
Ensure the following Secrets/Vars are set in this repository:

**Secrets**:
*   `AWS_ROLE_ARN`: The OIDC Role ARN (e.g., `arn:aws:iam::123456789012:role/github-oidc-role`).

**Variables**:
*   `AWS_REGION`: Target AWS Region (default: `us-east-1`).
*   `PROJECT_NAME`: Project tag to find resources (default: `flask-challenge`).

### 3. Deploy Infrastructure
Go to the **tech-challenge-infra** repository and run the **Terraform Apply** workflow.
*   This validates code, plans, and applies changes.
*   Resources created: VPC, ALB, EC2, ECR, IAM Roles.

### 4. Deploy Application
Push to `main` in this repository (`tech-challenge`).
*   **Workflow**: `.github/workflows/deploy.yml`
*   **Lookup Job**: Dynamically finds EC2 Instance ID and ECR Repo Name using tags.
*   **Build**: Docker build & push to ECR.
*   **Deploy**: AWS SSM Command to pull & restart container on EC2.
*   **Approval**: Production environment requires manual approval.

### 5. Access
Get the **ALB DNS Name** from the Terraform outputs (Infra repo).
```bash
curl http://<ALB_DNS_NAME>/info
```

## Assumptions & Decisions
*   **Security**: SSH is completely disabled. Access is via AWS SSM Session Manager only, exceeding the "restrict to IP" requirement.
*   **Cost**: Uses `t3.micro` and standard ECR. No NAT Gateway.
*   **Dynamic Config**: CI/CD pipeline dynamically looks up resources by Tag (`Project=flask-challenge`), avoiding hardcoded IDs.
*   **OIDC**: Uses AWS OIDC for passwordless, secure authentication in CI/CD.

## Cleanup
Run the **Terraform Destroy** workflow in the `tech-challenge-infra` repository.
