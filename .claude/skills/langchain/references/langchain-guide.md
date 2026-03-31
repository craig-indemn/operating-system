# LangChain Reference Guide

Comprehensive reference for LangChain patterns used in Indemn services — structured output, multimodal input, agents, and Anthropic integration.

Last updated: 2026-03-30
Source packages: `langchain-anthropic==1.4.0`, `langchain-core`, `langchain`

---

## Table of Contents

- [Package Versions and Requirements](#package-versions-and-requirements)
- [Structured Output: with_structured_output()](#structured-output-with_structured_output)
- [Structured Output: Schema Types](#structured-output-schema-types)
- [Structured Output: Method Parameter](#structured-output-method-parameter)
- [Anthropic Native Structured Output (Constrained Decoding)](#anthropic-native-structured-output-constrained-decoding)
- [JSON Schema Limitations (Anthropic Native)](#json-schema-limitations-anthropic-native)
- [Multimodal: Content Block Format Reference](#multimodal-content-block-format-reference)
- [Multimodal: Image Limits and Costs](#multimodal-image-limits-and-costs)
- [Multimodal: PDF Limits and Behavior](#multimodal-pdf-limits-and-behavior)
- [Multimodal: Files API](#multimodal-files-api)
- [Combining Multimodal + Structured Output](#combining-multimodal--structured-output)
- [Multiple Documents in One Request](#multiple-documents-in-one-request)
- [ReAct Agents](#react-agents)
- [Agents with Structured Output](#agents-with-structured-output)
- [Anthropic SDK Direct (Non-LangChain)](#anthropic-sdk-direct-non-langchain)
- [Performance and Caching](#performance-and-caching)
- [Troubleshooting](#troubleshooting)

---

## Package Versions and Requirements

| Package | Current Version | Key Feature Versions |
|---------|----------------|---------------------|
| `langchain-anthropic` | 1.4.0 | >=1.1.0 for native `json_schema` method |
| `langchain-core` | (matches langchain) | Content block standardization |
| `langchain` | (matches ecosystem) | `create_agent` factory |
| `langgraph` | (latest) | `create_react_agent` |
| `pydantic` | v2.x | Required by langchain-core |

Feature availability by version:
- `langchain-anthropic>=0.3.21` — Context management support
- `langchain-anthropic>=1.0.3` — Anthropic code execution tools
- `langchain-anthropic>=1.1.0` — Native `json_schema` structured output
- `langchain-anthropic>=1.3.5` — Cache creation fields, eager input streaming
- `langchain-anthropic>=1.4.0` — `AnthropicPromptCachingMiddleware`

---

## Structured Output: with_structured_output()

The `with_structured_output()` method on chat models binds a schema to the model so every invocation returns validated structured data.

```python
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    rating: float = Field(description="Rating out of 10")
    summary: str = Field(description="Brief review summary")

model = ChatAnthropic(model="claude-sonnet-4-5")
structured = model.with_structured_output(MovieReview, method="json_schema")

result = structured.invoke("Review the movie Inception")
assert isinstance(result, MovieReview)
print(result.title)   # "Inception"
print(result.rating)  # 8.8
```

### How It Works Internally

1. The Pydantic model is converted to a JSON schema
2. The schema is passed to the provider (Anthropic) as either a tool definition (`method="tool_calling"`) or as `output_config.format` (`method="json_schema"`)
3. The LLM generates output constrained to the schema
4. LangChain parses the response back into the Pydantic model
5. Pydantic validation runs on the parsed output

### Return Types

- **Pydantic BaseModel**: Returns a validated model instance. Recommended.
- **TypedDict**: Returns a plain `dict`. No validation beyond LLM enforcement.
- **JSON Schema dict**: Returns a plain `dict`. Most portable.

---

## Structured Output: Schema Types

### Pydantic BaseModel (recommended)

```python
from pydantic import BaseModel, Field
from typing import Optional

class Contact(BaseModel):
    name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number if available")
    company: str = Field(description="Company name")
    role: str = Field(description="Job title or role")

structured = model.with_structured_output(Contact, method="json_schema")
```

Supports: nested models, lists, optionals, enums, unions (via `anyOf`), default values, field descriptions.

### TypedDict

```python
from typing import TypedDict

class Contact(TypedDict):
    name: str
    email: str
    company: str

structured = model.with_structured_output(Contact, method="json_schema")
# Returns a plain dict: {"name": "...", "email": "...", "company": "..."}
```

### Raw JSON Schema

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Full name"},
        "email": {"type": "string", "description": "Email address"},
        "company": {"type": "string", "description": "Company name"},
    },
    "required": ["name", "email", "company"],
    "additionalProperties": False,
}

structured = model.with_structured_output(schema, method="json_schema")
# Returns a plain dict
```

### Nested Models

```python
from pydantic import BaseModel, Field

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float

class Invoice(BaseModel):
    invoice_number: str
    vendor: str
    vendor_address: Address
    line_items: list[LineItem]
    total: float
    due_date: str

structured = model.with_structured_output(Invoice, method="json_schema")
```

### Enum Fields

```python
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class EmailClassification(BaseModel):
    category: str = Field(description="Email category")
    priority: Priority
    requires_response: bool
    summary: str
```

---

## Structured Output: Method Parameter

### method="json_schema" (Anthropic native, recommended)

Uses Anthropic's constrained decoding. The model literally cannot generate tokens that violate the schema. Guaranteed valid JSON.

```python
structured = model.with_structured_output(MyModel, method="json_schema")
```

**Pros**: Guaranteed schema compliance, no retries needed, works with complex nested schemas.
**Cons**: ~100-300ms first-call latency for grammar compilation, schema constraints apply (see limitations below).

Under the hood, this maps to Anthropic's `output_config.format` parameter:
```python
# What LangChain sends to Anthropic
output_config={
    "format": {
        "type": "json_schema",
        "schema": {... your schema ...}
    }
}
```

### method="tool_calling" (default)

Converts the schema into a tool/function definition and forces the model to "call" that tool. Extracts the tool arguments as your structured data.

```python
structured = model.with_structured_output(MyModel)  # default
# or explicitly:
structured = model.with_structured_output(MyModel, method="tool_calling")
```

**Pros**: Works on all providers, no schema limitations, battle-tested.
**Cons**: Not guaranteed — the model could theoretically produce invalid JSON (rare with Claude), slightly different prompting path.

### method="json_mode"

Forces JSON output without schema enforcement. Not recommended for production use.

```python
structured = model.with_structured_output(MyModel, method="json_mode")
```

**Pros**: Simplest under the hood.
**Cons**: No schema enforcement by the provider, validation only happens client-side.

### Which to Choose

| Scenario | Method |
|----------|--------|
| Anthropic Claude, data extraction | `json_schema` |
| Anthropic Claude, classification | `json_schema` |
| Cross-provider compatibility needed | `tool_calling` |
| Schema uses recursive types | `tool_calling` |
| Schema uses `minLength`/`maximum` etc. | `tool_calling` |

---

## Anthropic Native Structured Output (Constrained Decoding)

When using `method="json_schema"`, Anthropic compiles your JSON schema into a grammar and actively restricts token generation. This is fundamentally different from prompting for JSON.

### Supported Models

GA: Claude Opus 4.6, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Opus 4.5, Claude Haiku 4.5.
Beta: Microsoft Foundry.

### Two Complementary Features

1. **JSON outputs** (`output_config.format`): Controls Claude's entire response format. Response is valid JSON in `response.content[0].text`. This is what `method="json_schema"` uses.

2. **Strict tool use** (`strict: true`): Guarantees tool input parameters match the schema exactly. Used in tool definitions for agents.

These can be combined in one request (structured response format + guaranteed tool params).

### SDK Schema Transformation

The Python SDK auto-transforms schemas with unsupported features:
1. Removes unsupported constraints (e.g., `minimum`, `maximum`)
2. Updates field descriptions with constraint info (e.g., "Must be at least 100")
3. Adds `additionalProperties: false` to all objects
4. Filters string formats to supported list only
5. Validates responses against original schema (with all constraints)

This means: define your Pydantic model with all the constraints you want. The SDK sends a simplified schema to Claude, but validates the response against your full model.

### Property Ordering

Required properties appear first in output, followed by optional properties. Both groups maintain the order from your schema definition. If property ordering matters to your application, mark all properties as required.

### Invalid Outputs (Rare Edge Cases)

Structured output can fail in two scenarios:
- **Refusal** (`stop_reason: "refusal"`): Claude refuses for safety reasons. Response may not match schema.
- **Token limit** (`stop_reason: "max_tokens"`): Response truncated, JSON incomplete. Set `max_tokens` high enough.

---

## JSON Schema Limitations (Anthropic Native)

These apply when using `method="json_schema"` with ChatAnthropic.

### Supported

- All basic types: `object`, `array`, `string`, `integer`, `number`, `boolean`, `null`
- `enum` (strings, numbers, bools, or nulls only — no complex types)
- `const`
- `anyOf` and `allOf` (with limitations — `allOf` with `$ref` not supported)
- `$ref`, `$def`, and `definitions` (external `$ref` not supported)
- `default` property for all supported types
- `required` and `additionalProperties` (must be `false` for objects)
- String formats: `date-time`, `time`, `date`, `duration`, `email`, `hostname`, `uri`, `ipv4`, `ipv6`, `uuid`
- Array `minItems` (only values 0 and 1)
- Basic regex patterns in `pattern`: `*`, `+`, `?`, `{n,m}`, `[]`, `.`, `\d`, `\w`, `\s`, groups

### NOT Supported

- Recursive schemas
- Complex types within enums
- External `$ref` (e.g., `$ref: http://...`)
- Numerical constraints: `minimum`, `maximum`, `multipleOf`, `exclusiveMinimum`, `exclusiveMaximum`
- String constraints: `minLength`, `maxLength`
- Array constraints beyond `minItems` of 0 or 1 (`maxItems`, `minItems > 1`)
- `additionalProperties` set to anything other than `false`
- Regex backreferences (`\1`), lookahead/lookbehind (`(?=...)`), word boundaries (`\b`)

Unsupported features return a 400 error. The Python/TypeScript SDKs auto-transform to avoid this (see SDK Schema Transformation above).

### Practical Impact on Pydantic Models

```python
# WORKS with json_schema method
class Good(BaseModel):
    name: str
    tags: list[str]
    priority: str  # Use description to hint at values
    count: int     # No min/max enforcement by provider

# PROBLEMATIC with json_schema method — SDK auto-transforms but constraints not enforced at generation
class Risky(BaseModel):
    name: str = Field(min_length=1, max_length=100)  # Transformed: constraint moved to description
    score: float = Field(ge=0, le=1.0)               # Transformed: constraint moved to description
    items: list[str] = Field(min_length=2)            # Not enforceable

# FAILS with json_schema method — use tool_calling instead
class Recursive(BaseModel):
    name: str
    children: list["Recursive"] = []  # Recursive — not supported
```

---

## Multimodal: Content Block Format Reference

LangChain uses a standardized content block format across providers. Blocks go in the `content` field of `HumanMessage` as a list.

### Image Blocks

```python
# URL-based
{"type": "image", "url": "https://example.com/photo.jpg"}

# Base64-encoded
{"type": "image", "base64": "<base64-string>", "mime_type": "image/jpeg"}

# Files API
{"type": "image", "file_id": "file_abc123"}
```

Supported image MIME types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`

### PDF / File Blocks

```python
# URL-based
{"type": "file", "url": "https://example.com/doc.pdf", "mime_type": "application/pdf"}

# Base64-encoded
{"type": "file", "base64": "<base64-string>", "mime_type": "application/pdf"}

# Files API
{"type": "file", "file_id": "file_abc123"}
```

### Text Blocks

```python
{"type": "text", "text": "Your prompt text here."}
```

### Complete Message Example

```python
from langchain_core.messages import HumanMessage
import base64

with open("invoice.pdf", "rb") as f:
    pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

msg = HumanMessage(content=[
    {"type": "text", "text": "Extract all line items from this invoice."},
    {"type": "file", "base64": pdf_b64, "mime_type": "application/pdf"},
])
```

### Anthropic-Native Format (Also Supported)

ChatAnthropic also accepts Anthropic's native content block format directly:

```python
# Anthropic native image format — also works with ChatAnthropic
msg = HumanMessage(content=[
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": image_b64,
        },
    },
    {"type": "text", "text": "Describe this image."},
])
```

The LangChain standard format (`"type": "image", "base64": ..., "mime_type": ...`) is preferred for portability across providers.

---

## Multimodal: Image Limits and Costs

### Size Limits

| Constraint | Limit |
|---|---|
| Supported formats | JPEG, PNG, GIF, WebP |
| Max file size (API) | 5 MB per image |
| Max images per request | 600 (100 for 200k-context models) |
| Max pixel dimensions | 8000x8000 px |
| Max pixels (>20 images) | 2000x2000 px per image |
| Optimal dimensions | <= 1568 px on longest edge, <= 1.15 megapixels |

### Token Costs

Formula: `tokens = (width * height) / 750`

| Image Size | Tokens | Cost at $3/M input |
|---|---|---|
| 200x200 (0.04 MP) | ~54 | ~$0.00016 |
| 1000x1000 (1 MP) | ~1,334 | ~$0.004 |
| 1092x1092 (1.19 MP) | ~1,590 | ~$0.0048 |

Images larger than 1568px on the longest edge are auto-resized (preserving aspect ratio) before processing. This adds latency with no quality benefit.

### Best Practices

- Resize images to <= 1568px before sending to avoid resize latency
- Images below 200px on any edge may degrade output quality
- Place images before text in the message for best results
- Claude cannot identify people by name in images
- Claude does not read image EXIF metadata

---

## Multimodal: PDF Limits and Behavior

### Size Limits

| Constraint | Limit |
|---|---|
| Max request payload | 32 MB total (includes all content) |
| Max pages per request | 600 (100 for 200k-context models) |
| Format | Standard PDF only (no passwords/encryption) |

### How PDFs Are Processed

1. Each page is converted to an image
2. Text is extracted from each page
3. Claude receives both the page image and extracted text
4. This enables analysis of charts, tables, diagrams, and layout

### Token Costs

- Text: ~1,500-3,000 tokens per page depending on density
- Image: Each page also incurs image token costs (page rendered as image)
- Dense PDFs can fill context before hitting page limits

### Best Practices

- Place PDFs before your question in the message
- Use standard fonts for best text extraction
- Ensure text is clear and legible
- Rotate pages to proper orientation
- Split large PDFs into sections for better results
- Use prompt caching for repeated analysis of the same PDF
- Base64 encoding adds ~33% to file size — consider Files API for large docs

---

## Multimodal: Files API

The Files API lets you upload files once and reference them by ID. This is important for:
- Multi-turn conversations (avoids resending base64 every turn)
- Large files (keeps request payload small)
- Repeated analysis of the same document

### Usage with LangChain

```python
import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# Upload via Anthropic SDK
client = anthropic.Anthropic()

# Upload a PDF
pdf_file = client.beta.files.upload(
    file=("document.pdf", open("document.pdf", "rb"), "application/pdf"),
)

# Upload an image
img_file = client.beta.files.upload(
    file=("photo.jpg", open("photo.jpg", "rb"), "image/jpeg"),
)

# Use in LangChain — must pass the beta header
model = ChatAnthropic(
    model="claude-sonnet-4-5",
    betas=["files-api-2025-04-14"],
)

msg = HumanMessage(content=[
    {"type": "text", "text": "Analyze this document."},
    {"type": "file", "file_id": pdf_file.id},
])

response = model.invoke([msg])
```

### When to Use Files API vs. Base64

| Scenario | Approach |
|----------|----------|
| Single request, small file | Base64 |
| Multi-turn conversation with same doc | Files API |
| Multiple large files in one request | Files API |
| Agent loop analyzing a document repeatedly | Files API |
| Quick one-shot extraction | Base64 |

---

## Combining Multimodal + Structured Output

The key pattern for extraction pipelines. Send visual content, get validated Pydantic models.

### PDF Extraction

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import base64

class InsuranceDocument(BaseModel):
    document_type: str = Field(description="Type: policy, claim, endorsement, etc.")
    policy_number: str = Field(description="Policy number if present")
    insured_name: str = Field(description="Name of the insured")
    effective_date: str = Field(description="Policy effective date")
    expiration_date: str = Field(description="Policy expiration date")
    coverage_types: list[str] = Field(description="Types of coverage listed")
    premium_amount: float = Field(description="Premium amount")
    deductible: float = Field(description="Deductible amount")

model = ChatAnthropic(model="claude-sonnet-4-5")
structured = model.with_structured_output(InsuranceDocument, method="json_schema")

with open("policy.pdf", "rb") as f:
    pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

msg = HumanMessage(content=[
    {"type": "text", "text": "Extract all policy information from this insurance document."},
    {"type": "file", "base64": pdf_b64, "mime_type": "application/pdf"},
])

result = structured.invoke([msg])
# result is an InsuranceDocument instance
print(result.policy_number)
print(result.coverage_types)
```

### Image Analysis

```python
class EmailScreenshot(BaseModel):
    sender: str = Field(description="Email sender name and address")
    subject: str = Field(description="Email subject line")
    date: str = Field(description="Date sent")
    body_summary: str = Field(description="Summary of the email body")
    has_attachments: bool = Field(description="Whether attachments are present")
    attachment_names: list[str] = Field(default_factory=list, description="Names of attachments")

structured = model.with_structured_output(EmailScreenshot, method="json_schema")

msg = HumanMessage(content=[
    {"type": "text", "text": "Extract all information from this email screenshot."},
    {"type": "image", "url": "https://example.com/email-screenshot.png"},
])

result = structured.invoke([msg])
```

### Multiple Documents to One Schema

```python
class DocumentComparison(BaseModel):
    doc1_summary: str
    doc2_summary: str
    differences: list[str]
    similarities: list[str]
    recommendation: str

structured = model.with_structured_output(DocumentComparison, method="json_schema")

msg = HumanMessage(content=[
    {"type": "text", "text": "Document 1:"},
    {"type": "file", "base64": pdf1_b64, "mime_type": "application/pdf"},
    {"type": "text", "text": "Document 2:"},
    {"type": "file", "base64": pdf2_b64, "mime_type": "application/pdf"},
    {"type": "text", "text": "Compare these documents. Identify all differences and similarities."},
])

result = structured.invoke([msg])
```

---

## Multiple Documents in One Request

### Pattern: Labeled Content Blocks

Label each document for clarity:

```python
msg = HumanMessage(content=[
    {"type": "text", "text": "Attachment 1 (invoice.pdf):"},
    {"type": "file", "base64": invoice_b64, "mime_type": "application/pdf"},
    {"type": "text", "text": "Attachment 2 (receipt.jpg):"},
    {"type": "image", "base64": receipt_b64, "mime_type": "image/jpeg"},
    {"type": "text", "text": "Attachment 3 (contract.pdf):"},
    {"type": "file", "base64": contract_b64, "mime_type": "application/pdf"},
    {"type": "text", "text": "Extract key data from all three attachments."},
])
```

### Pattern: Processing Email Attachments

```python
from pydantic import BaseModel, Field

class Attachment(BaseModel):
    filename: str
    file_type: str
    summary: str
    extracted_data: dict

class EmailAttachmentAnalysis(BaseModel):
    attachments: list[Attachment]
    overall_context: str = Field(description="How the attachments relate to each other")

structured = model.with_structured_output(EmailAttachmentAnalysis, method="json_schema")

# Build content blocks dynamically from email attachments
content_blocks = [
    {"type": "text", "text": "Analyze all attachments from this email:"},
]

for i, attachment in enumerate(email_attachments):
    content_blocks.append(
        {"type": "text", "text": f"Attachment {i+1} ({attachment.filename}):"}
    )
    if attachment.mime_type == "application/pdf":
        content_blocks.append(
            {"type": "file", "base64": attachment.b64_content, "mime_type": "application/pdf"}
        )
    elif attachment.mime_type.startswith("image/"):
        content_blocks.append(
            {"type": "image", "base64": attachment.b64_content, "mime_type": attachment.mime_type}
        )

content_blocks.append(
    {"type": "text", "text": "Extract and classify all attachment content."}
)

msg = HumanMessage(content=content_blocks)
result = structured.invoke([msg])
```

### Limits When Sending Multiple Files

- Total request payload: 32 MB (base64 adds ~33% overhead)
- Total pages across all PDFs: 600 (100 for 200k-context models)
- Images: 600 total (100 for 200k-context models), 2000x2000px max if >20 images
- Context window is the real constraint for dense documents

---

## ReAct Agents

ReAct (Reason + Act) agents reason through problems by iteratively calling tools and observing results.

### When to Use Agents vs. Structured Output

| Task Type | Approach |
|-----------|----------|
| Extract data from a document | Structured output (one call) |
| Classify content | Structured output (one call) |
| Research something across multiple sources | ReAct agent (multi-step) |
| Answer a question that needs external lookup | ReAct agent |
| Process a batch of items with same schema | Structured output in a loop |

### Basic ReAct Agent (LangGraph)

```python
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information."""
    # ... implementation
    return "search results"

@tool
def lookup_policy(policy_number: str) -> str:
    """Look up an insurance policy by number."""
    # ... implementation
    return "policy details"

model = ChatAnthropic(model="claude-sonnet-4-5")
agent = create_react_agent(model, tools=[search_knowledge_base, lookup_policy])

result = agent.invoke({
    "messages": [("user", "What coverage does policy INS-12345 have?")]
})
```

### Key Differences from Structured Output

| Aspect | Structured Output | ReAct Agent |
|--------|-------------------|-------------|
| LLM calls | 1 | Multiple (unbounded) |
| Tools | None | Iterative tool use |
| Cost | Predictable | Variable |
| Latency | Single round-trip | Multiple round-trips |
| Output | Always structured | Text by default |
| Use case | Extraction, classification | Research, multi-step reasoning |

---

## Agents with Structured Output

You can combine agents with structured final output using the `create_agent` factory.

### Using ProviderStrategy

```python
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from pydantic import BaseModel, Field

class ResearchReport(BaseModel):
    company_name: str
    industry: str
    key_findings: list[str]
    risk_factors: list[str]
    recommendation: str

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[search_tool, web_tool],
    response_format=ProviderStrategy(ResearchReport),
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Research INSURICA and assess partnership fit"}]
})

report = result["structured_response"]  # ResearchReport instance
```

### ProviderStrategy vs. ToolStrategy

- **ProviderStrategy**: Uses the provider's native structured output. For Anthropic, uses `output_config.format`.
- **ToolStrategy**: Uses tool calling to enforce structure. More portable.
- **Auto-detection**: Pass a bare schema type and LangChain picks the best strategy.

---

## Anthropic SDK Direct (Non-LangChain)

For cases where LangChain abstraction is unnecessary (simple one-shot extraction), the Anthropic SDK provides direct structured output.

### Using client.messages.parse()

```python
from anthropic import Anthropic
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str
    email: str
    company: str

client = Anthropic()

response = client.messages.parse(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    output_format=ContactInfo,
    messages=[
        {"role": "user", "content": "Extract: John Smith, john@acme.com, works at Acme Corp"}
    ],
)

contact = response.parsed_output  # ContactInfo instance
```

### Using output_config directly

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["name", "email"],
                "additionalProperties": False,
            },
        }
    },
    messages=[{"role": "user", "content": "Extract contact info from: ..."}],
)

import json
data = json.loads(response.content[0].text)
```

### When to Use Anthropic SDK Directly vs. LangChain

| Scenario | Use |
|----------|-----|
| Simple one-shot extraction | Anthropic SDK (`client.messages.parse()`) |
| Need provider portability | LangChain |
| Building with LangGraph agents | LangChain |
| Need prompt caching middleware | LangChain (`AnthropicPromptCachingMiddleware`) |
| Existing LangChain codebase | LangChain |
| Minimal dependencies | Anthropic SDK |

---

## Performance and Caching

### Grammar Compilation (json_schema method)

- First request with a new schema: ~100-300ms additional latency for grammar compilation
- Subsequent requests with same schema: cached for 24 hours from last use
- Cache invalidated by: schema structure changes, tool set changes
- Cache NOT invalidated by: `name`/`description` changes only

### Prompt Caching

When using structured outputs, Anthropic injects a system prompt explaining the format. This means:
- Input token count is slightly higher
- Changing `output_config.format` invalidates any prompt cache for that thread
- Use `cache_control: {"type": "ephemeral"}` on PDF/image blocks for repeated analysis

### Token Optimization

- PDFs: 1,500-3,000 text tokens + image tokens per page
- Images: `(width * height) / 750` tokens
- Structured output system prompt: small overhead (~100-200 tokens)
- Resize images before sending to avoid resize latency
- Use Files API to avoid resending base64 in multi-turn conversations

---

## Troubleshooting

### "validation error" on structured output response

**Cause**: LLM returned JSON that doesn't match the Pydantic model.
**Fix**: Use `method="json_schema"` instead of `method="tool_calling"` for guaranteed schema compliance. Ensure `langchain-anthropic>=1.1.0`.

### 400 error with "unsupported schema feature"

**Cause**: Your schema uses features not supported by Anthropic's native structured output (recursive types, `minLength`, etc.).
**Fix**: Either use `method="tool_calling"` or simplify the schema. The Python SDK auto-transforms most issues, but recursive schemas cannot be transformed.

### Truncated JSON response

**Cause**: `max_tokens` too low for the expected output size.
**Fix**: Increase `max_tokens`. Check for `stop_reason: "max_tokens"` in the response.

### Image not being processed

**Cause**: Wrong content block type or unsupported format.
**Fix**: Use `"type": "image"` for images (not `"type": "file"`). Ensure MIME type is one of: `image/jpeg`, `image/png`, `image/gif`, `image/webp`.

### PDF content not analyzed (Bedrock)

**Cause**: On Amazon Bedrock's Converse API, visual PDF analysis requires citations to be enabled.
**Fix**: Enable citations in the Converse API request, or use InvokeModel API instead.

### Request too large (32 MB limit)

**Cause**: Base64-encoded files exceed the 32 MB payload limit.
**Fix**: Use the Files API to upload large files and reference by `file_id`. Base64 adds ~33% overhead, so a 24 MB PDF becomes ~32 MB encoded.

### Intermittent failures with tool_calling method

**Cause**: Tool calling method does not guarantee schema compliance.
**Fix**: Switch to `method="json_schema"` for guaranteed compliance. This was a known issue (GitHub #30158) resolved in early 2026.
