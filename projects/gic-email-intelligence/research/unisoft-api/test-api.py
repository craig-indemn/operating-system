#!/usr/bin/env python3
"""Test Unisoft API connectivity — REST and SOAP."""

import json
import requests
import sys
from datetime import datetime

# UAT endpoints
REST_BASE = "https://ins-gic-api-gateway-uat-app.azurewebsites.net"
SOAP_BASE = "https://services.uat.gicunderwriters.co/management/imsservice.svc"

# Credentials
REST_USER = "ccerto"
REST_PASS = "GIC2026$$!"
SOAP_WS_USER = "UniClient"
SOAP_WS_PASS = "J5j!}7=r/z"
SOAP_CLIENT_ID = "GIC_UAT"


def test_rest_auth():
    """Test REST API authentication — returns JWT token."""
    print("\n" + "=" * 60)
    print("TEST 1: REST API Authentication")
    print("=" * 60)

    url = f"{REST_BASE}/api/authentication/login"
    payload = {
        "UserName": REST_USER,
        "Password": REST_PASS,
        "UseTwoFactorAuth": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"Auth successful: {data.get('isAuthSuccessful')}")
            token = data.get("accessToken", "")
            print(f"Token (first 50 chars): {token[:50]}...")
            print(f"Refresh token present: {bool(data.get('refreshToken'))}")
            return token
        else:
            print(f"FAILED: {resp.text[:500]}")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def test_rest_get_user(token):
    """Test REST API — get user profile."""
    print("\n" + "=" * 60)
    print("TEST 2: REST API — Get User Profile")
    print("=" * 60)

    url = f"{REST_BASE}/api/users/{REST_USER}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"User: {data.get('firstName')} {data.get('lastName')}")
            print(f"Email: {data.get('email')}")
            print(f"Roles: {data.get('roles')}")
            return True
        else:
            print(f"FAILED: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_rest_get_brokers(token):
    """Test REST API — get brokers list."""
    print("\n" + "=" * 60)
    print("TEST 3: REST API — Get Brokers")
    print("=" * 60)

    url = f"{REST_BASE}/api/1.0/brokers?forLookup=true"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"Brokers found: {len(data)}")
            for b in data[:5]:
                print(f"  - {b.get('name', b.get('brokerId'))}")
            return True
        else:
            print(f"FAILED: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_rest_task_dashboard(token):
    """Test REST API — get task dashboard."""
    print("\n" + "=" * 60)
    print("TEST 4: REST API — Task Dashboard")
    print("=" * 60)

    url = (
        f"{REST_BASE}/api/tasks/dashboard"
        f"?userName={REST_USER}&groupId=0&sectionId=0&actionId=0"
        f"&statusId=0&isPrivate=False&userGroupFilteringOption=ALL"
        f"&dueDateFilteringOption=Pending"
    )
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"Due today: {data.get('dueTodayTasksCount')}")
            print(f"Due tomorrow: {data.get('dueTomorrowTasksCount')}")
            print(f"Overdue: {data.get('overdueTasksCount')}")
            print(f"Pending: {data.get('pendingTasksCount')}")
            print(f"Completed: {data.get('completedTasksCount')}")
            return True
        else:
            print(f"FAILED: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


# ---------------------------------------------------------------------------
# SOAP Tests — raw XML with requests (no zeep needed)
# ---------------------------------------------------------------------------

def test_soap_wsdl():
    """Test SOAP — fetch WSDL to confirm service is reachable."""
    print("\n" + "=" * 60)
    print("TEST 5: SOAP Service — WSDL Fetch")
    print("=" * 60)

    url = f"{SOAP_BASE}?singleWsdl"

    try:
        resp = requests.get(url, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type', 'unknown')}")
        print(f"Response size: {len(resp.content)} bytes")

        if resp.status_code == 200 and b"wsdl" in resp.content[:500].lower():
            print("WSDL fetched successfully")
            return True
        else:
            print(f"Unexpected response: {resp.text[:300]}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_soap_rst():
    """
    Test SOAP — RequestSecurityToken to establish a SecurityContextToken.
    This is the WS-Trust RST/RSTR handshake.
    """
    print("\n" + "=" * 60)
    print("TEST 6: SOAP — WS-Trust RequestSecurityToken")
    print("=" * 60)

    # WS-Trust RST with UsernameToken
    # Based on the Fiddler captures, the client sends a WS-Trust RST
    # with UsernameToken credentials to establish an SCT.
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://www.w3.org/2005/08/addressing"
            xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
  <s:Header>
    <a:Action s:mustUnderstand="1">http://docs.oasis-open.org/ws-sx/ws-trust/200512/RST/SCT</a:Action>
    <a:MessageID>urn:uuid:{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-test</a:MessageID>
    <a:ReplyTo>
      <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
    </a:ReplyTo>
    <a:To s:mustUnderstand="1">{SOAP_BASE}</a:To>
    <o:Security s:mustUnderstand="1"
                xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
      <u:Timestamp u:Id="_0">
        <u:Created>{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')}</u:Created>
        <u:Expires>{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z').replace(str(datetime.utcnow().minute), str((datetime.utcnow().minute + 5) % 60))}</u:Expires>
      </u:Timestamp>
      <o:UsernameToken u:Id="uuid-usertoken-1">
        <o:Username>{SOAP_WS_USER}</o:Username>
        <o:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{SOAP_WS_PASS}</o:Password>
      </o:UsernameToken>
    </o:Security>
  </s:Header>
  <s:Body>
    <t:RequestSecurityToken xmlns:t="http://docs.oasis-open.org/ws-sx/ws-trust/200512">
      <t:TokenType>http://docs.oasis-open.org/ws-sx/ws-secureconversation/200512/sct</t:TokenType>
      <t:RequestType>http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue</t:RequestType>
      <t:Entropy>
        <t:BinarySecret Type="http://docs.oasis-open.org/ws-sx/ws-trust/200512/Nonce" u:Id="uuid-entropy-1">AAAAAAAAAAAAAAAAAAAAAA==</t:BinarySecret>
      </t:Entropy>
      <t:KeySize>256</t:KeySize>
    </t:RequestSecurityToken>
  </s:Body>
</s:Envelope>"""

    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
    }

    try:
        resp = requests.post(SOAP_BASE, data=envelope.encode("utf-8"), headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type', 'unknown')}")

        body = resp.text
        if resp.status_code == 200:
            # Look for SecurityContextToken in response
            if "SecurityContextToken" in body:
                print("SUCCESS — SecurityContextToken received!")
                # Extract the SCT identifier
                import re
                sct_match = re.search(r'<Identifier>(.*?)</Identifier>', body)
                if sct_match:
                    print(f"SCT Identifier: {sct_match.group(1)}")
            elif "RequestSecurityTokenResponse" in body:
                print("Got RSTR response (need to parse)")
            else:
                print(f"Unexpected 200 response: {body[:500]}")
            return body
        else:
            # Check for fault
            if "Fault" in body:
                import re
                reason = re.search(r'<s:Text[^>]*>(.*?)</s:Text>', body)
                subcode = re.search(r'<s:Subcode>.*?<s:Value>(.*?)</s:Value>', body, re.DOTALL)
                print(f"SOAP Fault: {reason.group(1) if reason else 'unknown'}")
                if subcode:
                    print(f"Subcode: {subcode.group(1)}")
            print(f"Response (first 800 chars): {body[:800]}")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def test_soap_simple_call():
    """
    Test SOAP — try a simple operation without full WS-Security.
    Some WCF services allow BasicHttpBinding or have a mex endpoint.
    """
    print("\n" + "=" * 60)
    print("TEST 7: SOAP — Direct Call (GetInsuranceLOBs, no security)")
    print("=" * 60)

    # Try a basic SOAP 1.2 call without WS-Security
    # (unlikely to work but worth testing to see the error)
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">http://tempuri.org/IIMSService/GetInsuranceLOBs</a:Action>
    <a:To s:mustUnderstand="1">{SOAP_BASE}</a:To>
  </s:Header>
  <s:Body>
    <GetInsuranceLOBs xmlns="http://tempuri.org/" />
  </s:Body>
</s:Envelope>"""

    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
    }

    try:
        resp = requests.post(SOAP_BASE, data=envelope.encode("utf-8"), headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")

        body = resp.text
        if "InsuranceLOB" in body:
            print("SUCCESS — Got LOB data (no security needed!)")
            # Parse LOBs
            import re
            lobs = re.findall(r'<[^:]*LOB>([^<]+)</[^:]*LOB>.*?<[^:]*Description>([^<]+)</[^:]*Description>', body, re.DOTALL)
            for code, desc in lobs[:10]:
                print(f"  {code}: {desc}")
        elif "Fault" in body:
            import re
            reason = re.search(r'<s:Text[^>]*>(.*?)</s:Text>', body)
            print(f"SOAP Fault (expected): {reason.group(1) if reason else body[:500]}")
        else:
            print(f"Response: {body[:500]}")
        return body
    except Exception as e:
        print(f"ERROR: {e}")
        return None


if __name__ == "__main__":
    print(f"Unisoft API Test — {datetime.now().isoformat()}")
    print(f"REST base: {REST_BASE}")
    print(f"SOAP base: {SOAP_BASE}")

    results = {}

    # REST tests
    token = test_rest_auth()
    results["rest_auth"] = bool(token)

    if token:
        results["rest_user"] = test_rest_get_user(token)
        results["rest_brokers"] = test_rest_get_brokers(token)
        results["rest_tasks"] = test_rest_task_dashboard(token)

    # SOAP tests
    results["soap_wsdl"] = test_soap_wsdl()
    rst_response = test_soap_rst()
    results["soap_rst"] = bool(rst_response) and "SecurityContextToken" in str(rst_response)
    test_soap_simple_call()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test:20s} {status}")
