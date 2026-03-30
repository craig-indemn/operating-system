---
name: langchain
description: Use LangChain for LLM integration — structured output, multimodal (PDFs/images), ReAct agents, Anthropic Claude integration. Use when building AI features with LangChain.
user-invocable: false
---

# LangChain

LLM integration framework used across Indemn services. Core packages: `langchain-core`, `langchain-anthropic`, `langchain`.

## Status Check

```bash
python3 -c "import langchain_core; print(f'langchain-core: {langchain_core.__version__}')" 2>/dev/null || echo "langchain-core NOT INSTALLED"
python3 -c "import langchain_anthropic; print(f'langchain-anthropic: {langchain_anthropic.__version__}')" 2>/dev/null || echo "langchain-anthropic NOT INSTALLED"
```

Minimum versions for key features:
- Structured output (native json_schema): `langchain-anthropic>=1.1.0`
- Code execution tools: `langchain-anthropic>=1.0.3`
- Current latest: `langchain-anthropic==1.4.0`

## Setup

### With uv (Indemn services)
```bash
uv add langchain-anthropic langchain-core langchain
```

### With pip
```bash
pip install langchain-anthropic langchain-core langchain
```

### For structured output with Pydantic
```bash
# Pydantic v2 is required — included as a dependency of langchain-core
python3 -c "import pydantic; print(pydantic.__version__)"
```

## Usage

### Structured Output (Primary Pattern)

Use `with_structured_output()` to get validated Pydantic models from Claude. Two methods available:

**Method 1: Native JSON schema (recommended for Anthropic)**
Uses Anthropic's constrained decoding — guaranteed valid JSON, no retries needed.

```python
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

class EmailExtraction(BaseModel):
    sender_name: str = Field(description="Name of the sender")
    sender_email: str = Field(description="Email address")
    intent: str = Field(description="Primary intent of the email")
    action_items: list[str] = Field(description="Action items found")
    priority: str = Field(description="high, medium, or low")

model = ChatAnthropic(model="claude-sonnet-4-5")
structured = model.with_structured_output(EmailExtraction, method="json_schema")

result = structured.invoke("Extract from this email: ...")
# result is an EmailExtraction instance — guaranteed valid
```

**Method 2: Tool calling (default)**
Uses function/tool calling under the hood. Works on all providers.

```python
structured = model.with_structured_output(EmailExtraction)  # method defaults to tool_calling
```

**Schema types supported**: Pydantic BaseModel (recommended), TypedDict, raw JSON Schema dict.

### Multimodal: Sending Images

Images go in `HumanMessage` content blocks. Three delivery methods:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

model = ChatAnthropic(model="claude-sonnet-4-5")

# URL-based (simplest)
msg = HumanMessage(content=[
    {"type": "text", "text": "Describe this image."},
    {"type": "image", "url": "https://example.com/photo.jpg"},
])

# Base64-encoded (for local files)
import base64
with open("photo.jpg", "rb") as f:
    b64 = base64.standard_b64encode(f.read()).decode("utf-8")

msg = HumanMessage(content=[
    {"type": "text", "text": "Describe this image."},
    {"type": "image", "base64": b64, "mime_type": "image/jpeg"},
])

# Files API (for repeated use — avoids resending bytes each turn)
import anthropic
client = anthropic.Anthropic()
file = client.beta.files.upload(
    file=("photo.jpg", open("photo.jpg", "rb"), "image/jpeg")
)
model_with_files = ChatAnthropic(
    model="claude-sonnet-4-5",
    betas=["files-api-2025-04-14"],
)
msg = HumanMessage(content=[
    {"type": "text", "text": "Describe this image."},
    {"type": "image", "file_id": file.id},
])

response = model.invoke([msg])
```

### Multimodal: Sending PDFs

PDFs use `"type": "file"` blocks (not `"type": "image"`):

```python
# URL-based
msg = HumanMessage(content=[
    {"type": "text", "text": "Summarize this document."},
    {"type": "file", "url": "https://example.com/doc.pdf", "mime_type": "application/pdf"},
])

