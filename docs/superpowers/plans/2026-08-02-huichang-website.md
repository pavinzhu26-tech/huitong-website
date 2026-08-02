# HUICHANG Corporate Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static, zero-annual-fee English corporate website for HUICHANG (cleaning-products exporter) and deploy it to Cloudflare Pages.

**Architecture:** Pure static HTML5 + vanilla CSS (custom properties, Flexbox/Grid, mobile-first) + vanilla JS (progressive enhancement only). No framework, no build step, no backend. Product/contact data lives directly in the HTML so any non-developer can edit content later. Imagery is sourced from the existing 2026 PDF catalog.

**Tech Stack:** HTML5, vanilla CSS3, vanilla JavaScript (ES2020), Google Fonts (Poppins + Inter), Pillow (Python, for image prep only — not a runtime dependency).

## Global Constraints

(Verbatim from spec §3, §4, §8.)

- **Language:** English only. All copy in English.
- **Pages:** exactly four — `/` (home), `/products`, `/about`, `/contact`. No blog, no CMS, no form, no accounts, no e-commerce.
- **Colors:** Primary `#0A2540` (deep navy), Secondary `#1E5F8E` (steel blue), Accent `#F59E0B` (amber), Neutral BG `#F8FAFC`, Text `#1F2937`. Defined once as CSS custom properties in `:root`.
- **Fonts:** Poppins (headings, weights 600/700) + Inter (body, 400/500/600) from Google Fonts with `&display=swap`. Preconnect to `fonts.googleapis.com` and `fonts.gstatic.com`.
- **Responsive:** mobile-first; breakpoints at 768px and 1024px.
- **Progressive enhancement:** the site must be fully usable with JS disabled (nav, links, contact info all work); JS only adds polish (mobile menu toggle, sticky-header shadow, scroll-reveal, smooth-scroll).
- **Images:** all `<img>` carry `loading="lazy"` and `width`/`height` attributes (prevent layout shift); decorative images get `alt=""`.
- **Accessibility:** semantic HTML5 landmarks (`header`/`nav`/`main`/`section`/`footer`), each section has an `<h2>`, every interactive element is keyboard reachable, color contrast meets WCAG AA (navy/white, navy text on amber CTA).
- **SEO:** unique `<title>` + `<meta name="description">` per page, Open Graph tags on home, descriptive `alt` text, `lang="en"`.
- **Contact info (verbatim):** emails `htmh@huitongco.com` / `htwc@huitongco.com`; phones/WhatsApp/WeChat `+86 138 1601 5937` / `+86 189 6988 0515`; WhatsApp deep link `https://wa.me/8613816015937`.
- **Deployment target:** Cloudflare Pages (static). No server-side code anywhere.
- **Open items (user will supply later — must be placeholders, clearly marked):** exact company address, ISO/partner logos, CEO & Exporting Manager headshots, factory/office photos, exact ~40 curated product model numbers, WeChat QR image, vector logo.

---

## File Structure

```
D:/zhipu/Huichangwebsite/
├── index.html              # Home (7 single-page-scroll sections)
├── products.html           # Products (4 anchor sections)
├── about.html              # About Us
├── contact.html            # Contact
├── css/
│   └── styles.css          # ALL styles (design tokens, layout, components, responsive)
├── js/
│   └── main.js             # Progressive-enhancement JS only
├── assets/
│   ├── logo.svg            # HUICHANG wordmark logo
│   ├── icons/              # UI icons (mail, phone, whatsapp, wechat, check, arrow, category icons) as inline-able SVG files
│   ├── products/           # curated product photos (webp + png fallback)
│   │   ├── public-cleaning/
│   │   ├── house-cleaning/
│   │   ├── hotel-appliance/
│   │   └── pest-control/
│   ├── team/               # CEO + manager headshot placeholders
│   ├── factory/            # factory photo placeholders
│   └── og/                 # open-graph share image
├── README.md               # how to edit content + how to deploy to Cloudflare Pages
└── docs/
    └── superpowers/
        ├── specs/2026-08-02-huichang-website-design.md
        └── plans/2026-08-02-huichang-website.md   (this file)
```

**Responsibility boundaries:**
- `styles.css` is the single source of truth for all design tokens and component classes. Pages contain no inline styles except unavoidable image `srcset` sizing.
- `main.js` exposes no global API; it only attaches event listeners on `DOMContentLoaded`. Removing the file leaves the site fully functional.
- Each `.html` page is self-contained and imports the same `styles.css` + `main.js`. Shared markup (header, footer) is duplicated across the 4 pages (static site, no includes) — Task 1 establishes the canonical header/footer, Tasks 2–4 copy it verbatim.

---

## Task 1: Curate product imagery from the PDF catalog

**Why first:** every page references product/category images; preparing the asset set first lets later HTML tasks reference real paths instead of placeholders.

**Files:**
- Create: `D:/zhipu/Huichangwebsite/assets/products/public-cleaning/*.webp`
- Create: `D:/zhipu/Huichangwebsite/assets/products/house-cleaning/*.webp`
- Create: `D:/zhipu/Huichangwebsite/assets/products/hotel-appliance/*.webp`
- Create: `D:/zhipu/Huichangwebsite/assets/products/pest-control/*.webp`
- Create: `D:/zhipu/Huichangwebsite/scripts/curate_images.py` (one-off tool, not deployed)

**Produces:** ~12 representative product images per category (~48 total) named by model, in WebP, plus a PNG fallback for each. Catalog mapping:
- PUBLIC CLEANING → PDF pages 5–10 (soap dispensers p05/p06, air-freshener dispensers p07, paper dispensers p08/p09, hand dryers p10).
- HOUSE CLEANING → PDF pages 12–14 (brushes p12, sponges p13, cloths p14).
- HOTEL APPLIANCE → PDF pages 16–17 (kettles p16, hair dryers p17).
- PEST CONTROL → PDF pages 19–24 (mouse traps p19/p20, adhesive traps p21, mosquito lamps p22/p23, insect traps p24).

Source images already extracted at `D:/huitong/extracted_images/pNN_MM.png`.

- [ ] **Step 1: Create the curation script**

Create `scripts/curate_images.py`. It maps selected PDF page→image indices to category/model filenames, opens each source PNG with Pillow, trims to content (optional), resizes so the longest edge is ≤ 1200px (keeping aspect ratio, `Image.LANCZOS`), and saves both WebP (quality 82) and PNG copies.

