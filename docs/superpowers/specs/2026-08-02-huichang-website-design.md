# HUICHANG Corporate Website — Design Spec

**Date:** 2026-08-02
**Company:** Taizhou Huitong Trading Co., Ltd / Ningbo Huichang Imp&Exp Co., Ltd (HUICHANG / 汇昌)
**Domain:** huitongco.com

## 1. Background & Goal

HUICHANG is a B2B exporter of cleaning products established in 2003, shipping to 80+ countries. The company currently pays high annual fees for an existing website. This project replaces it with a **static, self-hostable corporate website** whose only recurring cost is the domain renewal (~¥80/year), deployed on Cloudflare Pages.

**Primary goals:**
- Project a professional, factory-strong, internationally credible image for both domestic and overseas B2B audiences.
- Convert visitors into inquiries by making contact channels prominent.
- Eliminate annual hosting/maintenance fees.

## 2. Confirmed Requirements

| Dimension | Decision |
|-----------|----------|
| Target market | Domestic China + Overseas (dual) |
| Language | English only |
| Product depth | 4 categories + ~40 curated hero SKUs (user will specify exact models) |
| Operation model | Static site, no form, no CMS backend → near-zero annual cost |
| Pages | Home + Products + About + Contact |
| Visual tone | Professional business / factory-strength |
| Home layout | Classic single-page scroll |
| Primary palette | Deep navy business |
| Imagery source | Product photos extracted from the 2026 PDF catalog (white-bg catalog shots); factory/team photos supplied later by the user |
| Hosting | Cloudflare Pages (free CDN + HTTPS + custom domain) |

## 3. Technical Approach (chosen)

**Pure static HTML5 + vanilla CSS (Flexbox/Grid) + minimal vanilla JS.**

Rationale:
- Zero runtime dependencies → loads fast, best SEO, permanently maintainable.
- Runs on any free static host; no build step, no Node environment required to edit.
- Matches the "curated products" scope — product maintenance is copy/paste of a card block.

Rejected alternatives:
- Astro — good for large catalogs, but adds a build step and maintenance burden disproportionate to ~40 products.
- WordPress — violates the zero-annual-fee goal (needs PHP host + DB + security updates).

### Tech stack details
- HTML5 semantic markup.
- CSS: custom properties for the design tokens; Flexbox/Grid layout; mobile-first responsive with one breakpoint set (~768px, ~1024px).
- JS (vanilla, no framework): mobile nav toggle, sticky-header shadow on scroll, scroll-reveal animations via `IntersectionObserver`, smooth-scroll for in-page anchors. All progressively enhanced (site works without JS).
- Fonts: Poppins (headings) + Inter (body) via Google Fonts with `display=swap`.
- Images: WebP where possible, lazy-loaded (`loading="lazy"`), responsive `srcset`.

## 4. Visual Design

### Color system
```
Primary      Deep Navy   #0A2540   — nav, section titles, footer
Secondary    Steel Blue  #1E5F8E   — buttons, links, icons
Accent       Warm Amber  #F59E0B   — CTA buttons, stat highlights
Neutral BG   Light Gray  #F8FAFC   — alternating section backgrounds
Text         Slate       #1F2937   — body copy
             White       #FFFFFF
```
Navy conveys reliability/international factory strength; amber makes key stats (years, countries, sales) pop.

### Typography
- Headings: Poppins (geometric sans, professional + approachable).
- Body: Inter (highly legible, B2B standard).

### Visual手法
- White-background product photos placed directly on light-gray sections for a clean catalog feel.
- Large amber-highlighted numerals for achievement stats.
- Subtle card hover (lift + shadow) for tactile interactivity.
- Generous whitespace between sections.

## 5. Information Architecture

```
/                        Home (single-page scroll: 7 sections)
/products                Products (4 anchor sections: public / house / hotel / pest)
/about                   About Us
/contact                 Contact
```

Global fixed top nav (becomes white with shadow on scroll):
`HUICHANG logo   |   Products ▾   About Us   Why Us   Contact   |   [Get Quote →]`
Mobile: hamburger menu.

## 6. Page Specifications

### 6.1 Home (`/`)

**Section 1 — Hero** (navy gradient bg)
- H1: "Professional Cleaning Solutions for 80+ Countries"
- Sub: "20+ years of cleaning product R&D, manufacturing & export. Design · Manufacture · Export."
- Buttons: [Explore Products] [Request a Quote]
- Visual: product collage or navy geometric backdrop.

**Section 2 — Stats bar** (amber numerals)
`20+ Years (since 2003) | 80+ Countries | $2M+ Annual Sales | 150+ Global Clients (OEM/ODM welcomed)`

