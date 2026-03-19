# Product Showcase System — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a product showcase system on blog.indemn.ai that produces polished, landing-page-quality product pages — the first being the Indemn CLI & MCP Server.

**Architecture:** New Astro content collection (`products`) with reusable showcase components. Each product page is an MDX file with structured frontmatter (title, tagline, stats, features, demo tabs, FAQ, CTA) rendered by a `ShowcaseLayout`. The layout produces full-width, scroll-driven hero and demo sections with denser information sections below. Brand design follows the official Indemn brand guide (Iris/Lilac/Eggplant palette, Barlow font, logo-derived flourishes).

**Tech Stack:** Astro 5.17.1, MDX, vanilla CSS (no new dependencies), vanilla JS for interactive components (tabs, FAQ accordion). Deployed to blog.indemn.ai via Vercel.

**Working directory:** `/Users/home/Repositories/content-system/sites/indemn-blog/`

**Brand guide reference:** `/Users/home/Repositories/indemn-platform-v2/docs/brand/brand_design.pdf`

**Brand assets source:** `/Users/home/Repositories/indemn-platform-v2/docs/brand/Indemn Brand Assets/SVG/`

**Brainstorm decisions (in Hive):** 10 decisions captured on 2026-03-18 covering location, design, tabs, interactivity, messaging, brand, skill, roadmap.

---

## Task 1: Brand Assets and Showcase CSS Foundation

**Files:**
- Copy: SVG brand assets → `public/brand/`
- Modify: `src/styles/global.css` (append showcase tokens + styles)
- Modify: `src/consts.ts` (add product-related constants)

**Step 1: Copy brand SVG assets to the blog**

Copy these SVGs from the platform-v2 brand assets to the blog's `public/brand/` directory:

```bash
cd /Users/home/Repositories/content-system/sites/indemn-blog

# Flourishes
cp "/Users/home/Repositories/indemn-platform-v2/docs/brand/Indemn Brand Assets/SVG/04_Flourishes/01_Bubble/01_Solid/Indemn_BubbleFlourish_Gradient_LilacIris.svg" public/brand/flourish-bubble-gradient.svg
cp "/Users/home/Repositories/indemn-platform-v2/docs/brand/Indemn Brand Assets/SVG/04_Flourishes/02_Leaf/01_Solid/Indemn_LeafFlourish_Gradient_LilacIris.svg" public/brand/flourish-leaf-gradient.svg
cp "/Users/home/Repositories/indemn-platform-v2/docs/brand/Indemn Brand Assets/SVG/04_Flourishes/01_Bubble/02_Outline/Indemn_BubbleFlourish_Outline_Iris.svg" public/brand/flourish-bubble-outline.svg

# Patterns
cp "/Users/home/Repositories/indemn-platform-v2/docs/brand/Indemn Brand Assets/SVG/05_Patterns/02_Partial/Indemn_PartialPattern_Gradient_LilacIris.svg" public/brand/pattern-partial-gradient.svg

# Marks
cp "/Users/home/Repositories/indemn-platform-v2/docs/brand/Indemn Brand Assets/SVG/03_Mark/01_Bubble/Indemn_BubbleMark_White.svg" public/brand/mark-bubble-white.svg
cp "/Users/home/Repositories/indemn-platform-v2/docs/brand/Indemn Brand Assets/SVG/03_Mark/01_Bubble/Indemn_BubbleMark_Iris.svg" public/brand/mark-bubble-iris.svg
```

**Step 2: Append showcase CSS tokens and component styles to `src/styles/global.css`**

Add the following after the existing `:root` block's closing brace (after line 48):

```css
/* ============================================
   PRODUCT SHOWCASE STYLES
   Brand guide: brand_design.pdf
   ============================================ */

:root {
	/* Brand — extended palette */
	--color-olive: #2a2b1a;

	/* Brand gradients */
	--gradient-lilac-iris: linear-gradient(135deg, #a67cb7 0%, #4752a3 100%);
	--gradient-lilac-eggplant: linear-gradient(135deg, #a67cb7 0%, #1e2553 100%);
	--gradient-iris-eggplant: linear-gradient(135deg, #4752a3 0%, #1e2553 100%);
	--gradient-olive-lime: linear-gradient(135deg, #2a2b1a 0%, #e0da67 100%);

	/* Showcase-specific tokens */
	--showcase-max-width: 1200px;
	--showcase-section-padding: 5rem 2rem;
	--showcase-section-padding-mobile: 3rem 1.25rem;
}

/* Showcase page — override blog's constrained main */
.showcase-page main {
	max-width: none;
	padding: 0;
}

/* Showcase sections — full width with inner container */
.showcase-section {
	width: 100%;
	padding: var(--showcase-section-padding);
}

.showcase-section .section-inner {
	max-width: var(--showcase-max-width);
	margin: 0 auto;
}

/* Alternate section backgrounds */
.showcase-section.alt-bg {
	background-color: var(--color-surface-2);
}

.showcase-section.dark-bg {
	background: var(--gradient-iris-eggplant);
	color: #ffffff;
}

.showcase-section.dark-bg h2,
.showcase-section.dark-bg h3 {
	color: #ffffff;
}

.showcase-section.dark-bg p {
	color: rgba(255, 255, 255, 0.85);
}

/* Section titles — consistent across showcase */
.showcase-section-title {
	font-size: 2rem;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.02em;
	margin-bottom: 1rem;
}

.showcase-section-subtitle {
	font-size: 1.125rem;
	font-weight: 500;
	color: var(--color-muted);
	margin-bottom: 2.5rem;
	max-width: 640px;
}

/* Buttons — showcase style */
.btn-primary {
	display: inline-flex;
	align-items: center;
	gap: 0.5rem;
	padding: 0.875rem 2rem;
	background: var(--color-iris);
	color: #ffffff;
	font-family: "Barlow", system-ui, sans-serif;
	font-size: 1rem;
	font-weight: 600;
	border: none;
	border-radius: var(--radius-lg);
	cursor: pointer;
	transition: background-color 150ms ease, transform 100ms ease;
	text-decoration: none;
}

.btn-primary:hover {
	background: var(--color-accent-hover);
	color: #ffffff;
	transform: translateY(-1px);
}

.btn-secondary {
	display: inline-flex;
	align-items: center;
	gap: 0.5rem;
	padding: 0.875rem 2rem;
	background: transparent;
	color: var(--color-iris);
	font-family: "Barlow", system-ui, sans-serif;
	font-size: 1rem;
	font-weight: 600;
	border: 2px solid var(--color-iris);
	border-radius: var(--radius-lg);
	cursor: pointer;
	transition: background-color 150ms ease, color 150ms ease;
	text-decoration: none;
}

.btn-secondary:hover {
	background: var(--color-iris);
	color: #ffffff;
}

/* Fade-in animation for scroll */
.fade-in {
	opacity: 0;
	transform: translateY(20px);
	transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.fade-in.visible {
	opacity: 1;
	transform: translateY(0);
}

@media (max-width: 640px) {
	.showcase-section {
		padding: var(--showcase-section-padding-mobile);
	}
	.showcase-section-title {
		font-size: 1.5rem;
	}
}
```

