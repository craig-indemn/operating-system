---
ask: "How do external systems connect to the OS — integrations, adapters, and channel architecture?"
created: 2026-04-02
workstream: product-vision
session: 2026-03-30-a
sources:
  - type: conversation
    description: "Craig and Claude design session, 2026-03-30 to 2026-04-02"
---

# Design: Layer 4 — Integrations & Channels

## Core Principle: Entity Operations Own External Connectivity

There is no separate "integration layer" organized by external system type. Every entity defines its own operations. Some operations involve external systems. When they do, the adapter layer handles the connection.

The Integration entity + adapter pattern is the bridge between "what the entity needs to do" and "how the external system actually works." The entity doesn't know or care which method is used (API, web operator, email, file).

## How It Works

### Entity defines the operation:

```python
class Submission(Entity):
    @exposed
    async def submit_to_carrier(self):
        """Submit to the carrier via whatever method is configured."""
        adapter = await get_adapter(self.carrier, operation="submit")
        result = await adapter.submit(self.to_submission_payload())
        self.external_reference = result["reference_id"]
        self.transition_to("submitted")
        await self.save()
        return result

class Policy(Entity):
    @exposed
    async def sync_to_ams(self):
        """Push policy data to the customer's AMS."""
        adapter = await get_adapter(self.org, system_type="ams")
        await adapter.push_policy(self.to_ams_payload())

class Carrier(Entity):
    @exposed
    async def refresh_appetite(self):
        """Pull latest appetite data from the carrier."""
        adapter = await get_adapter(self, operation="appetite")
        appetite_data = await adapter.get_appetite()
        self.appetite = appetite_data
        await self.save()

class Certificate(Entity):
    @exposed
    async def deliver(self, channel: str, to: str):
        """Generate and deliver certificate via configured channel."""
        document = await self.generate_pdf()
        adapter = await get_adapter(self.org, channel_type=channel)
        await adapter.send(to=to, attachments=[document])

class Contact(Entity):
    @exposed
    async def enrich(self):
        """Enrich contact data from external sources."""
        adapter = await get_adapter(self.org, system_type="enrichment")
        data = await adapter.lookup(self.email or self.name)
        self.update_from_enrichment(data)
        await self.save()

class Email(Entity):
    @exposed
    async def fetch_new(self):
        """Poll for new emails from configured provider."""
        adapter = await get_adapter(self.org, channel_type="email")
        new_emails = await adapter.receive()
        for email_data in new_emails:
            email = Email(**email_data, org_id=self.org_id)
            await email.insert()
            await email.emit("email.received")

class Payment(Entity):
    @exposed
    async def charge(self):
        """Process payment through configured payment provider."""
        adapter = await get_adapter(self.org, system_type="payment")
        result = await adapter.charge(
            amount=self.amount,
            customer_ref=self.insured.external_payment_id,
            description=f"Policy {self.policy.policy_number}"
        )
        self.external_reference = result["transaction_id"]
        self.transition_to("completed")
        await self.save()
```

### The CLI exposes these naturally:

```bash
# Entity operations that happen to involve external systems
indemn submission submit-to-carrier SUB-001
indemn policy sync-to-ams POL-001
indemn carrier refresh-appetite CARR-001
indemn certificate deliver CERT-001 --channel email --to "agent@agency.com"
indemn contact enrich CONT-001
indemn email fetch-new --integration INT-001
indemn payment charge PAY-001
```

Associates call these same CLI commands. They don't know or care what's underneath — API, web operator, email, file transfer. The adapter handles it.

## The Integration Entity

An Integration entity configures the connection between the OS and an external system:

```python
class Integration(Entity):
    sub_domain = "platform"

    name: str                    # "GIC Outlook Email", "USLI Carrier API"
    system_type: str             # "email", "voice", "sms", "ams", "carrier", "payment", "enrichment", etc.
    provider: str                # "outlook", "gmail", "twilio", "applied-epic", "usli", "stripe"
    config: dict                 # Provider-specific config (credentials, endpoints, settings)
    status: Literal["configured", "connected", "active", "error"] = "configured"

    # Optional: associate for web operator-based integrations
    web_operator_id: Optional[str] = None

    state_machine = {
        "configured": ["connected"],
        "connected": ["active", "error"],
        "active": ["error", "configured"],
        "error": ["configured"],
    }

    class Settings:
        name = "integrations"
```

