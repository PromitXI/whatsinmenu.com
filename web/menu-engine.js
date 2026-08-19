const SOURCES = {
  bongeats: { name: "Bong Eats", url: "https://www.bongeats.com/recipes" },
  sanjeevkapoor: { name: "Sanjeev Kapoor", url: "https://www.sanjeevkapoor.com/Recipe" },
  hebbarskitchen: { name: "Hebbar's Kitchen", url: "https://hebbarskitchen.com/" },
};

const RECIPE_URLS = {
  b_p_01: "https://www.bongeats.com/recipe/rui-macher-jhol",
  b_p_03: "https://www.bongeats.com/recipe/chingri-malaikari",
  b_p_04: "https://www.bongeats.com/recipe/mutton-kosha",
  b_p_05: "https://www.bongeats.com/recipe/chicken-rezala",
  b_p_06: "https://www.bongeats.com/recipe/bhetki-machher-jhol",
  b_p_07: "https://www.bongeats.com/recipe/dimer-dalna",
  b_p_08: "https://www.bongeats.com/recipe/murgir-lal-jhol",
  b_p_09: "https://www.bongeats.com/recipe/katla-kalia",
  b_p_11: "https://www.bongeats.com/recipe/chingri-bhaape",
  b_p_12: "https://www.bongeats.com/recipe/pressure-cooker-chicken",
  b_p_14: "https://www.bongeats.com/recipe/chicken-curry",
  b_p_15: "https://www.bongeats.com/recipe/dimer-dalna",
  b_p_16: "https://www.bongeats.com/recipe/chicken-curry",
  b_p_17: "https://www.bongeats.com/recipe/katla-kalia",
  b_v_01: "https://www.bongeats.com/recipe/alu-posto",
  b_v_02: "https://www.bongeats.com/recipe/shukto",
  b_v_03: "https://www.bongeats.com/recipe/cholar-dal",
  b_v_04: "https://www.bongeats.com/recipe/dhokar-dalna",
  b_v_05: "https://www.bongeats.com/recipe/niramish-aloo-dum",
  b_v_06: "https://www.bongeats.com/recipe/labra",
  b_v_07: "https://www.bongeats.com/recipe/begun-bhaja",
  b_v_08: "https://www.bongeats.com/recipe/mochar-ghonto",
  b_v_09: "https://www.bongeats.com/recipe/palong-shaaker-ghonto",
  b_v_10: "https://www.bongeats.com/recipe/sheemer-bhorta",
  b_v_11: "https://www.bongeats.com/recipe/potoler-dorma-with-dal-stuffing",
  b_v_12: "https://www.bongeats.com/recipe/palong-shaak-bhaja",
  b_v_13: "https://www.bongeats.com/recipe/jhuri-alu-bhaja",
  b_v_14: "https://www.bongeats.com/recipe/korola-bhaja",
  b_v_15: "https://www.bongeats.com/recipe/bota-soho-begun-bhaja",
  b_v_16: "https://www.bongeats.com/recipe/aloo-bhorta",
  b_v_17: "https://www.bongeats.com/recipe/potoler-tel-jhol",
  b_v_18: "https://www.bongeats.com/recipe/ilish-maachh-bhaja",
  b_v_19: "https://www.bongeats.com/recipe/jhuri-alu-bhaja",
  b_v_20: "https://www.bongeats.com/recipe/potol-posto",
  b_v_21: "https://hebbarskitchen.com/bhindi-fry-recipe-bhindi-ki-sabji/",
  c_p_01: "https://www.sanjeevkapoor.com/Recipe/Chinese-Chilli-Chicken-Sirf-30-minute-FoodFood.html",
  c_p_02: "https://www.sanjeevkapoor.com/Recipe/Lemon-Chicken.html",
  c_p_03: "https://www.sanjeevkapoor.com/Recipe/Garlic-Chicken-Sanjeev-Kapoor-Kitchen-FoodFood.html",
  c_p_04: "https://www.sanjeevkapoor.com/Recipe/Chicken-Manchurian.html",
  c_p_06: "https://www.sanjeevkapoor.com/Recipe/Kung-Pao-Chicken-SK-Khazana.html",
  c_v_01: "https://hebbarskitchen.com/veg-fried-rice-vegetable-fried-rice/",
  c_v_02: "https://hebbarskitchen.com/hakka-noodles-recipe-veg-hakka-noodles/",
  c_v_03: "https://hebbarskitchen.com/manchurian-gravy-recipe-veg-manchurian/",
  c_v_04: "https://hebbarskitchen.com/chilli-garlic-fried-rice-recipe/",
  c_v_05: "https://hebbarskitchen.com/schezwan-fried-rice-recipe-schezwan-rice/",
  o_p_01: "https://hebbarskitchen.com/rajma-recipe-punjabi-rajma-masala/",
  o_p_02: "https://hebbarskitchen.com/chana-masala-recipe-chickpea-masala/",
  o_p_03: "https://hebbarskitchen.com/punjabi-dal-makhani-recipe/",
  o_p_04: "https://www.sanjeevkapoor.com/Recipe/Butter-Chicken-Sanjeev-Kapoor-Kitchen-FoodFood.html",
  o_p_05: "https://hebbarskitchen.com/paneer-butter-masala-recipe/",
  o_v_01: "https://hebbarskitchen.com/palak-paneer-recipe-restaurant-style/",
  o_v_02: "https://hebbarskitchen.com/aloo-gobi-masala-recipe-aloo-gobi-curry/",
  o_v_03: "https://hebbarskitchen.com/bhindi-masala-recipe-bhindi-ki-gravy/",
  o_v_04: "https://hebbarskitchen.com/mix-veg-recipe-mixed-vegetable-curry/",
};