**Step 3: Add product constants to `src/consts.ts`**

Append to the existing file:

```typescript
export const PRODUCTS_TITLE = 'Products — Indemn';
export const PRODUCTS_DESCRIPTION = 'The tools and systems powering frontier AI for insurance. Explore our product catalog.';
```

**Step 4: Verify build**

```bash
cd /Users/home/Repositories/content-system/sites/indemn-blog && npm run build
```

Expected: Clean build, no errors.

**Step 5: Commit**

```bash
git add public/brand/ src/styles/global.css src/consts.ts
git commit -m "feat(showcase): add brand assets and showcase CSS foundation"
```

---

## Task 2: Products Content Collection and Schema

**Files:**
- Modify: `src/content.config.ts`
- Create: `src/content/products/` directory

**Step 1: Update content.config.ts to add products collection**

Replace the entire file:

```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string(),
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: image().optional(),
			author: z.object({
				name: z.string(),
				title: z.string().optional(),
				linkedin: z.string().optional(),
				email: z.string().optional(),
			}).optional(),
		}),
});

const products = defineCollection({
	loader: glob({ base: './src/content/products', pattern: '**/*.{md,mdx}' }),
	schema: ({ image }) =>
		z.object({
			// Core
			title: z.string(),
			tagline: z.string(),
			description: z.string(),
			category: z.string(),
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: image().optional(),

			// Stats banner
			stats: z.array(z.object({
				value: z.string(),
				label: z.string(),
			})).optional(),

			// Feature grid
			features: z.array(z.object({
				title: z.string(),
				description: z.string(),
				icon: z.string().optional(),
			})).optional(),

			// Tabbed demo
			demoTabs: z.array(z.object({
				label: z.string(),
				type: z.enum(['video', 'image', 'placeholder']),
				src: z.string().optional(),
				alt: z.string().optional(),
				caption: z.string().optional(),
			})).optional(),

			// Setup walkthrough
			walkthrough: z.object({
				install: z.object({
					command: z.string(),
					description: z.string().optional(),
				}).optional(),
				platforms: z.array(z.object({
					name: z.string(),
					steps: z.array(z.object({
						title: z.string(),
						description: z.string(),
						code: z.string().optional(),
					})),
				})).optional(),
			}).optional(),

			// FAQ
			faq: z.array(z.object({
				question: z.string(),
				answer: z.string(),
			})).optional(),

			// CTA
			cta: z.object({
				headline: z.string().optional(),
				description: z.string().optional(),
				primary: z.object({
					text: z.string(),
					href: z.string(),
				}),
				secondary: z.object({
					text: z.string(),
					href: z.string(),
				}).optional(),
			}).optional(),
		}),
});

export const collections = { blog, products };
```

**Step 2: Create products content directory**

```bash
mkdir -p src/content/products
```

**Step 3: Verify build**

```bash
npm run build
```

Expected: Clean build. The products collection exists but has no entries yet.

**Step 4: Commit**

```bash
git add src/content.config.ts src/content/products/
git commit -m "feat(showcase): add products content collection with schema"
```

---

## Task 3: ShowcaseLayout and Page Routing

**Files:**
- Create: `src/layouts/ShowcaseLayout.astro`
- Create: `src/pages/products/index.astro`
- Create: `src/pages/products/[...slug].astro`

**Step 1: Create ShowcaseLayout.astro**

```astro
---
import BaseHead from '../components/BaseHead.astro';
import Header from '../components/Header.astro';
import Footer from '../components/Footer.astro';
import type { ImageMetadata } from 'astro';

interface Props {
	title: string;
	tagline: string;
	description: string;
	image?: ImageMetadata;
	faq?: Array<{ question: string; answer: string }>;
}

const { title, tagline, description, image, faq } = Astro.props;
---

<!doctype html>
<html lang="en" class="showcase-page">
	<head>
		<BaseHead title={`${title} — Indemn`} description={description} image={image} />
		{faq && faq.length > 0 && (
			<script type="application/ld+json" set:html={JSON.stringify({
				"@context": "https://schema.org",
				"@type": "FAQPage",
				"mainEntity": faq.map(item => ({
					"@type": "Question",
					"name": item.question,
					"acceptedAnswer": {
						"@type": "Answer",
						"text": item.answer,
					}
				}))
			})} />
		)}
	</head>
	<body>
		<Header />
		<main>
			<slot />
		</main>
		<Footer />
		<script>
			// Scroll-driven fade-in animation
			const observer = new IntersectionObserver((entries) => {
				entries.forEach(entry => {
					if (entry.isIntersecting) {
						entry.target.classList.add('visible');
					}
				});
			}, { threshold: 0.1 });

			document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
		</script>
	</body>
</html>
```

**Step 2: Create the products index page at `src/pages/products/index.astro`**

