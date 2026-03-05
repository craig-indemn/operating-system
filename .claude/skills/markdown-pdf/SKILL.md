---
name: markdown-pdf
description: Convert markdown files to PDF. Use when the user asks to generate a PDF, export markdown as PDF, or share a document as PDF.
user-invocable: false
---

# Markdown to PDF

Convert any markdown file to a clean PDF using `md-to-pdf`.

## Status Check

```bash
npx md-to-pdf --version 2>/dev/null && echo "READY" || echo "WILL AUTO-INSTALL ON FIRST USE"
```

No setup required — `npx` installs `md-to-pdf` on first use.

## Usage

```bash
npx md-to-pdf <input.md>
```

Output: `<input>.pdf` in the same directory as the input file.

## Notes

- No flags needed — it just works. Output goes next to the input file with `.pdf` extension.
- Renders standard GitHub-flavored markdown: headings, tables, code blocks, blockquotes, lists.
- For branded/custom reports with charts and metrics, use the `report-library` skill instead.
- This skill is for quick, no-frills markdown → PDF conversion.
