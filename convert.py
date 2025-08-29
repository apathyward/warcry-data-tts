import os
import cairosvg

SVG_DIR = "images/svgs"
PNG_DIR = "images/pngs"

os.makedirs(PNG_DIR, exist_ok=True)

for filename in os.listdir(SVG_DIR):
    if filename.lower().endswith(".svg"):
        svg_path = os.path.join(SVG_DIR, filename)
        png_path = os.path.join(PNG_DIR, filename.replace(".svg", ".png"))
        print(f"Converting {svg_path} -> {png_path}")
        cairosvg.svg2png(url=svg_path, write_to=png_path)
