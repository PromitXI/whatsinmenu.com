#!/usr/bin/env python3
"""Generate WhatsInMenu dish photography with Gemini 3.1 Flash Image.

The API key is read only from GEMINI_API_KEY. By default this generates the
three dishes for today's deterministic menu. Use --date YYYY-MM-DD for another
menu, --id DISH_ID (repeatable) for specific dishes, or --all for the catalogue.
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


def all_catalogue_dishes():
    for category in ("bengali", "chinese", "otherIndian"):
        for kind in ("protein", "vegetable"):
            yield from DISHES[category][kind]


def prompt_for(dish):
    return (
        f"Editorial overhead food photograph of {dish['name']}, served as everyday Indian home cooking. "
        "Warm natural window light, realistic food texture, simple cream ceramic bowl or plate on a worn "
        "wooden table, restrained chilli-red and dark-green textile accents, gently nostalgic magazine mood. "
        "The food must look achievable in a family kitchen rather than restaurant-plated. No people, no hands, "
        "no text, no lettering, no logo, no watermark added by the scene, no collage. Square composition."
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


def generate(dish, api_key, force=False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / f"{dish['id']}.jpg"
    if target.exists() and not force:
        print(f"Keeping existing {target.relative_to(REPO_ROOT)}")
        return
    payload = {
        "model": MODEL,
        "input": prompt_for(dish),
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
    return generate_for_date(date_str)["dishes"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Generate the three dishes for YYYY-MM-DD")
    parser.add_argument("--id", action="append", help="Generate one dish ID; may be repeated")
    parser.add_argument("--all", action="store_true", help="Generate the full catalogue")
    parser.add_argument("--force", action="store_true", help="Replace existing generated images")
    args = parser.parse_args()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Set GEMINI_API_KEY in your environment before generating images.")
    for dish in selected_dishes(args):
        generate(dish, api_key, args.force)


if __name__ == "__main__":
    main()
