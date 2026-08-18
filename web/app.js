import { DEFAULT_PREFERENCES, buildMenu, buildShoppingList, formatDate, menuShareText, normalizePreferences, todayInKolkata } from "./menu-engine.js";

const STORAGE = { preferences: "whatsinmenu.preferences.v2", swaps: "whatsinmenu.swaps.v2", feedback: "whatsinmenu.feedback.v2", history: "whatsinmenu.history.v2" };
const state = { date: todayInKolkata(), catalog: null, menu: null, preferences: loadJson(STORAGE.preferences, DEFAULT_PREFERENCES), swaps: loadJson(STORAGE.swaps, {}) };
const elements = Object.fromEntries(["dateLabel", "menuFacts", "selectionNote", "dishGrid", "mealSummary", "errorMessage", "preferencesDialog", "preferencesForm", "shoppingDialog", "shoppingList", "historyDialog", "historyList", "pantryForm", "pantryInput", "feedbackStatus"].map((id) => [id, document.getElementById(id)]));

function loadJson(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }
function saveJson(key, value) { localStorage.setItem(key, JSON.stringify(value)); }
function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]); }
async function loadCatalog() { const response = await fetch("../data/dishes.json"); if (!response.ok) throw new Error("The dish catalogue could not be loaded."); return response.json(); }
function currentOffsets() { return state.swaps[state.date] || [0, 0, 0]; }

function rebuildMenu() {
  elements.errorMessage.hidden = true;
  try {
    state.preferences = normalizePreferences(state.preferences);
    state.menu = buildMenu(state.catalog, state.date, state.preferences, currentOffsets());
    renderMenu();
    rememberMenu();
  } catch (error) {
    elements.errorMessage.textContent = error.message;
    elements.errorMessage.hidden = false;
    elements.dishGrid.replaceChildren();
  }
}

function renderMenu() {
  const menu = state.menu;
  elements.dateLabel.textContent = formatDate(menu.date);
  elements.menuFacts.innerHTML = `<span>${escapeHtml(menu.categoryLabel)}</span><span>Approx. ₹${menu.estimatedCost}</span><span>${menu.cookingMinutes} min</span><span>Serves ${menu.servings}</span>`;
  elements.selectionNote.textContent = menu.coldStart ? "Opening-week menu: familiar Bengali and North Indian cooking first." : `Chosen for your ${menu.preferences.budget} budget and ${menu.preferences.portion} portions.`;
  elements.dishGrid.innerHTML = menu.dishes.map((dish, index) => dishCard(dish, index)).join("");
  elements.dishGrid.querySelectorAll("[data-swap]").forEach((button) => button.addEventListener("click", () => swapDish(Number(button.dataset.swap))));
  elements.dishGrid.querySelectorAll("[data-image]").forEach((image) => { image.addEventListener("load", () => image.closest(".dish-photo").classList.add("has-image")); image.addEventListener("error", () => image.remove()); });
  const totals = menu.totals;
  elements.mealSummary.innerHTML = `
    <div class="summary-heading"><div><p class="eyebrow">Meal total</p><h2 id="mealSummaryTitle">Your dinner, approximately ${totals.energy} kcal per person</h2></div><label class="portion-control">Portion<select id="quickPortion"><option value="light" ${menu.preferences.portion === "light" ? "selected" : ""}>Light</option><option value="regular" ${menu.preferences.portion === "regular" ? "selected" : ""}>Regular</option><option value="hearty" ${menu.preferences.portion === "hearty" ? "selected" : ""}>Hearty</option></select></label></div>
    <div class="macro-row"><span><strong>${totals.protein} g</strong> protein</span><span><strong>${totals.carbs} g</strong> carbs</span><span><strong>${totals.fat} g</strong> fat</span><span><strong>${totals.fibre} g</strong> fibre</span></div>
    <details class="calculation-note"><summary>How was this calculated?</summary><p>These are planning estimates per serving, based on a typical portion and the listed ingredients—not medical-grade measurements. Oil, salt, garnish, substitutions, and recipe quantities can change the result. Estimated sodium: ${totals.sodium} mg; sugar: ${totals.sugar} g.</p></details>`;
  document.getElementById("quickPortion").addEventListener("change", (event) => { state.preferences.portion = event.target.value; saveJson(STORAGE.preferences, state.preferences); rebuildMenu(); });
  elements.pantryInput.value = state.preferences.pantry.join(", ");
}

