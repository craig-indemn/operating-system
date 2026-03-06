#!/bin/bash
# Run on dev EC2 — prints only variable NAMES, no values

echo "=== google oauth vars (tiledesk) ==="
grep -i "GOOGLE.*CLIENT\|GOOGLE.*SECRET\|GOOGLE.*CALLBACK\|OAUTH" /opt/tiledesk/.env 2>/dev/null | cut -d'=' -f1

echo "=== groq (bot-service) ==="
grep -i "GROQ" /opt/bot-service/.env 2>/dev/null | cut -d'=' -f1

echo "=== google cloud SA (voice-service) ==="
grep -i "GOOGLE\|GCP\|GCLOUD" /opt/voice-service/.env 2>/dev/null | cut -d'=' -f1

echo "=== S3/AWS in middleware ==="
grep -i "S3\|AWS.*KEY\|AWS.*SECRET\|BUCKET" /opt/middleware-service/.env 2>/dev/null | cut -d'=' -f1

echo "=== stripe (payment + tiledesk) ==="
grep -i "STRIPE" /opt/payment-service/.env /opt/tiledesk/.env 2>/dev/null | sed 's/=.*//'

echo "=== firebase (tiledesk) ==="
grep -i "FIREBASE" /opt/tiledesk/.env 2>/dev/null | cut -d'=' -f1

echo "=== service tokens (tiledesk + middleware) ==="
grep -i "SYSTEM_USER\|APPS_ACCESS\|CONVERSATION.*TOKEN\|CONVERSATION.*SERVICE" /opt/tiledesk/.env /opt/middleware-service/.env 2>/dev/null | sed 's/=.*//'

echo "=== copilot api (kb + ops + middleware) ==="
grep -i "COPILOT_API\|TILEDESK_API" /opt/openai-fastapi/.env /opt/operations_api/.env /opt/middleware-service/.env 2>/dev/null | sed 's/=.*//'

echo "=== admin passwords (tiledesk) ==="
grep -i "SUPER_PASS\|ADMIN_PASS\|ACCESS_TOKEN_SECRET" /opt/tiledesk/.env 2>/dev/null | cut -d'=' -f1
