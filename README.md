# Capstone Project 3 — Infrastructure-as-Code Pipeline

Terraform + GitHub Actions + Docker + Amazon ECR + ECS Fargate.

## Architecture
Developer PR/push → GitHub Actions CI (Terraform fmt/validate + Docker build/smoke test) → merge to main → OIDC authentication → ECR immutable image → ECS Fargate service behind an ALB. ECS health checks, CloudWatch logs, CPU autoscaling and deployment circuit-breaker rollback are configured in Terraform.

## Repository structure
- `app/`: minimal HTTP application and health endpoint
- `infra/`: Terraform AWS infrastructure
- `.github/workflows/ci.yml`: validation and container smoke test
- `.github/workflows/deploy.yml`: OIDC-based staging deployment and a deliberately guarded production placeholder

## Prerequisites
AWS CLI v2, Terraform >= 1.5, Docker, Git, AWS credentials with permission to provision the resources, and a GitHub repository.

## Quick start
1. Create a private GitHub repository named `infra-as-code-pipeline` and push this project.
2. Authenticate locally: `aws sts get-caller-identity`.
3. Set Terraform inputs without committing credentials:
   ```bash
   cd infra
   export TF_VAR_github_owner="YOUR_GITHUB_USERNAME"
   export TF_VAR_github_repo="infra-as-code-pipeline"
   terraform init
   terraform fmt -recursive
   terraform validate
   terraform plan
   ```
4. Review the plan and estimated AWS charges before running `terraform apply`.
5. Terraform creates the ECR repository and ECS service, but the initial task definition references a bootstrap image that does not exist yet. First build and push a bootstrap image:
   ```bash
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   REGION=ap-south-1
   REPO=infra-as-code-pipeline
   aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
   docker build -t "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:bootstrap" ../app
   docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:bootstrap"
   ```
   Because the ECR repository uses immutable tags, if `bootstrap` has already been pushed, use a new tag and update `infra/main.tf` before applying.
6. Create an IAM role trusted for this exact GitHub repository using GitHub OIDC, and attach least-privilege ECR push and ECS deployment permissions. Add its ARN as repository Actions secret `AWS_DEPLOY_ROLE_ARN`. Do not store AWS access keys in GitHub.
7. Configure GitHub Environments `staging` and `production`; add required reviewers to `production`. Do not enable production until a separate production ECS service and promotion workflow have been implemented.
8. After first deployment, check the `alb_url` Terraform output and open it in a browser.

## Remote state
The sample intentionally starts with local state so first-time setup is not blocked by backend bootstrapping. For the institute's remote-state requirement, create a private S3 bucket with versioning and encryption, then configure an S3 backend with state locking supported by your chosen Terraform version. Never commit state files.

## Runbook
- CI failure: open the failed GitHub Actions job and inspect Terraform validation or Docker smoke-test logs.
- ECS tasks unhealthy: check `aws ecs describe-services`, target group health, and `/ecs/infra-as-code-pipeline` CloudWatch logs.
- Failed rollout: ECS deployment circuit breaker is enabled with rollback; verify the previous task definition and application health.
- ALB 503: check ECS desired/running task count and target-group target health.
- Cleanup: after collecting evidence, run `terraform destroy` from `infra/` and confirm the plan carefully. ECR images/repository may require cleanup depending on the state and configuration.

## Cost and safety
An ALB, public IPv4 addresses, Fargate, logs, and data transfer can incur charges. This is a teaching scaffold, not a claim of production readiness. Review IAM permissions, subnet architecture, secrets, state locking, and deployment environments before production use.

## Evidence checklist
- [ ] CI passes on a pull request
- [ ] Terraform plan and validation output saved
- [ ] Docker health endpoint returns HTTP 200
- [ ] ECR image tagged with Git commit SHA
- [ ] ECS service stable and ALB URL loads
- [ ] Staging deployment workflow succeeds
- [ ] Production environment approval configured
- [ ] At least 15 meaningful commits
- [ ] Architecture, pipeline flow, runbook, cost estimate documented