# Base64-encoded
with open("document.pdf", "rb") as f:
    pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

msg = HumanMessage(content=[
    {"type": "text", "text": "Extract key information."},
    {"type": "file", "base64": pdf_b64, "mime_type": "application/pdf"},
])

# Files API
file = client.beta.files.upload(
    file=("doc.pdf", open("doc.pdf", "rb"), "application/pdf")
)
msg = HumanMessage(content=[
    {"type": "text", "text": "Summarize this document."},
    {"type": "file", "file_id": file.id},
])
```

### Multiple Images/PDFs in One Request

Include multiple content blocks in the same message. Label them for clarity:

```python
msg = HumanMessage(content=[
    {"type": "text", "text": "Document 1:"},
    {"type": "file", "base64": pdf1_b64, "mime_type": "application/pdf"},
    {"type": "text", "text": "Document 2:"},
    {"type": "file", "base64": pdf2_b64, "mime_type": "application/pdf"},
    {"type": "text", "text": "Compare these two documents and list the differences."},
])
```

### Combining Multimodal + Structured Output

This is the key pattern for extraction pipelines. Send visual content, get back a Pydantic model:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import base64

class InvoiceData(BaseModel):
    invoice_number: str
    vendor_name: str
    total_amount: float
    line_items: list[dict]
    due_date: str

model = ChatAnthropic(model="claude-sonnet-4-5")
structured = model.with_structured_output(InvoiceData, method="json_schema")

with open("invoice.pdf", "rb") as f:
    pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

msg = HumanMessage(content=[
    {"type": "text", "text": "Extract all invoice data from this PDF."},
    {"type": "file", "base64": pdf_b64, "mime_type": "application/pdf"},
])

result = structured.invoke([msg])
# result is an InvoiceData instance with validated fields
```

Works identically with images:

```python
class ImageAnalysis(BaseModel):
    description: str
    objects: list[str]
    text_content: str = Field(default="", description="Any text visible in the image")

structured = model.with_structured_output(ImageAnalysis, method="json_schema")
msg = HumanMessage(content=[
    {"type": "text", "text": "Analyze this image."},
    {"type": "image", "url": "https://example.com/screenshot.png"},
])
result = structured.invoke([msg])
```

### ReAct Agents vs. Structured Output

**Use structured output** when you need one-pass extraction/classification (PDF in, data out). One LLM call, no tools.

**Use a ReAct agent** when the task requires multi-step reasoning, tool calls, or iterative refinement.

```python
from langgraph.prebuilt import create_react_agent

# Simple agent with tools
agent = create_react_agent(model, tools=[search_tool, fetch_tool])
result = agent.invoke({"messages": [("user", "Research this company")]})

# Agent with structured final output
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[my_tools],
    response_format=ProviderStrategy(MyOutputSchema),
)
result = agent.invoke({"messages": [...]})
structured = result["structured_response"]  # MyOutputSchema instance
```

### Important Notes

- **Images before text**: Place images/PDFs before your question for best results.
- **Content block types**: Images use `"type": "image"`, PDFs use `"type": "file"` with `"mime_type": "application/pdf"`.
- **Schema constraints**: Anthropic's native structured output does not support recursive schemas, `minimum`/`maximum`, `minLength`/`maxLength`, or `additionalProperties` other than `false`. LangChain's SDK auto-transforms these (moves constraints to descriptions, validates client-side).
- **First-call latency**: Native `json_schema` method compiles a grammar on first use (~100-300ms overhead). Cached for 24 hours.
- **Files API for multi-turn**: In agentic loops, base64 data resends every turn. Use Files API to upload once and reference by `file_id`.

For full API details, content block formats, limits, and Anthropic native structured output internals, see `references/langchain-guide.md`.
