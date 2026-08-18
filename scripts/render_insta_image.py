#!/usr/bin/env python3
"""
Renders an Instagram-ready 1080x1080 PNG for a given date's Option 1, using
Playwright + the pre-installed Chromium (no external image-gen API needed).

This is a styled branded graphic, not an AI photo of the actual dish — a
real food photo would need an image-gen API key (OpenAI/Gemini), which
Promit hasn't provided yet. This is the no-extra-cost placeholder so the
Instagram posting pipeline can be demoed end-to-end today.

Usage:
    python3 render_insta_image.py 2026-08-18 out.png
"""
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
    opt = t["options"][0]
    src = SOURCES.get(opt["protein"].get("sourceSite"), {}).get("name", "trusted source")

    html = (
        TEMPLATE
        .replace("{{DATE}}", date_str)
        .replace("{{CATEGORY}}", t["categoryLabel"])
        .replace("{{PROTEIN}}", opt["protein"]["name"])
        .replace("{{VEGETABLE}}", opt["vegetable"]["name"])
        .replace("{{SOURCE}}", src)
    )
    tmp_html = REPO_ROOT / "_render_tmp.html"
    tmp_html.write_text(html)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.goto(f"file://{tmp_html}")
        page.screenshot(path=out_path)
        browser.close()
    tmp_html.unlink()
    print(f"Saved {out_path} for {date_str}: {opt['protein']['name']} + {opt['vegetable']['name']}")


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else "2026-08-18"
    out_arg = sys.argv[2] if len(sys.argv) > 2 else "insta_preview.png"
    render(date_arg, out_arg)
