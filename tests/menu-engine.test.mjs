import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { buildMenu, buildShoppingList } from "../web/menu-engine.js";

const catalog = JSON.parse(await readFile(new URL("../data/dishes.json", import.meta.url), "utf8"));
const preferences = { householdSize: 3, budget: "balanced", portion: "regular" };
const menu = buildMenu(catalog, "2026-08-19", preferences);

assert.equal(menu.choices.length, 3);
for (const choice of menu.choices) {
  assert.equal(choice.dishes.length, 3);
  assert.equal(choice.dishes[0].kind, "protein");
  assert.equal(choice.dishes[1].kind, "vegetable");
  assert.equal(choice.dishes[2].kind, "vegetable");
  assert.equal(new Set(choice.dishes.map((dish) => dish.id)).size, 3);
  assert.ok(choice.totals.energy > 0);
  assert.ok(choice.estimatedCost > 0);
  assert.ok(choice.dishes.every((dish) => /assets\/dishes\/.+\.jpg$/.test(dish.imagePath)));
}

const swapped = buildMenu(catalog, "2026-08-19", preferences, [[1, 1, 1], [0, 0, 0], [0, 0, 0]]);
assert.notDeepEqual(swapped.choices[0].dishes.map((dish) => dish.id), menu.choices[0].dishes.map((dish) => dish.id));
assert.deepEqual(swapped.choices[1].dishes.map((dish) => dish.id), menu.choices[1].dishes.map((dish) => dish.id));

const pantryIngredient = menu.choices[0].dishes.flatMap((dish) => dish.ingredients)[0];
const pantryMenu = buildMenu(catalog, "2026-08-19", { ...preferences, pantry: [pantryIngredient] });
const shopping = buildShoppingList(pantryMenu.choices[0]);
assert.ok(Object.values(shopping).flat().some((item) => item.atHome));
assert.ok(pantryMenu.choices.some((choice) => choice.dishes.some((dish) => dish.ingredients.includes(pantryIngredient))));

const vegetarian = buildMenu(catalog, "2026-09-01", { ...preferences, diet: "vegetarian" });
assert.ok(vegetarian.choices.every((choice) => !["chicken", "fish", "mutton"].includes(choice.dishes[0].proteinFamily)));

const chineseOnly = buildMenu(catalog, "2026-08-19", { ...preferences, cuisines: ["chinese"] });
assert.equal(chineseOnly.category, "chinese");
assert.ok(chineseOnly.choices.every((choice) => choice.dishes.every((dish) => dish.id.startsWith("c_"))));

for (const [category, prefix] of [["andhra", "a_"], ["southIndian", "s_"]]) {
  const cuisineOnly = buildMenu(catalog, "2026-08-19", { ...preferences, cuisines: [category] });
  assert.equal(cuisineOnly.category, category);
  assert.equal(cuisineOnly.choices.length, 3);
  assert.ok(cuisineOnly.choices.every((choice) => choice.dishes.length === 3));
  assert.ok(cuisineOnly.choices.every((choice) => choice.dishes.every((dish) => dish.id.startsWith(prefix))));
}

console.log("menu-engine tests passed");
