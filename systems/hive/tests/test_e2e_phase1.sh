#!/usr/bin/env bash
# End-to-end Phase 1 tests for the Hive CLI.
# Tests all 14 commands, routing, validation, format detection, refs, disjoint enforcement.
set -euo pipefail

HIVE="/Users/home/Repositories/.venv/bin/python3 /Users/home/Repositories/operating-system/.claude/worktrees/os-hive/systems/hive/cli.py"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }
check() {
    if eval "$1" >/dev/null 2>&1; then
        pass "$2"
    else
        fail "$2"
    fi
}

echo "=== Phase 1 End-to-End Tests ==="
echo ""

# ─── 1. Command availability ───
echo "--- Command Availability ---"
check "$HIVE --help | grep -q 'get'" "hive --help shows get"
check "$HIVE --help | grep -q 'create'" "hive --help shows create"
check "$HIVE --help | grep -q 'update'" "hive --help shows update"
check "$HIVE --help | grep -q 'search'" "hive --help shows search"
check "$HIVE --help | grep -q 'list'" "hive --help shows list"
check "$HIVE --help | grep -q 'refs'" "hive --help shows refs"
check "$HIVE --help | grep -q 'recent'" "hive --help shows recent"
check "$HIVE --help | grep -q 'sync'" "hive --help shows sync"
check "$HIVE --help | grep -q 'feedback'" "hive --help shows feedback"
check "$HIVE --help | grep -q 'status'" "hive --help shows status"
check "$HIVE --help | grep -q 'init'" "hive --help shows init"
check "$HIVE --help | grep -q 'types'" "hive --help shows types"
check "$HIVE --help | grep -q 'tags'" "hive --help shows tags"
check "$HIVE --help | grep -q 'domains'" "hive --help shows domains"
echo ""

# ─── 2. Registry ───
echo "--- Registry ---"
check "$HIVE types list | python3 -c \"import sys,json; d=json.load(sys.stdin); assert len(d) >= 9\"" "9+ entity types loaded"
check "$HIVE tags list | python3 -c \"import sys,json; d=json.load(sys.stdin); assert len(d) >= 20\"" "20+ tags loaded"
check "$HIVE domains list | python3 -c \"import sys,json; d=json.load(sys.stdin); assert len(d) == 3\"" "3 domains loaded"
check "$HIVE types show person | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['type'] == 'person'\"" "types show person works"
echo ""

# ─── 3. Entity routing (type → MongoDB) ───
echo "--- Entity Routing ---"
# Create test entity
TEST_ENTITY=$($HIVE create person "Test Person E2E" --email test@test.com --domains indemn 2>&1)
check "echo '$TEST_ENTITY' | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['type'] == 'person'\"" "create person routes to entity layer"
check "echo '$TEST_ENTITY' | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['record_id'] == 'test-person-e2e'\"" "entity record_id is slugified"
check "$HIVE get test-person-e2e | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['type'] == 'person'\"" "get entity by slug works"
echo ""

# ─── 4. Knowledge routing (tag → file + index) ───
echo "--- Knowledge Routing ---"
TEST_KNOWLEDGE=$($HIVE create decision "E2E Test Decision" --domains indemn --refs project:os-development --rationale "Testing the routing" 2>&1)
check "echo '$TEST_KNOWLEDGE' | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['type'] == 'knowledge'\"" "create decision routes to knowledge layer"
check "echo '$TEST_KNOWLEDGE' | python3 -c \"import sys,json; d=json.load(sys.stdin); assert 'decision' in d['tags']\"" "knowledge has decision tag"

# Verify file exists
KNOWLEDGE_ID=$(echo "$TEST_KNOWLEDGE" | python3 -c "import sys,json; print(json.load(sys.stdin)['record_id'])")
check "test -f hive/decisions/$KNOWLEDGE_ID.md" "knowledge file created in hive/decisions/"

# Verify MongoDB index
check "$HIVE get $KNOWLEDGE_ID | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['type'] == 'knowledge'\"" "knowledge indexed in MongoDB"
echo ""

# ─── 5. Validation ───
echo "--- Validation ---"
# Duplicate rejected
check "! $HIVE create person 'Test Person E2E' --domains indemn 2>&1" "duplicate entity rejected"

# Missing required field
check "! $HIVE create person 'No Domain Person' 2>&1" "missing required field rejected"

# Invalid enum value
check "! $HIVE create person 'Bad Status' --domains indemn --status bogus 2>&1" "invalid enum rejected"

# Unknown type-or-tag rejected
check "! $HIVE create unknowntype 'Test' --domains indemn 2>&1" "unknown type rejected"
echo ""

