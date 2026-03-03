---
name: aws
description: Manage AWS infrastructure — Secrets Manager, Parameter Store, EC2, IAM, and ECS. Use when the user asks about AWS services, secrets, infrastructure, or deployments.
---

# AWS CLI

Manage Indemn's AWS infrastructure. Single account (780354157690), us-east-1 region.

## Status Check

```bash
aws sts get-caller-identity && echo "AWS CLI AUTHENTICATED" || echo "AWS CLI NOT CONFIGURED"
```

## Setup

### Prerequisites
- AWS CLI v2 installed (`brew install awscli`)
- IAM user with appropriate permissions
- Access key configured in `~/.aws/credentials`

### Configure
```bash
aws configure
# Access Key ID: (from IAM console)
# Secret Access Key: (from IAM console)
# Default region: us-east-1
# Output format: json
```

### Environment Variables (in OS .env)
```
AWS_ACCOUNT_ID=780354157690
AWS_DEFAULT_REGION=us-east-1
AWS_DEV_INSTANCE_ID=i-0fde0af9d216e9182
AWS_PROD_INSTANCE_ID=i-00ef8e2bfa651aaa8
```

## Account Context

- **Account ID:** 780354157690
- **Region:** us-east-1
- **IAM User:** craig (admin access)
- **Key instances:** dev-services (i-0fde0af9d216e9182), prod-services (i-00ef8e2bfa651aaa8)

## What's Deployed

### IAM Roles
| Role | Purpose | Attached To |
|------|---------|-------------|
| `indemn-dev-services` | EC2 instance role — read `dev/*` secrets and `/dev/*` params, explicit deny on `prod/*` | dev-services EC2 (i-0fde0af9d216e9182) |
| `github-actions-deploy` | GitHub Actions OIDC — deploy to dev, read dev secrets, ECR push/pull, explicit deny on `prod/*` | GitHub OIDC federation (indemn-ai org) |

### OIDC Provider
- `arn:aws:iam::780354157690:oidc-provider/token.actions.githubusercontent.com`
- Scoped to `repo:indemn-ai/*:*`

### Secrets Manager (dev)
18 secrets under `dev/` — 16 shared (`dev/shared/*`), 2 observability-specific (`dev/observability/*`).
```bash
aws secretsmanager list-secrets --filters Key=name,Values="dev/" --query 'SecretList[].Name' --output table
```

### Parameter Store (dev)
37 parameters under `/dev/` — shared config and observability-specific.
```bash
aws ssm get-parameters-by-path --path "/dev/" --recursive --query 'Parameters[].Name' --output table
```

## Secrets Manager

Stores credentials: API keys, database passwords, tokens. Supports automatic rotation, JSON secrets, versioning.

### Path Convention
```
{env}/shared/{secret-name}        # Cross-service credentials (no leading slash)
{env}/{service}/{secret-name}     # Service-specific credentials
```

Examples: `dev/shared/mongodb-uri`, `dev/shared/anthropic-api-key`, `dev/observability/demo-credentials`

### Common Operations

```bash
# Create a plain string secret
aws secretsmanager create-secret \
  --name "dev/shared/mongodb-uri" \
  --description "MongoDB Atlas dev cluster connection string" \
  --secret-string "mongodb+srv://..."

# Create a JSON secret (group related values)
aws secretsmanager create-secret \
  --name "dev/shared/langfuse-keys" \
  --description "Langfuse public and secret keys" \
  --secret-string '{"public_key":"pk-lf-...","secret_key":"sk-lf-..."}'

# Read a secret
aws secretsmanager get-secret-value --secret-id "dev/shared/mongodb-uri" --query 'SecretString' --output text

# Read a JSON secret field
aws secretsmanager get-secret-value --secret-id "dev/shared/langfuse-keys" --query 'SecretString' --output text | jq -r '.secret_key'

# List secrets by prefix
aws secretsmanager list-secrets --filters Key=name,Values="dev/shared/" --query 'SecretList[].Name' --output table

# Update a secret
aws secretsmanager put-secret-value --secret-id "dev/shared/mongodb-uri" --secret-string "new-value"

# Delete a secret (7-day recovery window)
aws secretsmanager delete-secret --secret-id "dev/shared/mongodb-uri" --recovery-window-in-days 7
```

## Parameter Store

Stores non-sensitive configuration: service URLs, feature flags, environment names. Free for standard parameters.

### Path Convention
```
/{env}/shared/{param-name}         # Cross-service config (leading slash required)
/{env}/{service}/{param-name}      # Service-specific config
```

Examples: `/dev/shared/llm-provider`, `/dev/observability/auth-enabled`

### Common Operations

```bash
# Create a parameter
aws ssm put-parameter \
  --name "/dev/shared/llm-provider" \
  --value "anthropic" \
  --type "String" \
  --description "LLM provider for dev environment"

# Read a parameter
aws ssm get-parameter --name "/dev/shared/llm-provider" --query 'Parameter.Value' --output text

# List by path
aws ssm get-parameters-by-path --path "/dev/shared/" --query 'Parameters[].{Name:Name,Value:Value}' --output table

# List all for an environment (recursive)
aws ssm get-parameters-by-path --path "/dev/" --recursive --query 'Parameters[].{Name:Name,Value:Value}' --output table

# Update
aws ssm put-parameter --name "/dev/shared/llm-provider" --value "openai" --overwrite

# Delete
aws ssm delete-parameter --name "/dev/shared/llm-provider"
```

## EC2

```bash
# List running instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].{Name:Tags[?Key==`Name`].Value|[0],Id:InstanceId,Type:InstanceType,AZ:Placement.AvailabilityZone}' \
  --output table

# Check instance IAM role
aws ec2 describe-instances --instance-ids i-0fde0af9d216e9182 \
  --query 'Reservations[0].Instances[0].IamInstanceProfile.Arn' --output text
```

