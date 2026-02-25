---
name: image-gen
description: Use when generating images for blog posts, social media, or visual content. Use when the user asks for illustrations, hero images, diagrams, or brand-aware visuals. Generates images via Google Nano Banana (Gemini Flash Image) API.
---

# Image Generation

Generate images using Google Nano Banana (Gemini 2.5 Flash Image) via the Gemini API. General-purpose image generation — blog imagery, social visuals, diagrams, mockups, or anything else.

## Status Check

```bash
source .env && curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Generate an image: a small blue circle on white background"}]}],"generationConfig":{"responseModalities":["TEXT","IMAGE"]}}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if 'candidates' in d else f'ERROR: {d.get(\"error\",{}).get(\"message\",\"unknown\")}')"
```

## Setup

### Prerequisites
- Google account (any — craig@indemn.ai works)
- Billing enabled on Google AI Studio (free tier has zero image quota)

### Steps
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create an API key
3. Enable billing in AI Studio settings (required for image generation)
4. Add to `.env`: `GEMINI_API_KEY=<your-key>`

## Available Models

| Model | ID | Speed | Quality | Status |
|-------|----|-------|---------|--------|
| **Nano Banana** | `gemini-2.5-flash-image` | ~5s | Good | Stable (GA) |
| **Nano Banana Pro** | `gemini-3-pro-image-preview` | 20-40s | Best | Preview (unreliable) |
| **Imagen 4** | `imagen-4.0-generate-001` | Fast | High | Stable (different API) |

**Default to `gemini-2.5-flash-image`** — fast, reliable, good quality. Pro is frequently overloaded.

## Usage

### Generate an Image

```bash
source .env && curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
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
# Convert image to base64 first
IMG_B64=$(base64 -i input.png)

source .env && curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
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

**Core principle:** Describe scenes in narrative sentences, not keyword lists.

### Prompt Structure (7-part framework)

1. **Action**: "Generate an image:" or "Create a:"
2. **Subject**: What's in the image
3. **Attributes**: Visual details — colors, textures, materials
4. **Environment & Lighting**: Setting, time of day, light direction
5. **Style**: Photorealistic, illustration, vector, watercolor, etc.
6. **Brand constraints**: Color palette, mood, positioning
7. **Format**: Blog header, social card, icon, etc.

### Good vs Bad Prompts

```
BAD:  "AI evaluation neural network purple"
GOOD: "Generate an image: A clean, modern abstract illustration representing
       AI evaluation — showing a neural network pattern being measured by
       geometric scoring indicators. Cool blue and purple tones on white.
       Professional, minimal, suitable for a tech blog header."
```

### Photography Terms That Work

Shot types, lens specs, and lighting setups improve photorealistic output: "85mm portrait lens", "golden hour light", "Rembrandt lighting", "softbox studio lighting", "f/2.8 shallow depth of field".

### Iterative Editing

Break complex edits into steps rather than one massive prompt:
1. Generate base image
2. "Keep everything but change the background to..."
3. "Now adjust the color grading to..."

For detailed prompting techniques, see `references/prompting-guide.md`.

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
| Keyword-stuffed prompts | Write descriptive sentences instead |
| No brand colors specified | Always include hex codes for brand work |
| One massive edit prompt | Break into iterative steps |
| Using Pro model in production | Use Flash — Pro is unreliable in preview |
| Forgetting `responseModalities` | Must include `["TEXT", "IMAGE"]` or no image returned |
| Not saving the image | Response is base64 — must decode and write to file |
| Specifying aspect ratio in prompt text only | Model ignores it — use `imageConfig.aspectRatio` in `generationConfig` |
| Deploying images without cropping whitespace | Always auto-crop — Gemini leaves large white margins around content |

## Limitations

- All generated images include SynthID watermark (invisible, for authenticity)
- Free tier has zero image quota — billing required
- Flash model generates ~1K resolution by default (1024x1024 square, 1344x768 at 16:9)
- Text rendering can be inconsistent — may need retries
- Content policy blocks certain categories (violence, etc.)
