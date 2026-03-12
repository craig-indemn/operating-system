# Production Safety

**NEVER write to production systems or modify EC2 instances without explicit user permission.**

This rule applies to ALL tools, skills, and commands — no exceptions.

## What requires explicit permission

- **EC2**: Any command that modifies instance state — restart/stop/start services, deploy code, write files, kill processes, `docker stop/restart/rm/exec` with writes, package installs, config changes. This applies to ALL instances, not just production.
- **Production databases**: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or any schema change on production data.
- **Production secrets**: Creating, updating, or deleting secrets under `indemn/prod/*` in AWS Secrets Manager or Parameter Store.
- **Deployments**: Pushing to production branches, triggering production CI/CD, modifying production Vercel deployments.
- **Infrastructure**: Creating/terminating EC2 instances, modifying security groups, IAM roles, or any AWS resource that affects production.

## What is allowed without permission

- **Read-only EC2 commands**: `hostname`, `uptime`, `df -h`, `docker ps`, `docker logs`, `cat` (reading files/configs), `ls`, `top`, `free -m`, log tailing.
- **Read-only database queries**: SELECT statements on any database.
- **Read-only AWS queries**: `describe-instances`, `list-secrets`, `get-parameter`, instance status checks.

## How to ask

State what you want to do, which instance/system it affects, and why. Wait for explicit "yes" or "go ahead" before executing.
