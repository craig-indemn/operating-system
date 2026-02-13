---
name: stripe
description: Access Stripe revenue data, subscriptions, customers, and payments using the stripe CLI. Use for financial/billing queries.
---

# Stripe

Revenue analytics, subscription management, and payment data via official `stripe` CLI.

## Status Check

```bash
which stripe && echo "INSTALLED" || echo "NOT INSTALLED"
```

```bash
stripe customers list --limit 1 2>/dev/null && echo "AUTHENTICATED" || echo "NOT AUTHENTICATED"
```

## Setup

### Install
```bash
brew install stripe/stripe-cli/stripe
```

### Authenticate

**Option A: Interactive login (generates restricted key, valid 90 days)**
```bash
stripe login
```
**Note**: `stripe login` connects to whichever Stripe account you're logged into in the browser. If you only have sandbox access, it will connect to sandbox. For production data, ensure you're logged into the production Stripe account first, or use Option B with a live API key.

**Option B: API key (persistent)**
1. Go to Stripe Dashboard > Developers > API Keys
2. Copy the Secret key (`sk_live_...` for prod, `sk_test_...` for test)
3. Set environment variable:
```bash
export STRIPE_API_KEY="sk_live_..."
```

## Usage

### Revenue Overview
```bash
stripe charges list --limit 10 -d created[gte]=$(date -v-30d +%s)
stripe balance retrieve
```

### Customers
```bash
stripe customers list --limit 20
stripe customers retrieve cus_xxxxx
stripe customers search --query "email:'contact@insurica.com'"
```

### Subscriptions (MRR)
```bash
stripe subscriptions list --status active --limit 100
stripe subscriptions retrieve sub_xxxxx
```

### Invoices
```bash
stripe invoices list --customer cus_xxxxx --limit 10
stripe invoices retrieve in_xxxxx
```

### Webhook Testing (local dev)
```bash
stripe listen --forward-to localhost:4444/webhook
stripe trigger payment_intent.succeeded
```

### Live Logs
```bash
stripe logs tail
```

All commands support `--output json` for machine-readable output. Pipe to `jq` for filtering.
