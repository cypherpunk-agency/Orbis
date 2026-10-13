"""Equirectangular basemap textures for the WebGL underlay. Run: python3 tools/build/textures.py"""
import os
from PIL import Image
root = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = {  # name: (source file, quality)
    "satellite": ("BlueMarble_NextGeneration.jpg", 78),
    "night": ("VIIRS_Black_Marble.jpg", 82),
    "terrain": ("BlueMarble_ShadedRelief_Bathymetry.jpg", 78),
}
WIDTH = 4096  # 4096 x 2048 ≈ 9.8 km/px; keep each file under ~1 MB
for name, (src, q) in OUT.items():
    im = Image.open(os.path.join(root, ".cache/tex", src)).convert("RGB")
    im = im.resize((WIDTH, WIDTH // 2), Image.LANCZOS)
    out = os.path.join(root, "data/tex", f"{name}-{WIDTH}.webp")
    im.save(out, "WEBP", quality=q, method=6)
    print(out, os.path.getsize(out) // 1024, "KB")
