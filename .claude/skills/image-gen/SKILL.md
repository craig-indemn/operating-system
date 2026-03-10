---
name: image-gen
description: Use when generating images for blog posts, social media, or visual content. Use when the user asks for illustrations, hero images, diagrams, or brand-aware visuals. Generates images via Google Nano Banana (Gemini Flash Image) API.
---

# Image Generation

Generate images using Google Nano Banana (Gemini 2.5 Flash Image) via the Gemini API. General-purpose image generation — blog imagery, social visuals, diagrams, mockups, or anything else.

## Status Check

```bash
GEMINI_API_KEY=$(op read "op://cli-secrets/Gemini API Key/credential") && \
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Generate an image: a small blue circle on white background"}]}],"generationConfig":{"responseModalities":["TEXT","IMAGE"]}}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if 'candidates' in d else f'ERROR: {d.get(\"error\",{}).get(\"message\",\"unknown\")}')"
```

## Setup

### Prerequisites
- Google account (any — craig@indemn.ai works)
- Billing enabled on Google AI Studio (free tier has zero image quota)
- Gemini API Key stored in 1Password vault `cli-secrets`

### Steps
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create an API key
3. Enable billing in AI Studio settings (required for image generation)
4. Store in 1Password: `op item create --vault cli-secrets --category "API Credential" --title "Gemini API Key" credential=<your-key>`

### Retrieving the API Key

**Always use `op read`** — NOT `op item get --fields`:
```bash
# CORRECT — returns the actual secret value
GEMINI_API_KEY=$(op read "op://cli-secrets/Gemini API Key/credential")

# WRONG — returns a reference string, not the value
GEMINI_API_KEY=$(op item get "Gemini API Key" --vault cli-secrets --fields label=credential)
```

## Available Models

| Model | ID | Speed | Quality | Status |
|-------|----|-------|---------|--------|
| **Nano Banana** | `gemini-2.5-flash-image` | ~5s | Good | Stable (GA) |
| **Nano Banana Pro** | `gemini-3-pro-image-preview` | 20-40s | Best | Preview (unreliable) |
| **Imagen 4** | `imagen-4.0-generate-001` | Fast | High | Stable (different API) |

**Default to `gemini-2.5-flash-image`** — fast, reliable, good quality. Pro is frequently overloaded.

## Pricing

| Model | Cost | Notes |
|-------|------|-------|
| Gemini 2.5 Flash Image | ~$0.04/image | Per-token billing, 1,290 tokens per image at $30/1M output tokens |
| Imagen 4 | $0.02-0.06/image | Per-image, three quality tiers (fast/standard/ultra) |

No free tier for image generation. Batch mode halves Flash cost to ~$0.02/image.

## Usage

### Generate an Image

```bash
GEMINI_API_KEY=$(op read "op://cli-secrets/Gemini API Key/credential") && \
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "YOUR PROMPT HERE"}]}],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "16:9"
      }
    }
  }' | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
if 'error' in data:
    print('ERROR:', data['error']['message']); sys.exit(1)
for part in data['candidates'][0]['content']['parts']:
    if 'inlineData' in part:
        img = base64.b64decode(part['inlineData']['data'])
        with open('OUTPUT_PATH.png', 'wb') as f: f.write(img)
        print(f'Saved ({len(img)//1024}KB)')
    if 'text' in part:
        print(part['text'][:200])
"
```

Replace `YOUR PROMPT HERE`, `OUTPUT_PATH.png`, and the `aspectRatio` value. Omit `imageConfig` entirely for default 1:1 square.

### Edit an Existing Image

```bash
IMG_B64=$(base64 -i input.png)

GEMINI_API_KEY=$(op read "op://cli-secrets/Gemini API Key/credential") && \
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{\"parts\": [
      {\"inlineData\": {\"mimeType\": \"image/png\", \"data\": \"$IMG_B64\"}},
      {\"text\": \"EDIT INSTRUCTION HERE\"}
    ]}],
    \"generationConfig\": {\"responseModalities\": [\"TEXT\", \"IMAGE\"], \"imageConfig\": {\"aspectRatio\": \"16:9\"}}
  }" | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
if 'error' in data:
    print('ERROR:', data['error']['message']); sys.exit(1)
for part in data['candidates'][0]['content']['parts']:
    if 'inlineData' in part:
        img = base64.b64decode(part['inlineData']['data'])
        with open('OUTPUT_PATH.png', 'wb') as f: f.write(img)
        print(f'Saved ({len(img)//1024}KB)')
"
```

