# Nano Banana Prompting Guide

Detailed prompting techniques for Google Nano Banana (gemini-2.5-flash-image). For quick reference, see the main SKILL.md.

## The 7-Part Prompt Framework

### 1. Action/Goal
State what you want: "Generate an image:", "Edit this photo to:", "Create a:"

### 2. Subject(s)
Identify who/what with specifics — identity, quantity, positioning.

### 3. Attributes
Visual characteristics: clothing, expressions, colors, textures, materials, props. Use micro-constraints for precision: "navy blazer, single-breasted, notch lapel" not just "suit."

### 4. Environment & Lighting
Location, time of day, mood, atmosphere. Photography terms work well:
- **Lighting**: "Rembrandt lighting", "softbox studio", "golden hour", "flat lit", "rim lighting"
- **Lens**: "50mm portrait lens, f/2.8", "35mm wide angle", "85mm telephoto"
- **Atmosphere**: "foggy morning", "neon-lit street", "overcast diffused light"

### 5. Style & Finish
Choose explicitly:
- **Photo**: cinematic, studio, film grain, hyperreal, editorial
- **Illustration**: vector, cel-shaded, watercolor, oil painting, pencil sketch
- **Design**: flat design, isometric, minimalist, geometric, abstract
- **Specific**: "in the style of a technical whitepaper diagram", "like a SaaS landing page hero"

### 6. Constraints
What to avoid or preserve: "no text overlays", "keep the original face unchanged", "no stock photo aesthetic"

### 7. Consistency Token (optional)
For multi-image series, reuse a short reference phrase: "character token: 'Maya-blue-jacket'" to maintain identity across generations.

## Style Categories

### Photorealistic
Include camera/lens terms, lighting setups, specific atmospheric conditions.
```
Generate an image: Professional headshot of a software engineer, mid-30s,
confident expression. Softbox studio lighting, slightly warm tone. 85mm
portrait lens, f/2.8 shallow depth of field. Clean gray background.
4:5 portrait ratio.
```

### Abstract/Geometric (Best for Tech Blog Headers)
Specify shapes, patterns, color relationships, composition.
```
Generate an image: Abstract geometric composition representing data flow —
interconnected nodes and pathways in deep indigo (#1e2553) and iris purple
(#4752a3), with lilac (#a67cb7) accent highlights. Floating on clean white.
Minimal, modern, professional. Suitable as a wide blog header.
```

### Stylized Illustrations
Be explicit about art style, line weight, shading, palette.
```
Generate an image: Kawaii-style illustration of a friendly robot evaluating
test results on a clipboard. Soft pastel colors, thick outlines, cel-shaded.
Simple background with floating sparkle elements. Square format.
```

### Product/Commercial
Use studio photography terms, specify materials and angles.
```
Generate an image: SaaS dashboard screenshot mockup on a MacBook Pro,
angled 30 degrees on a clean white desk. Soft directional light from
top-left, subtle shadow. The screen shows a data visualization with
purple (#4752a3) accent bars. Ultra-clean, editorial product shot.
```

## Advanced Techniques

### Reference Anchors
Brief, verifiable details reduce ambiguity:
- Clothing: "navy blazer, single-breasted, notch lapel"
- Lighting: "Rembrandt lighting, key light from upper left"
- Camera: "50mm portrait lens, f/2.8, shallow DoF"
- Material: "brushed aluminum, matte finish, beveled edges"

### Micro-Constraints
Specify what must NOT change in edits:
- "Do not alter the tattoos on right forearm"
- "Preserve the original expression and eye color"
- "Keep product label legible and unchanged"

### Chain-of-Edits
Break complex work into steps:
1. Background swap
2. Outfit/element update
3. Color grading adjustment
4. Final retouch/polish

Each focused prompt reduces unexpected cross-effects.

### Iterative Refinement Loop
1. **Brief**: Write a clear prompt with intent and constraints
2. **Generate**: Produce 1-2 candidates
3. **Inspect**: Evaluate against the brief, note failures
4. **Constrain**: Change ONE variable per iteration

### Describe What You Want, Not What You Don't
```
BAD:  "no cars, no people, no buildings"
GOOD: "a quiet empty meadow under overcast sky"
```

## Blog Content Prompting Patterns

### Hero Image (Wide Banner)
```
Generate a wide 16:9 image: [Abstract/thematic description related to post topic].
Color palette: [brand colors with hex codes]. Professional, clean, modern.
No text. Suitable as a blog post hero image.
```

### Section Illustration
```
Generate an image: [Concept illustration for specific section]. Simple,
icon-like, [brand color] on white background. Minimal detail, clear at
small sizes. Square format.
```

### Process/Flow Diagram
```
Generate an image: Clean technical diagram showing [process]. Boxes connected
by arrows, labeled clearly. Use [brand colors] for boxes and borders on white
background. Professional infographic style, legible text.
```

### Before/After Comparison
```
Generate an image: Split-screen comparison. Left side: [before state, muted
colors]. Right side: [after state, vibrant brand colors]. Clean dividing
line in the middle. Professional, editorial style.
```

## Common Failure Modes

| Issue | Cause | Fix |
|-------|-------|-----|
| Identity drift | Over-generalized style | Add explicit "preserve" clause, attach original as reference |
| Inconsistent hands/props | Historically difficult for all models | Micro-constraints, close-up reference, targeted correction pass |
| Unnatural lighting | Large edits create mismatches | Specify directional light explicitly, provide lighting reference |
| Text rendering errors | Model limitation | Retry, tighter constraints, or add text in post-processing |
| Generic stock look | Prompt too vague | More specific style terms, explicit "no stock photo aesthetic" |
| Wrong aspect ratio | Prompt text ignored for aspect | Use `imageConfig.aspectRatio` in `generationConfig` — prompt text alone does NOT work |

## Brand-Aware Prompt Template

When generating for a specific brand, inject brand context into the prompt. The caller provides the brand details — this skill is brand-agnostic.

```
Generate an image: [DESCRIPTION OF CONCEPT].

Visual style: [brand aesthetic — e.g., clean/modern/playful/bold].
Color palette: [primary hex] as primary, [secondary hex] for accents,
[tertiary hex] for highlights, on [background color] background.

No stock photography aesthetic. No generic corporate imagery. No text unless
specifically requested. Suitable for [blog header / social card / section
illustration].
```
