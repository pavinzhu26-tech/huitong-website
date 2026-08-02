"""Apply scripts/image_map.json: process each mapped source PNG into a webp in
assets/products/<cat>/ named by a safe slug, and patch assets/products.js so
each matched SKU's `img` field points to that slug.

A safe slug is derived from the model number (lowercased, non-alnum -> '-'),
because some models contain '/' or spaces. We also record the mapping
model -> slug so products.js can be updated deterministically.

Run from D:/zhipu/Huichangwebsite:  python scripts/apply_image_map.py
"""
import json, os, re
from PIL import Image

IMGMAP = "scripts/image_map.json"
PROD_JS = "assets/products.js"
DST = "assets/products"
MAX_EDGE = 800

CATS = {
    "public-cleaning": "public",
    "house-cleaning": "house",
    "hotel-appliance": "hotel",
    "pest-control": "pest",
}

def slug(model):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(model)).strip("-").lower()
    return s or "item"

def process(src, cat, model):
    if not os.path.exists(src):
        return None
    out_dir = os.path.join(DST, cat)
    os.makedirs(out_dir, exist_ok=True)
    s = slug(model)
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    w, h = im.size
    scale = MAX_EDGE / max(w, h)
    if scale < 1:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    webp = os.path.join(out_dir, s + ".webp")
    im.save(webp, "WEBP", quality=82)
    return s

imgmap = json.load(open(IMGMAP))

# Build { cat_id: { model: slug } }
patched = {}
total_proc = 0
for cat_folder, models in imgmap.items():
    cat_id = CATS.get(cat_folder)
    if not cat_id:
        continue
    patched[cat_id] = {}
    for model, src in models.items():
        sl = process(src, cat_folder, model)
        if sl:
            patched[cat_id][model] = sl
            total_proc += 1
print(f"Processed {total_proc} images into {DST}")

# Patch assets/products.js: for each SKU, if model in patch map, set img: slug
js = open(PROD_JS, encoding="utf-8").read()

def patch_sku(js_text, model, slugval):
    """Find a sku object literal containing model: "MODEL" and ensure it has img: "slug".
    Handles two shapes:
      { model: "HC-1305",   spec: "...", img: "HC-1305" }   (already has img)
      { model: "HC-1305",   spec: "..." }                    (no img)
    We normalize the img value to slugval."""
    # escape model for regex
    mpat = re.escape(model)
    # match the model field plus optional spec plus optional existing img, up to closing }
    pattern = re.compile(
        r'(\{\s*model:\s*"' + mpat + r'"\s*,\s*spec:\s*"[^"]*"\s*)(,\s*img:\s*"[^"]*")?(\s*\})'
    )
    def repl(mo):
        return mo.group(1) + ', img: "' + slugval + '"' + mo.group(3)
    new_text, n = pattern.subn(repl, js_text, count=1)
    return new_text, n

changes = 0
for cat_id, models in patched.items():
    for model, sl in models.items():
        js, n = patch_sku(js, model, sl)
        changes += n

open(PROD_JS, "w", encoding="utf-8").write(js)
print(f"Patched {changes} SKU img fields in {PROD_JS}")
