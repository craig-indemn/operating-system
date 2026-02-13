---
name: github
description: Access GitHub repos, PRs, issues, and code review using the gh CLI. Use for any GitHub/code interaction.
---

# GitHub

Full GitHub access via `gh` CLI. Indemn org: `indemn-ai` (30 repos).

## Status Check

```bash
which gh && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
gh auth status 2>&1 | grep -q "Logged in" && echo "AUTHENTICATED" || echo "NOT AUTHENTICATED"
```

## Setup

### Install
```bash
brew install gh
```

### Authenticate
```bash
gh auth login
```
Select GitHub.com, HTTPS, authenticate via browser. Done.

## Usage

### Repos
```bash
gh repo list indemn-ai --limit 30
gh repo clone indemn-ai/bot-service
```

### Pull Requests
```bash
gh pr list --repo indemn-ai/bot-service
gh pr view 42 --repo indemn-ai/bot-service
gh pr create --title "Fix timeout bug" --body "Description here"
gh pr diff 42 --repo indemn-ai/bot-service
gh pr checks 42 --repo indemn-ai/bot-service
```

### Issues
```bash
gh issue list --repo indemn-ai/bot-service
gh issue create --title "Bug: timeout on large payloads" --body "Details"
gh issue view 15 --repo indemn-ai/bot-service
```

### Code Search
```bash
gh search code "extraction_pipeline" --owner indemn-ai
```

### API (raw)
For anything not covered by built-in commands:
```bash
gh api repos/indemn-ai/bot-service/pulls/42/comments
gh api repos/indemn-ai/bot-service/actions/runs --jq '.workflow_runs[:5]'
```

### Review PRs
```bash
gh pr review 42 --approve
gh pr review 42 --comment --body "Looks good, one nit on line 45"
gh pr review 42 --request-changes --body "Need tests for the new endpoint"
```
