---
ask: "Investigate CSS style leakage from federated React components into Angular dashboard on dev deployment"
created: 2026-02-19
workstream: platform-development
session: 2026-02-19-b
sources:
  - type: slack
    description: "Dolly's testing feedback in #dev-squad (2026-02-19 06:55 EST) with 2 screenshots"
  - type: github
    description: "Compared local federation build output vs deployed assets on devplatform.indemn.ai"
  - type: github
    description: "Read vite.federation.config.ts, createShadowMount.tsx, build-federation.js, remoteEntry.js output"
---

# CSS Style Leakage Investigation

## Problem

Dolly reported React styles affecting the Angular dashboard on dev (devplatform.indemn.ai), likely from module federation style leakage. Screenshots showed visual artifacts in the Angular layout.

## Key Finding: Dual CSS Injection

The federation CSS is being loaded **twice** — once correctly (Shadow DOM) and once as a global leak (document head).

### Path 1: Shadow DOM (Correct)

```
build-federation.js (pass 1) → extracts style-*.css → generates styles.ts
build-federation.js (pass 2) → embeds styles.ts in bundle
createShadowMount.tsx → reads federationCSS from styles.ts
                      → creates shadow root → injects <style> into shadow root
```

This path works correctly. CSS is isolated inside each shadow root.

### Path 2: Global Head Injection (The Leak)

```
@originjs/vite-plugin-federation → generates remoteEntry.js
remoteEntry.js → dynamicLoadingCss(["style-*.css"], false, './ComponentName')
                                                    ^^^^^
                                    dontAppendStylesToHead = false
dynamicLoadingCss() → creates <link rel="stylesheet" href="...style-*.css">
                    → appends to document.head
```

This injects the full 130KB Tailwind/React CSS bundle into the Angular app's global scope. Tailwind's `.grid { display: grid }` overrides PrimeFlex's `.grid { display: flex }`, among other conflicts.

### Why It Looks Fine Locally

Locally, the duplicate styles don't visibly conflict on the pages tested (Overview tab). The Shadow DOM isolation works, and the global CSS happens to not trigger visible layout breaks on the specific components viewed. On dev, different caching, timing, or page navigation patterns surface the conflicts.

## Root Cause

The `@originjs/vite-plugin-federation` plugin hardcodes `dontAppendStylesToHead = false` in the generated `remoteEntry.js`. There is no plugin config option to change this. The second argument to `dynamicLoadingCss()` controls whether CSS is appended to `<head>` or stored in a `window['css__platformV2__' + name]` array.

### remoteEntry.js (both local and dev)

```js
// Each exposed module triggers global CSS injection
"./AgentOverview":()=>{
    dynamicLoadingCss(["style-Bly5be26.css"], false, './AgentOverview');
    // false = DO append to head (leaks globally)
    // true  = DON'T append to head (store in window array)
    ...
}
```

### dynamicLoadingCss Implementation

```js
const dynamicLoadingCss = (cssFilePaths, dontAppendStylesToHead, exposeItemName) => {
    // ...
    if (dontAppendStylesToHead) {
        // Store URL in window array — no global injection
        const key = 'css__platformV2__' + exposeItemName;
        window[key] = window[key] || [];
        window[key].push(href);
        return;
    }
    // Falls through to creating a <link> in document.head — LEAKS
    const element = document.createElement('link');
    element.rel = 'stylesheet';
    element.href = href;
    document.head.appendChild(element);
};
```

## Fix: Patch remoteEntry.js in Build Script

The `scripts/build-federation.js` already does a two-pass build with post-processing (CSS extraction → styles.ts generation). Add a third step after the second pass:

**Patch `remoteEntry.js`** to replace `false` with `true` in all `dynamicLoadingCss` calls:

```js
// In build-federation.js, after phase 2 build:
const remoteEntryPath = path.join(distDir, 'assets/remoteEntry.js');
let remoteEntry = fs.readFileSync(remoteEntryPath, 'utf-8');
remoteEntry = remoteEntry.replace(
    /dynamicLoadingCss\(\[([^\]]+)\],\s*false,/g,
    'dynamicLoadingCss([$1], true,'
);
fs.writeFileSync(remoteEntryPath, remoteEntry);
```

This is safe because:
1. CSS delivery is already handled by `createShadowMount` reading from `styles.ts`
2. The global `<link>` injection is purely redundant
3. The build script already does custom post-processing of build output
4. Setting `true` stores URLs in `window['css__platformV2__*']` — harmless, and could be useful as a fallback later

## Verification Checklist

After the fix:
- [ ] `remoteEntry.js` contains `dynamicLoadingCss([...], true, ...)` (not `false`)
- [ ] No `<link>` tag for `style-*.css` in document `<head>` when federation loads
- [ ] CSS exists only inside shadow roots (`#container > shadow-root > style`)
- [ ] Angular layout (sidebar, header, nav) renders correctly
- [ ] React federated components (Overview, Evaluations, Jarvis) render correctly
- [ ] PrimeFlex `.grid` still uses `display: flex` in Angular context
- [ ] Tailwind `.grid` uses `display: grid` only inside shadow roots

## Additional Findings

### Dev Deployment Is Stale
- CI/CD runner for `copilot-dashboard-react` (platform-v2) has been stuck/cancelled since Feb 11
- All recent runs show "cancelled" with 24h timeouts — self-hosted runner appears broken
- User manually rebuilds containers on dev EC2
- The deployed `remoteEntry.js` last-modified is Feb 11 (8 days old at time of investigation)
- Chunk hashes differ between local and dev builds, confirming different code versions

### Loading Indicator Bug (Separate Issue)
- "Loading..." persists at bottom of AgentOverview tab — visible both locally and on dev
- This is a code bug, not deployment-specific (tracked in bead `jim`)