```astro
---
import BaseHead from '../../components/BaseHead.astro';
import Header from '../../components/Header.astro';
import Footer from '../../components/Footer.astro';
import { getCollection } from 'astro:content';
import { PRODUCTS_TITLE, PRODUCTS_DESCRIPTION } from '../../consts';

const products = (await getCollection('products')).sort(
	(a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
);
---

<!doctype html>
<html lang="en" class="showcase-page">
	<head>
		<BaseHead title={PRODUCTS_TITLE} description={PRODUCTS_DESCRIPTION} />
	</head>
	<body>
		<Header />
		<main>
			<!-- Hero -->
			<section class="catalog-hero">
				<div class="catalog-hero-inner">
					<img src="/brand/mark-bubble-iris.svg" alt="" class="catalog-mark" />
					<h1>Our Products</h1>
					<p>The tools and systems powering frontier AI for insurance.</p>
				</div>
			</section>

			<!-- Product Grid -->
			<section class="showcase-section">
				<div class="section-inner">
					{products.length === 0 ? (
						<p class="catalog-empty">Product showcases coming soon.</p>
					) : (
						<div class="product-grid">
							{products.map(product => (
								<a href={`/products/${product.id}/`} class="product-card">
									<span class="product-category">{product.data.category}</span>
									<h2 class="product-card-title">{product.data.title}</h2>
									<p class="product-card-tagline">{product.data.tagline}</p>
									<p class="product-card-description">{product.data.description}</p>
									<span class="product-card-link">View showcase &rarr;</span>
								</a>
							))}
						</div>
					)}
				</div>
			</section>
		</main>
		<Footer />
	</body>
</html>

<style>
	.catalog-hero {
		background: var(--gradient-iris-eggplant);
		padding: 6rem 2rem 4rem;
		text-align: center;
		color: #ffffff;
	}
	.catalog-hero-inner {
		max-width: var(--showcase-max-width);
		margin: 0 auto;
	}
	.catalog-mark {
		width: 64px;
		height: 64px;
		margin-bottom: 1.5rem;
	}
	.catalog-hero h1 {
		font-size: 3rem;
		font-weight: 700;
		text-transform: uppercase;
		color: #ffffff;
		margin-bottom: 0.75rem;
	}
	.catalog-hero p {
		font-size: 1.25rem;
		font-weight: 300;
		color: rgba(255, 255, 255, 0.85);
	}
	.catalog-empty {
		text-align: center;
		color: var(--color-muted);
		padding: 4rem 0;
	}
	.product-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
		gap: 1.5rem;
	}
	.product-card {
		display: flex;
		flex-direction: column;
		padding: 2rem;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		text-decoration: none;
		color: var(--color-foreground);
		transition: border-color 200ms ease, box-shadow 200ms ease, transform 200ms ease;
	}
	.product-card:hover {
		border-color: var(--color-iris);
		box-shadow: var(--shadow-lg);
		transform: translateY(-2px);
		color: var(--color-foreground);
	}
	.product-category {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--color-iris);
		margin-bottom: 0.75rem;
	}
	.product-card-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-eggplant);
		margin-bottom: 0.25rem;
	}
	.product-card-tagline {
		font-size: 1rem;
		font-weight: 500;
		color: var(--color-accent-secondary);
		margin-bottom: 0.75rem;
	}
	.product-card-description {
		font-size: 0.95rem;
		color: var(--color-muted);
		flex-grow: 1;
	}
	.product-card-link {
		font-size: 0.9rem;
		font-weight: 600;
		color: var(--color-iris);
		margin-top: 1rem;
	}

	@media (max-width: 640px) {
		.catalog-hero { padding: 4rem 1.25rem 3rem; }
		.catalog-hero h1 { font-size: 2rem; }
		.product-grid { grid-template-columns: 1fr; }
	}
</style>
```

**Step 3: Create the dynamic product page at `src/pages/products/[...slug].astro`**

```astro
---
import { type CollectionEntry, getCollection } from 'astro:content';
import ShowcaseLayout from '../../layouts/ShowcaseLayout.astro';
import ShowcaseHero from '../../components/showcase/ShowcaseHero.astro';
import FeatureGrid from '../../components/showcase/FeatureGrid.astro';
import TabbedDemo from '../../components/showcase/TabbedDemo.astro';
import StatsBanner from '../../components/showcase/StatsBanner.astro';
import SetupWalkthrough from '../../components/showcase/SetupWalkthrough.astro';
import FAQ from '../../components/showcase/FAQ.astro';
import ShowcaseCTA from '../../components/showcase/ShowcaseCTA.astro';

type Props = CollectionEntry<'products'>;

export async function getStaticPaths() {
	const products = await getCollection('products');
	return products.map((product) => ({
		params: { slug: product.id },
		props: product,
	}));
}

const product = Astro.props;
const { data } = product;
const { Content } = await product.render();
---

<ShowcaseLayout
	title={data.title}
	tagline={data.tagline}
	description={data.description}
	faq={data.faq}
>
	<ShowcaseHero title={data.title} tagline={data.tagline} category={data.category} />

	<!-- Problem / Story section — rendered from MDX body -->
	{Content && (
		<section class="showcase-section">
			<div class="section-inner showcase-prose">
				<Content />
			</div>
		</section>
	)}

	{data.features && data.features.length > 0 && (
		<FeatureGrid features={data.features} />
	)}

	{data.demoTabs && data.demoTabs.length > 0 && (
		<TabbedDemo tabs={data.demoTabs} />
	)}

	{data.stats && data.stats.length > 0 && (
		<StatsBanner stats={data.stats} />
	)}

	{data.walkthrough && (
		<SetupWalkthrough walkthrough={data.walkthrough} />
	)}

	{data.faq && data.faq.length > 0 && (
		<FAQ items={data.faq} />
	)}

	{data.cta && (
		<ShowcaseCTA cta={data.cta} />
	)}
</ShowcaseLayout>

<style>
	.showcase-prose {
		max-width: 800px;
	}
	.showcase-prose :global(h2) {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--color-eggplant);
		margin-bottom: 1rem;
	}
	.showcase-prose :global(p) {
		font-size: 1.125rem;
		font-weight: 300;
		line-height: 1.7;
		color: var(--color-foreground);
		margin-bottom: 1.25rem;
	}
	.showcase-prose :global(strong) {
		font-weight: 600;
		color: var(--color-eggplant);
	}
</style>
```

**Step 4: Create the showcase components directory**

```bash
mkdir -p src/components/showcase
```

Create placeholder components so the build doesn't break. Each will be replaced in subsequent tasks.

Create `src/components/showcase/ShowcaseHero.astro`:
```astro
---
interface Props { title: string; tagline: string; category: string; }
const { title, tagline, category } = Astro.props;
---
<section class="showcase-section"><div class="section-inner"><p>{category}</p><h1>{title}</h1><p>{tagline}</p></div></section>
```

Create identical placeholder stubs for each component:

`src/components/showcase/FeatureGrid.astro`:
```astro
---
const { features } = Astro.props;
---
<section class="showcase-section"><div class="section-inner"><p>Features: {features.length}</p></div></section>
```

`src/components/showcase/TabbedDemo.astro`:
```astro
---
const { tabs } = Astro.props;
---
<section class="showcase-section"><div class="section-inner"><p>Demo: {tabs.length} tabs</p></div></section>
```

`src/components/showcase/StatsBanner.astro`:
```astro
---
const { stats } = Astro.props;
---
<section class="showcase-section"><div class="section-inner"><p>Stats: {stats.length}</p></div></section>
```

`src/components/showcase/SetupWalkthrough.astro`:
```astro
---
const { walkthrough } = Astro.props;
---
<section class="showcase-section"><div class="section-inner"><p>Walkthrough</p></div></section>
```