```bash
# Set up email integration for a customer
indemn integration create --name "GIC Outlook" --system-type email --provider outlook
indemn integration configure INT-001 --config @outlook-config.json
indemn integration connect INT-001
indemn integration test INT-001

# Set up carrier integration — API-based
indemn integration create --name "USLI API" --system-type carrier --provider usli
indemn integration configure INT-002 --config @usli-api.json
indemn integration connect INT-002

# Set up carrier integration — web operator-based
indemn integration create --name "Hartford Portal" --system-type carrier --provider hartford
indemn associate create --name "Hartford Web Operator" --type web-operator
indemn associate add-skill ASSOC-002 --skill hartford-portal-navigation
indemn integration configure INT-003 --web-operator ASSOC-002
indemn integration connect INT-003

# Set up AMS integration
indemn integration create --name "GIC Applied Epic" --system-type ams --provider applied-epic
indemn integration configure INT-004 --config @applied-epic.json

# Set up payment
indemn integration create --name "EventGuard Stripe" --system-type payment --provider stripe
indemn integration configure INT-005 --config @stripe.json
```

## The Adapter Pattern

### Adapter Interface (per system type):

Each system type has an abstract adapter that defines what operations are available. Providers implement the adapter.

```python
class CarrierAdapter(ABC):
    """Operations for carrier connectivity. Implemented per carrier."""

    @abstractmethod
    async def submit(self, payload: dict) -> dict: ...

    @abstractmethod
    async def check_status(self, reference_id: str) -> dict: ...

    @abstractmethod
    async def get_quote(self, reference_id: str) -> dict: ...

    @abstractmethod
    async def get_appetite(self) -> dict: ...

    @abstractmethod
    async def download_documents(self, reference_id: str) -> list: ...
```

### Provider implementations:

```python
class USLIAdapter(CarrierAdapter):
    """USLI — full API available."""

    def __init__(self, config):
        self.client = USLIAPIClient(api_key=config["api_key"])

    async def submit(self, payload):
        response = await self.client.post("/submissions", payload)
        return {"reference_id": response["id"], "status": response["status"]}

    async def get_quote(self, reference_id):
        return await self.client.get(f"/quotes?submission={reference_id}")

class HartfordAdapter(CarrierAdapter):
    """Hartford — hybrid: web operator for submission, API for quotes."""

    def __init__(self, config):
        self.api = HartfordAPIClient(config.get("api_key"))
        self.web_operator_id = config["web_operator_associate_id"]

    async def submit(self, payload):
        # No submission API — web operator navigates portal
        return await invoke_associate(
            self.web_operator_id,
            objective=f"Submit to Hartford portal: {payload['submission_id']}"
        )

    async def get_quote(self, reference_id):
        # Hartford HAS a quote API
        return await self.api.get(f"/quotes/{reference_id}")
```

### The mapping function:

Every adapter translates between external system format and OS entity format:

```python
class OutlookEmailAdapter(EmailAdapter):

    def _map_to_os(self, outlook_msg: dict) -> dict:
        """Translate Outlook message to OS Email entity fields."""
        return {
            "external_id": outlook_msg["id"],
            "from_address": outlook_msg["from"]["emailAddress"]["address"],
            "to_addresses": [r["emailAddress"]["address"] for r in outlook_msg["toRecipients"]],
            "subject": outlook_msg["subject"],
            "body": outlook_msg["body"]["content"],
            "received_at": outlook_msg["receivedDateTime"],
            "thread_id": outlook_msg["conversationId"],
            "has_attachments": outlook_msg["hasAttachments"],
        }

    def _map_from_os(self, email_data: dict) -> dict:
        """Translate OS email fields to Outlook send format."""
        return {
            "message": {
                "toRecipients": [{"emailAddress": {"address": to}} for to in email_data["to_addresses"]],
                "subject": email_data["subject"],
                "body": {"contentType": "HTML", "content": email_data["body"]},
            }
        }
```

These mapping functions are the code that MUST be written per provider. No way around it — external systems have different data formats. Written once per provider, used by every customer on that provider.

## Adapter Resolution

When an entity operation needs an external system, `get_adapter()` resolves the right adapter:

```python
async def get_adapter(entity_or_org, system_type=None, channel_type=None, operation=None):
    """Find the right adapter for an entity's external operation."""

    # Determine the org
    org_id = entity_or_org.org_id if hasattr(entity_or_org, 'org_id') else entity_or_org.id

    # Find the matching integration
    query = {"org_id": org_id, "status": "active"}
    if system_type:
        query["system_type"] = system_type
    if channel_type:
        query["system_type"] = channel_type

    integration = await Integration.find_one(query)
    if not integration:
        raise IntegrationNotFound(f"No active {system_type or channel_type} integration for org {org_id}")

    # Load the adapter for this provider
    adapter_cls = ADAPTER_REGISTRY[integration.provider]
    return adapter_cls(integration.config)
```