function dishCard(dish, index) {
  const label = index === 0 ? "Protein" : `Side ${index}`;
  const initials = dish.name.split(/\s+/).slice(0, 2).map((word) => word[0]).join("");
  return `<article class="dish-card">
    <div class="dish-photo" aria-hidden="true"><span>${escapeHtml(initials)}</span><img data-image src="${escapeHtml(dish.imagePath)}" alt=""></div>
    <div class="dish-body"><div class="dish-kicker"><span>${label}</span><span>${dish.spiceLevel || "mild"}</span></div><h2>${escapeHtml(dish.name)}</h2><p class="dish-reason">${escapeHtml(dish.reason)}</p>
    <div class="dish-quick-facts"><span>${dish.cookingMinutes} min</span><span>~₹${dish.estimatedCostPerServing}/person</span><span>${dish.nutrition.energy} kcal</span><span>${dish.nutrition.protein} g protein</span></div>
    <details class="nutrition-panel"><summary>Nutrition and serving details</summary><p>${dish.servingLabel} · Carbs ${dish.nutrition.carbs} g · Fat ${dish.nutrition.fat} g · Fibre ${dish.nutrition.fibre} g</p><p>Sodium ${dish.nutrition.sodium} mg · Sugar ${dish.nutrition.sugar} g · Confidence: ${dish.nutritionConfidence}</p><p class="quiet">Estimated nutrition per serving. Actual values vary with ingredients, quantities, substitutions, and cooking method.</p></details>
    ${dish.advancePrep ? `<p class="prep-alert">Prepare ahead: ${escapeHtml(dish.prepNote || "allow extra preparation time")}</p>` : ""}
    <div class="dish-actions"><a href="${escapeHtml(dish.recipeUrl)}" target="_blank" rel="noopener">Recipe via ${escapeHtml(dish.sourceName)}</a><button type="button" data-swap="${index}" aria-label="Swap ${escapeHtml(dish.name)}">Not feeling this? Swap</button></div></div></article>`;
}

function swapDish(index) { const offsets = currentOffsets().slice(); offsets[index] += 1; state.swaps[state.date] = offsets; saveJson(STORAGE.swaps, state.swaps); rebuildMenu(); elements.dishGrid.children[index]?.scrollIntoView({ behavior: "smooth", block: "center" }); }

function rememberMenu() {
  const history = loadJson(STORAGE.history, []);
  const item = { date: state.menu.date, category: state.menu.categoryLabel, dishes: state.menu.dishes.map((dish) => dish.name), feedback: loadJson(STORAGE.feedback, {})[state.menu.date] || null };
  saveJson(STORAGE.history, [item, ...history.filter((entry) => entry.date !== item.date)].slice(0, 30));
}

function renderShoppingList() {
  const groups = buildShoppingList(state.menu);
  elements.shoppingList.innerHTML = Object.entries(groups).map(([group, items]) => `<section class="shopping-group"><h3>${group}</h3>${items.length ? `<ul>${items.map((item) => `<li class="${item.atHome ? "at-home" : ""}"><label><input type="checkbox" ${item.atHome ? "checked" : ""}> ${escapeHtml(item.name)}</label>${item.atHome ? "<small>At home</small>" : ""}</li>`).join("")}</ul>` : "<p class=\"quiet\">Nothing needed.</p>"}</section>`).join("");
}

function shoppingText() {
  const groups = buildShoppingList(state.menu);
  return Object.entries(groups).map(([group, items]) => { const needed = items.filter((item) => !item.atHome); return needed.length ? `${group}:\n${needed.map((item) => `- ${item.name}`).join("\n")}` : ""; }).filter(Boolean).join("\n\n");
}