`src/components/showcase/FAQ.astro`:
```astro
---
const { items } = Astro.props;
---
<section class="showcase-section"><div class="section-inner"><p>FAQ: {items.length} questions</p></div></section>
```

`src/components/showcase/ShowcaseCTA.astro`:
```astro
---
const { cta } = Astro.props;
---
<section class="showcase-section"><div class="section-inner"><p>CTA: {cta.primary.text}</p></div></section>
```

**Step 5: Verify build**

```bash
npm run build
```

Expected: Build passes. No products exist yet so no pages are generated, but the routing and layout are ready.

**Step 6: Commit**

```bash
git add src/layouts/ShowcaseLayout.astro src/pages/products/ src/components/showcase/
git commit -m "feat(showcase): add layout, routing, and placeholder components"
```

---

## Task 4: ShowcaseHero Component

**Files:**
- Modify: `src/components/showcase/ShowcaseHero.astro`

**Step 1: Replace the placeholder with the full hero component**

```astro
---
interface Props {
	title: string;
	tagline: string;
	category: string;
}

const { title, tagline, category } = Astro.props;
---

<section class="hero">
	<div class="hero-bg">
		<img src="/brand/flourish-bubble-gradient.svg" alt="" class="hero-flourish hero-flourish-1" />
		<img src="/brand/flourish-bubble-outline.svg" alt="" class="hero-flourish hero-flourish-2" />
	</div>
	<div class="hero-content">
		<span class="hero-category">{category}</span>
		<h1 class="hero-title">{title}</h1>
		<p class="hero-tagline">{tagline}</p>
	</div>
</section>

<style>
	.hero {
		position: relative;
		min-height: 70vh;
		display: flex;
		align-items: center;
		justify-content: center;
		text-align: center;
		background: var(--gradient-iris-eggplant);
		overflow: hidden;
		padding: 6rem 2rem;
	}

	.hero-bg {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}

	.hero-flourish {
		position: absolute;
		opacity: 0.08;
	}

	.hero-flourish-1 {
		width: 500px;
		height: 500px;
		top: -120px;
		right: -100px;
	}

	.hero-flourish-2 {
		width: 300px;
		height: 300px;
		bottom: -60px;
		left: -60px;
	}

	.hero-content {
		position: relative;
		z-index: 1;
		max-width: 800px;
	}

	.hero-category {
		display: inline-block;
		font-size: 0.8rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--color-lime);
		background: rgba(224, 218, 103, 0.15);
		padding: 0.375rem 1rem;
		border-radius: 100px;
		margin-bottom: 1.5rem;
	}

	.hero-title {
		font-size: 3.5rem;
		font-weight: 700;
		color: #ffffff;
		line-height: 1.15;
		margin-bottom: 1.25rem;
	}

	.hero-tagline {
		font-size: 1.375rem;
		font-weight: 300;
		color: rgba(255, 255, 255, 0.85);
		line-height: 1.5;
		max-width: 600px;
		margin: 0 auto;
	}

	@media (max-width: 640px) {
		.hero {
			min-height: 50vh;
			padding: 4rem 1.25rem;
		}
		.hero-title {
			font-size: 2.25rem;
		}
		.hero-tagline {
			font-size: 1.125rem;
		}
		.hero-flourish-1 {
			width: 300px;
			height: 300px;
		}
		.hero-flourish-2 {
			width: 180px;
			height: 180px;
		}
	}
</style>
```

**Step 2: Verify build**

```bash
npm run build
```

**Step 3: Commit**

```bash
git add src/components/showcase/ShowcaseHero.astro
git commit -m "feat(showcase): implement ShowcaseHero with brand gradients and flourishes"
```

---

## Task 5: FeatureGrid and StatsBanner Components

**Files:**
- Modify: `src/components/showcase/FeatureGrid.astro`
- Modify: `src/components/showcase/StatsBanner.astro`

**Step 1: Replace FeatureGrid placeholder**

```astro
---
interface Feature {
	title: string;
	description: string;
	icon?: string;
}

interface Props {
	features: Feature[];
}

const { features } = Astro.props;
---

<section class="showcase-section alt-bg fade-in">
	<div class="section-inner">
		<h2 class="showcase-section-title">How It Works</h2>
		<div class="feature-grid">
			{features.map((feature, i) => (
				<div class="feature-card">
					<div class="feature-number">{String(i + 1).padStart(2, '0')}</div>
					<h3 class="feature-title">{feature.title}</h3>
					<p class="feature-description">{feature.description}</p>
				</div>
			))}
		</div>
	</div>
</section>

<style>
	.feature-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
		gap: 1.5rem;
	}

	.feature-card {
		padding: 2rem;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		transition: border-color 200ms ease, box-shadow 200ms ease;
	}

	.feature-card:hover {
		border-color: var(--color-iris);
		box-shadow: var(--shadow-md);
	}

	.feature-number {
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-lilac);
		margin-bottom: 0.75rem;
		line-height: 1;
	}

	.feature-title {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-eggplant);
		margin-bottom: 0.5rem;
		border-left: 3px solid var(--color-iris);
		padding-left: 0.75rem;
	}

	.feature-description {
		font-size: 0.95rem;
		font-weight: 300;
		color: var(--color-muted);
		line-height: 1.6;
	}

	@media (max-width: 640px) {
		.feature-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
```

**Step 2: Replace StatsBanner placeholder**

```astro
---
interface Stat {
	value: string;
	label: string;
}

interface Props {
	stats: Stat[];
}

const { stats } = Astro.props;
---

<section class="stats-banner fade-in">
	<div class="stats-inner">
		{stats.map((stat) => (
			<div class="stat-item">
				<span class="stat-value">{stat.value}</span>
				<span class="stat-label">{stat.label}</span>
			</div>
		))}
	</div>
</section>

<style>
	.stats-banner {
		background: var(--gradient-lilac-iris);
		padding: 3.5rem 2rem;
	}

	.stats-inner {
		max-width: var(--showcase-max-width);
		margin: 0 auto;
		display: flex;
		justify-content: center;
		gap: 4rem;
		flex-wrap: wrap;
	}

	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
	}

	.stat-value {
		font-size: 3rem;
		font-weight: 700;
		color: #ffffff;
		line-height: 1.1;
	}

	.stat-label {
		font-size: 0.9rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.8);
		text-transform: uppercase;
		letter-spacing: 0.06em;
		margin-top: 0.25rem;
	}

	@media (max-width: 640px) {
		.stats-inner {
			gap: 2rem;
		}
		.stat-value {
			font-size: 2.25rem;
		}
	}
</style>
```

**Step 3: Verify build, then commit**