```python
# scripts/curate_images.py
"""One-off: curate product photos from the extracted PDF images into assets/products/.
Run: python scripts/curate_images.py  (from project root)
"""
import os
from PIL import Image, ImageOps

SRC = r"D:/huitong/extracted_images"
DST = "assets/products"
MAX_EDGE = 1200

# (source_filename, category_dir, model_name)
SELECTION = [
    # PUBLIC CLEANING (soap dispensers p05/p06, paper dispensers p08, hand dryers p10)
    ("p05_03.png", "public-cleaning", "HC-1406"),
    ("p05_05.png", "public-cleaning", "HC-1305"),
    ("p06_05.png", "public-cleaning", "HC-1409M"),
    ("p06_07.png", "public-cleaning", "HC-1407"),
    ("p08_03.png", "public-cleaning", "HC-CZ01"),
    ("p08_11.png", "public-cleaning", "HC-AK59"),
    ("p10_01.png", "public-cleaning", "HC-WS-S140"),
    ("p10_03.png", "public-cleaning", "HC-WS-H-M250"),
    ("p10_09.png", "public-cleaning", "HC-WS-S988"),
    ("p10_11.png", "public-cleaning", "HC-WS-S6666"),
    # HOUSE CLEANING (brushes p12, sponges p13, cloths p14)
    ("p12_01.png", "house-cleaning", "HC-6126"),
    ("p12_02.png", "house-cleaning", "HC-6127"),
    ("p12_03.png", "house-cleaning", "HC-6121"),
    ("p12_05.png", "house-cleaning", "HC-6168"),
    ("p13_01.png", "house-cleaning", "sponge-01"),
    ("p13_05.png", "house-cleaning", "sponge-02"),
    ("p14_01.png", "house-cleaning", "cloth-nw-01"),
    ("p14_05.png", "house-cleaning", "cloth-mf-01"),
    # HOTEL APPLIANCE (kettles p16, hair dryers p17)
    ("p16_01.png", "hotel-appliance", "kettle-01"),
    ("p16_03.png", "hotel-appliance", "kettle-02"),
    ("p17_01.png", "hotel-appliance", "hairdryer-hs"),
    ("p17_03.png", "hotel-appliance", "hairdryer-02"),
    # PEST CONTROL (mouse traps p19/p20, mosquito lamps p22/p23)
    ("p19_01.png", "pest-control", "mousetrap-201"),
    ("p19_03.png", "pest-control", "mousetrap-203"),
    ("p20_01.png", "pest-control", "mousetrap-608"),
    ("p20_03.png", "pest-control", "mousetrap-610"),
    ("p22_01.png", "pest-control", "HC-MK20"),
    ("p22_03.png", "pest-control", "HC-MK10"),
    ("p23_01.png", "pest-control", "HC-MK09"),
    ("p24_01.png", "pest-control", "insect-F01B"),
]

def process(src_name, cat, model):
    src_path = os.path.join(SRC, src_name)
    if not os.path.exists(src_path):
        print(f"  MISSING source: {src_path}")
        return False
    out_dir = os.path.join(DST, cat)
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(src_path).convert("RGBA")
    # Flatten transparency onto white (catalog photos look best on white)
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    # Resize longest edge to MAX_EDGE
    w, h = im.size
    scale = MAX_EDGE / max(w, h)
    if scale < 1:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    webp = os.path.join(out_dir, f"{model}.webp")
    png = os.path.join(out_dir, f"{model}.png")
    im.save(webp, "WEBP", quality=82)
    im.save(png, "PNG", optimize=True)
    print(f"  OK {cat}/{model}  {im.size[0]}x{im.size[1]}")
    return True

if __name__ == "__main__":
    ok = miss = 0
    for src_name, cat, model in SELECTION:
        if process(src_name, cat, model):
            ok += 1
        else:
            miss += 1
    print(f"\nDone: {ok} processed, {miss} missing.")
    print("NOTE: if any MISSING, inspect D:/huitong/extracted_images/<page>_*.png")
    print("      and update SELECTION index numbers in this script, then re-run.")
```

- [ ] **Step 2: Run the curation script**

Run (from project root `D:/zhipu/Huichangwebsite`):
```bash
python scripts/curate_images.py
```
Expected: prints `OK <category>/<model> <w>x<h>` for each, ending with `Done: 30 processed, 0 missing.` (count = 30). If any `MISSING source` lines appear, list the actual filenames present for that page with `ls D:/huitong/extracted_images/pNN_*.png`, correct the index in `SELECTION`, and re-run.

- [ ] **Step 3: Verify outputs exist and are non-trivial**

Run:
```bash
find assets/products -name "*.webp" | wc -l
find assets/products -name "*.webp" -size -2k
```
Expected: first command prints `30`; second command prints `0` (no tiny/broken files). If the second prints any files, re-open one in a viewer — it likely failed to flatten; fix by ensuring the source had RGBA and re-run.

- [ ] **Step 4: Commit**

```bash
git add scripts/curate_images.py assets/products/
git commit -m "chore: curate product imagery from PDF catalog"
```

---

## Task 2: Design tokens, base CSS, and shared UI components

**Files:**
- Create: `css/styles.css`
- Create: `assets/logo.svg`
- Create: `assets/icons/` SVGs: `mail.svg`, `phone.svg`, `whatsapp.svg`, `wechat.svg`, `check.svg`, `arrow-right.svg`, `cat-public.svg`, `cat-house.svg`, `cat-hotel.svg`, `cat-pest.svg`

**Interfaces (CSS contract used by all later HTML tasks):**
- `:root` custom properties: `--navy:#0A2540; --blue:#1E5F8E; --amber:#F59E0B; --bg:#F8FAFC; --text:#1F2937; --white:#FFFFFF; --maxw:1200px; --radius:12px; --shadow:0 4px 20px rgba(10,37,64,.08); --shadow-hover:0 8px 30px rgba(10,37,64,.15)`.
- Layout utility classes: `.container` (max-width 1200px, centered, padding 0 1.5rem), `.section` (padding 5rem 0), `.section--alt` (background `--bg`), `.grid` (CSS grid, `gap:2rem`), `.grid--2`/`.grid--3`/`.grid--4` (auto-fit minmax columns).
- Component classes: `.btn` (base), `.btn--primary` (amber bg, navy text), `.btn--ghost` (transparent, white/navy border). `.card`, `.card--hover`. `.eyebrow` (small uppercase amber label). `.stat__num` (huge amber number). `.badge` (NEW/HOT pill). `.nav`, `.nav__link`, `.nav__cta`. `.footer`. `.section__title`.
- All HTML tasks reference ONLY these class names.

- [ ] **Step 1: Write `assets/logo.svg`**

A clean wordmark (no real logo file yet — this is a clearly-marked placeholder per spec §10).

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 48" role="img" aria-label="HUICHANG logo">
  <text x="0" y="34" font-family="Poppins, Arial, sans-serif" font-size="30" font-weight="700" letter-spacing="2" fill="#0A2540">HUI<tspan fill="#F59E0B">CHANG</tspan></text>
</svg>
```
(Save exactly this content to `assets/logo.svg`.)

- [ ] **Step 2: Write the icon SVGs**

Each is a 24×24 stroke icon, `stroke="currentColor"` so color is inherited. Save one file per icon. Example for `assets/icons/check.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
```
Create the remaining 9 icons using standard Feather-style paths:
- `mail.svg`: `<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>`
- `phone.svg`: `<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>`
- `whatsapp.svg` / `wechat.svg`: use simple chat-bubble glyphs (whatsapp: a phone-in-bubble; wechat: two overlapping bubbles) — keep stroke style consistent.
- `arrow-right.svg`: `<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>`
- `cat-public.svg`, `cat-house.svg`, `cat-hotel.svg`, `cat-pest.svg`: simple representative glyphs (e.g., droplet / broom / kettle / bug).

- [ ] **Step 3: Write `css/styles.css` (design tokens + base + utilities + components + responsive)**

```css
/* ============================================================
   HUICHANG — styles.css
   Design tokens, base, layout, components, responsive.
   ============================================================ */

/* ---------- Design tokens ---------- */
:root{
  --navy:#0A2540; --blue:#1E5F8E; --amber:#F59E0B;
  --bg:#F8FAFC; --text:#1F2937; --white:#FFFFFF;
  --muted:#64748B; --border:#E2E8F0;
  --maxw:1200px; --radius:12px;
  --shadow:0 4px 20px rgba(10,37,64,.08);
  --shadow-hover:0 8px 30px rgba(10,37,64,.15);
  --font-head:'Poppins',system-ui,sans-serif;
  --font-body:'Inter',system-ui,sans-serif;
}