function openPreferences() {
  const prefs = normalizePreferences(state.preferences); const form = elements.preferencesForm;
  for (const name of ["householdSize", "budget", "portion", "diet", "whatsappNumber", "notificationTime"]) form.elements[name].value = prefs[name];
  form.elements.allergies.value = prefs.allergies.join(", "); form.elements.dislikes.value = prefs.dislikes.join(", ");
  form.querySelectorAll("[name=cuisines]").forEach((input) => { input.checked = prefs.cuisines.includes(input.value); });
  elements.preferencesDialog.showModal();
}

function savePreferences(event) {
  event.preventDefault(); const data = new FormData(event.currentTarget);
  state.preferences = normalizePreferences({ ...state.preferences, householdSize: data.get("householdSize"), budget: data.get("budget"), portion: data.get("portion"), diet: data.get("diet"), cuisines: data.getAll("cuisines"), allergies: data.get("allergies"), dislikes: data.get("dislikes"), whatsappNumber: data.get("whatsappNumber"), notificationTime: data.get("notificationTime") });
  saveJson(STORAGE.preferences, state.preferences); elements.preferencesDialog.close(); rebuildMenu();
}

function renderHistory() {
  const history = loadJson(STORAGE.history, []);
  elements.historyList.innerHTML = history.length ? history.map((item) => `<article class="history-item"><p><strong>${escapeHtml(formatDate(item.date))}</strong> · ${escapeHtml(item.category)}</p><p>${item.dishes.map(escapeHtml).join(" · ")}</p>${item.feedback ? `<small>Feedback: ${escapeHtml(item.feedback)}</small>` : ""}</article>`).join("") : "<p>No meals remembered yet.</p>";
}

function recordFeedback(value) {
  const feedback = loadJson(STORAGE.feedback, {});
  feedback[state.date] = value;
  saveJson(STORAGE.feedback, feedback);
  const ids = state.menu.dishes.map((dish) => dish.id);
  if (value === "skip") state.preferences.skippedDishIds = [...new Set([...(state.preferences.skippedDishIds || []), ...ids])];
  if (value === "loved") state.preferences.favoriteDishIds = [...new Set([...(state.preferences.favoriteDishIds || []), ...ids])];
  saveJson(STORAGE.preferences, state.preferences);
  rememberMenu();
  elements.feedbackStatus.textContent = value === "skip" ? "Understood. These dishes will stay out of future menus on this device." : "Saved. Thanks for keeping it simple.";
}

document.getElementById("preferencesButton").addEventListener("click", openPreferences);
document.getElementById("historyButton").addEventListener("click", () => { renderHistory(); elements.historyDialog.showModal(); });
document.getElementById("shoppingButton").addEventListener("click", () => { renderShoppingList(); elements.shoppingDialog.showModal(); });
document.getElementById("copyShoppingButton").addEventListener("click", async (event) => { await navigator.clipboard.writeText(shoppingText()); event.currentTarget.textContent = "Shopping list copied"; });
document.getElementById("whatsappButton").addEventListener("click", () => { const number = String(state.preferences.whatsappNumber || "").replace(/\D/g, ""); const path = number ? `https://wa.me/${number}` : "https://wa.me/"; window.open(`${path}?text=${encodeURIComponent(menuShareText(state.menu))}`, "_blank", "noopener"); });
elements.preferencesForm.addEventListener("submit", savePreferences);
elements.pantryForm.addEventListener("submit", (event) => { event.preventDefault(); state.preferences.pantry = event.currentTarget.elements.pantry.value; state.preferences = normalizePreferences(state.preferences); saveJson(STORAGE.preferences, state.preferences); elements.feedbackStatus.textContent = "Pantry saved. Your shopping list is updated."; });
document.querySelectorAll("[data-feedback]").forEach((button) => button.addEventListener("click", () => recordFeedback(button.dataset.feedback)));
document.querySelectorAll("[data-close]").forEach((button) => button.addEventListener("click", () => document.getElementById(button.dataset.close).close()));

try {
  state.catalog = await loadCatalog();
  rebuildMenu();
  if (location.hash === "#preferences") openPreferences();
} catch (error) {
  elements.errorMessage.textContent = `${error.message} Open the app through its local or hosted web address rather than directly from the file system.`;
  elements.errorMessage.hidden = false;
}
