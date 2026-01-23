# DevOps Technical Challenge

Deploy a containerized Flask application to AWS using Terraform and GitHub Actions.

## Architecture

```
User → ALB (Port 80) → EC2 (Port 5000) ← ECR (Docker Image)
```
*   **Infrastructure**: Modular Terraform (consolidated in `tech-challenge-infrastructure`).
*   **CI/CD**: reusable GitHub Actions workflows (`github-actions-library`).
*   **Security**: SSM Session Manager (No SSH port 22 open), Minimal IAM Roles, OIDC Authentication.

## Repositories
This solution is split into three repositories for enterprise modularity:
1.  **[tech-challenge](.)**: Application code & Deploy Workflow.
2.  **[tech-challenge-infrastructure](../tech-challenge-infrastructure)**: Terminated/Consolidated repository containing both Terraform modules and infrastructure implementation (formerly split into `terraform-modules` and `tech_challenge_infra`).
3.  **[github-actions-library](../github-actions-library)**: Reusable CI/CD workflows.

## Quick Start

### 1. Prerequisites
*   AWS Account & OIDC Provider configured for GitHub Actions.
*   **IMPORTANT**: You must add this specific repository (`the-tech-challenge/repo-name`) to your OIDC Provider's Trust Policy.
    *   This allows the pipeline to act as the IAM Role.
    *   Without this, the pipeline cannot push Docker images to ECR or look up EC2 instances.
*   Terraform installed locally (optional, for manual runs).

### 2. How Retrieval & Deployment Works
This pipeline uses a **dynamic lookup strategy** to ensure it deploys to the correct infrastructure, even for multiple environments:

1.  **Tag-Based Lookup**: The workflow uses the `PROJECT_NAME` variable (default: `flask-challenge`) to search for AWS resources with the tag `Project=<PROJECT_NAME>`.
    *   It finds the specific **EC2 Instance** to deploy to.
    *   It finds the specific **ECR Repository** to push the image to.
2.  **Scope by Project**: If you are deploying multiple projects or environments (e.g., `dev` vs `prod`) in the same account, simply change the `PROJECT_NAME` variable. The pipeline will automatically find the matching resources for *that* specific project.
3.  **No Hardcoding**: We do not hardcode Instance IDs or Repo URIs, making the pipeline portable and reusable.

### 2. Configure Repositories
Ensure the following Secrets/Vars are set in this repository:

**Secrets**:
*   `AWS_ROLE_ARN`: The OIDC Role ARN (e.g., `arn:aws:iam::123456789012:role/github-oidc-role`).

**Variables**:
*   `AWS_REGION`: Target AWS Region (default: `us-east-1`).
*   `PROJECT_NAME`: Project tag to find resources (default: `flask-challenge`).

### 3. Deploy Infrastructure
Go to the **tech-challenge-infrastructure** repository and run the **Terraform Apply** workflow.
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
Run the **Terraform Destroy** workflow in the `tech-challenge-infrastructure` repository.