## IAM — Instance Profiles for EC2

EC2 instances get IAM permissions through instance profiles. The pattern:

```bash
# 1. Write a trust policy that lets EC2 assume the role
cat > /tmp/ec2-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# 2. Create the role
aws iam create-role \
  --role-name "indemn-dev-services" \
  --description "Dev EC2 - read dev secrets only" \
  --assume-role-policy-document file:///tmp/ec2-trust-policy.json

# 3. Attach an inline policy (least-privilege, with explicit deny on prod)
aws iam put-role-policy \
  --role-name "indemn-dev-services" \
  --policy-name "dev-secrets-and-parameters-readonly" \
  --policy-document file:///tmp/dev-secrets-policy.json

# 4. Create instance profile and add role
aws iam create-instance-profile --instance-profile-name "indemn-dev-services"
aws iam add-role-to-instance-profile \
  --instance-profile-name "indemn-dev-services" \
  --role-name "indemn-dev-services"

# 5. Attach to EC2 (non-disruptive — doesn't restart anything)
aws ec2 associate-iam-instance-profile \
  --instance-id i-0fde0af9d216e9182 \
  --iam-instance-profile Name="indemn-dev-services"
```

### Least-Privilege Policy Pattern

Every env-scoped role should:
1. Allow read on `{env}/*` secrets and `/{env}/*` parameters
2. Explicitly deny the other environment's resources
3. Use inline policies (`put-role-policy`) for env-specific rules

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadDevSecrets",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
      "Resource": "arn:aws:secretsmanager:us-east-1:780354157690:secret:dev/*"
    },
    {
      "Sid": "ReadDevParameters",
      "Effect": "Allow",
      "Action": ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"],
      "Resource": "arn:aws:ssm:us-east-1:780354157690:parameter/dev/*"
    },
    {
      "Sid": "DenyProdExplicitly",
      "Effect": "Deny",
      "Action": ["secretsmanager:GetSecretValue", "ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:780354157690:secret:prod/*",
        "arn:aws:ssm:us-east-1:780354157690:parameter/prod/*"
      ]
    }
  ]
}
```

## GitHub Actions OIDC Federation

GitHub Actions authenticates to AWS by assuming an IAM role via OIDC — no long-lived access keys in GitHub secrets.

### What's Deployed
- OIDC provider: `token.actions.githubusercontent.com`
- Role: `github-actions-deploy` — scoped to `indemn-ai` org repos
- Permissions: read dev secrets/params, ECR push/pull, explicit prod deny

### Setup (already done, for reference)
```bash
# 1. Create OIDC provider (one-time per account)
aws iam create-open-id-connect-provider \
  --url "https://token.actions.githubusercontent.com" \
  --client-id-list "sts.amazonaws.com" \
  --thumbprint-list "1c58a3a8518e8759bf075b76b750d4f2df264fcd"

# 2. Create role with trust policy scoped to indemn-ai org
aws iam create-role \
  --role-name "github-actions-deploy" \
  --assume-role-policy-document file:///tmp/github-actions-trust-policy.json

# 3. Attach deploy permissions
aws iam put-role-policy \
  --role-name "github-actions-deploy" \
  --policy-name "deploy-dev-only" \
  --policy-document file:///tmp/github-actions-policy.json
```

### Workflow Usage
Add to any GitHub Actions workflow:
```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    steps:
      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::780354157690:role/github-actions-deploy
          aws-region: us-east-1
```

## Service Migration Playbook

To migrate a new service from `.env` files to AWS secrets:

### 1. Inventory env vars
Read the service's `.env`, `.env.dev`, `.env.prod` files. Classify each variable:
- **Secrets Manager**: API keys, passwords, tokens, connection strings with credentials
- **Parameter Store**: URLs, feature flags, environment names, non-sensitive config
- **Shared vs service-specific**: Does this value differ between services?

### 2. Create secrets and parameters
Shared values go under `{env}/shared/`, service-specific under `{env}/{service}/`.
Group related values as JSON secrets (e.g., `redis-credentials` with host, port, password, url).

### 3. Add aws-env-loader.sh
Copy `scripts/aws-env-loader.sh` from indemn-observability. Update the `export_secret` calls and `PARAM_MAP` dict for the new service's env var names.

### 4. Update Dockerfile
- Install AWS CLI v2 in the runtime stage
- Change CMD to ENTRYPOINT + CMD pattern:
  ```dockerfile
  ENTRYPOINT ["./scripts/aws-env-loader.sh"]
  CMD ["node", "server.js"]  # or whatever the service runs
  ```

### 5. Update docker-compose.yml
Replace `env_file: .env` with AWS env loader config:
```yaml
environment:
  - AWS_ENV=${AWS_ENV:-dev}
  - AWS_SERVICE=my-service
  - AWS_REGION=${AWS_REGION:-us-east-1}
  - AWS_SKIP_SECRETS=${AWS_SKIP_SECRETS:-false}
```

### 6. Backward compatibility
Set `AWS_SKIP_SECRETS=true` to fall back to `.env` files. This lets you deploy incrementally.

## Conventions

- Secrets Manager paths: **no** leading slash (`dev/shared/name`)
- Parameter Store paths: **with** leading slash (`/dev/shared/name`)
- Use `--query` and `--output` for clean output — prefer over piping through jq
- Tag resources with `Environment` (dev/prod) and `Service` tags
- Use `--description` on all secrets and parameters
- Always include explicit `Deny` on prod in dev roles (and vice versa)
- Never touch prod resources without explicit user confirmation
