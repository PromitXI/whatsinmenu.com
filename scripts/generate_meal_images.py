#!/usr/bin/env python3
"""Generate one complete-meal image for each of the day's three choices."""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
from generate_menu import generate_for_date

MODEL = "gemini-3.1-flash-image"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
STYLE_PATH = REPO_ROOT / "config" / "image_style.json"
OUTPUT_DIR = REPO_ROOT / "web" / "assets" / "meals"
IST = ZoneInfo("Asia/Kolkata")


def load_dotenv(path=REPO_ROOT / ".env"):
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def load_style():
    style = json.loads(STYLE_PATH.read_text())
    if style.get("model") != MODEL:
        raise ValueError(f"config/image_style.json must keep model set to {MODEL}")
    return style


def prompt_for(choice, style):
    dishes = ", ".join(dish["name"] for dish in choice["dishes"])
    avoid = "; ".join(style["avoid"])
    return (
        f"Create one photorealistic image for {choice['label']}, a complete Indian home dinner containing exactly: {dishes}. "
        f"{style['direction']} {style['composition']} {style['lighting']} {style['palette']} "
        f"Avoid: {avoid}. ABSOLUTELY NO visible words, captions, dish labels, typography, or graphic overlays anywhere in the image."
    )


def extract_image_data(response):
    direct = response.get("output_image") or {}
    if direct.get("data"):
        return direct["data"]
    for step in response.get("steps", []):
        for block in step.get("content", []):
            if block.get("type") == "image" and block.get("data"):
                return block["data"]
    raise ValueError("Gemini returned no image data")


def generate(choice, date_str, style, api_key, force=False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / f"{date_str}-choice-{choice['label'].split()[-1]}.jpg"
    if target.exists() and not force:
        print(f"Keeping existing {target.relative_to(REPO_ROOT)}")
        return
    payload = {
        "model": MODEL,
        "input": prompt_for(choice, style),
        "response_format": {
            "type": "image",
            "mime_type": "image/jpeg",
            "aspect_ratio": style["aspectRatio"],
            "image_size": style["imageSize"],
        },
    }
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": api_key}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as result:
            response = json.load(result)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini request failed ({error.code}): {detail}") from error
    target.write_bytes(base64.b64decode(extract_image_data(response)))
    print(f"Generated {target.relative_to(REPO_ROOT)} with {MODEL}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Menu date in YYYY-MM-DD; defaults to today in Kolkata")
    parser.add_argument("--choice", type=int, choices=(1, 2, 3), help="Generate only one numbered choice")
    parser.add_argument("--force", action="store_true", help="Replace existing images")
    args = parser.parse_args()
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Add GEMINI_API_KEY=your_key to the repository's .env file.")
    date_str = args.date or datetime.now(IST).strftime("%Y-%m-%d")
    style = load_style()
    choices = generate_for_date(date_str)["choices"]
    if args.choice:
        choices = [choices[args.choice - 1]]
    for choice in choices:
        generate(choice, date_str, style, api_key, args.force)


if __name__ == "__main__":
    main()
