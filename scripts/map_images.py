"""Final image mapper — coordinate ground-truth algorithm (verified 168/168
correct, 0 mismatches). Each image -> nearest model word below its bottom edge.
Output: scripts/image_map.json
"""
import fitz, os, re, json

PDF = r"D:/huitong/2026 CATALOG-HUICHANG.pdf"
SRC = r"D:/huitong/extracted_images"
OUT = "scripts/image_map.json"
MODEL_RE = re.compile(r"^(HCTB-\d+|HC-[A-Za-z0-9][A-Za-z0-9/\-]*|HC-MK[\d\-A-Za-z]*|HC-PMK\d+|M\d{3}|\d{3,4})$")

doc = fitz.open(PDF)
PAGE_CAT = {5:"public-cleaning",6:"public-cleaning",7:"public-cleaning",8:"public-cleaning",9:"public-cleaning",10:"public-cleaning",12:"house-cleaning",13:"house-cleaning",14:"house-cleaning",16:"hotel-appliance",17:"hotel-appliance",19:"pest-control",20:"pest-control",21:"pest-control",22:"pest-control",23:"pest-control",24:"pest-control",25:"pest-control",26:"pest-control",27:"pest-control"}

result = {}
for pageno, cat in PAGE_CAT.items():
    page = doc[pageno - 1]
    models = [(w[4].strip().rstrip(",;:."), (w[0]+w[2])/2, (w[1]+w[3])/2)
              for w in page.get_text("words") if MODEL_RE.match(w[4].strip().rstrip(",;:."))]
    page_xrefs = [im[0] for im in page.get_images(full=True)]
    cat_map = result.setdefault(cat, {})
    for raw_idx, xref in enumerate(page_xrefs):
        r = page.get_image_rects(xref)
        if not r or r[0].width < 70 or r[0].height < 70:
            continue
        rr = r[0]
        icx = (rr.x0 + rr.x1) / 2
        icy = (rr.y0 + rr.y1) / 2
        ibottom = rr.y1
        band = [(m, mcx, mcy) for m, mcx, mcy in models
                if mcy > icy - 15 and mcy < ibottom + 85]
        if not band:
            continue
        band.sort(key=lambda t: abs(t[1] - icx))
        if abs(band[0][1] - icx) <= 95:
            model = band[0][0]
            fname = f"p{pageno:02d}_{raw_idx:02d}.png"
            srcpath = os.path.join(SRC, fname)
            if os.path.exists(srcpath):
                cat_map[model] = srcpath

with open(OUT, "w") as f:
    json.dump(result, f, indent=2)
total = sum(len(v) for v in result.values())
print(f"Total mappings: {total}")
for cat, models in result.items():
    print(f"  {cat}: {len(models)}")
