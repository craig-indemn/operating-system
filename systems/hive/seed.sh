#!/usr/bin/env bash
# seed.sh — Idempotent seed script for initial Hive entities.
# Creates people, companies, products, projects, brands, platforms.
# Safe to re-run: checks for existing records before creating.
set -euo pipefail

HIVE="$(dirname "$0")/../../scripts/secrets-proxy/hive"

# Helper: create entity only if it doesn't already exist
create_if_missing() {
    local type="$1"
    local name="$2"
    shift 2
    # Check if record exists (by slugified name)
    local slug
    slug=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
    if $HIVE get "$slug" --format json 2>/dev/null | grep -q "record_id"; then
        echo "  EXISTS: $slug ($type)"
        return 0
    fi
    echo "  CREATE: $slug ($type)"
    $HIVE create "$type" "$name" "$@" 2>&1 | head -1
}

echo "=== Seeding Hive Entities ==="
echo ""

# ─── People ───
echo "People:"
create_if_missing person "Craig" --email craig@indemn.ai --role "Technical Partner" --company indemn --domains indemn,career-catalyst,personal
create_if_missing person "Cam" --email cam@indemn.ai --role "CEO" --company indemn --domains indemn
echo ""

# ─── Companies ───
echo "Companies:"
create_if_missing company "Indemn" --domains indemn --industry "Insurance Technology" --relationship own
echo ""

# ─── Products ───
echo "Products:"
create_if_missing product "Voice Agent" --company indemn --domains indemn --description "Conversational AI agent for insurance — voice and chat"
create_if_missing product "Chat Agent" --company indemn --domains indemn --description "V1 chat agent platform for insurance lead gen and FAQ"
create_if_missing product "Jarvis" --company indemn --domains indemn --description "AI agent builder — V2 platform config-driven agent creation"
create_if_missing product "Operating System" --domains indemn,career-catalyst,personal --description "Connected intelligence layer — skills, projects, systems, the Hive"
echo ""

# ─── Projects (dynamic from projects/ directory) ───
echo "Projects:"
OS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
for project_dir in "$OS_ROOT"/projects/*/; do
    project_name=$(basename "$project_dir")
    # Determine domain from project name
    domain="indemn"
    case "$project_name" in
        engineering-blog|content-system) domain="career-catalyst" ;;
        os-*) domain="indemn" ;;
    esac
    create_if_missing project "$project_name" --domains "$domain" --status active
done
echo ""

# ─── Brands ───
echo "Brands:"
create_if_missing brand "Personal" --domains career-catalyst,personal --voice "Authentic, technical, storytelling"
create_if_missing brand "Indemn" --domains indemn --voice "Professional, innovative, insurance-tech"
create_if_missing brand "Career Catalyst" --domains career-catalyst --voice "Empowering, practical, career growth"
echo ""

# ─── Platforms ───
echo "Platforms:"
create_if_missing platform "GitHub" --platform-type code --url "https://github.com/indemn-ai" --domains indemn,career-catalyst
create_if_missing platform "Linear" --platform-type project --url "https://linear.app" --domains indemn
create_if_missing platform "Slack" --platform-type communication --domains indemn
create_if_missing platform "Vercel" --platform-type infrastructure --url "https://vercel.com" --domains indemn,career-catalyst
create_if_missing platform "MongoDB Atlas" --platform-type infrastructure --domains indemn
create_if_missing platform "Stripe" --platform-type payment --domains indemn
create_if_missing platform "Airtable" --platform-type other --domains indemn
create_if_missing platform "Google Workspace" --platform-type communication --domains indemn
create_if_missing platform "LinkedIn" --platform-type publishing --domains career-catalyst
create_if_missing platform "Substack" --platform-type publishing --domains career-catalyst
echo ""

echo "=== Seed complete ==="
$HIVE status
