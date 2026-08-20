#!/usr/bin/env python3
"""Build WhatsInMenu's image manifest and discover reusable food photos.

Existing site photography is catalogued locally. Discovery uses Wikimedia
Commons because each result exposes machine-readable creator and licence data.
Discovered photos are never published automatically: a person must first
confirm that the picture is actually the named dish and mark it approved in
data/image_repository.json.
"""

import argparse
import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATALOG_PATH = ROOT / "data" / "dishes.json"
SEEDS_PATH = ROOT / "data" / "image_search_seeds.csv"
DATABASE_PATH = ROOT / "data" / "image_repository.json"
DISH_IMAGE_DIR = ROOT / "web" / "assets" / "dishes"
LIBRARY_DIR = ROOT / "web" / "assets" / "repository"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "WhatsInMenuImageLibrary/1.0 (https://github.com/PromitXI/whatsinmenu.com)"
ALLOWED_LICENSE_MARKERS = ("cc0", "cc by", "cc-by", "public domain")
STOP_WORDS = {
    "and", "style", "recipe", "indian", "punjabi", "bengali", "food",
    "the", "with", "dish", "curry", "masala", "machher", "machh", "da",
    "di", "ka", "ki", "er",
}


def clean_html(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def slug(value):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def tokens(value):
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 1 and token not in STOP_WORDS}


def catalogue_records():
    catalog = json.loads(CATALOG_PATH.read_text())
    style = json.loads((ROOT / "config" / "image_style.json").read_text())
    records = []
    for cuisine, section in catalog.items():
        if not isinstance(section, dict) or "protein" not in section:
            continue
        for collection in (section.get("protein", []), section.get("vegetable", [])):
            for dish in collection:
                relative = Path("web") / "assets" / "dishes" / f"{dish['id']}.jpg"
                exists = (ROOT / relative).exists()
                records.append({
                    "dishId": dish["id"],
                    "dishName": dish["name"],
                    "cuisine": cuisine,
                    "status": "available" if exists else "missing",
                    "shownOnWebsite": exists,
                    "localPath": str(relative) if exists else None,
                    "sourceType": "ai_generated" if exists else None,
                    "model": style.get("model") if exists else None,
                    "promptStyle": "config/image_style.json" if exists else None,
                    "externalAttributionRequired": False,
                })
    return sorted(records, key=lambda item: item["dishId"])


def seed_records():
    with SEEDS_PATH.open(newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def metadata_value(metadata, name):
    return clean_html((metadata.get(name) or {}).get("value", ""))


def allowed_license(short_name):
    value = short_name.lower()
    return any(marker in value for marker in ALLOWED_LICENSE_MARKERS) and "-nc" not in value and "-nd" not in value


def match_score(dish_name, title):
    expected = tokens(dish_name)
    found = tokens(title.removeprefix("File:"))
    return round(len(expected & found) / max(1, len(expected)), 3)


def discover_one(seed):
    query = f"{seed['dish_name']} {seed['cuisine']} cuisine"
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "8",
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata",
        "iiurlwidth": "1000",
        "origin": "*",
    }
    url = f"{COMMONS_API}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            pages = json.load(response).get("query", {}).get("pages", [])
    except Exception as error:  # network failures remain visible in the database
        return {**seed, "query": query, "status": "search_error", "error": str(error)}

    candidates = []
    for page in pages:
        info = (page.get("imageinfo") or [{}])[0]
        metadata = info.get("extmetadata") or {}
        license_name = metadata_value(metadata, "LicenseShortName")
        mime = info.get("mime", "")
        score = match_score(seed["dish_name"], page.get("title", ""))
        if mime not in {"image/jpeg", "image/png", "image/webp"} or not allowed_license(license_name):
            continue
        candidates.append({
            "score": score,
            "fileTitle": page.get("title"),
            "sourcePage": info.get("descriptionurl"),
            "originalUrl": info.get("url"),
            "previewUrl": info.get("thumburl") or info.get("url"),
            "creator": metadata_value(metadata, "Artist") or "See source page",
            "credit": metadata_value(metadata, "Credit"),
            "license": license_name,
            "licenseUrl": metadata_value(metadata, "LicenseUrl"),
            "attribution": metadata_value(metadata, "Attribution"),
        })
    candidates.sort(key=lambda item: item["score"], reverse=True)
    if not candidates or candidates[0]["score"] < 0.34:
        return {**seed, "query": query, "status": "no_confident_match", "candidates": candidates[:3]}
    return {
        **seed,
        "query": query,
        "status": "candidate_found",
        "reviewStatus": "needs_visual_review",
        "publishable": False,
        "candidate": candidates[0],
        "alternatives": candidates[1:3],
    }


