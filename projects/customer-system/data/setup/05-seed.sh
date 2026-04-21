#!/bin/bash
# =============================================================================
# Step 5: Seed Reference Data and Import
# =============================================================================
# Seeds reference entities with known data, then bulk imports from CSVs.
#
# Order matters: references first (other entities point to them),
# then conferences (companies reference them), then companies (contacts
# and everything else references them), then contacts.
#
# Note: The OS auto-generates per-entity CLI subcommands from entity
# definitions (e.g., `indemn stage create`, `indemn company list`).
# Field values are passed as --field-name flags with kebab-case names.
# =============================================================================

IMPORT_DIR="$(dirname "$0")/../import"

# ---------------------------------------------------------------------------
# Reference Data: Stages
# ---------------------------------------------------------------------------

indemn stage create --name "Contact" --probability 0.05 --stale-after-days 14 --order 1 \
  --definition "Initial contact made. No discovery conversation yet."

indemn stage create --name "Discovery" --probability 0.15 --stale-after-days 14 --order 2 \
  --definition "Active discovery conversation. Understanding their needs."

indemn stage create --name "Demo" --probability 0.25 --stale-after-days 10 --order 3 \
  --definition "Product demo scheduled or completed."

indemn stage create --name "Proposal" --probability 0.40 --stale-after-days 10 --order 4 \
  --definition "Proposal sent. Awaiting response."

indemn stage create --name "Negotiation" --probability 0.60 --stale-after-days 7 --order 5 \
  --definition "Active negotiation on terms, pricing, or scope."

indemn stage create --name "Verbal" --probability 0.80 --stale-after-days 5 --order 6 \
  --definition "Verbal agreement. Contract pending."

indemn stage create --name "Signed" --probability 1.00 --order 7 \
  --definition "Contract signed. Customer."

# ---------------------------------------------------------------------------
# Reference Data: Outcome Types (The Four Outcomes)
# ---------------------------------------------------------------------------

indemn outcometype create \
  --name "Revenue Growth" \
  --engine "Revenue Engine" \
  --description "Unlock capacity to capture missed revenue" \
  --key-metrics '["Premium from converted leads", "Conversion rate", "Average policy value", "After-hours capture rate"]' \
  --language-guidance "Lead with Revenue Growth — strongest proof point. Use 'Revenue Capacity' not 'cost savings'."

indemn outcometype create \
  --name "Operational Efficiency" \
  --engine "Efficiency Engine" \
  --description "Liberate staff from administrative drudgery" \
  --key-metrics '["Agent hours freed", "Resolution rate", "Touch reduction percentage", "Time to resolution"]' \
  --language-guidance "Use 'Resolution Rate' not 'deflection rate'. Frame as liberating people, not replacing them."

indemn outcometype create \
  --name "Client Retention" \
  --engine "Retention Engine" \
  --description "Protect the book, maximize lifetime value" \
  --key-metrics '["Policies retained", "Retention rate improvement", "Lapse prevention rate", "Cross-sell conversion"]' \
  --language-guidance "Frame as protecting the book. Renewal automation is the entry point."

indemn outcometype create \
  --name "Strategic Control" \
  --engine "Control Engine" \
  --description "Visibility, agility, governance" \
  --key-metrics '["Consistency score", "Compliance audit pass rate", "Brand adherence", "Data integration completeness"]' \
  --language-guidance "Frame as governance and visibility. SOC 2 Type II is a proof point."

# ---------------------------------------------------------------------------
# Bulk Import: Reference Entities
# ---------------------------------------------------------------------------

echo "Importing Associate Types..."
indemn associatetype bulk-create --source "$IMPORT_DIR/associate-types.csv"

# ---------------------------------------------------------------------------
# Bulk Import: Conferences (before companies -- companies reference them)
# ---------------------------------------------------------------------------

echo "Importing Conferences..."
indemn conference bulk-create --source "$IMPORT_DIR/conferences.csv"

# Transition conferences to their current stage
indemn conference transition "InsurTechNY Spring 2026" --to follow_up
indemn conference transition "ALER26 Spring 2026" --to follow_up

# ---------------------------------------------------------------------------
# Bulk Import: Companies
# ---------------------------------------------------------------------------

echo "Importing Companies (87 records)..."
indemn company bulk-create --source "$IMPORT_DIR/companies-merged.csv"

# ---------------------------------------------------------------------------
# Bulk Import: Contacts
# ---------------------------------------------------------------------------

echo "Importing Contacts (92 records)..."
indemn contact bulk-create --source "$IMPORT_DIR/contacts-merged.csv"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
echo "=== Seed Complete ==="
echo ""
indemn stage list
echo ""
indemn outcometype list
echo ""
indemn associatetype list --columns name,engine,maturity
echo ""
indemn conference list
echo ""
indemn company list --columns name,stage,cohort,owner --limit 10
echo ""
echo "Total companies: $(indemn company list --count)"
echo "Total contacts: $(indemn contact list --count)"
echo ""
echo "Done. The source of truth is live."
