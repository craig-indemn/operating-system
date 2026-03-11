---
name: markdown-pdf
description: Convert markdown files to PDF. Use when the user asks to generate a PDF, export markdown as PDF, or share a document as PDF.
user-invocable: false
---

# Markdown to PDF

Convert any markdown file to a clean, Indemn-branded PDF using `md-to-pdf`.

## Status Check

```bash
npx md-to-pdf --version 2>/dev/null && echo "READY" || echo "WILL AUTO-INSTALL ON FIRST USE"
```

No setup required — `npx` installs `md-to-pdf` on first use.

## Usage

**Branded (default)** — uses Indemn theme (Barlow font, iris headings, styled tables):

```bash
npx md-to-pdf <input.md> \
  --stylesheet /Users/home/Repositories/operating-system/.claude/skills/markdown-pdf/indemn-theme.css \
  --pdf-options '{"format": "Letter", "margin": {"top": "0.75in", "bottom": "0.75in", "left": "0.75in", "right": "0.75in"}}'
```

**Plain** — no branding, default styles:

```bash
npx md-to-pdf <input.md>
```

Output: `<input>.pdf` in the same directory as the input file.

## Theme

The Indemn theme at `indemn-theme.css` applies:
- **Font**: Barlow (Google Fonts import)
- **Headings**: Iris (#4752a3) with border accents
- **Tables**: Iris header, alternating row backgrounds
- **Blockquotes**: Lilac left border with light background
- **Code**: Light background with monospace font
- **Text**: Eggplant (#1e2553) body color

## Notes

- Renders standard GitHub-flavored markdown: headings, tables, code blocks, blockquotes, lists.
- For designed reports with charts, metric cards, and custom layouts, use the `report-library` skill instead.
- Always use the branded command above unless the user specifically asks for plain output.
