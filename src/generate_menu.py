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
    - Builds one complete dinner: one protein and two vegetable sides.
    - Attaches a combined shopping/ingredient list to the meal.
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
SIDES_PER_MEAL = 2
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
RECIPE_URLS = {
    "b_p_01": "https://www.bongeats.com/recipe/rui-macher-jhol",
    "b_p_03": "https://www.bongeats.com/recipe/chingri-malaikari",
    "b_p_04": "https://www.bongeats.com/recipe/mutton-kosha",
    "b_p_05": "https://www.bongeats.com/recipe/chicken-rezala",
    "b_p_06": "https://www.bongeats.com/recipe/bhetki-machher-jhol",
    "b_p_07": "https://www.bongeats.com/recipe/dimer-dalna",
    "b_p_08": "https://www.bongeats.com/recipe/murgir-lal-jhol",
    "b_p_09": "https://www.bongeats.com/recipe/katla-kalia",
    "b_p_11": "https://www.bongeats.com/recipe/chingri-bhaape",
    "b_p_12": "https://www.bongeats.com/recipe/pressure-cooker-chicken",
    "b_p_14": "https://www.bongeats.com/recipe/chicken-curry",
    "b_v_01": "https://www.bongeats.com/recipe/alu-posto",
    "b_v_02": "https://www.bongeats.com/recipe/shukto",
    "b_v_03": "https://www.bongeats.com/recipe/cholar-dal",
    "b_v_04": "https://www.bongeats.com/recipe/dhokar-dalna",
    "b_v_05": "https://www.bongeats.com/recipe/niramish-aloo-dum",
    "b_v_06": "https://www.bongeats.com/recipe/labra",
    "b_v_07": "https://www.bongeats.com/recipe/begun-bhaja",
    "b_v_08": "https://www.bongeats.com/recipe/mochar-ghonto",
    "b_v_09": "https://www.bongeats.com/recipe/palong-shaaker-ghonto",
    "b_v_10": "https://www.bongeats.com/recipe/sheemer-bhorta",
    "b_v_11": "https://www.bongeats.com/recipe/potoler-dorma-with-dal-stuffing",
    "b_v_12": "https://www.bongeats.com/recipe/palong-shaak-bhaja",
    "b_v_13": "https://www.bongeats.com/recipe/jhuri-alu-bhaja",
    "b_v_14": "https://www.bongeats.com/recipe/korola-bhaja",
    "b_v_15": "https://www.bongeats.com/recipe/bota-soho-begun-bhaja",
    "b_v_16": "https://www.bongeats.com/recipe/aloo-bhorta",
    "c_p_01": "https://www.sanjeevkapoor.com/Recipe/Chinese-Chilli-Chicken-Sirf-30-minute-FoodFood.html",
    "c_p_02": "https://www.sanjeevkapoor.com/Recipe/Lemon-Chicken.html",
    "c_p_03": "https://www.sanjeevkapoor.com/Recipe/Garlic-Chicken-Sanjeev-Kapoor-Kitchen-FoodFood.html",
    "c_p_04": "https://www.sanjeevkapoor.com/Recipe/Chicken-Manchurian.html",
    "c_p_06": "https://www.sanjeevkapoor.com/Recipe/Kung-Pao-Chicken-SK-Khazana.html",
    "c_v_01": "https://hebbarskitchen.com/veg-fried-rice-vegetable-fried-rice/",
    "c_v_02": "https://hebbarskitchen.com/hakka-noodles-recipe-veg-hakka-noodles/",
    "c_v_03": "https://hebbarskitchen.com/manchurian-gravy-recipe-veg-manchurian/",
    "c_v_04": "https://hebbarskitchen.com/chilli-garlic-fried-rice-recipe/",
    "c_v_05": "https://hebbarskitchen.com/schezwan-fried-rice-recipe-schezwan-rice/",
    "o_p_01": "https://hebbarskitchen.com/rajma-recipe-punjabi-rajma-masala/",
    "o_p_02": "https://hebbarskitchen.com/chana-masala-recipe-chickpea-masala/",
    "o_p_03": "https://hebbarskitchen.com/punjabi-dal-makhani-recipe/",
    "o_p_04": "https://www.sanjeevkapoor.com/Recipe/Butter-Chicken-Sanjeev-Kapoor-Kitchen-FoodFood.html",
    "o_p_05": "https://hebbarskitchen.com/paneer-butter-masala-recipe/",
    "o_v_01": "https://hebbarskitchen.com/palak-paneer-recipe-restaurant-style/",
    "o_v_02": "https://hebbarskitchen.com/aloo-gobi-masala-recipe-aloo-gobi-curry/",
    "o_v_03": "https://hebbarskitchen.com/bhindi-masala-recipe-bhindi-ki-gravy/",
    "o_v_04": "https://hebbarskitchen.com/mix-veg-recipe-mixed-vegetable-curry/",
}

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


