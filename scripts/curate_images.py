"""One-off: curate product photos from extracted PDF images into assets/products/.
Run: python scripts/curate_images.py  (from project root)
"""
import os
from PIL import Image

SRC = r"D:/huitong/extracted_images"
DST = "assets/products"
MAX_EDGE = 1000

# (source_filename, category_dir, model_name)
# Sizes verified to be real product photos (>25KB, reasonable dimensions)
SELECTION = [
    # PUBLIC CLEANING
    ("p05_05.png", "public-cleaning", "HC-1305"),       # 381x485 sensor soap dispenser
    ("p05_06.png", "public-cleaning", "HC-NSD01"),      # 431x431
    ("p06_05.png", "public-cleaning", "HC-1409M"),      # manual soap dispenser
    ("p06_06.png", "public-cleaning", "HC-1201"),
    ("p08_03.png", "public-cleaning", "HC-CZ01"),       # paper dispenser
    ("p08_11.png", "public-cleaning", "HC-AK59"),
    ("p10_03.png", "public-cleaning", "HC-WS-H-M250"),  # hand dryer
    ("p10_01.png", "public-cleaning", "HC-WS-S130H"),
    ("p10_09.png", "public-cleaning", "HC-WS-S988"),
    ("p10_11.png", "public-cleaning", "HC-WS-S6666"),
    # HOUSE CLEANING
    ("p12_01.png", "house-cleaning", "HC-6126"),        # brush
    ("p12_02.png", "house-cleaning", "HC-6127"),
    ("p12_03.png", "house-cleaning", "HC-6121"),
    ("p12_05.png", "house-cleaning", "HC-6168"),
    ("p13_01.png", "house-cleaning", "sponge-01"),      # sponge
    ("p13_05.png", "house-cleaning", "sponge-02"),
    ("p14_01.png", "house-cleaning", "cloth-nw-01"),    # cloth
    ("p14_05.png", "house-cleaning", "cloth-mf-01"),
    # HOTEL APPLIANCE
    ("p16_01.png", "hotel-appliance", "kettle-01"),     # kettle
    ("p16_03.png", "hotel-appliance", "kettle-02"),
    ("p17_03.png", "hotel-appliance", "hairdryer-hs"),  # hair dryer (large)
    ("p17_01.png", "hotel-appliance", "hairdryer-02"),
    # PEST CONTROL
    ("p19_01.png", "pest-control", "mousetrap-201"),    # wood mouse trap
    ("p19_03.png", "pest-control", "mousetrap-203"),
    ("p20_01.png", "pest-control", "mousetrap-608"),    # plastic mouse trap
    ("p20_03.png", "pest-control", "mousetrap-610"),
    ("p22_03.png", "pest-control", "HC-MK10"),          # mosquito lamp
    ("p22_01.png", "pest-control", "HC-MK20"),
    ("p23_01.png", "pest-control", "HC-MK09"),
    ("p24_01.png", "pest-control", "insect-F01B"),      # insect trap
]

def process(src_name, cat, model):
    src_path = os.path.join(SRC, src_name)
    if not os.path.exists(src_path):
        print(f"  MISSING source: {src_path}")
        return False
    out_dir = os.path.join(DST, cat)
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(src_path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
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