```bash
npm run build
git add src/components/showcase/FeatureGrid.astro src/components/showcase/StatsBanner.astro
git commit -m "feat(showcase): implement FeatureGrid and StatsBanner components"
```

---

## Task 6: TabbedDemo Component

**Files:**
- Modify: `src/components/showcase/TabbedDemo.astro`

This is the most interactive component. It uses a `<script>` tag for vanilla JS tab switching.

**Step 1: Replace TabbedDemo placeholder**

```astro
---
interface Tab {
	label: string;
	type: 'video' | 'image' | 'placeholder';
	src?: string;
	alt?: string;
	caption?: string;
}

interface Props {
	tabs: Tab[];
}

const { tabs } = Astro.props;
---

<section class="showcase-section fade-in" id="demo">
	<div class="section-inner">
		<h2 class="showcase-section-title">See It In Action</h2>
		<p class="showcase-section-subtitle">One platform, accessible from every AI assistant you already use.</p>

		<div class="demo-container">
			<div class="demo-tabs" role="tablist">
				{tabs.map((tab, i) => (
					<button
						role="tab"
						class={`demo-tab ${i === 0 ? 'active' : ''}`}
						aria-selected={i === 0 ? 'true' : 'false'}
						data-tab-index={i}
					>
						{tab.label}
					</button>
				))}
			</div>

			<div class="demo-panels">
				{tabs.map((tab, i) => (
					<div
						role="tabpanel"
						class={`demo-panel ${i === 0 ? 'active' : ''}`}
						data-panel-index={i}
					>
						{tab.type === 'video' && tab.src ? (
							<video controls preload="metadata" class="demo-media">
								<source src={tab.src} type="video/mp4" />
							</video>
						) : tab.type === 'image' && tab.src ? (
							<img src={tab.src} alt={tab.alt || tab.label} class="demo-media" />
						) : (
							<div class="demo-placeholder">
								<div class="demo-placeholder-icon">&#9654;</div>
								<p class="demo-placeholder-label">{tab.label} Demo</p>
								<p class="demo-placeholder-text">Recording coming soon</p>
							</div>
						)}
						{tab.caption && (
							<p class="demo-caption">{tab.caption}</p>
						)}
					</div>
				))}
			</div>
		</div>
	</div>
</section>

<script>
	document.addEventListener('DOMContentLoaded', () => {
		const tablist = document.querySelector('.demo-tabs');
		if (!tablist) return;

		tablist.addEventListener('click', (e) => {
			const button = (e.target as HTMLElement).closest('.demo-tab');
			if (!button) return;

			const index = button.getAttribute('data-tab-index');

			// Update tabs
			tablist.querySelectorAll('.demo-tab').forEach(tab => {
				tab.classList.remove('active');
				tab.setAttribute('aria-selected', 'false');
			});
			button.classList.add('active');
			button.setAttribute('aria-selected', 'true');

			// Update panels
			document.querySelectorAll('.demo-panel').forEach(panel => {
				panel.classList.remove('active');
			});
			const activePanel = document.querySelector(`.demo-panel[data-panel-index="${index}"]`);
			if (activePanel) activePanel.classList.add('active');
		});
	});
</script>

<style>
	.demo-container {
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		overflow: hidden;
		box-shadow: var(--shadow-lg);
	}

	.demo-tabs {
		display: flex;
		border-bottom: 1px solid var(--color-border);
		background: var(--color-surface-2);
		overflow-x: auto;
	}

	.demo-tab {
		padding: 1rem 1.5rem;
		font-family: "Barlow", system-ui, sans-serif;
		font-size: 0.95rem;
		font-weight: 500;
		color: var(--color-muted);
		background: none;
		border: none;
		border-bottom: 3px solid transparent;
		cursor: pointer;
		white-space: nowrap;
		transition: color 150ms ease, border-color 150ms ease;
	}

	.demo-tab:hover {
		color: var(--color-eggplant);
	}

	.demo-tab.active {
		color: var(--color-iris);
		border-bottom-color: var(--color-iris);
		font-weight: 600;
	}

	.demo-panels {
		min-height: 400px;
	}

	.demo-panel {
		display: none;
	}

	.demo-panel.active {
		display: block;
	}

	.demo-media {
		width: 100%;
		height: auto;
		display: block;
		border-radius: 0;
	}

	.demo-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
		background: var(--color-eggplant);
		color: #ffffff;
	}

	.demo-placeholder-icon {
		font-size: 3rem;
		opacity: 0.3;
		margin-bottom: 1rem;
	}

	.demo-placeholder-label {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 0.25rem;
	}

	.demo-placeholder-text {
		font-size: 0.9rem;
		font-weight: 300;
		opacity: 0.6;
	}

	.demo-caption {
		padding: 0.75rem 1.5rem;
		font-size: 0.875rem;
		color: var(--color-muted);
		border-top: 1px solid var(--color-border);
	}

	@media (max-width: 640px) {
		.demo-tab {
			padding: 0.75rem 1rem;
			font-size: 0.85rem;
		}
		.demo-panels {
			min-height: 250px;
		}
		.demo-placeholder {
			min-height: 250px;
		}
	}
</style>
```

**Step 2: Verify build, then commit**

```bash
npm run build
git add src/components/showcase/TabbedDemo.astro
git commit -m "feat(showcase): implement TabbedDemo with vanilla JS tab switching"
```

---

## Task 7: SetupWalkthrough Component

**Files:**
- Modify: `src/components/showcase/SetupWalkthrough.astro`

**Step 1: Replace SetupWalkthrough placeholder**