**Section 3 — Product Categories** (4 cards, 2x2 / 4-col responsive)
- PUBLIC CLEANING — soap dispensers, paper dispensers, hand dryers, air-freshener dispensers
- HOUSE CLEANING — brushes, spones, non-woven/microfiber cloths, wet wipes
- HOTEL APPLIANCE — electric kettles, hair dryers
- PEST CONTROL — mouse traps, adhesive traps, mosquito lamps, bee hives / bird feeders / pet houses

Each card: category image + name + 1-line description + "View Products →" linking to `/products#anchor`.

**Section 4 — Featured Products** (~12 hero SKUs in a grid/carousel)
White-bg product image + model no. + 1-line spec + optional NEW/HOT tag.

**Section 5 — About Us** (left text / right image)
Company story (2003 → 2020 Ningbo branch → 80 countries), integrated manufacturer/exporter positioning.

**Section 6 — Why Choose Us** (4 icon cards)
- Integrated Manufacturer & Exporter
- 20+ Years Industry Experience
- Global Reach (80+ Countries)
- OEM/ODM & Custom Solutions

**Section 7 — CTA + Contact teaser** (navy bg)
"Ready to source premium cleaning products?" + email/phone/WhatsApp/WeChat icons.

**Footer:** logo + 4 columns (Products / Company / Contact / Social) + copyright.

### 6.2 Products (`/products`)
Single page with 4 anchor sections (one per category). Nav dropdown jumps to each anchor.
- Each section: category title + description + product grid (8–15 curated SKUs each; ~40 total).
- Each product card: white-bg image + model no. + key spec + optional tag.
- User will specify exact model numbers; initial build uses representative selections from the catalog as placeholders.

### 6.3 About (`/about`)
- Detailed company profile.
- Milestones timeline: 2003 founded → 2008 $2M sales → 2010 serving 50 countries → 2016 Ningbo branch → 2020+ portfolio expansion.
- Team: CEO Ms. Hui Miao (Macquarie Univ., Commerce), Exporting Manager Ms. Chang Wu (Exeter BA, Warwick MSc Project Management). Professional headshots to be supplied.
- Capabilities: design center, ISO-certified manufacturing, OEM/ODM, integrated export.
- Factory imagery: placeholder until user supplies real photos.

### 6.4 Contact (`/contact`) — no form, multi-channel
- Emails (clickable mailto:): htmh@huitongco.com / htwc@huitongco.com
- Phone / WhatsApp / WeChat: +86 138 1601 5937 / +86 189 6988 0515
- WhatsApp deep link: wa.me/8613816015937
- WeChat QR code (placeholder → user replaces).
- Company address (Taizhou / Ningbo — user to supply exact address).
- Business hours + response commitment.

## 7. Imagery Plan

- **Product photos:** 409 images already extracted from `2026 CATALOG-HUICHANG.pdf` to `D:/huitong/extracted_images/`. White-background professional catalog shots — suitable as-is. ~40 curated hero SKUs will be selected (user-specified models).
- **Factory / office / team photos:** placeholders with clear `TODO: replace with real photo` markers; user will supply.
- **Logos / certifications (ISO etc.):** placeholders until user supplies.
- All images optimized to WebP, lazy-loaded, responsive `srcset`.

## 8. Deployment & Cost

```
huitongco.com (existing domain, ~¥80/yr renewal)
        ↓ points to
Cloudflare Pages (free)
   - global CDN
   - automatic HTTPS
   - free custom domain binding
   - git-push auto-deploy
```
**Recurring cost: domain renewal only.** No hosting, CMS, or maintenance fees.

## 9. Out of Scope (YAGNI)

- No inquiry form (per user choice — direct contact channels instead).
- No CMS / admin backend.
- No blog / news.
- No e-commerce / cart (B2B inquiry model).
- No Chinese version (English only).
- No user accounts / login.

## 10. Open Items (to be supplied by user during/after build)

- [ ] Exact company address (Taizhou HQ + Ningbo branch).
- [ ] Certifications / partner logos (ISO etc.).
- [ ] CEO & Exporting Manager professional headshots.
- [ ] Factory / workshop / office real photos.
- [ ] Exact list of ~40 curated product model numbers (per category).
- [ ] WeChat QR code image.
- [ ] Logo source file (vector) if available; otherwise a typographic "HUICHANG" wordmark will be used.

## 11. Deliverables

- Complete static site in `D:/zhipu/Huichangwebsite/`:
  - `index.html`, `products.html`, `about.html`, `contact.html`
  - `css/styles.css`
  - `js/main.js`
  - `assets/` (product images, icons, logo, optimized WebP copies)
- `README.md` with edit + deploy instructions (how to change content, how to push to Cloudflare Pages).
- All `TODO` placeholders clearly marked for later replacement.