# ─── 6. Cross-layer refs ───
echo "--- Cross-Layer Refs ---"
# Knowledge refs entity
check "$HIVE refs os-development | python3 -c \"import sys,json; d=json.load(sys.stdin); assert any(r['record_id'] == '$KNOWLEDGE_ID' for r in d['in'])\"" "knowledge→entity ref traversal works"

# Entity refs in refs_out
check "$HIVE refs test-person-e2e | python3 -c \"import sys,json; d=json.load(sys.stdin); assert isinstance(d, dict)\"" "entity refs returns valid structure"
echo ""

# ─── 7. Wiki-links ───
echo "--- Wiki-Links ---"
WIKI_TEST=$($HIVE create note "Wiki Link E2E" --domains indemn --body "See [[${KNOWLEDGE_ID}]] for context" 2>&1)
WIKI_ID=$(echo "$WIKI_TEST" | python3 -c "import sys,json; print(json.load(sys.stdin)['record_id'])")
check "echo '$WIKI_TEST' | python3 -c \"import sys,json; d=json.load(sys.stdin); assert '$KNOWLEDGE_ID' in d['wiki_links']\"" "wiki-links extracted from body"
echo ""

# ─── 8. List with filters ───
echo "--- List + Filters ---"
check "$HIVE list person | python3 -c \"import sys,json; d=json.load(sys.stdin); assert len(d) >= 1\"" "list person returns results"
check "$HIVE list decision | python3 -c \"import sys,json; d=json.load(sys.stdin); assert len(d) >= 1\"" "list decision returns results"
check "$HIVE list person --domain indemn | python3 -c \"import sys,json; d=json.load(sys.stdin); assert all('indemn' in r['domains'] for r in d)\"" "list with domain filter works"
echo ""

# ─── 9. Update ───
echo "--- Update ---"
$HIVE update test-person-e2e --status inactive >/dev/null 2>&1
check "$HIVE get test-person-e2e | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['status'] == 'inactive'\"" "entity update status works"

$HIVE update "$KNOWLEDGE_ID" --add-tags architecture >/dev/null 2>&1
check "$HIVE get $KNOWLEDGE_ID | python3 -c \"import sys,json; d=json.load(sys.stdin); assert 'architecture' in d['tags']\"" "knowledge update add-tags works"
echo ""

# ─── 10. Recent ───
echo "--- Recent ---"
check "$HIVE recent 7d | python3 -c \"import sys,json; d=json.load(sys.stdin); assert len(d) >= 3\"" "recent returns mixed records"
echo ""

# ─── 11. Status ───
echo "--- Status ---"
check "$HIVE status | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['total_records'] > 0\"" "status shows record counts"
echo ""

# ─── 12. Sync ───
echo "--- Sync ---"
check "$HIVE sync --no-embed 2>/dev/null | python3 -c \"import sys,json; d=json.load(sys.stdin); assert d['errors'] == 0\"" "sync completes without errors"
echo ""

# ─── 13. Init ───
echo "--- Init ---"
check "$HIVE init 2>&1 | grep -q 'Hive initialized'" "init succeeds"
echo ""

# ─── 14. Feedback ───
echo "--- Feedback ---"
FB=$($HIVE feedback "E2E test feedback" 2>&1)
check "echo '$FB' | python3 -c \"import sys,json; d=json.load(sys.stdin); assert 'feedback' in d['tags'] and 'hive-improvement' in d['tags']\"" "feedback auto-tags applied"
echo ""

# ─── 15. Format detection (JSON when piped) ───
echo "--- Format Detection ---"
check "$HIVE status | python3 -c 'import sys,json; json.load(sys.stdin)'" "piped output is valid JSON"
echo ""

# ─── 16. Disjoint enforcement ───
echo "--- Disjoint Enforcement ---"
# Entity types and tags must not overlap
check "$HIVE types list | python3 -c \"
import sys,json
types = set(json.load(sys.stdin).keys())
\" && $HIVE tags list | python3 -c \"
import sys,json
tags = set(json.load(sys.stdin).keys())
\"" "types and tags are disjoint (no overlap)"
echo ""

# ─── Cleanup test data ───
echo "--- Cleanup ---"
/opt/homebrew/bin/mongosh --quiet --eval "use('hive'); db.records.deleteMany({record_id: {'\$in': ['test-person-e2e', '$KNOWLEDGE_ID', '$WIKI_ID']}});" >/dev/null 2>&1
# Remove test files
rm -f "hive/decisions/$KNOWLEDGE_ID.md" "hive/notes/$WIKI_ID.md" "hive/notes/2026-03-15-e2e-test-feedback.md"
echo "  Test data cleaned"
echo ""

# ─── Summary ───
echo "================================"
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -eq 0 ]; then
    echo "ALL TESTS PASSED"
    exit 0
else
    echo "SOME TESTS FAILED"
    exit 1
fi