```astro
---
interface WalkthroughStep {
	title: string;
	description: string;
	code?: string;
}

interface Platform {
	name: string;
	steps: WalkthroughStep[];
}

interface Props {
	walkthrough: {
		install?: {
			command: string;
			description?: string;
		};
		platforms?: Platform[];
	};
}

const { walkthrough } = Astro.props;
---

<section class="showcase-section alt-bg fade-in" id="get-started">
	<div class="section-inner">
		<h2 class="showcase-section-title">Get Started</h2>

		{walkthrough.install && (
			<div class="install-block">
				{walkthrough.install.description && (
					<p class="install-description">{walkthrough.install.description}</p>
				)}
				<div class="install-command">
					<code>{walkthrough.install.command}</code>
					<button class="copy-btn" data-copy={walkthrough.install.command} aria-label="Copy to clipboard">
						Copy
					</button>
				</div>
			</div>
		)}

		{walkthrough.platforms && walkthrough.platforms.length > 0 && (
			<div class="platform-guides">
				<h3 class="platform-guides-title">Setup by Platform</h3>
				{walkthrough.platforms.map((platform) => (
					<details class="platform-guide">
						<summary class="platform-summary">
							<span class="platform-name">{platform.name}</span>
							<span class="platform-chevron">&#9662;</span>
						</summary>
						<div class="platform-steps">
							{platform.steps.map((step, i) => (
								<div class="walkthrough-step">
									<div class="step-number">{i + 1}</div>
									<div class="step-content">
										<h4 class="step-title">{step.title}</h4>
										<p class="step-description">{step.description}</p>
										{step.code && (
											<div class="step-code">
												<code>{step.code}</code>
												<button class="copy-btn" data-copy={step.code} aria-label="Copy to clipboard">
													Copy
												</button>
											</div>
										)}
									</div>
								</div>
							))}
						</div>
					</details>
				))}
			</div>
		)}
	</div>
</section>

<script>
	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll('.copy-btn').forEach(btn => {
			btn.addEventListener('click', async () => {
				const text = btn.getAttribute('data-copy');
				if (!text) return;
				await navigator.clipboard.writeText(text);
				const original = btn.textContent;
				btn.textContent = 'Copied!';
				setTimeout(() => { btn.textContent = original; }, 1500);
			});
		});
	});
</script>

<style>
	.install-block {
		margin-bottom: 3rem;
	}

	.install-description {
		font-size: 1.125rem;
		font-weight: 300;
		color: var(--color-muted);
		margin-bottom: 1rem;
	}

	.install-command,
	.step-code {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background: var(--color-eggplant);
		color: #ffffff;
		padding: 1rem 1.25rem;
		border-radius: var(--radius-md);
		font-family: "Courier New", monospace;
		font-size: 1rem;
	}

	.install-command code,
	.step-code code {
		flex-grow: 1;
		background: none;
		padding: 0;
		color: inherit;
		font-size: inherit;
	}

	.copy-btn {
		padding: 0.375rem 0.75rem;
		font-family: "Barlow", system-ui, sans-serif;
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--color-lime);
		background: rgba(224, 218, 103, 0.15);
		border: 1px solid rgba(224, 218, 103, 0.3);
		border-radius: var(--radius-sm);
		cursor: pointer;
		transition: background-color 150ms ease;
		white-space: nowrap;
	}

	.copy-btn:hover {
		background: rgba(224, 218, 103, 0.25);
	}

	.platform-guides-title {
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-eggplant);
		margin-bottom: 1rem;
	}

	.platform-guide {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		margin-bottom: 0.75rem;
		background: var(--color-surface-1);
		overflow: hidden;
	}

	.platform-summary {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.5rem;
		cursor: pointer;
		font-weight: 500;
		list-style: none;
	}

	.platform-summary::-webkit-details-marker {
		display: none;
	}

	.platform-name {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-eggplant);
	}

	.platform-chevron {
		color: var(--color-muted);
		transition: transform 200ms ease;
	}

	.platform-guide[open] .platform-chevron {
		transform: rotate(180deg);
	}

	.platform-steps {
		padding: 0 1.5rem 1.5rem;
		border-top: 1px solid var(--color-border-subtle);
	}

	.walkthrough-step {
		display: flex;
		gap: 1rem;
		padding: 1rem 0;
	}

	.walkthrough-step + .walkthrough-step {
		border-top: 1px solid var(--color-border-subtle);
	}

	.step-number {
		width: 28px;
		height: 28px;
		min-width: 28px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-iris);
		color: #ffffff;
		font-size: 0.8rem;
		font-weight: 700;
		border-radius: 50%;
		margin-top: 0.125rem;
	}

	.step-title {
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--color-eggplant);
		margin-bottom: 0.25rem;
	}

	.step-description {
		font-size: 0.9rem;
		font-weight: 300;
		color: var(--color-muted);
		margin-bottom: 0.5rem;
	}

	.step-code {
		font-size: 0.85rem;
		padding: 0.625rem 1rem;
	}

	@media (max-width: 640px) {
		.install-command,
		.step-code {
			flex-direction: column;
			align-items: stretch;
			gap: 0.5rem;
		}
		.copy-btn {
			align-self: flex-end;
		}
	}
</style>
```

**Step 2: Verify build, then commit**

```bash
npm run build
git add src/components/showcase/SetupWalkthrough.astro
git commit -m "feat(showcase): implement SetupWalkthrough with copy-to-clipboard"
```

---

## Task 8: FAQ Component with JSON-LD

**Files:**
- Modify: `src/components/showcase/FAQ.astro`

Note: JSON-LD structured data is already injected by ShowcaseLayout (Task 3). This component handles the visual accordion.

**Step 1: Replace FAQ placeholder**

```astro
---
interface FAQItem {
	question: string;
	answer: string;
}

interface Props {
	items: FAQItem[];
}

const { items } = Astro.props;
---

<section class="showcase-section fade-in" id="faq">
	<div class="section-inner">
		<h2 class="showcase-section-title">Frequently Asked Questions</h2>
		<div class="faq-list">
			{items.map((item) => (
				<details class="faq-item">
					<summary class="faq-question">
						<span>{item.question}</span>
						<span class="faq-chevron">+</span>
					</summary>
					<div class="faq-answer">
						<p>{item.answer}</p>
					</div>
				</details>
			))}
		</div>
	</div>
</section>

<script>
	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll('.faq-item').forEach(item => {
			item.addEventListener('toggle', () => {
				const chevron = item.querySelector('.faq-chevron');
				if (chevron) {
					chevron.textContent = (item as HTMLDetailsElement).open ? '\u2212' : '+';
				}
			});
		});
	});
</script>

<style>
	.faq-list {
		max-width: 800px;
	}

	.faq-item {
		border-bottom: 1px solid var(--color-border);
	}

	.faq-question {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem 0;
		cursor: pointer;
		font-size: 1.1rem;
		font-weight: 500;
		color: var(--color-eggplant);
		list-style: none;
	}

	.faq-question::-webkit-details-marker {
		display: none;
	}

	.faq-chevron {
		font-size: 1.5rem;
		font-weight: 300;
		color: var(--color-iris);
		min-width: 1.5rem;
		text-align: center;
	}

	.faq-answer {
		padding: 0 0 1.25rem;
	}

	.faq-answer p {
		font-size: 1rem;
		font-weight: 300;
		color: var(--color-muted);
		line-height: 1.7;
	}
</style>
```

**Step 2: Verify build, then commit**

```bash
npm run build
git add src/components/showcase/FAQ.astro
git commit -m "feat(showcase): implement FAQ accordion with toggle animation"
```

---