export const DEFAULT_PREFERENCES = {
  householdSize: 3,
  portion: "regular",
  budget: "balanced",
  cuisines: ["bengali", "chinese", "otherIndian"],
  diet: "omnivore",
  allergies: [],
  dislikes: [],
  pantry: [],
  skippedDishIds: [],
  favoriteDishIds: [],
  whatsappNumber: "",
  notificationTime: "18:00",
};

export const CATEGORY_LABELS = {
  bengali: "Bengali",
  chinese: "Chinese-style",
  otherIndian: "North Indian",
};

const LAUNCH_DATE = "2026-08-18";
const COLD_START_DAYS = 10;
const FAMILY_CATEGORIES = {
  fish: ["bengali"],
  mutton: ["bengali"],
  egg: ["bengali"],
  chicken: ["bengali", "chinese", "otherIndian"],
  paneer: ["otherIndian"],
  lentil: ["otherIndian"],
};
const CHICKEN_CATEGORY_WEIGHTS = [
  ["bengali", 0.7],
  ["chinese", 0.2],
  ["otherIndian", 0.1],
];
const PORTION_SCALE = { light: 0.8, regular: 1, hearty: 1.25 };
const OWNER_EXAMPLE_DATE = "2026-08-19";
const OWNER_EXAMPLE_CHOICES = [
  ["b_p_15", "b_v_13", "b_v_21"],
  ["b_p_16", "b_v_17", "b_v_19"],
  ["b_p_17", "b_v_18", "b_v_20"],
];

const PROTEIN_NUTRITION = {
  chicken: { energy: 285, protein: 27, carbs: 10, fat: 15, fibre: 2, sodium: 510, sugar: 4, cost: 85 },
  fish: { energy: 245, protein: 25, carbs: 8, fat: 13, fibre: 2, sodium: 430, sugar: 3, cost: 105 },
  mutton: { energy: 410, protein: 29, carbs: 10, fat: 28, fibre: 2, sodium: 570, sugar: 4, cost: 165 },
  egg: { energy: 230, protein: 15, carbs: 12, fat: 14, fibre: 2, sodium: 440, sugar: 4, cost: 45 },
  paneer: { energy: 355, protein: 19, carbs: 14, fat: 25, fibre: 3, sodium: 520, sugar: 6, cost: 80 },
  lentil: { energy: 305, protein: 16, carbs: 46, fat: 7, fibre: 12, sodium: 390, sugar: 6, cost: 38 },
};
const VEGETABLE_NUTRITION = { energy: 145, protein: 4, carbs: 23, fat: 5, fibre: 6, sodium: 280, sugar: 6, cost: 28 };

