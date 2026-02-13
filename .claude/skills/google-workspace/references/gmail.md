# Gmail Reference — gog gmail

Complete reference for Gmail operations via the `gog` CLI.

## Search Threads

```bash
gog gmail search "<query>" [--max=10] [--json]
```

Search for email threads using Gmail query syntax. Returns thread summaries.

```bash
# Recent emails from a person
gog gmail search "from:julia@insurica.com" --max=5 --json

# Unread emails with attachments
gog gmail search "is:unread has:attachment" --json

# Emails about a topic in a date range
gog gmail search "subject:renewal after:2025/01/01 before:2025/02/01" --max=20

# Emails in a specific label
gog gmail search "label:customers" --json

# Primary inbox only
gog gmail search "category:primary is:unread"
```

## Search Individual Messages

```bash
gog gmail messages search "<query>" [--json]
```

Like `search` but returns individual messages rather than grouped threads.

```bash
gog gmail messages search "from:cam@indemn.ai" --json
```

## Get a Message

```bash
gog gmail get <messageId> [--format=full|metadata|raw] [--json]
```

Retrieve a specific message by its ID.

```bash
# Full message content
gog gmail get 18d5a2b3c4e5f6a7 --format=full --json

# Headers/metadata only
gog gmail get 18d5a2b3c4e5f6a7 --format=metadata --json

# Raw RFC 2822 format
gog gmail get 18d5a2b3c4e5f6a7 --format=raw
```

## Send Email

```bash
gog gmail send --to=STRING --subject=STRING --body=STRING [--cc=STRING] [--bcc=STRING] [--attach=FILE] [--reply-to-message-id=STRING] [--thread-id=STRING] [--reply-all]
```

```bash
# Simple send
gog gmail send --to="person@company.com" --subject="Follow up" --body="Thanks for the call today."

# With CC and attachment
gog gmail send --to="person@company.com" --cc="manager@company.com" --subject="Proposal" --body="Attached." --attach=./proposal.pdf

# Reply to a specific message (stays in thread)
gog gmail send --to="person@company.com" --subject="Re: Renewal" --body="Sounds good." --reply-to-message-id=18d5a2b3c4e5f6a7 --thread-id=18d5a2b3c4e5f6a7

# Reply-all
gog gmail send --to="person@company.com" --subject="Re: Team sync" --body="Agreed." --reply-to-message-id=18d5a2b3c4e5f6a7 --thread-id=18d5a2b3c4e5f6a7 --reply-all

# BCC
gog gmail send --to="client@company.com" --bcc="internal@indemn.ai" --subject="Update" --body="Here's the latest."
```

## Drafts

```bash
# List all drafts
gog gmail drafts list [--json]

# Create a draft
gog gmail drafts create --to=STRING --subject=STRING --body=STRING

# Send an existing draft
gog gmail drafts send <draftId>
```

```bash
# Create a draft for review
gog gmail drafts create --to="client@company.com" --subject="Q1 Report" --body="Please find the Q1 summary below."

# List drafts then send one
gog gmail drafts list --json
gog gmail drafts send r-8234923849234
```

## Labels

```bash
gog gmail labels list
```

Lists all Gmail labels (both system and custom).

## Attachments

```bash
gog gmail attachment <messageId> <attachmentId>
```

Downloads an attachment from a specific message.

## Get Thread URL

```bash
gog gmail url <threadId>
```

Returns the web URL to open a thread in Gmail.

## Gmail Search Syntax

Gmail search queries support the following operators. Combine with spaces (AND) or the `OR` keyword.

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:julia@insurica.com` | Sender |
| `to:` | `to:cam@indemn.ai` | Recipient |
| `subject:` | `subject:renewal` | Subject line |
| `has:attachment` | `has:attachment` | Has attachments |
| `after:` | `after:2025/01/01` | Sent after date (YYYY/MM/DD) |
| `before:` | `before:2025/02/01` | Sent before date (YYYY/MM/DD) |
| `is:unread` | `is:unread` | Unread messages |
| `is:starred` | `is:starred` | Starred messages |
| `in:inbox` | `in:inbox` | In inbox |
| `label:` | `label:customers` | Has label |
| `category:` | `category:primary` | Gmail category (primary, social, promotions, updates, forums) |

**Combining operators:**
```
from:julia@insurica.com subject:renewal after:2025/01/01
is:unread OR is:starred
from:cam@indemn.ai has:attachment
```

## Common Patterns

**Find recent conversations with a contact:**
```bash
gog gmail search "from:contact@company.com OR to:contact@company.com" --max=10 --json
```

**Get unread count by searching:**
```bash
gog gmail search "is:unread in:inbox" --json
```

**Thread workflow — find thread, get messages, reply:**
```bash
# 1. Find the thread
gog gmail search "from:client@example.com subject:proposal" --json
# 2. Get the specific message (use messageId from search results)
gog gmail get <messageId> --format=full --json
# 3. Reply in the same thread
gog gmail send --to="client@example.com" --subject="Re: proposal" --body="Reply text" --reply-to-message-id=<messageId> --thread-id=<threadId>
```
