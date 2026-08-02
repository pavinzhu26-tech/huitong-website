"""Smart extraction v2: map PDF catalog images to model numbers.
Key insight from the catalog: product photos are arranged in a grid, and each
model number sits DIRECTLY BELOW its image (e.g. "HC-61010 | 27*9.5*31cm"
appears under the beehive photo). So we match each image to the nearest model
text block whose center-x is close and whose y is BELOW the image bottom.

We extract ALL model-like tokens from the page text (including multi-model
blocks like "HC-6126 | HC-6127" and "ITEM# HC-WS-S130H"), giving each token
its own (cx, cy) anchor.

Output: scripts/image_map.json = { category: { model: src_image_path } }
Run from D:/zhipu/Huichangwebsite:  python scripts/map_images.py
"""
import fitz, os, re, json

PDF = r"D:/huitong/2026 CATALOG-HUICHANG.pdf"
SRC = r"D:/huitong/extracted_images"
OUT = "scripts/image_map.json"

# Match model tokens: HC-xxx, HCTB-xxx, HC-MKxx, bare 3-4 digit (mouse traps 201..612), Mxxx
MODEL_TOKEN = re.compile(
    r"(HCTB-\d+|HC-[A-Za-z0-9][A-Za-z0-9/\-]*|M\d{3}|\b\d{3,4}\b)"
)

doc = fitz.open(PDF)

def page_model_anchors(page):
    """All model tokens on the page with their center positions.
    For multi-token blocks (e.g. 'HC-6126 | HC-6127'), distribute centers across
    the block width proportional to each token's position."""
    anchors = []  # (model, cx, cy)
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
        toks = MODEL_TOKEN.findall(txt)
        if not toks:
            continue
        # clean tokens: strip, drop pure page-noise (4-digit years etc handled by context)
        toks = [t.strip() for t in toks]
        if not toks:
            continue
        cy = (y0 + y1) / 2
        if len(toks) == 1:
            anchors.append((toks[0], (x0 + x1) / 2, cy))
        else:
            # distribute across block width using each token's char offset
            for t in toks:
                # find horizontal position of this token in the line
                idx = txt.find(t)
                # approximate cx by linear position in block
                frac = (idx + len(t) / 2) / max(1, len(txt))
                cx = x0 + frac * (x1 - x0)
                anchors.append((t, cx, cy))
    return anchors

def page_images(page):
    """Product images with bbox + center, dedup by xref."""
    imgs = []
    seen = set()
    for im in page.get_images(full=True):
        xref = im[0]
        if xref in seen:
            continue
        seen.add(xref)
        rects = page.get_image_rects(xref)
        if not rects:
            continue
        r = rects[0]
        if r.width < 70 or r.height < 70:
            continue
        cx = (r.x0 + r.x1) / 2
        cy = (r.y0 + r.y1) / 2
        imgs.append((xref, r.x0, r.y0, r.x1, r.y1, cx, cy))
    return imgs

def match(anchors, imgs):
    """Each image -> nearest model anchor that is BELOW the image (label under photo),
    close in x. Return {model: image_index}."""
    pairs = {}
    used_anchors = set()
    # sort images by reading order (y then x) for stable assignment
    for ii, (xref, ix0, iy0, ix1, iy1, icx, icy) in enumerate(imgs):
        best = None
        best_score = None
        for ai, (model, acx, acy) in enumerate(anchors):
            if ai in used_anchors:
                continue
            if acy < iy1 - 20:  # anchor must be below (or near) image bottom
                continue
            dx = abs(acx - icx)
            dy = acy - iy1  # how far below
            if dx > 90:  # wrong column
                continue
            if dy > 90:  # too far below (next row)
                continue
            score = dx * 1.0 + dy * 0.4
            if best_score is None or score < best_score:
                best_score = score
                best = (ai, model)
        if best is not None:
            used_anchors.add(best[0])
            pairs[best[1]] = ii
    return pairs

PAGE_CAT = {
    5: "public-cleaning", 6: "public-cleaning", 7: "public-cleaning",
    8: "public-cleaning", 9: "public-cleaning", 10: "public-cleaning",
    12: "house-cleaning", 13: "house-cleaning", 14: "house-cleaning",
    16: "hotel-appliance", 17: "hotel-appliance",
    19: "pest-control", 20: "pest-control", 21: "pest-control",
    22: "pest-control", 23: "pest-control", 24: "pest-control",
    25: "pest-control", 26: "pest-control", 27: "pest-control",
}

result = {}
stats = []
for pageno, cat in PAGE_CAT.items():
    page = doc[pageno - 1]
    anchors = page_model_anchors(page)
    imgs = page_images(page)
    pairs = match(anchors, imgs)
    # resolve image index -> extracted filename pNN_XX.png
    page_xrefs = [im[0] for im in page.get_images(full=True)]
    cat_map = result.setdefault(cat, {})
    for model, img_idx in pairs.items():
        xref, ix0, iy0, ix1, iy1, icx, icy = imgs[img_idx]
        try:
            raw_idx = page_xrefs.index(xref)
        except ValueError:
            continue
        fname = f"p{pageno:02d}_{raw_idx:02d}.png"
        srcpath = os.path.join(SRC, fname)
        if os.path.exists(srcpath):
            # normalize model (strip trailing slash/spaces)
            m = model.strip().rstrip("-/").strip()
            cat_map[m] = srcpath
    stats.append((pageno, cat, len(anchors), len(imgs), len(pairs)))

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)

print("page | cat              | anchors | imgs | matched")
for pageno, cat, na, ni, nm in stats:
    print(f" {pageno:2d}  | {cat:16s} | {na:7d} | {ni:4d} | {nm:4d}")
total = sum(len(v) for v in result.values())
print(f"\nTotal model->image mappings: {total}")
for cat, models in result.items():
    print(f"  {cat}: {len(models)} models with images")
