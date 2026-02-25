#!/usr/bin/env node
/**
 * Render .excalidraw files to SVG.
 * Must be run from this directory (lib/excalidraw-renderer/) so that
 * node_modules/@excalidraw/utils is found by excalidraw-to-svg.
 *
 * Post-processes the SVG to inject bound text that @excalidraw/utils@0.1.2
 * fails to render in jsdom.
 *
 * Usage: node render.js <input.excalidraw> <output-directory>
 */
const path = require('path');
const fs = require('fs');
const excalidrawToSvg = require('excalidraw-to-svg');

const [,, inputPath, outputDir] = process.argv;

if (!inputPath || !outputDir) {
  console.error('Usage: node render.js <input.excalidraw> <output-directory>');
  process.exit(1);
}

const absInput = path.resolve(inputPath);
const absOutput = path.resolve(outputDir);

if (!fs.existsSync(absInput)) {
  console.error(`Input file not found: ${absInput}`);
  process.exit(1);
}

if (!fs.existsSync(absOutput)) {
  fs.mkdirSync(absOutput, { recursive: true });
}

const diagram = JSON.parse(fs.readFileSync(absInput, 'utf-8'));
const baseName = path.basename(absInput, path.extname(absInput));
const outputFile = path.join(absOutput, `${baseName}.svg`);

// Font family mapping matching Excalidraw's values
const FONT_MAP = {
  1: 'Virgil, Segoe UI Emoji',
  3: 'Cascadia, Segoe UI Emoji',
  5: 'Virgil, Segoe UI Emoji',
  6: 'Nunito, Segoe UI Emoji',
};

/**
 * Build an index of elements by ID for quick lookup.
 */
function indexElements(elements) {
  const byId = {};
  for (const el of elements) {
    if (!el.isDeleted) byId[el.id] = el;
  }
  return byId;
}

/**
 * Compute the SVG viewBox offset from the diagram.
 * excalidraw-to-svg adds a 10px padding around the bounding box.
 */
function computeViewBoxOrigin(elements) {
  let minX = Infinity, minY = Infinity;
  for (const el of elements) {
    if (el.isDeleted) continue;
    if (el.type === 'text' && el.containerId) continue; // bound text has 0,0 coords
    if (el.x < minX) minX = el.x;
    if (el.y < minY) minY = el.y;
    // For arrows, check all points
    if (el.points) {
      for (const [px, py] of el.points) {
        if (el.x + px < minX) minX = el.x + px;
        if (el.y + py < minY) minY = el.y + py;
      }
    }
  }
  return { x: minX - 10, y: minY - 10 }; // 10px padding
}

/**
 * Escape XML special characters.
 */
function escapeXml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * Generate SVG text elements for bound text that excalidraw-to-svg missed.
 */
function generateBoundTextSvg(elements, viewOrigin) {
  const byId = indexElements(elements);
  const textElements = [];

  for (const el of elements) {
    if (el.isDeleted) continue;
    if (el.type !== 'text' || !el.containerId) continue;

    const container = byId[el.containerId];
    if (!container) continue;

    // Calculate center of container in SVG coordinates
    const cx = container.x + container.width / 2 - viewOrigin.x;
    const cy = container.y + container.height / 2 - viewOrigin.y;

    const fontSize = el.fontSize || 20;
    const fontFamily = FONT_MAP[el.fontFamily] || 'Nunito, Segoe UI Emoji';
    const fill = el.strokeColor || '#1e1e1e';
    const lines = el.text.split('\n');
    const lineHeight = fontSize * (el.lineHeight || 1.25);

    // Vertical centering: offset from center
    const totalHeight = lines.length * lineHeight;
    const startY = cy - totalHeight / 2 + fontSize * 0.85; // baseline offset

    let svgLines = '';
    for (let i = 0; i < lines.length; i++) {
      const y = startY + i * lineHeight;
      svgLines += `<text x="${cx}" y="${y}" font-family="${fontFamily}" font-size="${fontSize}px" fill="${fill}" text-anchor="middle" style="white-space: pre;" direction="ltr">${escapeXml(lines[i])}</text>`;
    }

    textElements.push(`<g transform="translate(0 0)">${svgLines}</g>`);
  }

  return textElements.join('\n');
}

excalidrawToSvg(diagram)
  .then((svg) => {
    let svgStr = svg.outerHTML || svg.toString();

    // Add Nunito font-face if not already present
    if (!svgStr.includes('Nunito')) {
      svgStr = svgStr.replace('</style>', `
      @font-face {
        font-family: "Nunito";
        src: url("https://excalidraw.nyc3.cdn.digitaloceanspaces.com/oss/fonts/Nunito/Nunito-Regular-XRXI3I6Li01BKofiOc5wtlZ2di8HDIkhdTQ3j6zbXWjgeg.woff2");
      }
</style>`);
    }

    // Inject bound text before closing </svg>
    const boundTextSvg = generateBoundTextSvg(diagram.elements, computeViewBoxOrigin(diagram.elements));
    if (boundTextSvg) {
      svgStr = svgStr.replace('</svg>', boundTextSvg + '\n</svg>');
    }

    fs.writeFileSync(outputFile, svgStr);
    console.log(`Rendered: ${outputFile}`);
  })
  .catch((err) => {
    console.error('Render failed:', err);
    process.exit(1);
  });