def discover(seeds, workers):
    output = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        jobs = {executor.submit(discover_one, seed): seed for seed in seeds}
        for number, future in enumerate(as_completed(jobs), start=1):
            output.append(future.result())
            if number % 25 == 0:
                print(f"Searched {number}/{len(seeds)} dishes")
    return sorted(output, key=lambda item: (item["cuisine"], item["dish_name"]))


def download_approved(records):
    downloaded = 0
    for record in records:
        if record.get("reviewStatus") != "approved" or not record.get("candidate"):
            continue
        candidate = record["candidate"]
        url = candidate.get("previewUrl")
        extension = Path(urllib.parse.urlparse(url).path).suffix.lower()
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            extension = ".jpg"
        target_dir = LIBRARY_DIR / record["cuisine"]
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{slug(record['dish_name'])}{extension}"
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response:
            target.write_bytes(response.read())
        record["localPath"] = str(target.relative_to(ROOT))
        record["status"] = "downloaded"
        record["publishable"] = True
        downloaded += 1
        time.sleep(0.1)
    return downloaded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover", action="store_true", help="Search Wikimedia Commons for all selected seed dishes")
    parser.add_argument("--discover-catalog", action="store_true", help="Search for missing images in the live dish catalogue")
    parser.add_argument("--cuisine", choices=("bengali", "punjabi"), help="Limit discovery to one seed group")
    parser.add_argument("--max-dishes", type=int, help="Limit discovery while testing")
    parser.add_argument("--workers", type=int, default=4, choices=range(1, 9))
    parser.add_argument("--download-approved", action="store_true", help="Download only records manually marked approved")
    args = parser.parse_args()

    previous = json.loads(DATABASE_PATH.read_text()) if DATABASE_PATH.exists() else {}
    site_images = catalogue_records()
    seeds = seed_records()
    if args.cuisine:
        seeds = [seed for seed in seeds if seed["cuisine"] == args.cuisine]
    if args.max_dishes:
        seeds = seeds[:args.max_dishes]

    discoveries = previous.get("discoveredImages", [])
    if args.discover:
        newly_discovered = discover(seeds, args.workers)
        selected_keys = {(item["cuisine"], item["dish_name"]) for item in seeds}
        discoveries = [item for item in discoveries if (item["cuisine"], item["dish_name"]) not in selected_keys]
        discoveries.extend(newly_discovered)
        discoveries.sort(key=lambda item: (item["cuisine"], item["dish_name"]))
    elif not discoveries:
        discoveries = [{**seed, "status": "not_searched"} for seed in seed_records()]

    if args.download_approved:
        print(f"Downloaded {download_approved(discoveries)} approved seed images")

    catalog_candidates = previous.get("catalogCandidates", [])
    if args.discover_catalog:
        missing = [{"cuisine": item["cuisine"], "dish_name": item["dishName"], "dishId": item["dishId"]} for item in site_images if item["status"] == "missing"]
        catalog_candidates = discover(missing, args.workers)
    if args.download_approved:
        print(f"Downloaded {download_approved(catalog_candidates)} approved catalogue images")

    database = {
        "schemaVersion": 1,
        "policy": {
            "discoverySource": "Wikimedia Commons",
            "automaticPublishing": False,
            "approvalRule": "Confirm the image depicts the named dish, then set reviewStatus to approved before download.",
            "attributionRule": "Keep creator, sourcePage, license, and licenseUrl visible wherever an external image is published.",
        },
        "siteImages": site_images,
        "catalogCandidates": catalog_candidates,
        "discoveredImages": discoveries,
    }
    DATABASE_PATH.write_text(json.dumps(database, indent=2, ensure_ascii=False) + "\n")
    available = sum(item["status"] == "available" for item in database["siteImages"])
    found = sum(item["status"] == "candidate_found" for item in discoveries)
    print(f"Catalogued {available}/{len(database['siteImages'])} current site images; {found}/{len(discoveries)} reusable candidates found")


if __name__ == "__main__":
    main()
