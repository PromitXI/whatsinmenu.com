#!/usr/bin/env python3
"""
WhatsInMenu — daily menu generator.

Two-stage pipeline, framed the way Promit asked for (an "agentic" decision,
kept deterministic/rule-based rather than live LLM calls so the webapp,
WhatsApp send, and Instagram post always agree on the same day's answer):

  MOTHER AGENT — sets the household rules before anything is picked:
    - Ilish (hilsa) is banned outright — too expensive.
    - Weekly protein budget: chicken up to 3x/week, fish/seafood 1x/week,
      mutton ~once every other week (~1-2x/month), rest filled with
      egg / paneer / lentil.
    - Skips anything on the wife/kid dislike list.
    - Skips "complex" multi-step recipes (separate mincing, grilling,
      multi-component assembly) — standard one-pan/one-pot home cooking only.

  COOK AGENT — from what the Mother agent allows, picks the actual dishes:
    - Builds 3 distinct protein+vegetable combos for the day.
    - Attaches a short shopping/ingredient list to each combo.
    - Flags anything that needs advance prep (soak/marinate) a day ahead.

Everything is deterministic per date (seeded hash of the date string) so the
webapp (client-side JS mirror) and any scheduled WhatsApp/Instagram send
always compute the exact same answer independently, with no shared database.

Usage:
    python3 generate_menu.py                # today, in Asia/Kolkata
    python3 generate_menu.py 2026-08-20      # specific date
"""
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from prng import rng_for_date, fisher_yates, mulberry32, hash_seed

REPO_ROOT = Path(__file__).parent.parent
DISHES = json.loads((REPO_ROOT / "data" / "dishes.json").read_text())
EXCLUSIONS = json.loads((REPO_ROOT / "config" / "exclusions.json").read_text())
IST = ZoneInfo("Asia/Kolkata")

# Change this if the real go-live date differs — it anchors both the
# 10-day "no Chinese yet" cold start AND the weekly protein-budget cycle.
LAUNCH_DATE = date(2026, 8, 18)
COLD_START_DAYS = 10
OPTIONS_PER_DAY = 3
# "Once a year" dishes (festival specials, and later Promit's own list of
# rare/expensive dishes) never show up before this many days from launch.
FESTIVAL_GATE_DAYS = 100
FESTIVALS = DISHES.get("festivals", [])
FESTIVAL_SPECIALS = DISHES.get("festivalSpecials", {})

CATEGORY_LABELS = {
    "bengali": "Bengali",
    "chinese": "Chinese",
    "otherIndian": "North Indian",
}
SPICE_ICON = {"mild": "🌶️", "medium": "🌶️🌶️", "spicy": "🌶️🌶️🌶️"}
SOURCES = DISHES.get("sources", {})

# Which category(ies) can supply each protein family.
FAMILY_CATEGORIES = {
    "fish": ["bengali"],
    "mutton": ["bengali"],
    "egg": ["bengali"],
    "chicken": ["bengali", "chinese", "otherIndian"],
    "paneer": ["otherIndian"],
    "lentil": ["otherIndian"],
}
# How often a "chicken" day leans Bengali vs Chinese vs North Indian —
# tuned so the week still lands close to the ~70-75% Bengali target once
# the fish/mutton/egg days (always Bengali) are added in.
CHICKEN_CATEGORY_WEIGHTS = [("bengali", 0.70), ("chinese", 0.20), ("otherIndian", 0.10)]


# ---------- helpers ----------

def _excluded_terms():
    return list(EXCLUSIONS.get("disliked_by_wife", [])) + list(EXCLUSIONS.get("disliked_by_kid", []))


def _is_excluded(dish, excluded_terms):
    if not excluded_terms:
        return False
    hay = f"{dish['id']} {dish['name']}".lower()
    return any(term.lower() in hay for term in excluded_terms if term.strip())


def _mother_agent_filter(dishes, excluded_terms, allow_complex=False):
    """Mother agent: drop excluded/complex dishes. Ilish is already fully
    removed from data/dishes.json, so no runtime check needed for that."""
    out = [d for d in dishes if not _is_excluded(d, excluded_terms)]
    if not allow_complex:
        out = [d for d in out if d.get("complexity") != "complex"]
    return out or dishes  # never return an empty pool


def _week_index(date_str: str) -> int:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (d - LAUNCH_DATE).days // 7


def _day_offset_in_week(date_str: str) -> int:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (d - LAUNCH_DATE).days % 7


def weekly_protein_plan(week_index: int):
    """Mother agent's weekly protein budget, shuffled onto the 7 days of
    that week. Mutton appears on every OTHER week (~1-2x/month)."""
    base = ["chicken", "chicken", "chicken", "fish", "egg", "paneer"]
    seventh = "mutton" if week_index % 2 == 0 else "paneer"
    families = base + [seventh]
    rng = mulberry32(hash_seed(f"week-{week_index}"))
    return fisher_yates(rng, families)


def _is_cold_start(date_str: str) -> bool:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return 0 <= (d - LAUNCH_DATE).days < COLD_START_DAYS


def _festival_gate_open(date_str: str) -> bool:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (d - LAUNCH_DATE).days >= FESTIVAL_GATE_DAYS


def get_festival_special(date_str: str):
    """Returns {festivalName, dish} if today is a known festival AND the
    100-day gate has passed, else None. Only ONE festival is matched per day."""
    if not _festival_gate_open(date_str):
        return None
    for fest in FESTIVALS:
        if fest["date"] == date_str:
            special = FESTIVAL_SPECIALS.get(fest["specialId"])
            if special:
                return {"festivalName": fest["name"], "dish": special}
    return None


