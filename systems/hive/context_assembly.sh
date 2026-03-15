#!/usr/bin/env bash
# context_assembly.sh — Demonstrates the 6-step context assembly workflow.
# This is a reference implementation showing how a context assembly session
# would gather context from the Hive CLI.
#
# Usage: bash systems/hive/context_assembly.sh <workflow-id-or-topic> [objective]
#
# Example:
#   bash systems/hive/context_assembly.sh voice-scoring-ui "Build the scoring component"
#   bash systems/hive/context_assembly.sh "observatory analytics" "Add usage dashboard"
set -euo pipefail

HIVE="$(dirname "$0")/../../scripts/secrets-proxy/hive"
WORKFLOW_OR_TOPIC="${1:?Usage: context_assembly.sh <workflow-id-or-topic> [objective]}"
OBJECTIVE="${2:-$WORKFLOW_OR_TOPIC}"

echo "=== Context Assembly ==="
echo "Topic: $WORKFLOW_OR_TOPIC"
echo "Objective: $OBJECTIVE"
echo ""

# Step 1: Find the workflow (deterministic lookup)
echo "--- Step 1: Workflow Lookup ---"
WORKFLOW=$($HIVE get "$WORKFLOW_OR_TOPIC" --format json 2>/dev/null || echo "null")
if [ "$WORKFLOW" != "null" ] && echo "$WORKFLOW" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('type') == 'workflow'" 2>/dev/null; then
    echo "Found workflow: $WORKFLOW_OR_TOPIC"
    echo "$WORKFLOW" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  Objective: {d.get(\"objective\",\"N/A\")}')
print(f'  Status: {d.get(\"status\",\"N/A\")}')
print(f'  Current context: {(d.get(\"current_context\",\"N/A\") or \"N/A\")[:100]}')
print(f'  Sessions: {len(d.get(\"sessions\",[]))}')
"
else
    echo "No workflow found for '$WORKFLOW_OR_TOPIC' — will search by topic"
fi
echo ""

# Step 2: Traverse connected records
echo "--- Step 2: Connected Records ---"
REFS=$($HIVE refs "$WORKFLOW_OR_TOPIC" --depth 2 --format json 2>/dev/null || echo '{"out":[],"in":[]}')
echo "$REFS" | python3 -c "
import sys,json; d=json.load(sys.stdin)
out = d.get('out',[])
inn = d.get('in',[])
print(f'  Outbound: {len(out)} records')
for r in out[:5]:
    print(f'    [{r.get(\"type\",\"?\")}] {r[\"record_id\"]}')
print(f'  Inbound: {len(inn)} records')
for r in inn[:5]:
    print(f'    [{r.get(\"type\",\"?\")}] {r[\"record_id\"]}')
"
echo ""

# Step 3: Semantic search for decisions and designs
echo "--- Step 3: Decisions & Designs ---"
DECISIONS=$($HIVE search "$OBJECTIVE" --tags decision --recent 60d --limit 5 --format json 2>/dev/null || echo "[]")
echo "$DECISIONS" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  Found {len(d)} decisions')
for r in d[:3]:
    print(f'    {r[\"record_id\"]}: {r.get(\"title\",\"?\")[:80]}')
"

DESIGNS=$($HIVE search "$OBJECTIVE" --tags design --recent 60d --limit 5 --format json 2>/dev/null || echo "[]")
echo "$DESIGNS" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  Found {len(d)} designs')
for r in d[:3]:
    print(f'    {r[\"record_id\"]}: {r.get(\"title\",\"?\")[:80]}')
"
echo ""

# Step 4: Recent activity
echo "--- Step 4: Recent Activity (7 days) ---"
RECENT=$($HIVE recent 7d --limit 10 --format json 2>/dev/null || echo "[]")
echo "$RECENT" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  {len(d)} recent records')
for r in d[:5]:
    t = r.get('type','?')
    label = r.get('title') or r.get('name') or r['record_id']
    print(f'    [{t}] {label[:60]}')
"
echo ""

# Step 5: Session summaries
echo "--- Step 5: Session Summaries ---"
SUMMARIES=$($HIVE search "$OBJECTIVE" --tags session_summary --recent 30d --limit 5 --format json 2>/dev/null || echo "[]")
echo "$SUMMARIES" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  Found {len(d)} session summaries')
for r in d:
    print(f'    {r[\"record_id\"]}: {r.get(\"title\",\"?\")[:80]}')
"
echo ""

# Step 6: System status
echo "--- Step 6: Hive Status ---"
$HIVE status --format json 2>/dev/null | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  Total records: {d[\"total_records\"]}')
for t, c in sorted(d.get('by_type',{}).items()):
    print(f'    {t}: {c}')
"
echo ""

echo "=== Assembly Complete ==="
echo "In a real context assembly session, this data would be synthesized into"
echo "a comprehensive context note and saved via:"
echo "  hive create note 'Context: $OBJECTIVE' --tags context_assembly --domains indemn"
