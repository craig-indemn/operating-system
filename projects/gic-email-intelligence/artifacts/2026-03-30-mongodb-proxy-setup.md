---
ask: "Document the MongoDB Atlas proxy setup on dev-services EC2 for Railway deployment"
created: 2026-03-30
workstream: gic-email-intelligence
session: 2026-03-30-a
sources:
  - type: aws
    description: "EC2 dev-services instance, security group sg-d4163da4, SSM commands"
---

# MongoDB Atlas Proxy — Railway to Atlas via EC2

## Why This Exists

Railway can't connect directly to MongoDB Atlas because the Atlas IP allowlist doesn't include Railway's IPs, and nobody currently has Atlas admin access to add them. As an intermediate step, we proxy MongoDB traffic through the `dev-services` EC2 instance (44.196.55.84), which is already in the Atlas allowlist.

**This is temporary.** Once someone gets Atlas admin access, add Railway's static IP (`162.220.234.15`) directly to the Atlas allowlist and remove the proxy.

## Architecture

```
Railway (162.220.234.15) → EC2 dev-services (44.196.55.84) → MongoDB Atlas
                              socat TCP proxy
```

## What Was Set Up

### EC2: dev-services (i-0fde0af9d216e9182)

**socat installed** via `apt-get install socat`

**6 proxy processes** running (nohup, not systemd):

| EC2 Port | Forwards To | Cluster |
|----------|-------------|---------|
| 27017 | ac-2daqzel-shard-00-00.pj4xyep.mongodb.net:27017 | Dev |
| 27018 | ac-2daqzel-shard-00-01.pj4xyep.mongodb.net:27017 | Dev |
| 27019 | ac-2daqzel-shard-00-02.pj4xyep.mongodb.net:27017 | Dev |
| 27020 | prod-indemn-shard-00-00.3h3ab.mongodb.net:27017 | Prod |
| 27021 | prod-indemn-shard-00-01.3h3ab.mongodb.net:27017 | Prod |
| 27022 | prod-indemn-shard-00-02.3h3ab.mongodb.net:27017 | Prod |

**Logs:** `/var/log/mongodb-proxy-{dev,prod}-{0,1,2}.log`

**Note:** These are nohup processes, NOT systemd services. They will stop on EC2 reboot. To restart:
```bash
# SSH or SSM into dev-services, then:
nohup socat TCP-LISTEN:27017,fork,reuseaddr TCP:ac-2daqzel-shard-00-00.pj4xyep.mongodb.net:27017 > /var/log/mongodb-proxy-dev-0.log 2>&1 &
nohup socat TCP-LISTEN:27018,fork,reuseaddr TCP:ac-2daqzel-shard-00-01.pj4xyep.mongodb.net:27017 > /var/log/mongodb-proxy-dev-1.log 2>&1 &
nohup socat TCP-LISTEN:27019,fork,reuseaddr TCP:ac-2daqzel-shard-00-02.pj4xyep.mongodb.net:27017 > /var/log/mongodb-proxy-dev-2.log 2>&1 &
nohup socat TCP-LISTEN:27020,fork,reuseaddr TCP:prod-indemn-shard-00-00.3h3ab.mongodb.net:27017 > /var/log/mongodb-proxy-prod-0.log 2>&1 &
nohup socat TCP-LISTEN:27021,fork,reuseaddr TCP:prod-indemn-shard-00-01.3h3ab.mongodb.net:27017 > /var/log/mongodb-proxy-prod-1.log 2>&1 &
nohup socat TCP-LISTEN:27022,fork,reuseaddr TCP:prod-indemn-shard-00-02.3h3ab.mongodb.net:27017 > /var/log/mongodb-proxy-prod-2.log 2>&1 &
```

### Security Group: sg-d4163da4 (ptrkdy)

**Added rule:** TCP 27017-27022 from `162.220.234.15/32` (Railway's static outbound IP)

Only Railway can reach the proxy ports. No other IPs are allowed.

### Railway Connection Strings

**Dev environment:**
```
MONGODB_URI=mongodb://devadmin:<password>@44.196.55.84:27017/?tls=true&authSource=admin&directConnection=true&tlsAllowInvalidCertificates=true
MONGODB_DATABASE=gic_email_intelligence_dev
TILEDESK_DB_URI=mongodb://devadmin:<password>@44.196.55.84:27017/tiledesk?tls=true&authSource=admin&directConnection=true&tlsAllowInvalidCertificates=true
```

**Prod environment (when ready):**
```
MONGODB_URI=mongodb://devadmin:<password>@44.196.55.84:27020/?tls=true&authSource=admin&directConnection=true&tlsAllowInvalidCertificates=true
MONGODB_DATABASE=gic_email_intelligence
TILEDESK_DB_URI=mongodb://devadmin:<password>@44.196.55.84:27020/tiledesk?tls=true&authSource=admin&directConnection=true&tlsAllowInvalidCertificates=true
```

**Key parameters:**
- `directConnection=true` — prevents MongoDB driver from discovering replica set members and trying to connect to Atlas hostnames directly (which would bypass the proxy)
- `tlsAllowInvalidCertificates=true` — the TLS certificate is for the Atlas hostname, not the EC2 IP, so certificate validation would fail
- `tls=true` — Atlas requires TLS

## How to Remove (When Atlas Access Is Available)

1. Add Railway's static IP `162.220.234.15` to MongoDB Atlas Network Access allowlist (both dev and prod clusters)
2. Change Railway env vars back to direct Atlas connection:
   ```
   MONGODB_URI=mongodb+srv://devadmin:<password>@dev-indemn.pj4xyep.mongodb.net
   ```
3. Kill socat processes on dev-services: `pkill -f "socat TCP-LISTEN:2701"`
4. Remove security group rule: `aws ec2 revoke-security-group-ingress --group-id sg-d4163da4 --protocol tcp --port 27017-27022 --cidr 162.220.234.15/32`

## Credentials Reference

All from AWS Secrets Manager — see `artifacts/2026-03-30-production-deployment-plan.md` for the full env var list.

- MongoDB Atlas dev URI secret: `indemn/dev/shared/mongodb-uri`
- MongoDB Atlas prod URI secret: `indemn/prod/shared/mongodb-uri`
- Graph API credentials: `indemn/dev/services/gic-email-intel/graph-credentials`