function toArray(value) {
  if (Array.isArray(value)) return value.map(String).map((item) => item.trim()).filter(Boolean);
  return String(value || "").split(",").map((item) => item.trim()).filter(Boolean);
}

export function normalizePreferences(input = {}) {
  const prefs = { ...DEFAULT_PREFERENCES, ...input };
  prefs.householdSize = Math.min(12, Math.max(1, Number(prefs.householdSize) || 3));
  prefs.cuisines = toArray(prefs.cuisines).filter((item) => CATEGORY_LABELS[item]);
  if (!prefs.cuisines.length) prefs.cuisines = [...DEFAULT_PREFERENCES.cuisines];
  prefs.allergies = toArray(prefs.allergies);
  prefs.dislikes = toArray(prefs.dislikes);
  prefs.pantry = toArray(prefs.pantry);
  prefs.skippedDishIds = toArray(prefs.skippedDishIds);
  prefs.favoriteDishIds = toArray(prefs.favoriteDishIds);
  if (!PORTION_SCALE[prefs.portion]) prefs.portion = "regular";
  return prefs;
}

export function hashSeed(value) {
  let hash = 5381;
  for (let i = 0; i < value.length; i += 1) {
    hash = ((hash << 5) + hash + value.charCodeAt(i)) | 0;
  }
  return hash;
}