def _category_for_chicken(rng) -> str:
    r = rng()
    acc = 0.0
    for cat, weight in CHICKEN_CATEGORY_WEIGHTS:
        acc += weight
        if r < acc:
            return cat
    return CHICKEN_CATEGORY_WEIGHTS[-1][0]


def _combo(protein, vegetable):
    needs_advance_prep = bool(protein.get("advancePrep") or vegetable.get("advancePrep"))
    prep_notes = [d.get("prepNote") for d in (protein, vegetable) if d.get("advancePrep") and d.get("prepNote")]
    ingredients = sorted(set((protein.get("ingredients") or []) + (vegetable.get("ingredients") or [])))
    return {
        "protein": protein,
        "vegetable": vegetable,
        "needsAdvancePrep": needs_advance_prep,
        "prepNotes": prep_notes,
        "ingredients": ingredients,
    }


def generate_for_date(date_str: str) -> dict:
    excluded = _excluded_terms()
    cold_start = _is_cold_start(date_str)

    # --- Mother agent: decide today's protein family + category ---
    week_index = _week_index(date_str)
    day_offset = _day_offset_in_week(date_str)
    family = weekly_protein_plan(week_index)[day_offset]

    rng = rng_for_date(date_str)  # day-level rng, independent of the week-level rng above
    if family == "chicken":
        category = _category_for_chicken(rng)
    else:
        category = FAMILY_CATEGORIES[family][0]

    if cold_start and category == "chinese":
        category = "bengali"  # cold-start override: no Chinese in the first 10 days

    # --- Cook agent: pick actual dishes within what Mother allows ---
    protein_pool = _mother_agent_filter(DISHES[category]["protein"], excluded)
    veg_pool = _mother_agent_filter(DISHES[category]["vegetable"], excluded)

    family_pool = [d for d in protein_pool if d.get("proteinFamily") == family]
    lead_pool = family_pool or protein_pool  # fall back if the family has no dish in this category

    proteins_shuffled = fisher_yates(rng, protein_pool)
    # Make sure the family-matching dish leads the list (Option 1 honours the weekly budget).
    lead = fisher_yates(rng, lead_pool)[0]
    ordered_proteins = [lead] + [p for p in proteins_shuffled if p["id"] != lead["id"]]

    n = min(OPTIONS_PER_DAY, len(ordered_proteins), len(veg_pool))
    proteins = ordered_proteins[:n]
    veggies = fisher_yates(rng, veg_pool)[:n]

    options = [_combo(p, v) for p, v in zip(proteins, veggies)]

    return {
        "date": date_str,
        "category": category,
        "categoryLabel": CATEGORY_LABELS[category],
        "coldStart": cold_start,
        "proteinFamily": family,
        "options": options,
        "anyNeedsAdvancePrep": any(o["needsAdvancePrep"] for o in options),
    }


def build_daily_payload(today_str: str) -> dict:
    """What the scheduled task sends/shows: today's 3 options, plus a heads-up
    if any of TOMORROW's options need advance prep (so soaking/marinating can
    start tonight in case that's the one she picks)."""
    today = generate_for_date(today_str)
    tomorrow_date = (datetime.strptime(today_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = generate_for_date(tomorrow_date)

    return {
        "today": today,
        "advanceNoticeForTomorrow": tomorrow if tomorrow["anyNeedsAdvancePrep"] else None,
        "festiveOption": get_festival_special(today_str),
    }


def _source_line(dish: dict) -> str:
    src = SOURCES.get(dish.get("sourceSite", ""))
    spice = SPICE_ICON.get(dish.get("spiceLevel"), "")
    src_txt = f" — recipe via {src['name']}: {src['url']}" if src else ""
    return f"{spice}{src_txt}"


def format_whatsapp_message(payload: dict, group_share: bool = True) -> str:
    t = payload["today"]
    lines = [
        "🍽️ *WhatsInMenu — Today's Options*",
        f"_{t['categoryLabel']} style_" + (" _(cold-start window: Bengali/North Indian only)_" if t["coldStart"] else ""),
        "",
    ]

    fest = payload.get("festiveOption")
    if fest:
        lines.append(f"🎉 *{fest['festivalName']} Special*")
        lines.append(f"✨ {fest['dish']['name']}")
        lines.append("   🛒 " + ", ".join(fest["dish"]["ingredients"]))
        lines.append("")

    for i, opt in enumerate(t["options"], start=1):
        lines.append(f"*Option {i}*")
        lines.append(f"🍛 {opt['protein']['name']}")
        lines.append(f"   {_source_line(opt['protein'])}")
        lines.append(f"🥗 {opt['vegetable']['name']}")
        lines.append(f"   {_source_line(opt['vegetable'])}")
        lines.append("   🛒 " + ", ".join(opt["ingredients"]))
        if opt["needsAdvancePrep"] and opt["prepNotes"]:
            lines.append("   ⏰ " + "; ".join(opt["prepNotes"]))
        lines.append("")

    tomorrow = payload["advanceNoticeForTomorrow"]
    if tomorrow:
        prep_dishes = []
        for opt in tomorrow["options"]:
            if opt["needsAdvancePrep"]:
                dish_name = opt["protein"]["name"] if opt["protein"].get("advancePrep") else opt["vegetable"]["name"]
                prep_dishes.append(dish_name)
        lines.append(f"📅 *Heads up for tomorrow:* {', '.join(prep_dishes)} — if you might pick that, start prep tonight.")
        lines.append("")

    lines.append("_Recipes are sourced from Bong Eats / Sanjeev Kapoor / Hebbar's Kitchen — not AI-written._")
    if group_share:
        lines.append("Forward this to the family group 👨‍👩‍👧")
    return "\n".join(lines)


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else datetime.now(IST).strftime("%Y-%m-%d")
    result = build_daily_payload(date_arg)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n--- WhatsApp message preview ---\n")
    print(format_whatsapp_message(result))
