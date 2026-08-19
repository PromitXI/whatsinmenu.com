#!/usr/bin/env python3
"""Generate one WhatsInMenu photograph per dish with Gemini 3.1 Flash Image.

The API key is read from the repository's git-ignored .env or GEMINI_API_KEY.
By default this generates every individual dish across today's three choices.
Use --date YYYY-MM-DD for another menu, --id DISH_ID (repeatable) for specific
dishes, or --all for the catalogue.
Existing images are preserved unless --force is supplied.
"""
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

from generate_menu import DISHES, generate_for_date

MODEL = "gemini-3.1-flash-image"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
OUTPUT_DIR = REPO_ROOT / "web" / "assets" / "dishes"
IST = ZoneInfo("Asia/Kolkata")
STYLE_PATH = REPO_ROOT / "config" / "image_style.json"


def load_dotenv(path=REPO_ROOT / ".env"):
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_style():
    style = json.loads(STYLE_PATH.read_text())
    if style.get("model") != MODEL:
        raise ValueError(f"config/image_style.json must keep model set to {MODEL}")
    return style


def all_catalogue_dishes():
    for category in ("bengali", "chinese", "otherIndian"):
        for kind in ("protein", "vegetable"):
            yield from DISHES[category][kind]


def prompt_for(dish, style):
    avoid = "; ".join(style["avoid"])
    return (
        f"{style['promptTemplate'].replace('{name}', dish['name'])} {style['look']} "
        "Close food-focused square frame with this single dish clearly visible and recognizable. "
        f"Avoid: {avoid}. No other prepared dishes in the frame. ABSOLUTELY NO visible words, captions, "
        "dish labels, typography, or graphic overlays anywhere in the image."
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


def generate(dish, style, api_key, force=False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / f"{dish['id']}.jpg"
    if target.exists() and not force:
        print(f"Keeping existing {target.relative_to(REPO_ROOT)}")
        return
    payload = {
        "model": MODEL,
        "input": prompt_for(dish, style),
        "response_format": {
            "type": "image",
            "mime_type": "image/jpeg",
            "aspect_ratio": "1:1",
            "image_size": "1K",
        },
    }
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as result:
            response = json.load(result)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini request failed ({error.code}): {detail}") from error
    target.write_bytes(base64.b64decode(extract_image_data(response)))
    print(f"Generated {target.relative_to(REPO_ROOT)} with {MODEL}")


def selected_dishes(args):
    catalogue = list(all_catalogue_dishes())
    if args.all:
        return catalogue
    if args.id:
        requested = set(args.id)
        selected = [dish for dish in catalogue if dish["id"] in requested]
        missing = requested - {dish["id"] for dish in selected}
        if missing:
            raise ValueError("Unknown dish IDs: " + ", ".join(sorted(missing)))
        return selected
    date_str = args.date or datetime.now(IST).strftime("%Y-%m-%d")
    choices = generate_for_date(date_str)["choices"]
    return list({dish["id"]: dish for choice in choices for dish in choice["dishes"]}.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Generate every dish across the three choices for YYYY-MM-DD")
    parser.add_argument("--id", action="append", help="Generate one dish ID; may be repeated")
    parser.add_argument("--all", action="store_true", help="Generate the full catalogue")
    parser.add_argument("--force", action="store_true", help="Replace existing generated images")
    args = parser.parse_args()
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Add GEMINI_API_KEY=your_key to the repository's .env file.")
    style = load_style()
    for dish in selected_dishes(args):
        generate(dish, style, api_key, args.force)


if __name__ == "__main__":
    main()
