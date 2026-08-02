# HUICHANG Corporate Website

Static English corporate website for **HUICHANG** (Taizhou Huitong Trading Co., Ltd / Ningbo Huichang Imp&Exp Co., Ltd). Built as pure HTML/CSS/JS — no framework, no build step, no backend — so the only recurring cost is the domain renewal.

## Run locally

From the project folder:

```
python -m http.server 8000
```

Open http://localhost:8000/ in your browser.

## Pages

| Page | File | Purpose |
|------|------|---------|
| Home | `index.html` | Hero, stats, product categories, featured products, about teaser, why-us, CTA |
| Products | `products.html` | Four category sections (Public Cleaning, House Cleaning, Hotel Appliance, Pest Control) |
| About | `about.html` | Company profile, milestones timeline, team, capabilities |
| Contact | `contact.html` | Email / phone / WhatsApp / WeChat + address + business hours |

## Editing content

- **Text:** open the relevant `.html` file in any text editor; all copy is right there in the markup.
- **Products:** each product is a `<div class="card">` block. Copy one, then change the image `src`, `alt` text, model number and spec line.
- **Product images:** drop a `.webp` into `assets/products/<category>/` and reference it from the card.
- **Contact details:** the email/phone/WhatsApp numbers appear on the home page, contact page, and in the footer of every page — update them in all those spots if they change.
- **Colors / fonts:** change once in `:root` at the top of `css/styles.css` and the whole site updates.

## Replacing placeholders

Search the project for `TODO` to find every spot that needs a real asset:

- `assets/team/ceo-placeholder.jpg` and `assets/team/manager-placeholder.jpg` → real headshots (referenced in `about.html`).
- `assets/factory/placeholder-about.jpg` → real factory/office photo (referenced in `index.html` and `about.html`).
- WeChat QR code block in `contact.html` → replace the dashed placeholder `<div>` with `<img src="assets/wechat-qr.jpg" ...>`.
- Exact company addresses in `contact.html` → replace the "Taizhou, Zhejiang" / "Ningbo, Zhejiang" placeholder text.
- ISO / partner logos: add an image where the capabilities section is, if available.
- `assets/logo.svg`: currently a typographic "HUICHANG" wordmark — replace with the real vector logo if one is available.

## Deploying to Cloudflare Pages (free)

1. Push this folder to a GitHub or GitLab repository.
2. Sign in to https://dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
3. Pick the repository. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/` (the project root)
4. **Save and Deploy.** Cloudflare builds and serves the site on a `*.pages.dev` URL with HTTPS automatically.
5. **Custom domain:** in the project → **Custom domains** → **Set up a custom domain** → enter `huitongco.com` (and `www.huitongco.com`). Cloudflare gives you the DNS records to add at your registrar (or configures them automatically if the domain is already on Cloudflare). Free, automatic HTTPS via Cloudflare's CDN.

Future updates: just `git push` — Cloudflare redeploys automatically.

## Cost

- Domain renewal (~¥80/year) — your only recurring cost.
- Hosting, global CDN, HTTPS certificate: free on Cloudflare Pages.

## Structure

```
index.html  products.html  about.html  contact.html
css/styles.css            js/main.js
assets/
  logo.svg
  icons/                  (10 SVG UI icons)
  products/               (curated product photos, .webp + .png)
    public-cleaning/  house-cleaning/  hotel-appliance/  pest-control/
  team/                   (headshot placeholders)
  factory/                (facility photo placeholder)
scripts/curate_images.py  (one-off tool that produced the product images)
docs/superpowers/         (design spec + implementation plan)
```

## Tech notes

- **Progressive enhancement:** the site is fully usable with JavaScript disabled — every link, contact method and all text works. `js/main.js` only adds polish: a mobile menu toggle, a sticky-header shadow on scroll, scroll-reveal animations, and the footer copyright year.
- **Scroll-reveal safety:** reveal content is visible by default in CSS. JavaScript only enables the hidden start state (via `html.js-io`) when `IntersectionObserver` is confirmed supported, and a 1.2s timeout force-reveals everything as a backstop — so content is never permanently hidden regardless of observer behavior.
- **Responsive:** mobile-first; grids reflow at 768px and 1024px.
- **Accessibility:** semantic HTML5 landmarks, per-section headings, keyboard-reachable controls, WCAG-AA color contrast.
