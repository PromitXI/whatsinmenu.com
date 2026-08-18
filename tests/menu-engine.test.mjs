import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { buildMenu, buildShoppingList } from "../web/menu-engine.js";

const catalog = JSON.parse(await readFile(new URL("../data/dishes.json", import.meta.url), "utf8"));
const preferences = { householdSize: 3, budget: "balanced", portion: "regular" };
const menu = buildMenu(catalog, "2026-08-19", preferences);

assert.equal(menu.dishes.length, 3);
assert.equal(menu.dishes[0].kind, "protein");
assert.equal(menu.dishes[1].kind, "vegetable");
assert.equal(menu.dishes[2].kind, "vegetable");
assert.equal(new Set(menu.dishes.map((dish) => dish.id)).size, 3);
assert.equal(menu.proteinFamily, menu.dishes[0].proteinFamily);
assert.deepEqual(menu.dishes.map((dish) => dish.id), ["b_p_07", "b_v_03", "b_v_16"]);
assert.ok(menu.totals.energy > 0);
assert.ok(menu.estimatedCost > 0);

const swapped = buildMenu(catalog, "2026-08-19", preferences, [1, 1, 1]);
assert.notDeepEqual(swapped.dishes.map((dish) => dish.id), menu.dishes.map((dish) => dish.id));

const pantryIngredient = menu.dishes.flatMap((dish) => dish.ingredients)[0];
const pantryMenu = buildMenu(catalog, "2026-08-19", { ...preferences, pantry: [pantryIngredient] });
const shopping = buildShoppingList(pantryMenu);
assert.ok(Object.values(shopping).flat().some((item) => item.atHome));
assert.ok(pantryMenu.dishes.some((dish) => dish.ingredients.includes(pantryIngredient)));

const vegetarian = buildMenu(catalog, "2026-09-01", { ...preferences, diet: "vegetarian" });
assert.ok(!["chicken", "fish", "mutton"].includes(vegetarian.dishes[0].proteinFamily));

console.log("menu-engine tests passed");
