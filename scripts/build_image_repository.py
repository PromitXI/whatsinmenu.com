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
PUBLIC_LIBRARY_PATH = ROOT / "web" / "image-library.json"
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
QUERY_CUISINE = {
    "bengali": "Bengali",
    "punjabi": "Punjabi",
    "chinese": "Indo-Chinese",
    "andhra": "Andhra",
    "southIndian": "South Indian",
    "otherIndian": "North Indian",
}
CURATED_COMMONS_TITLES = {
    "b_v_08": "File:Mochar ghonto-MB04.jpg",
    "o_p_01": "File:Rajma..JPG",
    "o_p_02": "File:Chana-Masala.jpg",
    "o_p_05": "File:Paneer Butter Masala - The Indismart Hotel - Salt Lake City - Kolkata 2023-08-13 3304.jpg",
    "o_v_01": "File:Palak Paneer (Cottage cheese in spinach gravy).jpg",
    "o_v_02": "File:Aaloo Gobhi.JPG",
    "o_v_04": "File:Mixed vegetable curry 1.jpg",
    "o_v_05": "File:Jeera rice.jpg",
    "o_v_06": "File:Fried Masala Papad.jpg",
    "o_v_07": "File:Boondi Raita.jpg",
    "o_v_08": "File:Kachumber Salad.JPG",
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
    query = f"{seed['dish_name']} {QUERY_CUISINE.get(seed['cuisine'], seed['cuisine'])} food"
    curated_title = CURATED_COMMONS_TITLES.get(seed.get("dishId"))
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata",
        "iiurlwidth": "1000",
        "origin": "*",
    }
    if curated_title:
        params["titles"] = curated_title
        query = curated_title
    else:
        params.update({"generator": "search", "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": "8"})
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
        score = 1.0 if curated_title else match_score(seed["dish_name"], page.get("title", ""))
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
        target = target_dir / f"{record.get('dishId') or slug(record['dish_name'])}{extension}"
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        if not target.exists():
            for attempt in range(5):
                try:
                    with urllib.request.urlopen(request, timeout=60) as response:
                        target.write_bytes(response.read())
                    break
                except Exception:
                    if attempt == 4:
                        raise
                    time.sleep(5)
        record["localPath"] = str(target.relative_to(ROOT))
        record["status"] = "downloaded"
        record["publishable"] = True
        downloaded += 1
        time.sleep(0.1)
    return downloaded


def write_public_library(records):
    approved = {}
    for record in records:
        candidate = record.get("candidate") or {}
        if not record.get("publishable") or not record.get("localPath") or not record.get("dishId"):
            continue
        approved[record["dishId"]] = {
            "imagePath": record["localPath"].removeprefix("web/"),
            "creator": candidate.get("creator") or "See source",
            "sourcePage": candidate.get("sourcePage"),
            "license": candidate.get("license"),
            "licenseUrl": candidate.get("licenseUrl"),
        }
    PUBLIC_LIBRARY_PATH.write_text(json.dumps(approved, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover", action="store_true", help="Search Wikimedia Commons for all selected seed dishes")
    parser.add_argument("--discover-catalog", action="store_true", help="Search for missing images in the live dish catalogue")
    parser.add_argument("--cuisine", choices=("bengali", "punjabi"), help="Limit discovery to one seed group")
    parser.add_argument("--max-dishes", type=int, help="Limit discovery while testing")
    parser.add_argument("--workers", type=int, default=4, choices=range(1, 9))
    parser.add_argument("--download-approved", action="store_true", help="Download only records manually marked approved")
    parser.add_argument("--approve", action="append", default=[], metavar="DISH_ID", help="Approve a visually reviewed catalogue candidate")
    args = parser.parse_args()

    previous = json.loads(DATABASE_PATH.read_text()) if DATABASE_PATH.exists() else {}
    site_images = catalogue_records()
    seeds = seed_records()
    if args.cuisine:
        seeds = [seed for seed in seeds if seed["cuisine"] == args.cuisine]
    if args.max_dishes:
        seeds = seeds[:args.max_dishes]

    all_seed_keys = {(item["cuisine"], item["dish_name"]) for item in seed_records()}
    discoveries = [item for item in previous.get("discoveredImages", []) if (item["cuisine"], item["dish_name"]) in all_seed_keys]
    if args.discover:
        newly_discovered = discover(seeds, args.workers)
        selected_keys = {(item["cuisine"], item["dish_name"]) for item in seeds}
        discoveries = [item for item in discoveries if (item["cuisine"], item["dish_name"]) not in selected_keys]
        discoveries.extend(newly_discovered)
        discoveries.sort(key=lambda item: (item["cuisine"], item["dish_name"]))
    else:
        existing_keys = {(item["cuisine"], item["dish_name"]) for item in discoveries}
        discoveries.extend({**seed, "status": "not_searched"} for seed in seed_records() if (seed["cuisine"], seed["dish_name"]) not in existing_keys)
        discoveries.sort(key=lambda item: (item["cuisine"], item["dish_name"]))

    if args.download_approved:
        print(f"Downloaded {download_approved(discoveries)} approved seed images")

    catalog_candidates = previous.get("catalogCandidates", [])
    if args.discover_catalog:
        missing = [{"cuisine": item["cuisine"], "dish_name": item["dishName"], "dishId": item["dishId"]} for item in site_images if item["status"] == "missing"]
        prior_approved = {item.get("dishId"): item for item in catalog_candidates if item.get("reviewStatus") == "approved"}
        catalog_candidates = [prior_approved.get(item.get("dishId"), item) for item in discover(missing, args.workers)]
    approved_ids = set(args.approve)
    known_ids = {item.get("dishId") for item in catalog_candidates}
    unknown_ids = approved_ids - known_ids
    if unknown_ids:
        raise SystemExit("No discovered catalogue candidate for: " + ", ".join(sorted(unknown_ids)))
    for record in catalog_candidates:
        if record.get("dishId") in approved_ids:
            record["reviewStatus"] = "approved"
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
    write_public_library(catalog_candidates)
    available = sum(item["status"] == "available" for item in database["siteImages"])
    found = sum(item["status"] == "candidate_found" for item in discoveries)
    print(f"Catalogued {available}/{len(database['siteImages'])} current site images; {found}/{len(discoveries)} reusable candidates found")


if __name__ == "__main__":
    main()