### Aspect Ratio Control

Use `imageConfig.aspectRatio` in `generationConfig` to control output dimensions. **Do NOT rely on prompt text alone** — the model ignores natural language aspect instructions and generates 1024x1024 by default.

Supported values: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

```json
"generationConfig": {
  "responseModalities": ["TEXT", "IMAGE"],
  "imageConfig": {
    "aspectRatio": "16:9"
  }
}
```

Common use cases:
- Blog headers: `"16:9"` (produces ~1344x768)
- Social cards: `"3:2"` or `"4:3"`
- Portrait/mobile: `"9:16"` or `"3:4"`
- Ultra-wide banners: `"21:9"`
- Square (default): `"1:1"` or omit `imageConfig`

## Prompting

**Core principle:** Structure prompts as design briefs, not keyword lists. Lead with style, then content, then constraints.

### The ICS Framework (Image type → Content → Style)

Every prompt should have three clearly separated sections:

1. **Image type** — What kind of image: "Technical process diagram", "UI dashboard mockup", "Comparison infographic", "Hero illustration"
2. **Content** — Every element explicitly described: icons, labels, layout positions, data, relationships
3. **Style** — Visual treatment: "Flat vector, Figma export quality", line weights, fills, canvas color

### Diagram Prompt Template

```
Image type: [diagram type] for a [context].

Content: [describe every element, its position, icon, and label]
- Element 1 (position): description, icon, label
- Element 2 (position): description, icon, label
- Relationships: arrows, connections, flow direction
- Center/footer: any summary element

Style: Flat vector illustration as if exported from Figma. Solid color fills,
no gradients, no shadows, no 3D, no decorative elements. Consistent 2px line
weight throughout. White background. Clean sans-serif typography.

Layout: [spatial arrangement — columns, compass positions, rows, containers]

Colors (use ONLY these):
- #XXXXXX (name): usage description
- #XXXXXX (name): usage description
```

### What Works (Tested)

| Technique | Impact | Example |
|-----------|--------|---------|
| **Style-first declaration** | High | "Flat vector, Figma export, solid fills, 2px lines" before any content |
| **ICS structure** | High | Separate Image type / Content / Style sections |
| **"UI mockup" framing** | Very High | For dashboards — "Dashboard screenshot mockup" produces SaaS-quality output |
| **Explicit spatial layout** | High | "Four columns separated by hairlines", "compass positions N/E/S/W" |
| **Container shapes** | High | "Each stage in a rounded rectangle, corner radius 12px, lavender fill, indigo border" |
| **Hex codes + usage** | Medium | "#475293 for arrows and borders" — not just a palette list |
| **Subtitles per element** | Medium | Adds a one-line description under each icon for clarity |
| **Icon descriptions** | Medium | "clipboard with checkmarks" not just "evaluation icon" |

### What Doesn't Work

| Technique | Impact | Why |
|-----------|--------|-----|
| **Negative constraints** | Low | "DO NOT include gradients" is weaker than "solid fills only" |
| **Brand references** | Low | "Like Stripe docs" or "Notion style" — model doesn't reliably know these |
| **Imagen 4 for diagrams** | Poor | Renders hex codes as literal text labels instead of using them as colors |
| **Keyword-stuffed prompts** | Poor | "diagram technical professional 4k clean" produces worse results than narrative |

### Framing by Diagram Type

| Type | Framing | Key Instructions |
|------|---------|-----------------|
| **Process/flow** | "Technical process diagram" | Compass positions, curved arrows, center element |
| **Dashboard** | "Dashboard screenshot mockup" | Card layout, donut charts, tables, failure bars — describe as real UI |
| **Comparison** | "Comparison infographic" | Equal-width columns, hairline separators, shared footer element |
| **Architecture** | "System architecture diagram" | Boxes for services, arrows for data flow, layers for tiers |
| **Hero/banner** | "Cinematic hero illustration" | Abstract, moody, no text — dark backgrounds work well |

### Photography/Illustration Prompts

For non-diagram images, these terms improve output:
- Shot types: "85mm portrait lens", "wide establishing shot"
- Lighting: "golden hour", "Rembrandt lighting", "softbox studio"
- Depth: "f/2.8 shallow depth of field", "tilt-shift miniature"
- Style: "editorial photograph", "watercolor illustration", "isometric 3D"

