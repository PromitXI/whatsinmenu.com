#!/usr/bin/env python3
"""
Renders an Instagram-ready 1080x1080 PNG for a given date's first meal choice, using
Playwright + the pre-installed Chromium (no external image-gen API needed).

This is a styled branded graphic, not an AI food photograph. Actual meal
photographs are generated separately with Gemini 3.1 Flash Image.

Usage:
    python3 render_insta_image.py 2026-08-18 out.png
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
from generate_menu import build_daily_payload, SOURCES

TEMPLATE = (REPO_ROOT / "web" / "insta_template.html").read_text()


def render(date_str: str, out_path: str):
    payload = build_daily_payload(date_str)
    t = payload["today"]
    protein, side_one, side_two = t["choices"][0]["dishes"]
    src = SOURCES.get(protein.get("sourceSite"), {}).get("name", "trusted source")

    html = (
        TEMPLATE
        .replace("{{DATE}}", date_str)
        .replace("{{CATEGORY}}", t["categoryLabel"])
        .replace("{{PROTEIN}}", protein["name"])
        .replace("{{SIDE_ONE}}", side_one["name"])
        .replace("{{SIDE_TWO}}", side_two["name"])
        .replace("{{SOURCE}}", src)
    )
    tmp_html = REPO_ROOT / "_render_tmp.html"
    tmp_html.write_text(html)

    try:
        with sync_playwright() as p:
            executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
            browser = p.chromium.launch(**({"executable_path": executable} if executable else {}))
            page = browser.new_page(viewport={"width": 1080, "height": 1080})
            page.goto(f"file://{tmp_html}")
            page.screenshot(path=out_path)
            browser.close()
    finally:
        tmp_html.unlink(missing_ok=True)
    print(f"Saved {out_path} for {date_str}: {protein['name']} + {side_one['name']} + {side_two['name']}")


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else "2026-08-18"
    out_arg = sys.argv[2] if len(sys.argv) > 2 else "insta_preview.png"
    render(date_arg, out_arg)
