"""Ground-truth verifier: for each catalog page, build the CORRECT image->model
mapping purely from PyMuPDF coordinates (image bbox vs model word bbox), then
compare against scripts/image_map.json and report discrepancies.

Correct rule: each image -> the model word whose y-center is below the image's
bottom edge (within 80px) AND whose x-center is closest. This is deterministic
and treats the coordinate data as ground truth.
"""
import fitz, re, json, os

PDF = r"D:/huitong/2026 CATALOG-HUICHANG.pdf"
doc = fitz.open(PDF)

MODEL_RE = re.compile(r"^(HCTB-\d+|HC-[A-Za-z0-9][A-Za-z0-9/\-]*|HC-MK[\d\-A-Za-z]*|HC-PMK\d+|M\d{3}|\d{3,4})$")

def ground_truth(pageno):
    page = doc[pageno - 1]
    models = [(w[4].strip().rstrip(",;:."), (w[0]+w[2])/2, (w[1]+w[3])/2)
              for w in page.get_text("words") if MODEL_RE.match(w[4].strip().rstrip(",;:."))]
    page_xrefs = [im[0] for im in page.get_images(full=True)]
    imgs = []
    for raw_idx, xref in enumerate(page_xrefs):
        r = page.get_image_rects(xref)
        if r and r[0].width > 70 and r[0].height > 70:
            rr = r[0]
            imgs.append((f"p{pageno:02d}_{raw_idx:02d}", (rr.x0+rr.x1)/2, (rr.y0+rr.y1)/2, rr.y1))
    correct = {}
    for fname, icx, icy, ibottom in imgs:
        band = [(m, mcx, mcy) for m, mcx, mcy in models
                if mcy > icy - 15 and mcy < ibottom + 85]
        if not band:
            continue
        band.sort(key=lambda t: abs(t[1] - icx))
        if abs(band[0][1] - icx) <= 95:
            correct[fname] = band[0][0]
    return correct

PAGE_CAT = {5:"public-cleaning",6:"public-cleaning",7:"public-cleaning",8:"public-cleaning",9:"public-cleaning",10:"public-cleaning",12:"house-cleaning",13:"house-cleaning",14:"house-cleaning",16:"hotel-appliance",17:"hotel-appliance",19:"pest-control",20:"pest-control",21:"pest-control",22:"pest-control",23:"pest-control",24:"pest-control",25:"pest-control",26:"pest-control",27:"pest-control"}

mymap = json.load(open("scripts/image_map.json"))

total_correct = 0
total_mismatch = 0
total_missed = 0
mismatch_details = []
for pageno, cat in PAGE_CAT.items():
    gt = ground_truth(pageno)
    cat_map = mymap.get(cat, {})
    my_for_page = {os.path.basename(v).replace(".png",""): k for k, v in cat_map.items() if f"p{pageno:02d}_" in v}
    for fname, corr_model in gt.items():
        my_model = my_for_page.get(fname)
        if my_model is None:
            total_missed += 1
        elif my_model == corr_model:
            total_correct += 1
        else:
            total_mismatch += 1
            mismatch_details.append((fname, my_model, corr_model))

print(f"Correct: {total_correct}")
print(f"Mismatched: {total_mismatch}")
print(f"Missed (ground truth had a match, mine didn't): {total_missed}")
print()
if mismatch_details:
    print("=== MISMATCHES (mine vs correct) ===")
    for fname, mine, corr in mismatch_details:
        print(f"  {fname}: mine={mine}  correct={corr}")