The adapter registry maps provider names to adapter classes:

```python
ADAPTER_REGISTRY = {
    "outlook": OutlookEmailAdapter,
    "gmail": GmailEmailAdapter,
    "twilio-voice": TwilioVoiceAdapter,
    "twilio-sms": TwilioSMSAdapter,
    "stripe": StripePaymentAdapter,
    "applied-epic": AppliedEpicAMSAdapter,
    "usli": USLICarrierAdapter,
    "hartford": HartfordCarrierAdapter,
    # ... grows with every new provider integration
}
```

New providers = new adapter class + register in the registry. Everything else (entities, CLI, associates) works automatically.

## Hybrid Integrations (API + Web Operator)

Some external systems have partial API coverage — API for some operations, web portal for others. The adapter handles this internally:

```python
class HartfordAdapter(CarrierAdapter):
    """Some operations via API, others via web operator."""

    async def submit(self, payload):
        # No submission API — delegate to web operator
        return await invoke_associate(self.web_operator_id,
            objective=f"Submit via Hartford portal")

    async def get_quote(self, reference_id):
        # Quote API exists
        return await self.api.get(f"/quotes/{reference_id}")

    async def check_status(self, reference_id):
        # Status only on portal — delegate to web operator
        return await invoke_associate(self.web_operator_id,
            objective=f"Check status on Hartford portal")
```

The caller (entity operation or associate) doesn't know which method is used. `indemn carrier submit --integration INT-003` works regardless of whether it's an API call or a web operator navigating a portal.

## Communication Channels

Email, voice, SMS, web chat are a specific category of integration — they're how the OS communicates with the outside world. They follow the same adapter pattern but are used differently:

- **Inbound**: channel receives input → creates an entity (Email, Interaction, Message) → emits event → triggers associate
- **Outbound**: associate or entity operation sends through channel → adapter handles delivery

```
Inbound:  External → Channel Adapter → OS Entity → Event → Associate
Outbound: Associate → CLI command → Entity operation → Channel Adapter → External
```

Channel adapters that already exist in the current system:
- middleware-socket-service → web chat channel
- voice-service / voice-livekit → voice channel
- GIC Email Intelligence → Outlook email channel (partial — needs to become a full adapter)
- Stripe → payment (EventGuard)

These existing implementations get wrapped as adapters. No rebuild — just a standard interface on top of what works.

## What Gets Built Per Provider

| Component | Nature | Effort |
|-----------|--------|--------|
| Adapter class | Code — implements operation interface | Per provider, written once |
| Mapping functions | Code — translates data formats | Per provider, written once |
| Provider config schema | Definition — what config fields are needed | Per provider |
| Web operator skills | Skill markdown — for portal automation | Per carrier portal |
| Integration test | Test — verify adapter works | Per provider |

Once built, every customer who uses that provider gets the adapter for free. The integration library grows with each new provider, and the network effect applies — more customers = more providers = more customers.

## What's Configurable vs. What's Code

| Aspect | How | Who |
|--------|-----|-----|
| Which integrations a customer has | CLI / entity config | FDE or customer or associate |
| Integration credentials and settings | CLI / entity config (encrypted) | FDE or customer |
| Adapter implementations | Python code | Indemn engineering |
| Mapping functions | Python code | Indemn engineering |
| Web operator skills | SKILL.md files | Indemn engineering (or AI-generated) |
| New provider support | Adapter code + registration | Indemn engineering |

The customer-facing work is configuration (CLI). The engineering work is writing adapters for new providers. Over time, the adapter library covers the common providers and less engineering is needed.

## Key Layer 4 Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration architecture | Entity operations own external connectivity | No artificial categorization. Every entity defines what it needs. |
| Adapter pattern | Abstract interface per system type, implemented per provider | Clean separation. Written once per provider. |
| Integration entity | CLI-configurable, same patterns as all entities | Tier 3 compatible. Associates can set up integrations. |
| Hybrid integrations | Adapter internally mixes API + web operator | Caller doesn't know the method. One interface. |
| Web operators | Deep agent associates with browser sandbox | Same harness as all associates. |
| Existing infrastructure | Wrap current implementations as adapters | No rebuild. Standard interface on existing code. |
| Adapter resolution | Registry pattern — provider name → adapter class | Simple. New providers = register + implement. |
| Channel inbound flow | Channel → entity → event → associate | Standard event-driven pattern. |
