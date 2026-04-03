"""Unisoft REST Proxy client."""
import requests
from typing import Any, Optional


class UnisoftClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def call(self, operation: str, params: Optional[dict] = None) -> dict:
        """Call any Unisoft SOAP operation via the proxy."""
        resp = requests.post(
            f"{self.base_url}/api/soap/{operation}",
            json=params or {},
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            timeout=self.timeout,
        )
        data = resp.json()
        if resp.status_code >= 400:
            raise UnisoftError(resp.status_code, data)
        return data

    def health(self) -> dict:
        resp = requests.get(f"{self.base_url}/api/health", timeout=10)
        return resp.json()

    # Convenience methods for common operations
    def get_lobs(self) -> list:
        return self.call("GetInsuranceLOBs").get("InsuranceLOBs", [])

    def get_sub_lobs(self, lob: str) -> list:
        return self.call("GetInsuranceSubLOBs", {"LOB": lob}).get("InsuranceSubLOBs", [])

    def get_carriers(self) -> list:
        return self.call("GetCarriersForLookup").get("CarriersForLookup", [])

    def get_agents(self) -> list:
        return self.call("GetAgentsAndProspectsForLookup").get("AgentsMinimal", [])

    def create_quote(self, quote_data: dict, action: str = "Insert") -> dict:
        return self.call("SetQuote", {"Action": action, "IsNewSystem": True, "Quote": quote_data})

    def create_submission(self, submission_data: dict, action: str = "Insert") -> dict:
        return self.call("SetSubmission", {"PersistSubmission": action, "Submission": submission_data})

    def create_activity(self, activity_data: dict, action: str = "Insert") -> dict:
        return self.call("SetActivity", {"Action": action, "Activity": activity_data})

    def get_quote(self, quote_id: int) -> dict:
        return self.call("GetQuote", {"QuoteID": quote_id})

    def get_submissions(self, quote_id: int) -> dict:
        return self.call("GetSubmissions", {"QuoteID": quote_id})

    # File service methods
    def get_quote_attachments(self, quote_number: int, mga_number: int = 1) -> list:
        """Get attachments for a quote."""
        resp = requests.get(
            f"{self.base_url}/api/file/attachments",
            params={"quoteNumber": quote_number, "mgaNumber": mga_number},
            headers={"X-Api-Key": self.api_key},
            timeout=self.timeout,
        )
        data = resp.json()
        if resp.status_code >= 400:
            raise UnisoftError(resp.status_code, data)
        return data.get("QuoteAttachments", [])

    def upload_quote_attachment(
        self,
        quote_number: int,
        file_content: bytes,
        file_name: str,
        file_type: str | None = None,
        description: str | None = None,
        created_by: str = "automation",
        mga_number: int = 1,
    ) -> dict:
        """Upload a file attachment to a quote."""
        import base64
        if file_type is None:
            ext = file_name.rsplit(".", 1)[-1].upper() if "." in file_name else "PDF"
            file_type = ext
        resp = requests.post(
            f"{self.base_url}/api/file/upload",
            json={
                "quoteNumber": quote_number,
                "mgaNumber": mga_number,
                "fileContent": base64.b64encode(file_content).decode("ascii"),
                "fileName": file_name,
                "fileType": file_type,
                "createdBy": created_by,
                "description": description or file_name,
            },
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            timeout=120,
        )
        data = resp.json()
        if resp.status_code >= 400:
            raise UnisoftError(resp.status_code, data)
        return data


class UnisoftError(Exception):
    def __init__(self, status_code: int, data: dict):
        self.status_code = status_code
        self.data = data
        super().__init__(f"Unisoft API error {status_code}: {data}")
