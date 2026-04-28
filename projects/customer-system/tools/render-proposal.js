#!/usr/bin/env node
/**
 * Indemn Proposal Renderer
 *
 * Hydrates a Handlebars proposal template with structured JSON data and renders
 * it to PDF via headless Chrome (puppeteer-core, against the system Chrome).
 *
 * Designed to be the rendering step of the Artifact Generator pipeline:
 *   (Proposal entity + Phases + Touchpoints + Playbook → JSON via the associate)
 *     → render-proposal.js → styled PDF
 *
 * Inputs:
 *   --data <path>     JSON data file (see schema in skills/artifact-generator.md)
 *   --out  <path>     Output PDF path
 *   --html <path>     (optional) Also write the hydrated HTML to this path
 *   --template <path> (optional) Override default template.hbs path
 *
 * Usage:
 *   node tools/render-proposal.js \
 *     --data    artifacts/2026-04-27-alliance-proposal-v2.json \
 *     --out     artifacts/2026-04-27-alliance-proposal-v2.pdf  \
 *     --html    artifacts/2026-04-27-alliance-proposal-v2.html
 */

const fs = require("fs");
const path = require("path");
const Handlebars = require("handlebars");
const puppeteer = require("puppeteer-core");

// === macOS Chrome path. Update if running on Linux/Windows. ===
const CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

// === Argv parsing (no deps) ===
function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 2) {
    const k = argv[i].replace(/^--/, "");
    args[k] = argv[i + 1];
  }
  return args;
}

// === Handlebars helpers ===
Handlebars.registerHelper("eq", (a, b) => a === b);

// === Main ===
(async () => {
  const args = parseArgs(process.argv);
  if (!args.data || !args.out) {
    console.error("Usage: render-proposal.js --data <json> --out <pdf> [--html <html>] [--template <hbs>]");
    process.exit(1);
  }

  const projectRoot = path.resolve(__dirname, "..");
  const templatePath = args.template
    ? path.resolve(args.template)
    : path.join(projectRoot, "templates", "proposal", "template.hbs");
  const templateDir = path.dirname(templatePath);
  const partialPath = path.join(templateDir, "saas-agreement.partial.hbs");
  const cssPath = path.join(templateDir, "template.css");
  const logoPath = path.join(templateDir, "assets", "indemn-logo-iris.png");

  // Read inputs
  const data = JSON.parse(fs.readFileSync(path.resolve(args.data), "utf8"));
  const templateSrc = fs.readFileSync(templatePath, "utf8");
  const partialSrc = fs.readFileSync(partialPath, "utf8");

  // Register partial
  Handlebars.registerPartial("saas_agreement", partialSrc);

  // Compile + render
  const template = Handlebars.compile(templateSrc, { noEscape: false });
  const html = template(data);

  // Write hydrated HTML alongside the template so its relative paths
  // (template.css, assets/Barlow-*.ttf) resolve when Chrome loads it.
  const tempHtmlPath = path.join(templateDir, ".rendered.tmp.html");
  fs.writeFileSync(tempHtmlPath, html, "utf8");
  if (args.html) {
    fs.writeFileSync(path.resolve(args.html), html, "utf8");
  }

  // Footer template — SVG swoosh + WHITE Indemn logo + page number.
  // Swoosh shape (matches Cam's Alliance / Branch / Charley / Johnson / GIC / Physicians Mutual portfolio):
  //   - Smooth ROUNDED LEFT edge (half-pill curve)
  //   - Flat top edge running across to the right
  //   - BLEEDS off the right edge of the page
  //   - BLEEDS off the bottom edge
  // Logo: rendered WHITE (CSS filter inverts the iris source) — sits ON the swoosh on the right.
  // Page number: dark eggplant, in white space LEFT of the swoosh.
  const logoB64 = fs.readFileSync(logoPath).toString("base64");
  const footerTemplate = `
    <style>
      .footer {
        font-family: "Barlow", -apple-system, system-ui, sans-serif;
        font-size: 9pt;
        font-weight: 700;
        color: #1e2553;
        width: 100%;
        height: 1.0in;
        position: relative;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      .footer .swoosh-wrap {
        position: absolute;
        left: 0; right: 0; bottom: 0;
        height: 1.0in;
      }
      .footer .swoosh-wrap svg {
        display: block;
        width: 100%;
        height: 100%;
      }
      /* Logo sits ON the swoosh, white via filter (inverts iris-on-white source to white-on-anything) */
      .footer img.logo {
        position: absolute;
        bottom: 0.20in;
        right: 0.55in;
        height: 0.40in;
        filter: brightness(0) invert(1);
      }
      .footer .page-num {
        position: absolute;
        bottom: 0.30in;
        left: 0.65in;
        font-size: 10pt;
        font-weight: 700;
        color: #1e2553;
        font-variant-numeric: tabular-nums;
      }
    </style>
    <div class="footer">
      <div class="swoosh-wrap">
        <svg viewBox="0 0 1000 100" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="swooshGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#c8a8d6"/>
              <stop offset="100%" stop-color="#4752a3"/>
            </linearGradient>
          </defs>
          <!-- Cam's swoosh shape: ONLY top-left corner rounded.
               Left edge runs STRAIGHT down to sharp 90° bottom-left corner.
               Flat top, bleeds RIGHT and BOTTOM.
               viewBox 1000x100. preserveAspectRatio=none stretches to fit footer area. -->
          <path d="M 1000,100 L 1000,15 L 380,15 Q 290,15 290,55 L 290,100 Z"
                fill="url(#swooshGradient)" />
        </svg>
      </div>
      <img class="logo" src="data:image/png;base64,${logoB64}" />
      <span class="page-num"><span class="pageNumber"></span></span>
    </div>
  `;
  // Empty header (puppeteer requires both when displayHeaderFooter is true)
  const headerTemplate = `<div></div>`;

  // Launch Chrome
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: "new",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });

  try {
    const page = await browser.newPage();
    const fileUrl = "file://" + tempHtmlPath;
    await page.goto(fileUrl, { waitUntil: "networkidle0" });

    await page.pdf({
      path: path.resolve(args.out),
      format: "Letter",
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate,
      footerTemplate,
      // Page margins. Bottom margin reserves space for the swoosh footer (which
      // bleeds off the bottom and right edges, sized to ~1.0in tall).
      margin: {
        top: "0.95in",
        bottom: "1.0in",
        left: "0.95in",
        right: "0.95in",
      },
    });

    console.log(`Wrote ${path.resolve(args.out)}`);
  } finally {
    await browser.close();
    // Clean up the temp render
    try { fs.unlinkSync(tempHtmlPath); } catch (_) {}
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
