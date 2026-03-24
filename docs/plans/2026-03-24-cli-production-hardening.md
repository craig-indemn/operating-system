# Indemn CLI Production Hardening Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Harden the API key auth (copilot-server) and CLI (indemn-cli) for production use by the team.

**Architecture:** Two repos, two PRs. Copilot-server gets 3 security fixes to the API key auth middleware/routes. Indemn-cli gets 2 fixes (config file permissions, dependency vulnerability). After both merge, deploy copilot-server to prod, test E2E, generate prod API keys, publish CLI v1.2.0.

**Tech Stack:** Node.js (copilot-server), TypeScript (indemn-cli), MongoDB, Firebase Auth

---

## Repo 1: copilot-server

**Branch from:** `origin/main` (at or after PR #806 merge)
**Branch name:** `fix/api-key-security-hardening`
**Repo path:** `/Users/home/Repositories/copilot-server`

### Task 1: Set up the branch

**Step 1: Pull latest main and create branch**

```bash
cd /Users/home/Repositories/copilot-server
git checkout main
git pull origin main
git checkout -b fix/api-key-security-hardening
```

**Step 2: Verify API key auth files exist on main**

```bash
ls -la middleware/apiKeyToJwt.js routes/apiKeys.js services/apiKeyService.js models/apiKey.js
```

Expected: All 4 files present (from PR #806).

**Step 3: Commit (nothing to commit yet — just verification)**

---

### Task 2: Add JWT expiration to API-key-generated tokens

**Files:**
- Modify: `middleware/apiKeyToJwt.js:43-47`

**Why:** JWTs generated from API keys have no expiration. If a JWT is somehow intercepted, it's valid forever. Adding a short expiry ensures the per-request JWT is bounded. The API key itself remains long-lived (intended), but the JWT it generates should expire quickly since it's a per-request passthrough.

**Step 1: Modify apiKeyToJwt.js**

In `middleware/apiKeyToJwt.js`, replace the signOptions block (lines 43-47):

```javascript
      var signOptions = {
        issuer: process.env.SIGN_OPTIONS_ISSUER,
        subject: "user",
        audience: process.env.SIGN_OPTIONS_ISSUER,
      };
```

With:

```javascript
      var signOptions = {
        issuer: process.env.SIGN_OPTIONS_ISSUER,
        subject: "user",
        audience: process.env.SIGN_OPTIONS_ISSUER,
        expiresIn: "1h",
      };
```

**Rationale:** 1 hour is generous for a per-request passthrough JWT. The middleware generates a fresh JWT on every API call, so the expiry just limits reuse if intercepted. No impact on the API key's own lifetime.

**Step 2: Verify the file**

```bash
grep -n "expiresIn" middleware/apiKeyToJwt.js
```

Expected: Line ~47 shows `expiresIn: "1h"`

**Step 3: Commit**

```bash
git add middleware/apiKeyToJwt.js
git commit -m "fix: add 1h expiration to API-key-generated JWTs"
```

---

### Task 3: Validate bearer token format

**Files:**
- Modify: `middleware/apiKeyToJwt.js:27-32`

**Why:** Currently any string starting with `ind_` is passed to validateKey, regardless of length or content. A strict regex rejects malformed tokens immediately, avoiding unnecessary database lookups and preventing oversized tokens from being processed.

**Step 1: Modify apiKeyToJwt.js**

Replace lines 27-32:

```javascript
  var token = parts[1];

  // Only intercept Bearer tokens that look like API keys (ind_ prefix)
  if (scheme.toLowerCase() !== "bearer" || !token.startsWith("ind_")) {
    return next();
  }
```

With:

```javascript
  var token = parts[1];

  // Only intercept Bearer tokens that match API key format: ind_dev_ or ind_live_ + 64 hex chars
  if (scheme.toLowerCase() !== "bearer" || !/^ind_(dev_|live_)[a-f0-9]{64}$/.test(token)) {
    return next();
  }
```

**Rationale:** API keys are generated as `ind_dev_` or `ind_live_` + 32 random bytes (64 hex chars). This regex matches exactly that format and rejects everything else without hitting the database.

**Step 2: Verify the file**

```bash
grep -n "ind_" middleware/apiKeyToJwt.js
```

Expected: The regex pattern on the line that previously had `startsWith`.

**Step 3: Commit**

```bash
git add middleware/apiKeyToJwt.js
git commit -m "fix: validate API key format with strict regex before DB lookup"
```

---

### Task 4: Validate API key name field

**Files:**
- Modify: `routes/apiKeys.js:15-21`

**Why:** The name field accepts any string with no length or character restrictions. Add trim, length limit, and safe character pattern to prevent injection or abuse.

**Step 1: Modify routes/apiKeys.js**

Replace lines 14-21:

```javascript
    var userId = req.user._id;
    var name = req.body.name;

    if (!name) {
      return res
        .status(400)
        .json({ success: false, msg: "Name is required." });
    }
```

With:

```javascript
    var userId = req.user._id;
    var name = typeof req.body.name === "string" ? req.body.name.trim() : "";

    if (!name) {
      return res
        .status(400)
        .json({ success: false, msg: "Name is required." });
    }

    if (name.length > 255) {
      return res
        .status(400)
        .json({ success: false, msg: "Name must be 255 characters or less." });
    }

    if (!/^[a-zA-Z0-9\-_\s.]+$/.test(name)) {
      return res
        .status(400)
        .json({ success: false, msg: "Name contains invalid characters. Use letters, numbers, hyphens, underscores, spaces, and periods." });
    }
```

**Rationale:** Trims whitespace, enforces max length, restricts to safe characters. The pattern allows common key names like "Craig's CLI", "dev-testing", "ci_pipeline_v2".

Wait — single quotes aren't in the regex. Let me adjust. Actually, keep it simple: alphanumeric, hyphens, underscores, spaces, periods. If someone wants "Craig's CLI" they can use "Craigs CLI" or "craig-cli". Safer to not allow quotes.

**Step 2: Verify the file**

```bash
grep -n "255\|invalid characters" routes/apiKeys.js
```

Expected: Both validation messages appear.

**Step 3: Commit**

```bash
git add routes/apiKeys.js
git commit -m "fix: validate API key name — trim, max length, safe characters"
```

---

### Task 5: Create PR for copilot-server

**Step 1: Push and create PR**

```bash
cd /Users/home/Repositories/copilot-server
git push -u origin fix/api-key-security-hardening
gh pr create --title "fix: API key auth security hardening" --body "$(cat <<'EOF'
## Summary
Security hardening for the API key authentication system (PR #806) before production deployment.

- **JWT expiration:** API-key-generated JWTs now expire after 1 hour (previously no expiry)
- **Token format validation:** Strict regex rejects malformed bearer tokens before DB lookup
- **Name field validation:** Trim, 255-char max, safe character pattern on key creation

## Context
Preparing to deploy CLI/MCP API key auth to production copilot-server. These fixes address findings from a security audit of the auth middleware.

## Test plan
- [ ] Create API key with valid name — succeeds
- [ ] Create API key with >255 char name — rejected with 400
- [ ] Create API key with special chars in name — rejected with 400
- [ ] Use valid API key — request succeeds, JWT has exp claim
- [ ] Use malformed bearer token (wrong prefix, wrong length) — passes through to passport (401)
- [ ] Existing API keys continue to work (no breaking change)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Repo 2: indemn-cli

**Branch from:** `main`
**Branch name:** `fix/production-security-hardening`
**Repo path:** `/Users/home/Repositories/indemn-cli`

### Task 6: Set up the branch

**Step 1: Create branch**

```bash
cd /Users/home/Repositories/indemn-cli
git checkout main
git pull origin main
git checkout -b fix/production-security-hardening
```

---

### Task 7: Fix config file permissions

**Files:**
- Modify: `src/sdk/client.ts:64-69`

**Why:** `~/.indemn/config.json` is created with default permissions (644 — world-readable). The file contains the API key in plaintext. On shared systems, any user can read it. Fix: chmod 600 after every save.

**Step 1: Add fs import and chmod after save**

In `src/sdk/client.ts`, replace the `saveConfig` method (lines 64-69):

```typescript
  static saveConfig(config: Partial<IndemnConfig>): void {
    const store = IndemnClient.getConfigStore();
    for (const [key, value] of Object.entries(config)) {
      store.set(key as keyof IndemnConfig, value);
    }
  }
```

With:

```typescript
  static saveConfig(config: Partial<IndemnConfig>): void {
    const store = IndemnClient.getConfigStore();
    for (const [key, value] of Object.entries(config)) {
      store.set(key as keyof IndemnConfig, value);
    }
    // Restrict config file to owner-only (contains API key)
    try {
      const fs = await import('node:fs');
      fs.chmodSync(store.path, 0o600);
    } catch {
      // Non-fatal — Windows doesn't support Unix permissions
    }
  }
```

Wait — `saveConfig` is not async. Use dynamic require instead:

```typescript
  static saveConfig(config: Partial<IndemnConfig>): void {
    const store = IndemnClient.getConfigStore();
    for (const [key, value] of Object.entries(config)) {
      store.set(key as keyof IndemnConfig, value);
    }
    // Restrict config file to owner-only (contains API key)
    try {
      const { chmodSync } = require('node:fs');
      chmodSync(store.path, 0o600);
    } catch {
      // Non-fatal — Windows doesn't support Unix permissions
    }
  }
```

Actually, this is an ESM project (`"type": "module"` in package.json). Use `import { chmodSync } from 'node:fs'` at the top of the file.

**Corrected approach:** Add the import at the top of `client.ts`:

Add to the top of the file (after line 2):
```typescript
import { chmodSync } from 'node:fs';
```

Then replace `saveConfig`:

```typescript
  static saveConfig(config: Partial<IndemnConfig>): void {
    const store = IndemnClient.getConfigStore();
    for (const [key, value] of Object.entries(config)) {
      store.set(key as keyof IndemnConfig, value);
    }
    // Restrict config file to owner-only (contains API key)
    try {
      chmodSync(store.path, 0o600);
    } catch {
      // Non-fatal — Windows doesn't support Unix permissions
    }
  }
```

**Step 2: Build and verify**

```bash
cd /Users/home/Repositories/indemn-cli
npm run build
```

Expected: Clean build, no errors.

**Step 3: Manually verify permissions fix**

```bash
# Check current permissions
ls -la ~/.indemn/config.json
# Run any command that triggers saveConfig (e.g., login)
# Or: node -e "import('./dist/sdk/client.js').then(m => m.IndemnClient.saveConfig({}))"
# Check permissions after
ls -la ~/.indemn/config.json
```

Expected: Permissions change from `-rw-r--r--` to `-rw-------`.

**Step 4: Commit**

```bash
git add src/sdk/client.ts
git commit -m "fix: restrict config file permissions to owner-only (600)"
```

---

### Task 8: Fix socket.io-parser vulnerability

**Files:**
- Modify: `package.json` (dependency update)

**Why:** `npm audit` flags a high-severity DoS vulnerability in socket.io-parser 4.0.0-4.2.5 (unbounded binary attachments). Updating socket.io-client pulls in the fix.

**Step 1: Run npm audit to confirm**

```bash
cd /Users/home/Repositories/indemn-cli
npm audit 2>&1 | head -20
```

Expected: High severity vulnerability in socket.io-parser.

**Step 2: Update socket.io-client**

```bash
npm install socket.io-client@latest
```

**Step 3: Verify audit is clean**

```bash
npm audit 2>&1 | tail -5
```

Expected: `found 0 vulnerabilities` or no high/critical.

**Step 4: Build to verify nothing broke**

```bash
npm run build
```

Expected: Clean build.

**Step 5: Commit**

```bash
git add package.json package-lock.json
git commit -m "fix: update socket.io-client to patch high-severity DoS vulnerability"
```

---

### Task 9: Bump version to 1.2.0

**Files:**
- Modify: `package.json:3`

**Step 1: Bump version**

```bash
cd /Users/home/Repositories/indemn-cli
npm version minor --no-git-tag-version
```

This changes version from `1.1.1` to `1.2.0`.

**Step 2: Update CLI version string if hardcoded anywhere**

```bash
grep -rn "1\.1\.1" src/ --include="*.ts"
```

If any matches, update them to `1.2.0`.

**Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore: bump version to 1.2.0 for production release"
```

---

### Task 10: Build, test, and create PR

**Step 1: Full build**

```bash
cd /Users/home/Repositories/indemn-cli
npm run build
```

Expected: Clean build.

**Step 2: Run existing tests**

```bash
npm test
```

Expected: All tests pass.

**Step 3: Push and create PR**

```bash
git push -u origin fix/production-security-hardening
gh pr create --title "fix: production security hardening" --body "$(cat <<'EOF'
## Summary
Security hardening before production deployment.

- **Config file permissions:** `~/.indemn/config.json` now set to 600 (owner-only) after every save
- **Dependency fix:** Updated socket.io-client to patch high-severity DoS vulnerability (GHSA-677m-j7p3-52f9)
- **Version bump:** 1.1.1 → 1.2.0

## Test plan
- [ ] `indemn login` creates config with `-rw-------` permissions
- [ ] `npm audit` shows 0 high/critical vulnerabilities
- [ ] All existing E2E tests pass
- [ ] `npm run build` clean

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Deployment (after both PRs merge)

### Task 11: Verify production environment

**Step 1: Check GLOBAL_SECRET is set in prod**

This is the most critical pre-deployment check. If GLOBAL_SECRET is not set, anyone can forge JWTs using the hardcoded fallback `"nodeauthsecret"`.

```bash
# Check prod copilot-server environment for GLOBAL_SECRET
# Method depends on deployment platform — check Vercel env vars, AWS Parameter Store, etc.
# DO NOT print the actual secret value — just verify it exists and is non-empty
```

If GLOBAL_SECRET is not set in production, **STOP** — set it before deploying.

**Step 2: Check SIGN_OPTIONS_ISSUER is set in prod**

The JWT signOptions use `process.env.SIGN_OPTIONS_ISSUER` for issuer and audience. If unset, these will be `undefined` in the JWT. Not a security hole, but bad practice.

```bash
# Verify SIGN_OPTIONS_ISSUER is set in prod environment
```

---

### Task 12: Deploy copilot-server to production

**REQUIRES EXPLICIT USER PERMISSION** — this modifies production infrastructure.

Steps depend on the deployment pipeline. Options:
1. Merge PR to main → auto-deploy via CI/CD
2. Manual deploy via Vercel/AWS
3. SSH/SSM and pull latest

Verify after deployment:
```bash
# Smoke test: hit prod API with a known-bad key format
curl -s -o /dev/null -w "%{http_code}" https://copilot.indemn.ai/api/auth/api-keys \
  -H "Authorization: Bearer ind_bogus"
```

Expected: 401 (not 500).

---

### Task 13: Test E2E against production

**Step 1: Login against prod**

```bash
indemn login --env production
```

Use a valid team account. Verify:
- Firebase auth succeeds
- MFA flow works (if enabled)
- API key is generated and saved
- Config shows `environment: production`

**Step 2: Verify config permissions**

```bash
ls -la ~/.indemn/config.json
```

Expected: `-rw-------`

**Step 3: Test core commands against prod**

```bash
indemn whoami
indemn agents list
indemn kb list
indemn rubrics list
```

All should return data without errors.

**Step 4: Test MCP server**

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | indemn mcp serve 2>/dev/null | head -5
```

Should return the tool list JSON.

---

### Task 14: Publish CLI and generate prod API keys

**Step 1: Publish to npm**

```bash
cd /Users/home/Repositories/indemn-cli
npm publish --access public
```

**Step 2: Verify published version**

```bash
npm info @indemn/cli version
```

Expected: `1.2.0`

**Step 3: Generate API keys for team members**

Each team member runs:
```bash
npm install -g @indemn/cli
indemn login --env production
```

Or generate keys via curl for distribution:
```bash
# Generate a JWT for key creation (requires copilot-server access)
# Then: POST /api/auth/api-keys with { name: "team-member-name" }
```

---

## Summary

| Task | Repo | What | Risk |
|------|------|------|------|
| 1 | copilot-server | Branch setup | None |
| 2 | copilot-server | JWT expiration (1h) | Low — per-request passthrough |
| 3 | copilot-server | Token format regex | Low — rejects invalid tokens earlier |
| 4 | copilot-server | Name field validation | Low — new validation on new endpoint |
| 5 | copilot-server | Create PR | None |
| 6 | indemn-cli | Branch setup | None |
| 7 | indemn-cli | Config chmod 600 | Low — non-fatal on Windows |
| 8 | indemn-cli | Update socket.io-client | Low — patch dependency |
| 9 | indemn-cli | Version bump 1.2.0 | None |
| 10 | indemn-cli | Build, test, PR | None |
| 11 | Prod env | Verify GLOBAL_SECRET | **Critical check** |
| 12 | Prod deploy | Deploy copilot-server | **Production change** |
| 13 | Prod E2E | Full login + command test | None |
| 14 | npm | Publish + team keys | Public release |