def _dish_with_source(dish, role):
    enriched = dict(dish)
    source = SOURCES.get(dish.get("sourceSite"), {})
    enriched.update({
        "role": role,
        "sourceName": source.get("name", "Trusted source"),
        "recipeUrl": RECIPE_URLS.get(dish["id"], source.get("url", "")),
    })
    return enriched


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

    protein = fisher_yates(rng, lead_pool)[0]
    veggies = fisher_yates(rng, veg_pool)[:SIDES_PER_MEAL]
    dishes = [_dish_with_source(protein, "protein")]
    dishes.extend(_dish_with_source(veg, "side") for veg in veggies)
    ingredients = sorted(set(item for dish in dishes for item in dish.get("ingredients", [])))
    prep_notes = [dish.get("prepNote") for dish in dishes if dish.get("advancePrep") and dish.get("prepNote")]

    return {
        "date": date_str,
        "category": category,
        "categoryLabel": CATEGORY_LABELS[category],
        "coldStart": cold_start,
        "proteinFamily": family,
        "dishes": dishes,
        "ingredients": ingredients,
        "prepNotes": prep_notes,
        "anyNeedsAdvancePrep": any(dish.get("advancePrep") for dish in dishes),
    }


def build_daily_payload(today_str: str) -> dict:
    """Build today's complete dinner and tomorrow's advance-prep notice."""
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
    recipe_url = RECIPE_URLS.get(dish.get("id"), src.get("url", "") if src else "")
    src_txt = f" — recipe via {src['name']}: {recipe_url}" if src else ""
    return f"{spice}{src_txt}"


def format_whatsapp_message(payload: dict, group_share: bool = True) -> str:
    t = payload["today"]
    lines = [
        "🍽️ *WhatsInMenu — Tonight's Menu*",
        f"_{t['categoryLabel']} style_" + (" _(cold-start window: Bengali/North Indian only)_" if t["coldStart"] else ""),
        "",
    ]

    fest = payload.get("festiveOption")
    if fest:
        lines.append(f"🎉 *{fest['festivalName']} Special*")
        lines.append(f"✨ {fest['dish']['name']}")
        lines.append("   🛒 " + ", ".join(fest["dish"]["ingredients"]))
        lines.append("")

    for index, dish in enumerate(t["dishes"]):
        label = "Protein" if index == 0 else f"Side {index}"
        icon = "🍛" if index == 0 else "🥗"
        lines.append(f"*{label}* — {icon} {dish['name']}")
        lines.append(f"   {_source_line(dish)}")
    lines.append("")
    lines.append("🛒 *Combined shopping list:* " + ", ".join(t["ingredients"]))
    if t["prepNotes"]:
        lines.append("⏰ " + "; ".join(t["prepNotes"]))
    lines.append("")
    lines.append("*Actions:* Cook this · Swap a dish in the app · Open the combined shopping list")
    lines.append("")

    tomorrow = payload["advanceNoticeForTomorrow"]
    if tomorrow:
        prep_dishes = [dish["name"] for dish in tomorrow["dishes"] if dish.get("advancePrep")]
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
