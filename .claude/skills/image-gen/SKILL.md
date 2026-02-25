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
      "responseModalities": ["TEXT", "IMAGE"]
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

Replace `YOUR PROMPT HERE` and `OUTPUT_PATH.png`.

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
    \"generationConfig\": {\"responseModalities\": [\"TEXT\", \"IMAGE\"]}
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

### Supported Aspect Ratios

`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

Specify in the prompt text (e.g., "wide 16:9 landscape") — the model respects natural language aspect instructions.

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

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Keyword-stuffed prompts | Write descriptive sentences instead |
| No brand colors specified | Always include hex codes for brand work |
| One massive edit prompt | Break into iterative steps |
| Using Pro model in production | Use Flash — Pro is unreliable in preview |
| Forgetting `responseModalities` | Must include `["TEXT", "IMAGE"]` or no image returned |
| Not saving the image | Response is base64 — must decode and write to file |

## Limitations

- All generated images include SynthID watermark (invisible, for authenticity)
- Free tier has zero image quota — billing required
- Flash model generates ~1K resolution by default
- Text rendering can be inconsistent — may need retries
- Content policy blocks certain categories (violence, etc.)