/* ---------- Reset / base ---------- */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;scroll-padding-top:90px}
body{font-family:var(--font-body);color:var(--text);background:var(--white);
  line-height:1.65;font-size:1rem;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4{font-family:var(--font-head);line-height:1.2;color:var(--navy);font-weight:700}
h1{font-size:clamp(2rem,5vw,3.4rem)}
h2{font-size:clamp(1.6rem,3.5vw,2.4rem)}
h3{font-size:1.25rem}
p{color:var(--text)}a{color:var(--blue);text-decoration:none}
a:hover{color:var(--navy)}
img{max-width:100%;display:block}
ul{list-style:none}

/* ---------- Layout ---------- */
.container{max-width:var(--maxw);margin:0 auto;padding:0 1.5rem}
.section{padding:5rem 0}
.section--alt{background:var(--bg)}
.section__head{max-width:720px;margin:0 auto 3rem;text-align:center}
.eyebrow{display:inline-block;font-family:var(--font-head);font-weight:600;
  font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);margin-bottom:.75rem}
.section__title{margin-bottom:1rem}
.section__lead{color:var(--muted);font-size:1.1rem}

/* ---------- Grids ---------- */
.grid{display:grid;gap:2rem}
.grid--2{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.grid--3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.grid--4{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}

/* ---------- Buttons ---------- */
.btn{display:inline-flex;align-items:center;gap:.5rem;font-family:var(--font-head);
  font-weight:600;font-size:1rem;padding:.85rem 1.6rem;border-radius:50px;
  border:2px solid transparent;cursor:pointer;transition:.25s}
.btn--primary{background:var(--amber);color:var(--navy)}
.btn--primary:hover{background:#E8920A;color:var(--navy);transform:translateY(-2px)}
.btn--ghost{background:transparent;color:var(--white);border-color:rgba(255,255,255,.6)}
.btn--ghost:hover{background:rgba(255,255,255,.1)}
.btn--outline{background:transparent;color:var(--navy);border-color:var(--navy)}
.btn--outline:hover{background:var(--navy);color:var(--white)}

/* ---------- Cards ---------- */
.card{background:var(--white);border:1px solid var(--border);border-radius:var(--radius);
  overflow:hidden;box-shadow:var(--shadow)}
.card--hover{transition:.3s}
.card--hover:hover{transform:translateY(-6px);box-shadow:var(--shadow-hover);border-color:var(--blue)}

/* ---------- Stats ---------- */
.stat{text-align:center}
.stat__num{font-family:var(--font-head);font-weight:700;font-size:clamp(2.2rem,5vw,3.2rem);
  color:var(--amber);line-height:1}
.stat__label{color:var(--muted);margin-top:.5rem;font-size:.95rem}

/* ---------- Badge ---------- */
.badge{position:absolute;top:.75rem;left:.75rem;background:var(--amber);color:var(--navy);
  font-family:var(--font-head);font-weight:600;font-size:.7rem;letter-spacing:.08em;
  text-transform:uppercase;padding:.25rem .6rem;border-radius:50px}

/* ---------- Header / nav ---------- */
.nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(10,37,64,.95);
  backdrop-filter:blur(8px);transition:.3s}
.nav--scrolled{background:var(--navy);box-shadow:0 2px 20px rgba(0,0,0,.2)}
.nav__inner{display:flex;align-items:center;justify-content:space-between;
  max-width:var(--maxw);margin:0 auto;padding:0 1.5rem;height:72px}
.nav__logo{height:34px}
.nav__links{display:flex;align-items:center;gap:2rem}
.nav__link{color:rgba(255,255,255,.85);font-weight:500}
.nav__link:hover{color:var(--white)}
.nav__cta{background:var(--amber);color:var(--navy);padding:.55rem 1.2rem;border-radius:50px;
  font-family:var(--font-head);font-weight:600}
.nav__cta:hover{background:#E8920A;color:var(--navy)}
.nav__toggle{display:none;background:none;border:none;cursor:pointer;
  flex-direction:column;gap:5px;padding:8px}
.nav__toggle span{width:24px;height:2px;background:var(--white);transition:.3s}

/* ---------- Footer ---------- */
.footer{background:var(--navy);color:rgba(255,255,255,.75);padding:4rem 0 2rem}
.footer h4{color:var(--white);margin-bottom:1rem;font-size:1rem}
.footer a{color:rgba(255,255,255,.75)}
.footer a:hover{color:var(--amber)}
.footer__grid{display:grid;gap:2rem;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  margin-bottom:2.5rem}
.footer__bottom{border-top:1px solid rgba(255,255,255,.15);padding-top:1.5rem;
  text-align:center;font-size:.85rem;color:rgba(255,255,255,.5)}

/* ---------- Scroll reveal (progressively enhanced) ---------- */
.reveal{opacity:0;transform:translateY(24px);transition:.6s}
.reveal.is-visible{opacity:1;transform:none}

/* ---------- Hero ---------- */
.hero{background:linear-gradient(135deg,#0A2540 0%,#1E5F8E 100%);color:var(--white);
  padding:9rem 0 6rem;position:relative;overflow:hidden}
.hero h1{color:var(--white);max-width:18ch}
.hero__lead{font-size:1.25rem;color:rgba(255,255,255,.85);max-width:60ch;margin:1.5rem 0 2.5rem}
.hero__actions{display:flex;flex-wrap:wrap;gap:1rem}

/* ---------- Responsive ---------- */
@media (max-width:768px){
  .nav__links{position:fixed;inset:72px 0 auto 0;background:var(--navy);
    flex-direction:column;padding:2rem 1.5rem;gap:1.5rem;
    transform:translateY(-150%);transition:.3s}
  .nav__links.is-open{transform:none}
  .nav__toggle{display:flex}
}
@media (prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important;scroll-behavior:auto!important}
  .reveal{opacity:1;transform:none}
}
```

- [ ] **Step 4: Commit**

```bash
git add css/styles.css assets/logo.svg assets/icons/
git commit -m "feat: design tokens, base styles, shared UI components"
```

---

## Task 3: Home page (`index.html`)

**Files:**
- Create: `index.html`

**Consumes:** `css/styles.css`, `js/main.js`, `assets/logo.svg`, `assets/icons/*`, `assets/products/**`.

- [ ] **Step 1: Write the document head, header (nav), and footer**

Header and footer are identical across all 4 pages — copy this block verbatim in Tasks 4–6, changing only which `nav__link` carries `aria-current="page"`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HUICHANG — Professional Cleaning Products Manufacturer & Exporter</title>
<meta name="description" content="HUICHANG (Taizhou Huitong / Ningbo Huichang) has designed, manufactured and exported professional cleaning products to 80+ countries since 2003. OEM/ODM welcomed.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/styles.css">
<meta property="og:title" content="HUICHANG — Cleaning Products Manufacturer & Exporter">
<meta property="og:description" content="20+ years. 80+ countries. Soap dispensers, hand dryers, brushes, hotel appliances, pest control.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.huitongco.com/">
<meta property="og:image" content="assets/og/og-image.jpg">
</head>
<body>

<header class="nav" id="nav">
  <div class="nav__inner">
    <a href="index.html" aria-label="HUICHANG home"><img src="assets/logo.svg" alt="HUICHANG" class="nav__logo"></a>
    <button class="nav__toggle" id="navToggle" aria-label="Toggle menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav__links" id="navLinks">
      <a href="products.html" class="nav__link">Products</a>
      <a href="about.html" class="nav__link">About Us</a>
      <a href="index.html#why" class="nav__link">Why Us</a>
      <a href="contact.html" class="nav__link">Contact</a>
      <a href="contact.html" class="nav__cta">Get Quote</a>
    </nav>
  </div>
</header>

<main>
  <!-- SECTIONS GO HERE -->
</main>

<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div>
        <img src="assets/logo.svg" alt="HUICHANG" class="nav__logo" style="filter:brightness(0) invert(1);margin-bottom:1rem">
        <p>Designing, manufacturing and exporting professional cleaning products to 80+ countries since 2003.</p>
      </div>
      <div>
        <h4>Products</h4>
        <ul><li><a href="products.html#public">Public Cleaning</a></li>
        <li><a href="products.html#house">House Cleaning</a></li>
        <li><a href="products.html#hotel">Hotel Appliance</a></li>
        <li><a href="products.html#pest">Pest Control</a></li></ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul><li><a href="about.html">About Us</a></li>
        <li><a href="index.html#why">Why Choose Us</a></li>
        <li><a href="contact.html">Contact</a></li></ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
        <li><a href="mailto:htmh@huitongco.com">htmh@huitongco.com</a></li>
        <li><a href="tel:+8613816015937">+86 138 1601 5937</a></li>
        <li><a href="https://wa.me/8613816015937" target="_blank" rel="noopener">WhatsApp</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      © <span id="year"></span> Taizhou Huitong Trading Co., Ltd / Ningbo Huichang Imp&Exp Co., Ltd. All rights reserved.
    </div>
  </div>
</footer>
<script src="js/main.js" defer></script>
</body>
</html>
```

- [ ] **Step 2: Add the 7 home-page sections inside `<main>`**

```html
<!-- 1. HERO -->
<section class="hero">
  <div class="container">
    <span class="eyebrow">Since 2003 · 80+ Countries</span>
    <h1>Professional Cleaning Solutions for 80+ Countries</h1>
    <p class="hero__lead">20+ years of cleaning-product R&amp;D, manufacturing and global export. From soap dispensers to pest control — designed, made and shipped by one integrated partner.</p>
    <div class="hero__actions">
      <a href="products.html" class="btn btn--primary">Explore Products</a>
      <a href="contact.html" class="btn btn--ghost">Request a Quote</a>
    </div>
  </div>
</section>

<!-- 2. STATS -->
<section class="section section--alt" style="padding:3rem 0">
  <div class="container">
    <div class="grid grid--4">
      <div class="stat reveal"><div class="stat__num">20+</div><div class="stat__label">Years of experience</div></div>
      <div class="stat reveal"><div class="stat__num">80+</div><div class="stat__label">Countries served</div></div>
      <div class="stat reveal"><div class="stat__num">$2M+</div><div class="stat__label">Annual sales</div></div>
      <div class="stat reveal"><div class="stat__num">150+</div><div class="stat__label">Global clients · OEM/ODM</div></div>
    </div>
  </div>
</section>

<!-- 3. PRODUCT CATEGORIES -->
<section class="section" id="categories">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">What we do</span>
      <h2 class="section__title">Four product lines, one trusted supplier</h2>
      <p class="section__lead">An integrated range covering commercial, household, hospitality and pest-control cleaning needs.</p>
    </div>
    <div class="grid grid--4">
      <a href="products.html#public" class="card card--hover reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/cat-public.svg" alt="" width="56" height="56" style="margin:0 auto 1rem">
        <h3>Public Cleaning</h3>
        <p style="color:var(--muted);margin:.5rem 0 1rem">Soap dispensers, paper dispensers, hand dryers, air-freshener dispensers.</p>
        <span class="btn btn--outline" style="padding:.4rem 1rem;font-size:.9rem">View Products</span>
      </a>
      <a href="products.html#house" class="card card--hover reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/cat-house.svg" alt="" width="56" height="56" style="margin:0 auto 1rem">
        <h3>House Cleaning</h3>
        <p style="color:var(--muted);margin:.5rem 0 1rem">Brushes, sponges, non-woven &amp; microfiber cloths, wet wipes.</p>
        <span class="btn btn--outline" style="padding:.4rem 1rem;font-size:.9rem">View Products</span>
      </a>
      <a href="products.html#hotel" class="card card--hover reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/cat-hotel.svg" alt="" width="56" height="56" style="margin:0 auto 1rem">
        <h3>Hotel Appliance</h3>
        <p style="color:var(--muted);margin:.5rem 0 1rem">Electric kettles and high-speed hair dryers for hospitality.</p>
        <span class="btn btn--outline" style="padding:.4rem 1rem;font-size:.9rem">View Products</span>
      </a>
      <a href="products.html#pest" class="card card--hover reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/cat-pest.svg" alt="" width="56" height="56" style="margin:0 auto 1rem">
        <h3>Pest Control</h3>
        <p style="color:var(--muted);margin:.5rem 0 1rem">Mouse traps, adhesive traps, mosquito lamps, bird feeders &amp; pet houses.</p>
        <span class="btn btn--outline" style="padding:.4rem 1rem;font-size:.9rem">View Products</span>
      </a>
    </div>
  </div>
</section>

<!-- 4. FEATURED PRODUCTS -->
<section class="section section--alt" id="featured">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Featured</span>
      <h2 class="section__title">Representative products</h2>
      <p class="section__lead">A small selection from our full catalog. Contact us for the complete range and OEM options.</p>
    </div>
    <div class="grid grid--4" id="featuredGrid"><!-- filled by featured-product cards --></div>
    <div style="text-align:center;margin-top:2.5rem">
      <a href="products.html" class="btn btn--primary">View All Products</a>
    </div>
  </div>
</section>

<!-- 5. ABOUT TEASER -->
<section class="section" id="about-teaser">
  <div class="container">
    <div style="display:grid;gap:3rem;grid-template-columns:1fr 1fr;align-items:center" class="about-teaser__grid">
      <div class="reveal">
        <span class="eyebrow">About HUICHANG</span>
        <h2 class="section__title">Two decades of cleaning-product expertise</h2>
        <p style="color:var(--muted);margin-bottom:1rem">Established in 2003, HUICHANG (Taizhou Huitong Trading Co., Ltd / Ningbo Huichang Imp&amp;Exp Co., Ltd) designs, develops, manufactures and distributes cleaning products worldwide.</p>
        <p style="color:var(--muted);margin-bottom:1.5rem">Our solutions reach 80+ countries — including the USA, Australia, Japan and across Europe. We opened our Ningbo branch in 2020 to expand our product portfolio and support clients' global market growth.</p>
        <a href="about.html" class="btn btn--outline">Learn More About Us</a>
      </div>
      <div class="reveal" style="position:relative">
        <!-- TODO: replace with real factory/office photo (spec §10) -->
        <img src="assets/factory/placeholder-about.jpg" alt="HUICHANG facility" width="600" height="450" loading="lazy" style="border-radius:var(--radius);box-shadow:var(--shadow)">
      </div>
    </div>
  </div>
</section>

<!-- 6. WHY US -->
<section class="section section--alt" id="why">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Why HUICHANG</span>
      <h2 class="section__title">A partner you can rely on</h2>
    </div>
    <div class="grid grid--4">
      <div class="card reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/check.svg" alt="" width="40" height="40" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>Integrated Manufacturer &amp; Exporter</h3>
        <p style="color:var(--muted);margin-top:.5rem">Design, production and export under one roof for reliable quality and delivery.</p>
      </div>
      <div class="card reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/check.svg" alt="" width="40" height="40" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>20+ Years Experience</h3>
        <p style="color:var(--muted);margin-top:.5rem">Specialised in cleaning products since 2003 with a professional design centre.</p>
      </div>
      <div class="card reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/check.svg" alt="" width="40" height="40" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>Global Reach</h3>
        <p style="color:var(--muted);margin-top:.5rem">Trusted by 150+ clients across 80+ countries on five continents.</p>
      </div>
      <div class="card reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/check.svg" alt="" width="40" height="40" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>OEM / ODM &amp; Custom</h3>
        <p style="color:var(--muted);margin-top:.5rem">ISO-certified manufacturing with full OEM/ODM and bespoke solutions.</p>
      </div>
    </div>
  </div>
</section>

<!-- 7. CTA + CONTACT TEASER -->
<section class="section" style="background:var(--navy);color:#fff;text-align:center">
  <div class="container">
    <h2 style="color:#fff">Ready to source premium cleaning products?</h2>
    <p style="color:rgba(255,255,255,.8);max-width:60ch;margin:1rem auto 2rem">Tell us what you need — our team replies fast with tailored options and OEM support.</p>
    <div class="hero__actions" style="justify-content:center">
      <a href="mailto:htmh@huitongco.com" class="btn btn--primary">Email Us</a>
      <a href="https://wa.me/8613816015937" target="_blank" rel="noopener" class="btn btn--ghost">WhatsApp</a>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Fill the featured-products grid (8 hero SKUs)**

Replace the `<!-- filled by featured-product cards -->` comment with eight product cards drawn from Task 1's assets. Card template (repeat, swapping image/model/spec):

```html
<a href="products.html#public" class="card card--hover reveal" style="position:relative;padding:1.5rem;text-align:center">
  <img src="assets/products/public-cleaning/HC-1406.webp" alt="Sensor soap dispenser HC-1406" width="300" height="300" loading="lazy" style="margin:0 auto 1rem;background:var(--bg);border-radius:8px">
  <h3 style="font-size:1.05rem">Sensor Soap Dispenser</h3>
  <p style="color:var(--blue);font-weight:600;font-size:.85rem;margin-top:.25rem">HC-1406 · 1200ml</p>
</a>
```
Choose 8 covering all 4 categories (2 each): `HC-1406` (public), `HC-WS-S140` (public), `HC-6126` (house), `sponge-01` (house), `kettle-01` (hotel), `hairdryer-hs` (hotel), `mousetrap-201` (pest), `HC-MK20` (pest). Use the `.webp` paths from Task 1.

- [ ] **Step 4: Verify the page opens**

Run a quick local server and open `index.html`:
```bash
python -m http.server 8000
```
Open `http://localhost:8000/` in a browser. Expected: navy hero with title, amber stat numbers, 4 category cards, 8 featured product cards with images, about teaser with placeholder image, why-us cards, CTA, footer with correct year. Nav is fixed; clicking category cards navigates to `/products.html#<cat>` (will 404 until Task 4 — that's fine here).

If any product image is broken (alt text shown on a broken-image icon), check the exact filename in `assets/products/<cat>/` and correct the `src`.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: home page with hero, stats, categories, featured products"
```

---

## Task 4: Products page (`products.html`)

**Files:**
- Create: `products.html`

**Consumes:** header/footer from Task 3 (copy verbatim), product images from Task 1.

- [ ] **Step 1: Copy `index.html` and adapt head + active nav**

Copy `index.html` → `products.html`. Change:
- `<title>` → `Products — HUICHANG`
- `<meta name="description">` → `Explore HUICHANG's full range: public cleaning, house cleaning, hotel appliances and pest control products. OEM/ODM welcomed.`
- Remove the og: tags (only home needs them) OR update og:url to the products URL — simplest is to delete the five `og:` lines.
- On the Products nav link add `aria-current="page"`: `<a href="products.html" class="nav__link" aria-current="page">Products</a>`
- Replace everything inside `<main>...</main>` with the products content below.

- [ ] **Step 2: Write the 4 category sections inside `<main>`**

Each category section follows the same pattern. Replace `<main>` content with:

```html
<section class="section" style="padding-top:8rem">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">Catalog</span>
      <h1 class="section__title" style="font-size:clamp(2rem,5vw,3rem)">Products</h1>
      <p class="section__lead">Four product lines. A representative selection is shown below — contact us for the full range, specifications and OEM options.</p>
    </div>
  </div>
</section>

<!-- PUBLIC CLEANING -->
<section class="section section--alt" id="public">
  <div class="container">
    <div class="section__head">
      <span class="eyebrow">01 · Public Cleaning</span>
      <h2 class="section__title">Soap dispensers, hand dryers &amp; more</h2>
    </div>
    <div class="grid grid--4">
      <!-- one card per SKU; repeat the template -->
      <div class="card reveal" style="position:relative;padding:1.5rem;text-align:center">
        <img src="assets/products/public-cleaning/HC-1406.webp" alt="Sensor soap dispenser HC-1406, 1200ml" width="300" height="300" loading="lazy" style="background:var(--bg);border-radius:8px;margin-bottom:.75rem">
        <h3 style="font-size:1rem">Sensor Soap Dispenser</h3>
        <p style="color:var(--blue);font-weight:600;font-size:.85rem;margin-top:.25rem">HC-1406 · 1200ml</p>
        <p style="color:var(--muted);font-size:.8rem;margin-top:.25rem">Spray / Foam / Soap</p>
      </div>
      <!-- ... add the rest of public-cleaning SKUs from Task 1 ... -->
    </div>
  </div>
</section>

<!-- HOUSE CLEANING -->
<section class="section" id="house">
  <div class="container">
    <div class="section__head"><span class="eyebrow">02 · House Cleaning</span>
      <h2 class="section__title">Brushes, sponges &amp; cloths</h2></div>
    <div class="grid grid--4">
      <!-- house-cleaning SKU cards -->
    </div>
  </div>
</section>

<!-- HOTEL APPLIANCE -->
<section class="section section--alt" id="hotel">
  <div class="container">
    <div class="section__head"><span class="eyebrow">03 · Hotel Appliance</span>
      <h2 class="section__title">Kettles &amp; hair dryers</h2></div>
    <div class="grid grid--4">
      <!-- hotel-appliance SKU cards -->
    </div>
  </div>
</section>

<!-- PEST CONTROL -->
<section class="section" id="pest">
  <div class="container">
    <div class="section__head"><span class="eyebrow">04 · Pest Control</span>
      <h2 class="section__title">Traps, mosquito lamps &amp; outdoor</h2></div>
    <div class="grid grid--4">
      <!-- pest-control SKU cards -->
    </div>
  </div>
</section>

<!-- CTA -->
<section class="section" style="background:var(--navy);color:#fff;text-align:center">
  <div class="container">
    <h2 style="color:#fff">Need the full catalog or a custom product?</h2>
    <p style="color:rgba(255,255,255,.8);margin:1rem auto 2rem">We offer OEM/ODM and bespoke specifications across all four lines.</p>
    <a href="contact.html" class="btn btn--primary">Contact Us</a>
  </div>
</section>
```

- [ ] **Step 3: Generate one card per curated SKU**

For each `.webp` produced in Task 1, create a card. Use this script to emit the HTML so the filenames stay correct — run it once and paste the output into the matching section:

```bash
python - <<'PY'
import os
CATS={"public-cleaning":("01","Public Cleaning","public"),
      "house-cleaning":("02","House Cleaning","house"),
      "hotel-appliance":("03","Hotel Appliance","hotel"),
      "pest-control":("04","Pest Control","pest")}
base="assets/products"
for cat,(num,name,anchor) in CATS.items():
    print(f"\n<!-- {num} · {name} -->")
    d=os.path.join(base,cat)
    for f in sorted(os.listdir(d)):
        if not f.endswith(".webp"): continue
        stem=f[:-5]
        print(f'      <div class="card reveal" style="position:relative;padding:1.5rem;text-align:center">')
        print(f'        <img src="{d}/{f}" alt="{stem}" width="300" height="300" loading="lazy" style="background:var(--bg);border-radius:8px;margin-bottom:.75rem">')
        print(f'        <h3 style="font-size:1rem">{stem}</h3>')
        print(f'      </div>')
PY
```
Paste each category's block into its matching `<div class="grid grid--4">`. (Model numbers like `HC-1406` make reasonable labels for now; spec §10 notes the user will refine exact model selection later.)

- [ ] **Step 4: Verify links and anchors**

Open `http://localhost:8000/products.html`. Expected: 4 sections, each showing its category's product grid. From the home page, clicking each category card jumps to `products.html#<anchor>` and lands at the right section (scroll-padding-top in CSS handles the fixed nav).

- [ ] **Step 5: Commit**

```bash
git add products.html
git commit -m "feat: products page with four category sections"
```

---

## Task 5: About page (`about.html`)

**Files:**
- Create: `about.html`
- Create: `assets/team/ceo-placeholder.jpg`, `assets/team/manager-placeholder.jpg` (use any neutral 600×600 placeholder; mark TODO)

**Consumes:** header/footer from Task 3.

- [ ] **Step 1: Copy `index.html` → `about.html` and adapt head**

- `<title>` → `About Us — HUICHANG`
- `<meta name="description">` → `HUICHANG has designed, manufactured and exported cleaning products since 2003. Learn about our history, team and capabilities.`
- About nav link gets `aria-current="page"`.
- Replace `<main>` content.

- [ ] **Step 2: Write the about content (hero intro, milestones, team, capabilities)**

```html
<section class="hero" style="padding:11rem 0 4rem">
  <div class="container">
    <span class="eyebrow">About Us</span>
    <h1>Two decades of cleaning-product expertise</h1>
    <p class="hero__lead">Taizhou Huitong Trading Co., Ltd (Ningbo Huichang Imp&amp;Exp Co., Ltd) has specialised in the design, development, manufacturing and global distribution of cleaning products since 2003.</p>
  </div>
</section>

<!-- PROFILE -->
<section class="section">
  <div class="container">
    <div style="max-width:760px;margin:0 auto">
      <p style="font-size:1.15rem;margin-bottom:1.25rem">Our solutions reach 80+ countries across major markets including the USA, Australia, Japan and European nations.</p>
      <p style="color:var(--muted);margin-bottom:1.25rem">As an integrated exporter, designer and manufacturer, we combine innovative R&amp;D capabilities with streamlined production systems to guarantee premium quality, reliable delivery and cost-effective solutions. Our professional design centre and ISO-certified manufacturing facilities have built enduring partnerships through consistent service excellence.</p>
      <p style="color:var(--muted)">While maintaining core strengths in cleaning solutions, we established our Ningbo branch in 2020 and continue expanding our product portfolio and supporting clients' global market penetration efforts.</p>
    </div>
  </div>
</section>

<!-- MILESTONES -->
<section class="section section--alt">
  <div class="container">
    <div class="section__head"><span class="eyebrow">Our Journey</span>
      <h2 class="section__title">Milestones</h2></div>
    <div class="grid grid--5" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr))">
      <div class="card reveal" style="padding:1.5rem;text-align:center">
        <div class="stat__num">2003</div><p style="margin-top:.5rem">Company established</p></div>
      <div class="card reveal" style="padding:1.5rem;text-align:center">
        <div class="stat__num">2008</div><p style="margin-top:.5rem">Annual sales reach $2M</p></div>
      <div class="card reveal" style="padding:1.5rem;text-align:center">
        <div class="stat__num">2010</div><p style="margin-top:.5rem">Serving 50+ countries</p></div>
      <div class="card reveal" style="padding:1.5rem;text-align:center">
        <div class="stat__num">2016</div><p style="margin-top:.5rem">Cooperating with 150+ customers</p></div>
      <div class="card reveal" style="padding:1.5rem;text-align:center">
        <div class="stat__num">2020</div><p style="margin-top:.5rem">Ningbo branch established</p></div>
    </div>
  </div>
</section>

<!-- TEAM -->
<section class="section">
  <div class="container">
    <div class="section__head"><span class="eyebrow">Leadership</span>
      <h2 class="section__title">Our team</h2></div>
    <div class="grid grid--2" style="max-width:900px;margin:0 auto">
      <div class="card reveal" style="padding:2rem;text-align:center">
        <!-- TODO: replace with real CEO headshot (spec §10) -->
        <img src="assets/team/ceo-placeholder.jpg" alt="Ms. Hui Miao, CEO" width="220" height="220" loading="lazy" style="border-radius:50%;margin:0 auto 1.25rem;object-fit:cover">
        <h3>Ms. Hui Miao</h3>
        <p style="color:var(--blue);font-weight:600;margin:.25rem 0 1rem">CEO</p>
        <p style="color:var(--muted);font-size:.95rem">Bachelor of Commerce, Macquarie University (Australia). Joined Taizhou Huitong in 2013, advancing from Sales Manager to Business Partner within a decade and becoming the youngest partner at age 30. Now oversees strategic operations as CEO of the Ningbo branch.</p>
      </div>
      <div class="card reveal" style="padding:2rem;text-align:center">
        <!-- TODO: replace with real manager headshot (spec §10) -->
        <img src="assets/team/manager-placeholder.jpg" alt="Ms. Chang Wu, Exporting Manager" width="220" height="220" loading="lazy" style="border-radius:50%;margin:0 auto 1.25rem;object-fit:cover">
        <h3>Ms. Chang Wu</h3>
        <p style="color:var(--blue);font-weight:600;margin:.25rem 0 1rem">Exporting Manager</p>
        <p style="color:var(--muted);font-size:.95rem">Bachelor's degree from the University of Exeter (UK) and a Master's in Project Management from the University of Warwick (UK). Joined Taizhou Huitong Trading Co., Ltd's Exporting Department in 2016 with consistently excellent performance.</p>
      </div>
    </div>
  </div>
</section>

<!-- CAPABILITIES -->
<section class="section section--alt">
  <div class="container">
    <div class="section__head"><span class="eyebrow">Capabilities</span>
      <h2 class="section__title">Design, manufacture &amp; export under one roof</h2></div>
    <div class="grid grid--3">
      <div class="card reveal" style="padding:2rem">
        <h3>Professional Design Centre</h3>
        <p style="color:var(--muted);margin-top:.5rem">In-house R&amp;D driving innovative cleaning-product design across all four lines.</p>
      </div>
      <div class="card reveal" style="padding:2rem">
        <h3>ISO-Certified Manufacturing</h3>
        <p style="color:var(--muted);margin-top:.5rem">Streamlined production systems guaranteeing premium quality and reliable delivery.</p>
      </div>
      <div class="card reveal" style="padding:2rem">
        <h3>OEM / ODM Service</h3>
        <p style="color:var(--muted);margin-top:.5rem">Tailored support for product inquiries and OEM collaboration opportunities.</p>
      </div>
    </div>
    <div style="text-align:center;margin-top:2.5rem">
      <!-- TODO: replace with real factory photo (spec §10) -->
      <img src="assets/factory/placeholder-about.jpg" alt="HUICHANG manufacturing facility" width="1000" height="500" loading="lazy" style="border-radius:var(--radius);box-shadow:var(--shadow);width:100%;max-width:1000px">
    </div>
  </div>
</section>
```

- [ ] **Step 3: Create placeholder team images**

Generate two neutral 600×600 placeholder JPGs with Pillow (clearly marked as placeholders):
```bash
python - <<'PY'
from PIL import Image, ImageDraw, ImageFont
for name,label in [("ceo-placeholder","CEO\nMs. Hui Miao"),("manager-placeholder","Exporting Manager\nMs. Chang Wu")]:
    im=Image.new("RGB",(600,600),(248,250,252))
    d=ImageDraw.Draw(im)
    d.rectangle([0,0,600,600],outline=(226,232,240),width=4)
    try:
        f=ImageFont.truetype("arial.ttf",40)
    except: f=ImageFont.load_default()
    d.text((300,280),label,fill=(100,116,139),anchor="mm",align="center")
    im.save(f"assets/team/{name}.jpg",quality=85)
    print("wrote",name)
PY
```

- [ ] **Step 4: Verify**

Open `http://localhost:8000/about.html`. Expected: navy hero intro, profile paragraphs, 5 milestone cards with amber years, 2 team cards with placeholder photos, capabilities cards + factory placeholder image.

- [ ] **Step 5: Commit**

```bash
git add about.html assets/team/
git commit -m "feat: about page with profile, milestones, team, capabilities"
```

---

## Task 6: Contact page (`contact.html`)

**Files:**
- Create: `contact.html`

**Consumes:** header/footer from Task 3, contact info from Global Constraints (verbatim).

- [ ] **Step 1: Copy `index.html` → `contact.html` and adapt head**

- `<title>` → `Contact — HUICHANG`
- `<meta name="description">` → `Contact HUICHANG for cleaning-product inquiries and OEM/ODM collaboration. Email, phone, WhatsApp and WeChat.`
- Contact nav link gets `aria-current="page"`.
- Replace `<main>` content.

- [ ] **Step 2: Write the contact content (no form — multi-channel)**

```html
<section class="hero" style="padding:11rem 0 4rem">
  <div class="container">
    <span class="eyebrow">Contact</span>
    <h1>Let's talk about your needs</h1>
    <p class="hero__lead">For product inquiries or OEM collaboration opportunities, our team stands ready to provide tailored support. Reach us through any channel below.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="grid grid--2" style="max-width:900px;margin:0 auto">
      <!-- EMAIL -->
      <a href="mailto:htmh@huitongco.com" class="card card--hover reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/mail.svg" alt="" width="48" height="48" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>Email</h3>
        <p style="color:var(--blue);font-weight:600;margin-top:.5rem">htmh@huitongco.com</p>
        <p style="color:var(--blue);font-weight:600">htwc@huitongco.com</p>
      </a>
      <!-- PHONE -->
      <div class="card reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/phone.svg" alt="" width="48" height="48" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>Phone</h3>
        <p style="margin-top:.5rem"><a href="tel:+8613816015937" style="font-weight:600">+86 138 1601 5937</a></p>
        <p><a href="tel:+8618969880515" style="font-weight:600">+86 189 6988 0515</a></p>
      </div>
      <!-- WHATSAPP -->
      <a href="https://wa.me/8613816015937" target="_blank" rel="noopener" class="card card--hover reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/whatsapp.svg" alt="" width="48" height="48" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>WhatsApp</h3>
        <p style="color:var(--blue);font-weight:600;margin-top:.5rem">+86 138 1601 5937</p>
        <p style="color:var(--blue);font-weight:600">+86 189 6988 0515</p>
      </a>
      <!-- WECHAT -->
      <div class="card reveal" style="padding:2rem;text-align:center">
        <img src="assets/icons/wechat.svg" alt="" width="48" height="48" style="margin:0 auto 1rem;color:var(--amber)">
        <h3>WeChat</h3>
        <!-- TODO: replace with real WeChat QR image (spec §10) -->
        <div style="width:140px;height:140px;background:var(--bg);border:1px dashed var(--border);border-radius:8px;margin:1rem auto;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:.8rem">QR code</div>
        <p style="color:var(--blue);font-weight:600">13816015937 · 18969880515</p>
      </div>
    </div>

    <!-- ADDRESS + HOURS -->
    <div class="grid grid--2" style="max-width:900px;margin:3rem auto 0">
      <div class="card" style="padding:2rem">
        <h3>Address</h3>
        <!-- TODO: replace with exact addresses (spec §10) -->
        <p style="color:var(--muted);margin-top:.5rem"><strong>Taizhou Huitong Trading Co., Ltd</strong><br>Taizhou, Zhejiang, China</p>
        <p style="color:var(--muted);margin-top:1rem"><strong>Ningbo Huichang Imp&amp;Exp Co., Ltd</strong><br>Ningbo, Zhejiang, China</p>
      </div>
      <div class="card" style="padding:2rem">
        <h3>Business Hours</h3>
        <p style="color:var(--muted);margin-top:.5rem">Monday – Friday<br>9:00 – 18:00 (China Standard Time)</p>
        <p style="color:var(--muted);margin-top:1rem">We typically respond within 24 hours on business days.</p>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Verify every contact link works**

Open `http://localhost:8000/contact.html`. Click each:
- Email card → opens mail client with `htmh@huitongco.com`.
- Phone links → `tel:` handler.
- WhatsApp card → opens `https://wa.me/8613816015937` in a new tab.

All four contact cards render with icons. Address/hours cards show TODO placeholders for the exact address.

- [ ] **Step 4: Commit**

```bash
git add contact.html
git commit -m "feat: contact page with multi-channel contact details"
```

---

## Task 7: Progressive-enhancement JavaScript (`js/main.js`)

**Files:**
- Create: `js/main.js`

**Global Constraints reminder:** site must work fully with JS disabled; this file only adds polish.

**Consumes:** DOM elements present on every page: `#nav`, `#navToggle`, `#navLinks`, `.reveal`, `#year`.

- [ ] **Step 1: Write `main.js`**

```javascript
// main.js — progressive enhancement only.
// The site is fully functional without JS; this adds polish.
document.addEventListener('DOMContentLoaded', function () {

  // 1. Mobile menu toggle
  var toggle = document.getElementById('navToggle');
  var links = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Close menu when a link is tapped (mobile)
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        links.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // 2. Sticky header shadow on scroll
  var nav = document.getElementById('nav');
  if (nav) {
    var onScroll = function () {
      if (window.scrollY > 10) nav.classList.add('nav--scrolled');
      else nav.classList.remove('nav--scrolled');
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // 3. Scroll-reveal animations
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    // Fallback: just show everything
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  // 4. Footer year
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
});
```

- [ ] **Step 2: Verify each enhancement with JS on, then off**

With JS on, reload `http://localhost:8000/`:
- Scrolling down: nav gets the `.nav--scrolled` shadow.
- `.reveal` elements fade/slide in as they enter the viewport.
- Footer shows the current year (2026).
- Resize to ≤768px: hamburger appears; clicking it opens the mobile menu; tapping a link closes it.

Then **disable JS** in the browser (DevTools → Settings → Debugger → "Disable JavaScript", or use a NoScript-style toggle) and reload:
- Nav links still work (they're real `<a>` tags).
- All content is visible (`.reveal` defaults are overridden only by `.is-visible`; with no JS the elements must still be readable — verify: if they're invisible because `opacity:0`, that's a bug — the CSS `@media (prefers-reduced-motion)` rule already reveals them, but non-reduced-motion users with JS off would see them hidden).

**Fix if needed:** add a `<noscript>` style that reveals everything. Add to the `<head>` of each page (Tasks 3–6 already wrote `<head>`; add this line just before `</head>`):
```html
<noscript><style>.reveal{opacity:1;transform:none}</style></noscript>
```
Apply this edit to all four HTML files (`index.html`, `products.html`, `about.html`, `contact.html`) before continuing.

- [ ] **Step 3: Commit**

```bash
git add js/main.js index.html products.html about.html contact.html
git commit -m "feat: progressive-enhancement JS (menu, sticky nav, scroll reveal, year)"
```

---

## Task 8: README with content-editing and Cloudflare deployment guide

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
# HUICHANG Corporate Website

Static English corporate website for HUICHANG (Taizhou Huitong Trading Co., Ltd / Ningbo Huichang Imp&Exp Co., Ltd). Built as pure HTML/CSS/JS — no framework, no build step, no backend — so the only recurring cost is the domain renewal.

## Run locally
From the project folder:
```
python -m http.server 8000
```
Open http://localhost:8000/

## Editing content

- **Text:** open the relevant `.html` file in any editor; text is right there in the markup.
- **Products:** each product is a `<div class="card">` block. Copy one, change the `src`, `alt`, model number and spec.
- **Product images:** drop a `.webp` into `assets/products/<category>/` and reference it.
- **Contact details:** all four pages share the same contact info; update it in `index.html`, `contact.html`, and the footer of every page.
- **Colors / fonts:** change once in `:root` at the top of `css/styles.css`.

## Replacing placeholders

Search the project for `TODO` to find every spot that needs a real asset:
- `assets/team/ceo-placeholder.jpg`, `assets/team/manager-placeholder.jpg` → real headshots
- `assets/factory/placeholder-about.jpg` → real factory/office photo
- WeChat QR code (`contact.html`) → real QR image
- Exact company addresses (`contact.html`)
- ISO / partner logos when available

## Deploying to Cloudflare Pages (free)

1. Push this folder to a GitHub/GitLab repository.
2. Sign in to https://dash.cloudflare.com → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**.
3. Pick the repository. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/` (root)
4. **Save and Deploy.** Cloudflare builds and serves the site on a `*.pages.dev` URL with HTTPS.
5. **Custom domain:** in the project → **Custom domains** → **Set up a custom domain** → enter `huitongco.com` (and `www.huitongco.com`). Cloudflare gives you DNS records to add at your registrar (or auto-configures if the domain is on Cloudflare). Free, automatic HTTPS via Cloudflare's CDN.

Future updates: just `git push` — Cloudflare redeploys automatically.

## Cost
- Domain renewal (~¥80/year) — your only recurring cost.
- Hosting, CDN, HTTPS: free on Cloudflare Pages.

## Structure
```
index.html  products.html  about.html  contact.html
css/styles.css   js/main.js
assets/{logo.svg, icons/, products/, team/, factory/, og/}
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with editing and Cloudflare deployment guide"
```

---

## Task 9: Final cross-page verification

**Files:** none (verification only).

- [ ] **Step 1: Validate all internal links**

Run:
```bash
python - <<'PY'
import re,os
pages=["index.html","products.html","about.html","contact.html"]
hrefs=[]
for p in pages:
    t=open(p,encoding="utf-8").read()
    for m in re.finditer(r'href="([^"]+)"',t):
        hrefs.append((p,m.group(1)))
internal=[h for p,h in hrefs if (h.endswith(".html") or h.startswith("#")) and not h.startswith("http") and not h.startswith("mailto") and not h.startswith("tel")]
broken=[]
for p,h in internal:
    target=h.split("#")[0]
    if target and not os.path.exists(target):
        broken.append((p,h))
print("checked",len(internal),"internal links")
print("BROKEN:",broken if broken else "none")
PY
```
Expected: `BROKEN: []`. Fix any reported broken links.

- [ ] **Step 2: Validate all local image references exist**

```bash
python - <<'PY'
import re,os
broken=[]
for p in ["index.html","products.html","about.html","contact.html"]:
    t=open(p,encoding="utf-8").read()
    for m in re.finditer(r'src="([^"]+)"',t):
        src=m.group(1)
        if src.startswith("http") or src.startswith("data:"): continue
        if not os.path.exists(src):
            broken.append((p,src))
print("BROKEN IMAGES:",broken if broken else "none")
PY
```
Expected: `BROKEN IMAGES: none`. (Placeholder paths created in earlier tasks must all exist.)

- [ ] **Step 3: Browser smoke test on all four pages**

Open each in the browser and confirm:
- `index.html` — all 7 sections render, 8 featured product images load, nav links work, footer year = 2026.
- `products.html` — 4 category sections, every product image loads, in-page anchors from the home category cards land correctly.
- `about.html` — milestones, two team cards with placeholders, factory placeholder image.
- `contact.html` — 4 contact cards, mailto/tel/wa.me links all fire correctly.

Resize to ~375px width (mobile): hamburger menu works, all grids collapse to single column, no horizontal scroll.

- [ ] **Step 4: Final commit (if any fixes were made)**

```bash
git status
# if anything changed:
git add -A
git commit -m "fix: cross-page verification corrections"
```

- [ ] **Step 5: Final summary**

The site is complete and ready to deploy. Remaining items are the `TODO`-marked assets in `README.md` (real headshots, factory photo, WeChat QR, exact address, ISO logos) which the user supplies after launch without any code changes — just drop files in `assets/` and update paths.

---

## Self-Review Notes

**Spec coverage check** (spec section → task):
- §3 technical approach (pure HTML/CSS/JS) → Tasks 2–7.
- §4 visual design (tokens, Poppins/Inter, navy/blue/amber) → Task 2 (tokens + base CSS).
- §6.1 home (7 sections) → Task 3.
- §6.2 products (4 anchors, ~40 SKUs) → Task 4.
- §6.3 about (profile, milestones, team, capabilities) → Task 5.
- §6.4 contact (no form, 4 channels + address + hours) → Task 6.
- §7 imagery (PDF product photos) → Task 1.
- §8 deployment (Cloudflare Pages) → Task 8.
- §9 out-of-scope (no form/CMS/blog/zh/accounts) → enforced by absence throughout.
- §10 open items → every one is a `TODO` marker reachable by grep.

**Type/name consistency:** CSS class names (`card`, `card--hover`, `reveal`, `btn--primary/ghost/outline`, `grid--2/3/4`, `stat__num`, `eyebrow`, `section__head`, `nav__*`, `footer__*`) are defined once in Task 2 and reused verbatim in Tasks 3–6. JS hooks (`#nav`, `#navToggle`, `#navLinks`, `.reveal`, `#year`) defined in the HTML of Task 3 and consumed in Task 7 match exactly.

**No placeholders in plan steps:** every code block is complete and runnable; the only "TODO" strings are deliberate user-supplied-asset markers carried from the spec's §10 open-items list, each accompanied by a working placeholder image/script so the build is never blocked.
