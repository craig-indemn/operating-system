"""Integration tests for the Unisoft REST proxy."""
import os
import sys
from unisoft_client import UnisoftClient, UnisoftError

PROXY_URL = os.environ.get("UNISOFT_PROXY_URL", "http://localhost:5000")
API_KEY = os.environ.get("UNISOFT_PROXY_KEY", "dev-key")

passed = 0
failed = 0


def test(name, fn):
    global passed, failed
    try:
        fn()
        print("  PASS: " + name)
        passed += 1
    except Exception as e:
        print("  FAIL: " + name + " -- " + str(e))
        failed += 1


def test_health():
    h = client.health()
    if h["status"] != "ok":
        raise Exception("Expected status 'ok', got " + h["status"])


def test_lobs():
    lobs = client.get_lobs()
    if len(lobs) != 18:
        raise Exception("Expected 18 LOBs, got " + str(len(lobs)))


def test_sub_lobs():
    subs = client.get_sub_lobs("CG")
    if len(subs) != 4:
        raise Exception("Expected 4 sub-LOBs, got " + str(len(subs)))


def test_carriers():
    carriers = client.get_carriers()
    if len(carriers) != 46:
        raise Exception("Expected 46 carriers, got " + str(len(carriers)))


def test_agents():
    agents = client.get_agents()
    if len(agents) < 3000:
        raise Exception("Expected 3000+ agents, got " + str(len(agents)))


def test_quote_actions():
    result = client.call("GetQuoteActions")
    if "_meta" not in result:
        raise Exception("Missing _meta in response")
    if result["_meta"]["ReplyStatus"] != "Success":
        raise Exception("ReplyStatus is not Success")


def test_auth_failure():
    bad_client = UnisoftClient(PROXY_URL, "wrong-key")
    try:
        bad_client.call("GetInsuranceLOBs")
        raise Exception("Expected UnisoftError for bad API key")
    except UnisoftError as e:
        if e.status_code != 401:
            raise Exception("Expected 401, got " + str(e.status_code))


if __name__ == "__main__":
    client = UnisoftClient(PROXY_URL, API_KEY)
    print("=== Unisoft Proxy Integration Tests ===")
    print("URL: " + PROXY_URL + "\n")

    test("Health check", test_health)
    test("GetInsuranceLOBs returns 18", test_lobs)
    test("GetInsuranceSubLOBs CG returns 4", test_sub_lobs)
    test("GetCarriersForLookup returns 46", test_carriers)
    test("GetAgentsAndProspectsForLookup returns 3000+", test_agents)
    test("GetQuoteActions returns actions", test_quote_actions)
    test("Invalid API key returns 401", test_auth_failure)

    print("\n=== Results: " + str(passed) + " passed, " + str(failed) + " failed ===")
    sys.exit(0 if failed == 0 else 1)