## Task 9: ShowcaseCTA Component

**Files:**
- Modify: `src/components/showcase/ShowcaseCTA.astro`

**Step 1: Replace CTA placeholder**

```astro
---
interface Props {
	cta: {
		headline?: string;
		description?: string;
		primary: { text: string; href: string };
		secondary?: { text: string; href: string };
	};
}

const { cta } = Astro.props;
---

<section class="cta-section">
	<div class="cta-bg">
		<img src="/brand/pattern-partial-gradient.svg" alt="" class="cta-pattern" />
	</div>
	<div class="cta-content">
		{cta.headline && <h2 class="cta-headline">{cta.headline}</h2>}
		{cta.description && <p class="cta-description">{cta.description}</p>}
		<div class="cta-buttons">
			<a href={cta.primary.href} class="btn-primary">{cta.primary.text}</a>
			{cta.secondary && (
				<a href={cta.secondary.href} class="btn-secondary cta-btn-secondary">{cta.secondary.text}</a>
			)}
		</div>
	</div>
</section>

<style>
	.cta-section {
		position: relative;
		background: var(--gradient-iris-eggplant);
		padding: 5rem 2rem;
		text-align: center;
		overflow: hidden;
	}

	.cta-bg {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}

	.cta-pattern {
		position: absolute;
		right: -100px;
		bottom: -100px;
		width: 400px;
		height: 400px;
		opacity: 0.06;
	}

	.cta-content {
		position: relative;
		z-index: 1;
		max-width: 640px;
		margin: 0 auto;
	}

	.cta-headline {
		font-size: 2.25rem;
		font-weight: 700;
		color: #ffffff;
		margin-bottom: 1rem;
	}

	.cta-description {
		font-size: 1.125rem;
		font-weight: 300;
		color: rgba(255, 255, 255, 0.85);
		margin-bottom: 2rem;
		line-height: 1.6;
	}

	.cta-buttons {
		display: flex;
		justify-content: center;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.cta-btn-secondary {
		color: #ffffff;
		border-color: rgba(255, 255, 255, 0.4);
	}

	.cta-btn-secondary:hover {
		background: rgba(255, 255, 255, 0.15);
		color: #ffffff;
		border-color: rgba(255, 255, 255, 0.6);
	}

	@media (max-width: 640px) {
		.cta-section { padding: 3rem 1.25rem; }
		.cta-headline { font-size: 1.75rem; }
		.cta-buttons { flex-direction: column; align-items: center; }
	}
</style>
```

**Step 2: Verify build, then commit**

```bash
npm run build
git add src/components/showcase/ShowcaseCTA.astro
git commit -m "feat(showcase): implement ShowcaseCTA with brand pattern decoration"
```

---

## Task 10: CLI Showcase Page Content

**Files:**
- Create: `src/content/products/indemn-cli.mdx`

This is the first actual product page. Frontmatter contains all structured data; the MDX body is the "problem/story" section.

**Step 1: Create the CLI showcase MDX file**

Create `src/content/products/indemn-cli.mdx`:

```mdx
---
title: "Indemn CLI & MCP Server"
tagline: "Build, configure, and improve AI agents from the tools you already use — Claude Code, Claude AI, ChatGPT, or Gemini."
description: "The full Indemn agent platform — create, configure, evaluate, and improve AI agents for insurance — accessible as CLI commands and MCP tools from any AI assistant."
category: "Developer Tools"
pubDate: 2026-03-18

stats:
  - value: "58"
    label: "MCP Tools"
  - value: "35+"
    label: "CLI Commands"
  - value: "< 2 min"
    label: "Setup Time"
  - value: "4"
    label: "AI Platforms"

features:
  - title: "Create Agents"
    description: "Spin up a new AI agent, configure its personality, connect knowledge bases, and define custom functions — all through natural language or CLI commands."
  - title: "Evaluate Quality"
    description: "Design test scenarios, build scoring rubrics, and run evaluations against your agents. Get quantified confidence before going live."
  - title: "Improve Autonomously"
    description: "Read evaluation results, identify failures, adjust configuration, and re-evaluate. The full improvement loop without leaving your AI assistant."
  - title: "Export & Report"
    description: "Generate branded PDF agent cards and evaluation reports. Share results with stakeholders in a format they can trust."

demoTabs:
  - label: "Claude Code"
    type: "placeholder"
    caption: "Full agent lifecycle — create, configure, evaluate, improve — in a single Claude Code session."
  - label: "Claude AI"
    type: "placeholder"
    caption: "MCP tools accessible directly in the Claude AI chat interface."
  - label: "ChatGPT"
    type: "placeholder"
    caption: "The same MCP server works in ChatGPT — platform independent."
  - label: "Gemini"
    type: "placeholder"
    caption: "Google Gemini support through the Model Context Protocol."

walkthrough:
  install:
    command: "npm install -g @indemn/cli"
    description: "One command. That's it."
  platforms:
    - name: "Claude Code"
      steps:
        - title: "Install the CLI"
          description: "The MCP server is bundled with the CLI package."
          code: "npm install -g @indemn/cli"
        - title: "Log in"
          description: "Authenticate with your Indemn account."
          code: "indemn login"
        - title: "Add to Claude Code"
          description: "Register the MCP server in your Claude Code configuration."
          code: "indemn mcp install"
        - title: "Start building"
          description: "Open Claude Code and ask it to create an agent. The MCP tools are automatically available."
    - name: "Claude AI (chat)"
      steps:
        - title: "Install the CLI"
          description: "Same package provides the MCP server."
          code: "npm install -g @indemn/cli"
        - title: "Log in"
          description: "Authenticate with your Indemn account."
          code: "indemn login"
        - title: "Connect to Claude AI"
          description: "Add the MCP server in Claude AI settings under 'Integrations'. Point it to the indemn binary."
        - title: "Start building"
          description: "Ask Claude to list your agents or create a new one. It will use the MCP tools automatically."
    - name: "ChatGPT"
      steps:
        - title: "Install the CLI"
          description: "The MCP server is compatible with any MCP-enabled client."
          code: "npm install -g @indemn/cli"
        - title: "Log in"
          description: "Authenticate with your Indemn account."
          code: "indemn login"
        - title: "Configure ChatGPT"
          description: "In ChatGPT settings, add a new MCP connection and point it to the indemn MCP server."
        - title: "Start building"
          description: "ChatGPT can now create and manage Indemn agents through natural conversation."
    - name: "Gemini"
      steps:
        - title: "Install the CLI"
          description: "Works with any AI assistant that supports MCP."
          code: "npm install -g @indemn/cli"
        - title: "Log in"
          description: "Authenticate with your Indemn account."
          code: "indemn login"
        - title: "Connect to Gemini"
          description: "Add the Indemn MCP server in your Gemini MCP configuration."
        - title: "Start building"
          description: "Gemini now has full access to the Indemn agent platform."

faq:
  - question: "How do I build an AI agent for insurance?"
    answer: "Indemn provides a complete platform for building conversational AI agents purpose-built for insurance workflows. With the Indemn CLI, you can create an agent, connect it to your knowledge base, define custom functions for quoting and binding, and deploy it across web chat, voice, and email — all from your terminal or AI assistant."
  - question: "What is an MCP server and how do I use one?"
    answer: "MCP (Model Context Protocol) is an open standard that lets AI assistants like Claude, ChatGPT, and Gemini connect to external tools and services. The Indemn MCP server exposes 58 tools that give your AI assistant the ability to create agents, manage knowledge bases, run evaluations, and more — all through natural conversation."
  - question: "Can I create AI agents with ChatGPT?"
    answer: "Yes. The Indemn MCP server works with any AI assistant that supports the Model Context Protocol, including ChatGPT, Claude (Code and AI), and Google Gemini. Install the CLI, authenticate, connect the MCP server to your preferred AI assistant, and start building agents through natural language."
  - question: "How do I automate insurance workflows with AI?"
    answer: "Indemn agents go beyond simple chatbots — they execute full insurance workflows including quoting, binding, claims intake, policy servicing, and customer support across web, voice, and email channels. The CLI lets you configure these workflows programmatically and test them through automated evaluations before deploying to production."
  - question: "What's the best tool for managing AI agents programmatically?"
    answer: "The Indemn CLI provides 35+ commands for the full agent lifecycle — create, configure, evaluate, improve, and export. Combined with the MCP server's 58 tools, it's the most comprehensive programmatic interface for building and managing insurance AI agents. Install with npm install -g @indemn/cli."
  - question: "Do I need coding experience to use the Indemn CLI?"
    answer: "No. While the CLI is a developer tool, the MCP server lets you manage agents through natural language in any AI assistant. Ask Claude or ChatGPT to 'create an agent for quoting auto insurance' and it handles the technical details. The CLI is there when you want more control."

cta:
  headline: "Ready to Build?"
  description: "Install the CLI, connect your AI assistant, and start building agents in minutes."
  primary:
    text: "Get Started"
    href: "https://www.npmjs.com/package/@indemn/cli"
  secondary:
    text: "Talk to Us"
    href: "https://indemn.ai"
---

## Why This Matters

Insurance runs on manual processes — **$140B+ worth**. Every quote, every endorsement, every renewal involves humans navigating legacy systems, re-keying data, and following workflows that haven't changed in decades.

Indemn builds AI agents that automate these workflows and **generate revenue** for insurance businesses. Agents that quote, bind, service, and sell — across web chat, voice, and email.

But building these agents has required our dashboard. **Until now.**

The Indemn CLI and MCP Server make the entire agent platform **programmatically accessible** — designed from the ground up for AI assistants to operate. The same tools our engineering team uses internally, available to anyone building with AI.

**This is what it looks like when a company doesn't just use AI but is built around it at every level.** The platform that builds insurance agents is itself accessible to AI agents. The flywheel turns.
```

