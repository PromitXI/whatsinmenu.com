#!/usr/bin/env python3
"""
WhatsInMenu — daily menu generator.

Two-stage pipeline, framed the way Promit asked for (an "agentic" decision,
kept deterministic/rule-based rather than live LLM calls so the webapp,
WhatsApp send, and Instagram post always agree on the same day's answer):

  MOTHER AGENT — sets the household rules before anything is picked:
    - Ilish (hilsa) is banned outright — too expensive.
    - Weekly protein budget: chicken up to 3x/week, fish/seafood 1x/week,
      mutton on the fourth Sunday only (at most once/month), rest filled with
      egg / paneer / lentil.
    - Skips anything on the wife/kid dislike list.
    - Skips "complex" multi-step recipes (separate mincing, grilling,
      multi-component assembly) — standard one-pan/one-pot home cooking only.

  COOK AGENT — from what the Mother agent allows, picks the actual dishes:
    - Builds three complete dinner choices, each with three coordinated dishes.
    - Attaches a combined shopping/ingredient list to every choice.
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
OWNER_EXAMPLE_DATE = "2026-08-19"
OWNER_EXAMPLE_CHOICES = [
    ["b_p_15", "b_v_17", "b_v_21"],
    ["b_p_16", "b_v_02", "b_v_19"],
    ["b_p_17", "b_v_09", "b_v_07"],
]
# "Once a year" dishes (festival specials, and later Promit's own list of
# rare/expensive dishes) never show up before this many days from launch.
FESTIVAL_GATE_DAYS = 100
FESTIVALS = DISHES.get("festivals", [])
FESTIVAL_SPECIALS = DISHES.get("festivalSpecials", {})

CATEGORY_LABELS = {
    "bengali": "Bengali",
    "chinese": "Chinese",
    "otherIndian": "North Indian",
    "andhra": "Andhra",
    "southIndian": "South Indian",
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
    "b_p_15": "https://mitarcooking.com/dim-posto/",
    "b_p_16": "https://atanurrannagharrecipe.com/easy-simple-chicken-curry-recipe/",
    "b_p_17": "https://www.spicypunch.com/doi-maach-recipe/",
    "b_v_01": "https://notoutofthebox.in/2014/08/aloo-posto/",
    "b_v_02": "https://www.bongeats.com/recipe/shukto",
    "b_v_03": "https://experiencesofagastronomad.com/narkol-diye-cholar-dal-bengali-chana-dal-with-fried-coconut-slices-recipe/",
    "b_v_04": "https://www.bongeats.com/recipe/dhokar-dalna",
    "b_v_05": "https://www.bongeats.com/recipe/niramish-aloo-dum",
    "b_v_06": "https://www.bongeats.com/recipe/labra",
    "b_v_07": "https://www.bongeats.com/recipe/begun-bhaja",
    "b_v_08": "https://pikturenama.com/mochar-ghonto-bengali-recipe-banana-blossom/",
    "b_v_09": "https://www.bongeats.com/recipe/palong-shaaker-ghonto",
    "b_v_10": "https://www.bongeats.com/recipe/sheemer-bhorta",
    "b_v_11": "https://www.bongeats.com/recipe/potoler-dorma-with-dal-stuffing",
    "b_v_12": "https://www.bongeats.com/recipe/palong-shaak-bhaja",
    "b_v_13": "https://www.bongeats.com/recipe/jhuri-alu-bhaja",
    "b_v_14": "https://www.bongeats.com/recipe/korola-bhaja",
    "b_v_15": "https://www.bongeats.com/recipe/bota-soho-begun-bhaja",
    "b_v_16": "https://www.bongeats.com/recipe/aloo-bhorta",
    "b_v_17": "https://www.sanjeevkapoor.com/Recipe/Aloo-Potol---SK-Khazana.html",
    "b_v_18": "https://www.cookingandme.com/bengali-fish-fry-mach-bhaja-recipe/",
    "b_v_19": "https://www.vegrecipesofindia.com/aloo-capsicum-indian-recipe-made-with-capsicum-potatoes/",
    "b_v_20": "https://kitchenofdebjani.com/2014/10/ghee-bhat/",
    "b_v_21": "https://simpleindianrecipes.com/Home/Bhendi-Bhaja.aspx",
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
    "c_v_06": "https://hebbarskitchen.com/rice-bowl-recipe-indian-paneer-garlic/",
    "c_v_07": "https://hebbarskitchen.com/chilli-mushroom-recipe-mushroom-chilli/",
    "c_v_08": "https://hebbarskitchen.com/crispy-veg-recipe-veg-crispy-chinese/",
    "c_v_09": "https://hebbarskitchen.com/baby-corn-chilli-recipe-chilli-baby-corn/",
    "a_p_01": "https://www.indianhealthyrecipes.com/gongura-chicken-curry-chicken-with-red-sorrel-leaves/",
    "a_p_02": "https://www.yummytummyaarthi.com/andhra-spicy-fish-curry-recipe-andhra/",
    "a_p_03": "https://www.sanjeevkapoor.com/Recipe/Kodi-Guddu-Pulusu-Sirf-30-minute-FoodFood.html",
    "a_p_04": "https://www.archanaskitchen.com/recipe/andhra-style-palak-kura-pappu-recipe-spinach-dal-recipe",
    "a_p_05": "https://www.indianhealthyrecipes.com/tomato-pappu-recipe/",
    "a_v_01": "https://www.vegrecipesofindia.com/gutti-vankaya-kura-recipe/",
    "a_v_02": "https://hebbarskitchen.com/bendakaya-pulusu-recipe-okra-in-tamarind/",
    "a_v_03": "https://www.subbuskitchen.com/dondakaya-vepudu/",
    "a_v_04": "https://hebbarskitchen.com/pulihora-recipe-chintapandu-pulihora/",
    "a_v_05": "https://www.vegrecipesofindia.com/gongura-pachadi/",
    "a_v_06": "https://www.indianhealthyrecipes.com/cabbage-curry-recipe/",
    "a_v_07": "https://www.archanaskitchen.com/recipe/beerakaya-tomato-koora-recipe-andhra-style-ridge-gourd-curry",
    "s_p_01": "https://www.indianhealthyrecipes.com/chicken-chettinad/",
    "s_p_02": "https://www.indianhealthyrecipes.com/kerala-meen-fish-curry/",
    "s_p_03": "https://www.indianhealthyrecipes.com/egg-kurma-recipe/",
    "s_p_04": "https://hebbarskitchen.com/south-indian-vegetable-sambar-recipe/",
    "s_p_05": "https://hebbarskitchen.com/paneer-chettinad-curry-recipe-chettinad/",
    "s_v_01": "https://www.indianhealthyrecipes.com/lemon-rice-recipe/",
    "s_v_02": "https://hebbarskitchen.com/carrot-beans-poriyal-recipe/",
    "s_v_03": "https://hebbarskitchen.com/cabbage-poriyal-cabbage-thoran-stir-fry/",
    "s_v_04": "https://hebbarskitchen.com/avial-recipe-aviyal/",
    "s_v_05": "https://www.indianhealthyrecipes.com/coconut-rice-recipe/",
    "s_v_06": "https://www.indianhealthyrecipes.com/tomato-rasam-recipe/",
    "s_v_07": "https://www.vegrecipesofindia.com/beetroot-poriyal/",
    "o_p_01": "https://hebbarskitchen.com/rajma-recipe-punjabi-rajma-masala/",
    "o_p_02": "https://hebbarskitchen.com/chana-masala-recipe-chickpea-masala/",
    "o_p_03": "https://hebbarskitchen.com/punjabi-dal-makhani-recipe/",
    "o_p_04": "https://www.sanjeevkapoor.com/Recipe/Butter-Chicken-Sanjeev-Kapoor-Kitchen-FoodFood.html",
    "o_p_05": "https://hebbarskitchen.com/paneer-butter-masala-recipe/",
    "o_v_01": "https://hebbarskitchen.com/palak-paneer-recipe-restaurant-style/",
    "o_v_02": "https://hebbarskitchen.com/aloo-gobi-masala-recipe-aloo-gobi-curry/",
    "o_v_03": "https://hebbarskitchen.com/bhindi-masala-recipe-bhindi-ki-gravy/",
    "o_v_04": "https://hebbarskitchen.com/mix-veg-recipe-mixed-vegetable-curry/",
    "o_v_05": "https://hebbarskitchen.com/jeera-rice-recipe-jeera-pulao/",
    "o_v_06": "https://hebbarskitchen.com/masala-papad-recipe-homemade-masala/",
    "o_v_07": "https://hebbarskitchen.com/boondi-raita-recipe-boondi-ka-raita/",
    "o_v_08": "https://www.vegrecipesofindia.com/kachumber-salad-kuchumber-salad/",
}
RECIPE_SOURCE_NAMES = {
    "b_p_15": "Mitar Cooking",
    "b_p_17": "SpicyPunch",
    "b_v_17": "Sanjeev Kapoor",
    "b_v_18": "Cooking and Me",
    "b_v_19": "Dassana's Veg Recipes",
    "b_v_20": "Debjanir Rannaghar",
    "b_v_21": "Simple Indian Recipes",
}

# Which category(ies) can supply each protein family.
FAMILY_CATEGORIES = {
    "fish": ["bengali", "andhra", "southIndian"],
    "mutton": ["bengali"],
    "egg": ["bengali", "andhra", "southIndian"],
    "chicken": ["bengali", "chinese", "otherIndian", "andhra", "southIndian"],
    "paneer": ["otherIndian", "southIndian"],
    "lentil": ["otherIndian", "andhra", "southIndian"],
}
# How often a chicken day leans into each selected launch cuisine.
CHICKEN_CATEGORY_WEIGHTS = [
    ("bengali", 0.55),
    ("chinese", 0.15),
    ("otherIndian", 0.10),
    ("andhra", 0.10),
    ("southIndian", 0.10),
]


# ---------- helpers ----------

def _excluded_terms():
    return list(EXCLUSIONS.get("disliked_by_wife", [])) + list(EXCLUSIONS.get("disliked_by_kid", []))


def _is_excluded(dish, excluded_terms):
    label = f"{dish.get('name', '')} {' '.join(dish.get('ingredients', []))}".lower()
    if "ilish" in label or "hilsa" in label:
        return True
    if not excluded_terms:
        return False
    hay = f"{dish['id']} {dish['name']}".lower()
    return any(term.lower() in hay for term in excluded_terms if term.strip())


def _mother_agent_filter(dishes, excluded_terms, allow_complex=False):
    """Mother agent: permanently drop Hilsa/Ilish plus excluded/complex dishes."""
    out = [d for d in dishes if not _is_excluded(d, excluded_terms)]
    if not allow_complex:
        out = [d for d in out if d.get("complexity") != "complex"]
    return out


def _week_index(date_str: str) -> int:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (d - LAUNCH_DATE).days // 7


def _day_offset_in_week(date_str: str) -> int:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (d - LAUNCH_DATE).days % 7


def weekly_protein_plan(week_index: int):
    """Mother agent's normal weekly protein budget. Monthly mutton is
    injected separately so it can never appear more than once per month."""
    base = ["chicken", "chicken", "chicken", "fish", "egg", "paneer"]
    seventh = "paneer"
    families = base + [seventh]
    rng = mulberry32(hash_seed(f"week-{week_index}"))
    return fisher_yates(rng, families)


def is_monthly_mutton_day(date_str: str) -> bool:
    current = datetime.strptime(date_str, "%Y-%m-%d").date()
    return 22 <= current.day <= 28 and current.weekday() == 6


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


def _side_role(dish):
    if dish.get("mealRole"):
        return dish["mealRole"]
    if dish.get("proteinFamily"):
        return "protein"
    label = dish["name"].lower()
    if any(term in label for term in ("rice", "bhaat", "pulao", "pulihora", "noodle")):
        return "starch"
    if any(term in label for term in ("dal", "pappu", "sambar", "rasam")):
        return "dal"
    if any(term in label for term in ("bhaja", "fry", "vepudu", "roast", "crispy")):
        return "fry"
    if any(term in label for term in ("pachadi", "chutney", "bharta", "bhorta", "papad", "raita", "salad")):
        return "accompaniment"
    return "vegetable"


def _dish_with_source(dish, role):
    enriched = dict(dish)
    source = SOURCES.get(dish.get("sourceSite"), {})
    enriched.update({
        "role": role,
        "mealRole": "protein" if role == "protein" else _side_role(dish),
        "sourceName": RECIPE_SOURCE_NAMES.get(dish["id"], source.get("name", "Trusted source")),
        "recipeUrl": RECIPE_URLS.get(dish["id"], source.get("url", "")),
        "cookingMinutes": (45 if dish.get("complexity") == "standard" else 30) + (15 if dish.get("advancePrep") else 0),
    })
    return enriched


def generate_for_date(date_str: str) -> dict:
    excluded = _excluded_terms()
    cold_start = _is_cold_start(date_str)

    # --- Mother agent: decide today's protein family + category ---
    week_index = _week_index(date_str)
    day_offset = _day_offset_in_week(date_str)
    monthly_mutton_day = is_monthly_mutton_day(date_str)
    family = "mutton" if monthly_mutton_day else weekly_protein_plan(week_index)[day_offset]

    rng = rng_for_date(date_str)  # day-level rng, independent of the week-level rng above
    if family == "chicken":
        category = _category_for_chicken(rng)
    else:
        category = FAMILY_CATEGORIES[family][0]

    if cold_start and category == "chinese":
        category = "bengali"  # cold-start override: no Chinese in the first 10 days

    # --- Cook agent: pick actual dishes within what Mother allows ---
    protein_pool = [
        dish
        for dish in _mother_agent_filter(DISHES[category]["protein"], excluded)
        if monthly_mutton_day or dish.get("proteinFamily") != "mutton"
    ]
    veg_pool = _mother_agent_filter(DISHES[category]["vegetable"], excluded)

    family_pool = [d for d in protein_pool if d.get("proteinFamily") == family]
    protein_order = fisher_yates(rng, family_pool or protein_pool)
    protein_order += fisher_yates(mulberry32(hash_seed(f"{date_str}-alternatives")), [d for d in protein_pool if d not in protein_order])
    side_order = fisher_yates(rng, veg_pool)
    vegetable_order = [dish for dish in side_order if _side_role(dish) == "vegetable"]
    accompaniment_order = [dish for dish in side_order if _side_role(dish) not in ("vegetable", "protein")]
    first_side_order = vegetable_order or [dish for dish in side_order if _side_role(dish) != "starch"] or side_order
    second_side_order = accompaniment_order or side_order

    choices = []
    for choice_index in range(3):
        owner_example = OWNER_EXAMPLE_CHOICES[choice_index] if date_str == OWNER_EXAMPLE_DATE and category == "bengali" else None
        if owner_example:
            protein = next(dish for dish in protein_pool if dish["id"] == owner_example[0])
            first_side = next(dish for dish in veg_pool if dish["id"] == owner_example[1])
            second_side = next(dish for dish in veg_pool if dish["id"] == owner_example[2])
        else:
            protein = protein_order[choice_index % len(protein_order)]
            first_side = first_side_order[choice_index % len(first_side_order)]
            remaining = [dish for dish in second_side_order if dish["id"] != first_side["id"]]
            if not remaining:
                remaining = [dish for dish in side_order if dish["id"] != first_side["id"]]
            second_side = remaining[choice_index % len(remaining)]
            if _side_role(first_side) == "starch" and _side_role(second_side) == "starch":
                non_starch = [dish for dish in side_order if dish["id"] != first_side["id"] and _side_role(dish) != "starch"]
                if non_starch:
                    second_side = non_starch[choice_index % len(non_starch)]
        dishes = [_dish_with_source(protein, "protein"), _dish_with_source(first_side, "vegetable"), _dish_with_source(second_side, "accompaniment")]
        one_cook_minutes = min(60, round(dishes[0]["cookingMinutes"] * 0.8 + dishes[1]["cookingMinutes"] * 0.35 + dishes[2]["cookingMinutes"] * 0.25))
        choices.append({
            "id": f"{date_str}-choice-{choice_index + 1}",
            "label": f"Choice {choice_index + 1}",
            "dishes": dishes,
            "ingredients": sorted(set(item for dish in dishes for item in dish.get("ingredients", []))),
            "prepNotes": [dish.get("prepNote") for dish in dishes if dish.get("advancePrep") and dish.get("prepNote")],
            "anyNeedsAdvancePrep": any(dish.get("advancePrep") for dish in dishes),
            "cookingMinutes": one_cook_minutes,
        })

    return {
        "date": date_str,
        "category": category,
        "categoryLabel": CATEGORY_LABELS[category],
        "coldStart": cold_start,
        "proteinFamily": family,
        "choices": choices,
        "anyNeedsAdvancePrep": any(choice["anyNeedsAdvancePrep"] for choice in choices),
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
        f"_{t['categoryLabel']} style_" + (" _(cold-start window: Chinese-style menus are paused)_" if t["coldStart"] else ""),
        "",
    ]

    fest = payload.get("festiveOption")
    if fest:
        lines.append(f"🎉 *{fest['festivalName']} Special*")
        lines.append(f"✨ {fest['dish']['name']}")
        lines.append("   🛒 " + ", ".join(fest["dish"]["ingredients"]))
        lines.append("")

    for choice in t["choices"]:
        lines.append(f"*{choice['label']}* — " + " + ".join(dish["name"] for dish in choice["dishes"]))
    lines.append("")
    lines.append("*Actions:* Choose one meal · Swap any dish · Open that choice's shopping list")
    lines.append("")

    tomorrow = payload["advanceNoticeForTomorrow"]
    if tomorrow:
        prep_dishes = [dish["name"] for choice in tomorrow["choices"] for dish in choice["dishes"] if dish.get("advancePrep")]
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
