"""Render the site's link preview card and icons from art/preview.html and art/favicon.html, with a
headless Edge or Chrome (they load the logo's fonts from Google Fonts, so this needs a connection).

    python art/render_images.py

Writes docs/preview.png (1200 x 630), docs/favicon.png (32), docs/apple-touch-icon.png (180)
and docs/favicon.ico (16, 32, 48).
"""
import os
import shutil
import subprocess
import tempfile
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs")
BROWSERS = (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            shutil.which("google-chrome") or "", shutil.which("chromium") or "")


def shoot(page, size, out, transparent=False):
    browser = next(b for b in BROWSERS if b and os.path.exists(b))
    with tempfile.TemporaryDirectory() as profile:
        args = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                f"--window-size={size[0]},{size[1]}", "--virtual-time-budget=8000", f"--screenshot={out}"]
        if transparent:
            args.append("--default-background-color=00000000")
        subprocess.run(args + ["file:///" + os.path.join(HERE, page).replace("\\", "/")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(120):            # Edge's launcher can return before the page is drawn
            if os.path.exists(out) and os.path.getsize(out):
                break
            time.sleep(0.25)
        time.sleep(0.5)
        img = Image.open(out)
        img.load()
        return img.convert("RGBA")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        card = shoot("preview.html", (1200, 630), os.path.join(tmp, "card.png")).crop((0, 0, 1200, 630))
        card.convert("RGB").save(os.path.join(DOCS, "preview.png"), optimize=True)
        icon = shoot("favicon.html", (512, 512), os.path.join(tmp, "icon.png"), transparent=True).crop((0, 0, 512, 512))
    icon.resize((32, 32), Image.LANCZOS).save(os.path.join(DOCS, "favicon.png"), optimize=True)
    icon.resize((180, 180), Image.LANCZOS).save(os.path.join(DOCS, "apple-touch-icon.png"), optimize=True)
    icon.save(os.path.join(DOCS, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    print("wrote docs/preview.png, favicon.png, apple-touch-icon.png, favicon.ico")


if __name__ == "__main__":
    main()