**Step 2: Verify by building and previewing**

```bash
npm run build
npm run dev
# Visit http://localhost:4321/products/indemn-cli/
```

Expected: The full showcase page renders with all sections — hero, story, features, demo tabs (placeholders), stats, walkthrough, FAQ, CTA.

**Step 3: Commit**

```bash
git add src/content/products/indemn-cli.mdx
git commit -m "feat(showcase): add CLI & MCP Server product showcase page"
```

---

## Task 11: Header Navigation Update

**Files:**
- Modify: `src/components/Header.astro`

Add a "Products" link to the site navigation.

**Step 1: Read the current Header.astro and add a Products link**

Find the navigation section and add a HeaderLink for Products. Add it before the Blog link:

```astro
<HeaderLink href="/products">Products</HeaderLink>
```

**Step 2: Verify build, then commit**

```bash
npm run build
git add src/components/Header.astro
git commit -m "feat(showcase): add Products navigation link to header"
```

---

## Task 12: Preview, Visual QA, and Deploy

**Step 1: Run local preview**

```bash
cd /Users/home/Repositories/content-system/sites/indemn-blog
npm run dev
```

Check:
- `http://localhost:4321/products/` — catalog page with CLI card
- `http://localhost:4321/products/indemn-cli/` — full showcase page
- Hero section: gradient background, flourishes, lime category pill, white text
- Story section: prose with proper typography
- Feature grid: 4 cards with numbered steps
- Demo tabs: 4 tabs, click each, see placeholder with "Recording coming soon"
- Stats banner: gradient background, 4 stats in a row
- Walkthrough: install command with copy button, 4 expandable platform guides
- FAQ: 6 questions, click to expand, + becomes −
- CTA: gradient background with two buttons
- Mobile: resize to 375px width, verify all sections stack properly
- Navigation: Products link appears in header

**Step 2: Build for production**

```bash
npm run build
```

Expected: Clean build, no warnings or errors.

**Step 3: Deploy to Vercel**

```bash
cd /Users/home/Repositories/content-system/sites/indemn-blog
vercel --prod
```

**Step 4: Verify live site**

Visit `https://blog.indemn.ai/products/indemn-cli/` and confirm it looks correct.

**Step 5: Commit any final adjustments**

```bash
git add -A
git commit -m "feat(showcase): visual QA adjustments and production deploy"
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Brand assets + CSS foundation | `public/brand/`, `global.css`, `consts.ts` |
| 2 | Products content collection | `content.config.ts` |
| 3 | ShowcaseLayout + routing + stubs | `layouts/`, `pages/products/`, `components/showcase/` |
| 4 | ShowcaseHero component | `ShowcaseHero.astro` |
| 5 | FeatureGrid + StatsBanner | `FeatureGrid.astro`, `StatsBanner.astro` |
| 6 | TabbedDemo (interactive) | `TabbedDemo.astro` |
| 7 | SetupWalkthrough | `SetupWalkthrough.astro` |
| 8 | FAQ with JSON-LD | `FAQ.astro` |
| 9 | ShowcaseCTA | `ShowcaseCTA.astro` |
| 10 | CLI showcase content | `indemn-cli.mdx` |
| 11 | Header nav update | `Header.astro` |
| 12 | Preview, QA, deploy | — |

**Total: 12 tasks, ~12 commits, zero new dependencies.**