### Iterative Editing

Break complex edits into steps rather than one massive prompt:
1. Generate base image
2. Upload result + "Keep everything but change the background to..."
3. Upload result + "Now adjust the color grading to..."

The model maintains context when you send the previous image back as input.

## Brand-Aware Generation

When generating for a specific brand, include the brand's color palette and visual identity in the prompt. The caller is responsible for providing brand context — this skill doesn't hardcode any brand.

**Pattern:** Read the brand config (colors, style preferences) from wherever it lives, then inject it into the prompt alongside the image description.

```
Generate an image: [DESCRIPTION].
Color palette: [hex codes]. Style: [brand aesthetic]. [Format/size context].
```

## Post-Processing: Whitespace Cropping

Gemini often generates images with significant white margins around the actual content, even with `imageConfig.aspectRatio` set. **Always crop after generation** — especially for blog/web use where whitespace creates awkward gaps.

### Auto-Crop Script

Requires Pillow (`pip install Pillow`). Python at `/Users/home/Repositories/.venv/bin/python3` has it.

```bash
/Users/home/Repositories/.venv/bin/python3 -c "
from PIL import Image

img = Image.open('INPUT.png').convert('RGB')
pixels = img.load()
w, h = img.size
threshold = 245  # pixels above this in all channels = white

def is_white_row(y):
    for x in range(w):
        r, g, b = pixels[x, y]
        if r < threshold or g < threshold or b < threshold:
            return False
    return True

def is_white_col(x):
    for y in range(h):
        r, g, b = pixels[x, y]
        if r < threshold or g < threshold or b < threshold:
            return False
    return True

top = next(y for y in range(h) if not is_white_row(y))
bottom = next(y for y in range(h-1, -1, -1) if not is_white_row(y))
left = next(x for x in range(w) if not is_white_col(x))
right = next(x for x in range(w-1, -1, -1) if not is_white_col(x))

pad = 15
top, bottom = max(0, top-pad), min(h-1, bottom+pad)
left, right = max(0, left-pad), min(w-1, right+pad)

cropped = img.crop((left, top, right+1, bottom+1))
cropped.save('OUTPUT.png')
print(f'{w}x{h} -> {cropped.size[0]}x{cropped.size[1]}')
"
```

Replace `INPUT.png` and `OUTPUT.png`. The threshold of 245 handles near-white artifacts that `ImageChops.difference` misses.

### Why This Matters

- Model generates content in a small region even when `aspectRatio` is set correctly
- A 1344x768 image may have content in only a 1200x300 band — the rest is white
- On a blog, the browser renders the full image dimensions, creating huge visual gaps
- Cropping removes the dead space so content fits tightly in the page layout

### When to Crop

**Always crop** for web/blog use. The only exception is if you specifically want whitespace padding (e.g., an image meant to float with breathing room).

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Keyword-stuffed prompts | Write narrative sentences with ICS structure instead |
| No brand colors specified | Always include hex codes with usage descriptions |
| One massive edit prompt | Break into iterative steps — generate base, then refine |
| Using Pro model in production | Use Flash — Pro is unreliable in preview |
| Forgetting `responseModalities` | Must include `["TEXT", "IMAGE"]` or no image returned |
| Not saving the image | Response is base64 — must decode and write to file |
| Specifying aspect ratio in prompt text only | Model ignores it — use `imageConfig.aspectRatio` in `generationConfig` |
| Deploying images without cropping whitespace | Always auto-crop — Gemini leaves large white margins around content |
| Using Imagen 4 for diagrams | Imagen 4 renders hex codes as literal text — use Gemini Flash for diagrams |
| Using `source .env` for API key | Blocked by secrets guard — use `op read "op://cli-secrets/Gemini API Key/credential"` |
| Using `op item get --fields` | Returns reference strings — use `op read` to get actual secret values |
| Vague style like "clean and professional" | Be specific: "Flat vector, Figma export, solid fills, 2px lines, no gradients" |
| Using "like Stripe docs" style references | Model doesn't know brand aesthetics — describe the style explicitly instead |

## Limitations

- All generated images include SynthID watermark (invisible, for authenticity)
- Free tier has zero image quota — billing required
- Flash model generates ~1K resolution by default (1024x1024 square, 1344x768 at 16:9)
- Text rendering can be inconsistent — may need retries
- Content policy blocks certain categories (violence, etc.)