export function mulberry32(seed) {
  let state = seed | 0;
  return function random() {
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function shuffle(rng, values) {
  const result = values.slice();
  for (let index = result.length - 1; index > 0; index -= 1) {
    const target = Math.floor(rng() * (index + 1));
    [result[index], result[target]] = [result[target], result[index]];
  }
  return result;
}

function daysBetween(first, second) {
  const [ay, am, ad] = first.split("-").map(Number);
  const [by, bm, bd] = second.split("-").map(Number);
  return Math.round((Date.UTC(by, bm - 1, bd) - Date.UTC(ay, am - 1, ad)) / 86400000);
}

function weeklyProteinPlan(weekIndex, prefs) {
  let base = ["chicken", "chicken", "chicken", "fish", "egg", "paneer"];
  let seventh = weekIndex % 2 === 0 ? "mutton" : "paneer";
  if (prefs.budget === "economical") {
    base = ["chicken", "chicken", "egg", "egg", "paneer", "lentil"];
    seventh = "lentil";
  } else if (prefs.budget === "generous") {
    base = ["chicken", "chicken", "chicken", "fish", "fish", "paneer"];
    seventh = weekIndex % 2 === 0 ? "mutton" : "egg";
  }
  if (prefs.diet === "vegetarian") base = ["paneer", "lentil", "egg", "paneer", "lentil", "egg"];
  if (prefs.diet === "vegan") base = ["lentil", "lentil", "lentil", "lentil", "lentil", "lentil"];
  const families = base.concat([prefs.diet === "omnivore" ? seventh : base[weekIndex % base.length]]);
  const defaultPlan = prefs.budget === "balanced" && prefs.diet === "omnivore";
  const seed = defaultPlan ? `week-${weekIndex}` : `week-${weekIndex}-${prefs.budget}-${prefs.diet}`;
  return shuffle(mulberry32(hashSeed(seed)), families);
}

function chooseChickenCategory(rng, allowed) {
  const weighted = CHICKEN_CATEGORY_WEIGHTS.filter(([category]) => allowed.includes(category));
  if (!weighted.length) return allowed[0];
  const total = weighted.reduce((sum, [, weight]) => sum + weight, 0);
  const roll = rng() * total;
  let running = 0;
  for (const [category, weight] of weighted) {
    running += weight;
    if (roll < running) return category;
  }
  return weighted.at(-1)[0];
}

function isAllowed(dish, prefs) {
  if (dish.complexity === "complex") return false;
  if (prefs.skippedDishIds.includes(dish.id)) return false;
  const haystack = `${dish.id} ${dish.name} ${(dish.ingredients || []).join(" ")}`.toLowerCase();
  const blocked = [...prefs.dislikes, ...prefs.allergies].some((term) => haystack.includes(term.toLowerCase()));
  if (blocked) return false;
  if (prefs.diet === "vegetarian" && ["chicken", "fish", "mutton"].includes(dish.proteinFamily)) return false;
  if (prefs.diet === "vegan") {
    if (["chicken", "fish", "mutton", "egg", "paneer"].includes(dish.proteinFamily)) return false;
    if (/milk|ghee|butter|cream|yogurt|paneer|egg/.test(haystack)) return false;
  }
  return true;
}

function pantryScore(dish, prefs) {
  if (!prefs.pantry.length) return 0;
  const ingredients = (dish.ingredients || []).map((item) => item.toLowerCase());
  return prefs.pantry.reduce((score, pantryItem) => {
    const needle = pantryItem.toLowerCase();
    return score + (ingredients.some((item) => item.includes(needle) || needle.includes(item)) ? 1 : 0);
  }, 0);
}

function preferPantry(dishes, prefs) {
  return dishes
    .map((dish, index) => ({ dish, index, score: pantryScore(dish, prefs) }))
    .sort((first, second) => second.score - first.score || first.index - second.index)
    .map((item) => item.dish);
}

function recipeFor(dish) {
  return RECIPE_URLS[dish.id] || SOURCES[dish.sourceSite]?.url || "#";
}

function estimateNutrition(dish, kind, portion) {
  let base = kind === "protein"
    ? { ...(PROTEIN_NUTRITION[dish.proteinFamily] || PROTEIN_NUTRITION.lentil) }
    : { ...VEGETABLE_NUTRITION };
  const lower = dish.name.toLowerCase();
  if (kind === "vegetable" && /dal|paneer/.test(lower)) {
    base = { energy: 235, protein: 10, carbs: 31, fat: 8, fibre: 8, sodium: 340, sugar: 5, cost: 38 };
  }
  if (/fried|bhaja|butter|malai|rezala/.test(lower)) {
    base.energy += 55;
    base.fat += 6;
  }
  const scale = PORTION_SCALE[portion] || 1;
  return Object.fromEntries(Object.entries(base).map(([key, value]) => [key, Math.round(value * scale)]));
}

function selectionReason(dish, kind, family, category, prefs) {
  if (kind === "protein") {
    if (dish.proteinFamily === family) return `Fits this week’s ${family} rhythm and your ${prefs.budget} budget.`;
    return `A practical ${CATEGORY_LABELS[category].toLowerCase()} protein for tonight.`;
  }
  if (dish.advancePrep) return "Chosen early so there is enough time for soaking or resting.";
  return `A ${dish.complexity || "simple"} side that keeps the meal familiar and balanced.`;
}

function enrichDish(dish, kind, family, category, prefs) {
  const nutrition = estimateNutrition(dish, kind, prefs.portion);
  const baseMinutes = dish.complexity === "standard" ? 45 : 30;
  const cookingMinutes = baseMinutes + (dish.advancePrep ? 15 : 0);
  return {
    ...dish,
    kind,
    sourceName: SOURCES[dish.sourceSite]?.name || "Trusted source",
    recipeUrl: recipeFor(dish),
    cookingMinutes,
    servingLabel: kind === "protein" ? "1 bowl" : "1 small bowl",
    nutrition,
    estimatedCostPerServing: nutrition.cost,
    nutritionConfidence: RECIPE_URLS[dish.id] ? "medium" : "low",
    reason: selectionReason(dish, kind, family, category, prefs),
  };
}

function categoryForFamily(family, rng, prefs, coldStart) {
  let allowed = prefs.cuisines.slice();
  if (coldStart) allowed = allowed.filter((category) => category !== "chinese");
  if (!allowed.length) allowed = ["bengali", "otherIndian"];
  if (family === "chicken") return chooseChickenCategory(rng, allowed);
  const preferred = (FAMILY_CATEGORIES[family] || []).find((category) => allowed.includes(category));
  return preferred || allowed[0];
}

export function buildMenu(catalog, dateStr, inputPreferences = {}, swapOffsets = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]) {
  const prefs = normalizePreferences(inputPreferences);
  const day = daysBetween(LAUNCH_DATE, dateStr);
  const weekIndex = Math.floor(day / 7);
  const dayOffset = ((day % 7) + 7) % 7;
  let family = weeklyProteinPlan(weekIndex, prefs)[dayOffset];
  const defaultPlanning = prefs.budget === "balanced"
    && prefs.diet === "omnivore"
    && prefs.cuisines.join("|") === DEFAULT_PREFERENCES.cuisines.join("|");
  const daySeed = defaultPlanning ? dateStr : `${dateStr}-${prefs.budget}-${prefs.diet}-${prefs.cuisines.join("|")}`;
  const rng = mulberry32(hashSeed(daySeed));
  const coldStart = day >= 0 && day < COLD_START_DAYS;
  let category = categoryForFamily(family, rng, prefs, coldStart);
  let categoryData = catalog[category];

  let proteins = (categoryData?.protein || []).filter((dish) => isAllowed(dish, prefs));
  let vegetables = (categoryData?.vegetable || []).filter((dish) => isAllowed(dish, prefs));
  let matchingProteins = proteins.filter((dish) => dish.proteinFamily === family);

  if (!matchingProteins.length) {
    for (const fallbackCategory of prefs.cuisines) {
      const fallback = catalog[fallbackCategory];
      const pool = (fallback?.protein || []).filter((dish) => isAllowed(dish, prefs));
      const matching = pool.filter((dish) => dish.proteinFamily === family);
      if (matching.length && (fallback?.vegetable || []).length >= 2) {
        category = fallbackCategory;
        categoryData = fallback;
        proteins = pool;
        vegetables = fallback.vegetable.filter((dish) => isAllowed(dish, prefs));
        matchingProteins = matching;
        break;
      }
    }
  }

  if (!matchingProteins.length) {
    matchingProteins = proteins;
    family = proteins[0]?.proteinFamily || family;
  }
  if (!matchingProteins.length || vegetables.length < 2) {
    throw new Error("Your current preferences remove too many dishes. Loosen one allergy, dislike, cuisine, or diet filter.");
  }

  const matchingOrder = preferPantry(shuffle(rng, matchingProteins), prefs);
  const proteinCandidates = matchingOrder.concat(
    shuffle(
      mulberry32(hashSeed(`${daySeed}-protein-alternatives`)),
      proteins.filter((dish) => !matchingProteins.some((match) => match.id === dish.id)),
    ),
  );
  const vegetableOrder = preferPantry(shuffle(rng, vegetables), prefs);

  const choices = Array.from({ length: 3 }, (_, choiceIndex) => {
    const offsets = Array.isArray(swapOffsets[choiceIndex]) ? swapOffsets[choiceIndex] : [0, 0, 0];
    const ownerExample = dateStr === OWNER_EXAMPLE_DATE && category === "bengali" && prefs.diet === "omnivore" ? OWNER_EXAMPLE_CHOICES[choiceIndex] : null;
    const proteinStart = ownerExample ? Math.max(0, proteinCandidates.findIndex((dish) => dish.id === ownerExample[0])) : choiceIndex;
    const protein = proteinCandidates[(proteinStart + Math.abs(Number(offsets[0]) || 0)) % proteinCandidates.length];
    const defaultFirstSideIndex = ownerExample ? Math.max(0, vegetableOrder.findIndex((dish) => dish.id === ownerExample[1])) : choiceIndex * 2;
    const firstSideIndex = (defaultFirstSideIndex + Math.abs(Number(offsets[1]) || 0)) % vegetableOrder.length;
    const firstSide = vegetableOrder[firstSideIndex];
    const remainingSides = vegetableOrder.filter((dish) => dish.id !== firstSide.id);
    const defaultSecondSideIndex = ownerExample ? Math.max(0, remainingSides.findIndex((dish) => dish.id === ownerExample[2])) : choiceIndex * 2 + 1;
    const secondSide = remainingSides[(defaultSecondSideIndex + Math.abs(Number(offsets[2]) || 0)) % remainingSides.length];
    const dishes = [
      enrichDish(protein, "protein", family, category, prefs),
      enrichDish(firstSide, "vegetable", family, category, prefs),
      enrichDish(secondSide, "vegetable", family, category, prefs),
    ];
    const totals = dishes.reduce((result, dish) => {
      for (const key of ["energy", "protein", "carbs", "fat", "fibre", "sodium", "sugar"]) result[key] += dish.nutrition[key];
      return result;
    }, { energy: 0, protein: 0, carbs: 0, fat: 0, fibre: 0, sodium: 0, sugar: 0 });
    return {
      id: `${dateStr}-choice-${choiceIndex + 1}`,
      label: `Choice ${choiceIndex + 1}`,
      dishes,
      totals,
      servings: prefs.householdSize,
      estimatedCost: dishes.reduce((sum, dish) => sum + dish.estimatedCostPerServing, 0) * prefs.householdSize,
      cookingMinutes: Math.max(...dishes.map((dish) => dish.cookingMinutes)),
      needsAdvancePrep: dishes.some((dish) => dish.advancePrep),
      imagePath: `assets/meals/${dateStr}-choice-${choiceIndex + 1}.jpg`,
      imagePrompt: `A complete ${CATEGORY_LABELS[category]} home dinner containing ${dishes.map((dish) => dish.name).join(", ")}`,
      preferences: prefs,
    };
  });

  return {
    date: dateStr,
    category,
    categoryLabel: CATEGORY_LABELS[category],
    proteinFamily: family,
    coldStart,
    choices,
    preferences: prefs,
  };
}

const GROUP_RULES = {
  Protein: /chicken|fish|prawn|mutton|egg|paneer|lentil|dal|chickpea|rajma|kidney bean|urad/,
  Vegetables: /potato|tomato|onion|spinach|eggplant|brinjal|vegetable|gourd|cabbage|carrot|okra|cauliflower|beans|peas|banana flower|capsicum|coriander|spring onion/,
  Spices: /chili|chilli|turmeric|cumin|coriander powder|garam masala|panch phoron|bay leaf|whole spices|kasuri methi|mustard paste|poppy seed|ginger|garlic|fennel/,
};

export function buildShoppingList(menu) {
  const pantry = menu.preferences.pantry.map((item) => item.toLowerCase());
  const groups = { Protein: [], Vegetables: [], Spices: [], Pantry: [] };
  const seen = new Set();
  for (const dish of menu.dishes) {
    for (const ingredient of dish.ingredients || []) {
      const key = ingredient.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      const group = Object.entries(GROUP_RULES).find(([, pattern]) => pattern.test(key))?.[0] || "Pantry";
      groups[group].push({ name: ingredient, atHome: pantry.some((item) => key.includes(item) || item.includes(key)) });
    }
  }
  return groups;
}

export function todayInKolkata(now = new Date()) {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata" }).format(now);
}

export function addDays(dateStr, amount) {
  const [year, month, day] = dateStr.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day + amount)).toISOString().slice(0, 10);
}

export function formatDate(dateStr) {
  const [year, month, day] = dateStr.split("-").map(Number);
  return new Intl.DateTimeFormat("en-IN", { weekday: "long", day: "numeric", month: "long" }).format(new Date(Date.UTC(year, month - 1, day)));
}

export function menuShareText(menu) {
  const choices = menu.choices.map((choice) => `${choice.label}: ${choice.dishes.map((dish) => dish.name).join(" + ")}`).join("\n");
  const pageUrl = typeof location === "undefined" ? "" : `\nView the menu: ${location.href}`;
  return `Tonight's three WhatsInMenu choices:\n${choices}${pageUrl}`;
}
