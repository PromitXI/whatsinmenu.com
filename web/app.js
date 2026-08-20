import { DEFAULT_PREFERENCES, buildMenu, buildShoppingList, filterCatalogByAvailableImages, formatDate, menuShareText, nextSwapOffsets, normalizePreferences, todayInKolkata } from "./menu-engine.js?v=12";

const STORAGE = { preferences: "whatsinmenu.preferences.v3", swaps: "whatsinmenu.swaps.v3", selected: "whatsinmenu.selected.v3", feedback: "whatsinmenu.feedback.v3", history: "whatsinmenu.history.v3" };
const state = { date: todayInKolkata(), rawCatalog: null, catalog: null, imageLibrary: {}, menu: null, preferences: loadJson(STORAGE.preferences, DEFAULT_PREFERENCES), swaps: loadJson(STORAGE.swaps, {}), selected: loadJson(STORAGE.selected, {}) };
const elements = Object.fromEntries(["dateLabel", "menuFacts", "selectionNote", "dishGrid", "mealSummary", "errorMessage", "preferencesDialog", "preferencesForm", "shoppingDialog", "shoppingList", "historyDialog", "historyList", "pantryForm", "pantryInput", "feedbackStatus"].map((id) => [id, document.getElementById(id)]));

function loadJson(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }
function saveJson(key, value) { localStorage.setItem(key, JSON.stringify(value)); }
function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]); }
async function loadCatalog() { const response = await fetch("../data/dishes.json?v=9", { cache: "no-store" }); if (!response.ok) throw new Error("The dish catalogue could not be loaded."); return response.json(); }
async function loadImageLibrary() { const response = await fetch("image-library.json?v=2", { cache: "no-store" }); return response.ok ? response.json() : {}; }
function blankOffsets() { return [[0, 0, 0], [0, 0, 0], [0, 0, 0]]; }
function currentOffsets() { return state.swaps[state.date] || blankOffsets(); }
function selectedIndex() { return Math.min(2, Math.max(0, Number(state.selected[state.date]) || 0)); }
function selectedChoice() { return state.menu.choices[selectedIndex()]; }

function removeUnavailableImage(dishId) {
  if (!state.imageLibrary[dishId]) return;
  delete state.imageLibrary[dishId];
  state.catalog = filterCatalogByAvailableImages(state.rawCatalog, state.imageLibrary);
  rebuildMenu();
}

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
  elements.menuFacts.innerHTML = `<span>3 complete choices</span><span>${escapeHtml(menu.categoryLabel)}</span><span>3 dishes in each</span>`;
  elements.selectionNote.textContent = menu.coldStart ? "Opening-week choices favour familiar home cooking." : `Built for your ${menu.preferences.budget} budget and ${menu.preferences.portion} portions.`;
  elements.dishGrid.innerHTML = menu.choices.map((choice, index) => choiceCard(choice, index)).join("");
  elements.dishGrid.querySelectorAll("[data-swap]").forEach((button) => button.addEventListener("click", () => swapDish(Number(button.dataset.choice), Number(button.dataset.dish))));
  elements.dishGrid.querySelectorAll("[data-select]").forEach((button) => button.addEventListener("click", () => chooseMeal(Number(button.dataset.select))));
  elements.dishGrid.querySelectorAll("[data-image]").forEach((image) => { image.addEventListener("load", () => image.closest(".dish-image").classList.add("has-image")); image.addEventListener("error", () => removeUnavailableImage(image.dataset.dishId)); });
  renderMealSummary();
  elements.pantryInput.value = state.preferences.pantry.join(", ");
}

function choiceCard(choice, choiceIndex) {
  const selected = choiceIndex === selectedIndex();
  return `<article class="choice-card ${selected ? "is-selected" : ""}">
    <div class="choice-body">
      <div class="choice-heading"><div><p class="eyebrow">${choice.label}</p><h2>Complete three-dish dinner</h2></div>${selected ? "<span class=\"selected-badge\">Selected</span>" : ""}</div>
      <div class="choice-dishes">${choice.dishes.map((dish, dishIndex) => dishRow(dish, choiceIndex, dishIndex)).join("")}</div>
      <div class="choice-meta"><span>₹${choice.estimatedCost}</span><span>${choice.cookingMinutes} min</span><span>${choice.totals.energy} kcal/person</span><span>Serves ${choice.servings}</span></div>
      <button class="${selected ? "outline-button" : "pill-button"} full-width" type="button" data-select="${choiceIndex}">${selected ? "This is tonight’s meal" : `Choose ${choice.label}`}</button>
    </div>
  </article>`;
}

function dishRow(dish, choiceIndex, dishIndex) {
  const initials = dish.name.split(/\s+/).slice(0, 2).map((word) => word[0]).join("");
  const labels = { protein: "Protein", vegetable: "Vegetable", starch: "Rice / noodles", dal: "Dal / rasam", fry: "Fry", accompaniment: "Accompaniment" };
  const credit = dish.imageCredit ? `<a class="image-credit" href="${escapeHtml(dish.imageCredit.sourcePage)}" target="_blank" rel="noopener">Photo: ${escapeHtml(dish.imageCredit.creator)} · ${escapeHtml(dish.imageCredit.license)}</a>` : "";
  return `<section class="choice-dish"><div class="dish-image"><span aria-hidden="true">${escapeHtml(initials)}</span><img data-image data-dish-id="${escapeHtml(dish.id)}" src="${escapeHtml(dish.imagePath)}" alt="${escapeHtml(dish.name)}">${credit}</div><div class="choice-dish-content"><div><small>${labels[dish.mealRole] || `Dish ${dishIndex + 1}`}</small><h3>${escapeHtml(dish.name)}</h3><p>${dish.nutrition.energy} kcal · ${dish.nutrition.protein} g protein</p></div><div class="choice-dish-actions"><a href="${escapeHtml(dish.recipeUrl)}" target="_blank" rel="noopener">Recipe by ${escapeHtml(dish.sourceName)}</a><button type="button" data-swap data-choice="${choiceIndex}" data-dish="${dishIndex}" aria-label="Swap ${escapeHtml(dish.name)}"><span aria-hidden="true">↻</span> Swap</button></div></div></section>`;
}

function renderMealSummary() {
  const choice = selectedChoice();
  const totals = choice.totals;
  elements.mealSummary.innerHTML = `<div class="summary-heading"><div><p class="eyebrow">Selected dinner · ${choice.label}</p><h2 id="mealSummaryTitle">${choice.dishes.map((dish) => escapeHtml(dish.name)).join(" + ")}</h2></div><label class="portion-control">Portion<select id="quickPortion"><option value="light" ${state.menu.preferences.portion === "light" ? "selected" : ""}>Light</option><option value="regular" ${state.menu.preferences.portion === "regular" ? "selected" : ""}>Regular</option><option value="hearty" ${state.menu.preferences.portion === "hearty" ? "selected" : ""}>Hearty</option></select></label></div><div class="macro-row"><span><strong>${totals.energy}</strong> kcal</span><span><strong>${totals.protein} g</strong> protein</span><span><strong>${totals.carbs} g</strong> carbs</span><span><strong>${totals.fat} g</strong> fat</span></div><details class="calculation-note"><summary>How was this calculated?</summary><p>Planning estimates per person, not medical-grade measurements. Ingredients, oil, salt, substitutions, and portion size change the result. Estimated fibre: ${totals.fibre} g; sodium: ${totals.sodium} mg.</p></details>`;
  document.getElementById("quickPortion").addEventListener("change", (event) => { state.preferences.portion = event.target.value; saveJson(STORAGE.preferences, state.preferences); rebuildMenu(); });
}

function chooseMeal(index) { state.selected[state.date] = index; saveJson(STORAGE.selected, state.selected); renderMenu(); rememberMenu(); }
function swapDish(choiceIndex, dishIndex) {
  const before = currentOffsets();
  const offsets = nextSwapOffsets(state.catalog, state.date, state.preferences, before, choiceIndex, dishIndex);
  if (JSON.stringify(offsets) === JSON.stringify(before)) {
    elements.selectionNote.textContent = "No other compatible dish is available in this meal slot yet.";
    return;
  }
  state.swaps[state.date] = offsets;
  saveJson(STORAGE.swaps, state.swaps);
  rebuildMenu();
  document.querySelector(`[data-select="${choiceIndex}"]`)?.scrollIntoView({ behavior: "smooth", block: "center" });
}

function rememberMenu() {
  const history = loadJson(STORAGE.history, []); const choice = selectedChoice();
  const item = { date: state.menu.date, category: state.menu.categoryLabel, choice: choice.label, dishes: choice.dishes.map((dish) => dish.name), feedback: loadJson(STORAGE.feedback, {})[state.menu.date] || null };
  saveJson(STORAGE.history, [item, ...history.filter((entry) => entry.date !== item.date)].slice(0, 30));
}

function renderShoppingList() { const groups = buildShoppingList(selectedChoice()); elements.shoppingList.innerHTML = `<p class="quiet">For ${selectedChoice().label}: ${selectedChoice().dishes.map((dish) => escapeHtml(dish.name)).join(" + ")}</p>${Object.entries(groups).map(([group, items]) => `<section class="shopping-group"><h3>${group}</h3>${items.length ? `<ul>${items.map((item) => `<li class="${item.atHome ? "at-home" : ""}"><label><input type="checkbox" ${item.atHome ? "checked" : ""}> ${escapeHtml(item.name)}</label>${item.atHome ? "<small>At home</small>" : ""}</li>`).join("")}</ul>` : "<p class=\"quiet\">Nothing needed.</p>"}</section>`).join("")}`; }
function shoppingText() { const groups = buildShoppingList(selectedChoice()); return `${selectedChoice().label}: ${selectedChoice().dishes.map((dish) => dish.name).join(" + ")}\n\n${Object.entries(groups).map(([group, items]) => { const needed = items.filter((item) => !item.atHome); return needed.length ? `${group}:\n${needed.map((item) => `- ${item.name}`).join("\n")}` : ""; }).filter(Boolean).join("\n\n")}`; }

function openPreferences() { const prefs = normalizePreferences(state.preferences); const form = elements.preferencesForm; for (const name of ["householdSize", "budget", "portion", "diet", "whatsappNumber", "notificationTime"]) form.elements[name].value = prefs[name]; form.elements.allergies.value = prefs.allergies.join(", "); form.elements.dislikes.value = prefs.dislikes.join(", "); form.querySelectorAll("[name=cuisines]").forEach((input) => { input.checked = prefs.cuisines.includes(input.value); }); elements.preferencesDialog.showModal(); }
function savePreferences(event) { event.preventDefault(); const data = new FormData(event.currentTarget); state.preferences = normalizePreferences({ ...state.preferences, householdSize: data.get("householdSize"), budget: data.get("budget"), portion: data.get("portion"), diet: data.get("diet"), cuisines: data.getAll("cuisines"), allergies: data.get("allergies"), dislikes: data.get("dislikes"), whatsappNumber: data.get("whatsappNumber"), notificationTime: data.get("notificationTime") }); saveJson(STORAGE.preferences, state.preferences); elements.preferencesDialog.close(); rebuildMenu(); }
function renderHistory() { const history = loadJson(STORAGE.history, []); elements.historyList.innerHTML = history.length ? history.map((item) => `<article class="history-item"><p><strong>${escapeHtml(formatDate(item.date))}</strong> · ${escapeHtml(item.choice || "Selected meal")}</p><p>${item.dishes.map(escapeHtml).join(" · ")}</p>${item.feedback ? `<small>Feedback: ${escapeHtml(item.feedback)}</small>` : ""}</article>`).join("") : "<p>No meals remembered yet.</p>"; }
function recordFeedback(value) { const feedback = loadJson(STORAGE.feedback, {}); feedback[state.date] = value; saveJson(STORAGE.feedback, feedback); const ids = selectedChoice().dishes.map((dish) => dish.id); if (value === "skip") state.preferences.skippedDishIds = [...new Set([...(state.preferences.skippedDishIds || []), ...ids])]; if (value === "loved") state.preferences.favoriteDishIds = [...new Set([...(state.preferences.favoriteDishIds || []), ...ids])]; saveJson(STORAGE.preferences, state.preferences); rememberMenu(); elements.feedbackStatus.textContent = value === "skip" ? "Understood. This selected meal will stay out of future choices on this device." : "Saved for your selected meal."; }

document.getElementById("preferencesButton").addEventListener("click", openPreferences);
document.getElementById("historyButton").addEventListener("click", () => { renderHistory(); elements.historyDialog.showModal(); });
document.getElementById("shoppingButton").addEventListener("click", () => { renderShoppingList(); elements.shoppingDialog.showModal(); });
document.getElementById("copyShoppingButton").addEventListener("click", async (event) => { await navigator.clipboard.writeText(shoppingText()); event.currentTarget.textContent = "Shopping list copied"; });
document.getElementById("whatsappButton").addEventListener("click", () => { const number = String(state.preferences.whatsappNumber || "").replace(/\D/g, ""); const path = number ? `https://wa.me/${number}` : "https://wa.me/"; window.open(`${path}?text=${encodeURIComponent(menuShareText(state.menu))}`, "_blank", "noopener"); });
elements.preferencesForm.addEventListener("submit", savePreferences);
elements.pantryForm.addEventListener("submit", (event) => { event.preventDefault(); state.preferences.pantry = event.currentTarget.elements.pantry.value; state.preferences = normalizePreferences(state.preferences); saveJson(STORAGE.preferences, state.preferences); elements.feedbackStatus.textContent = "Pantry saved. Your selected meal’s shopping list is updated."; });
document.querySelectorAll("[data-feedback]").forEach((button) => button.addEventListener("click", () => recordFeedback(button.dataset.feedback)));
document.querySelectorAll("[data-close]").forEach((button) => button.addEventListener("click", () => document.getElementById(button.dataset.close).close()));

try { const [catalog, imageLibrary] = await Promise.all([loadCatalog(), loadImageLibrary()]); state.rawCatalog = catalog; state.imageLibrary = imageLibrary; state.catalog = filterCatalogByAvailableImages(catalog, imageLibrary); rebuildMenu(); if (location.hash === "#preferences") openPreferences(); } catch (error) { elements.errorMessage.textContent = `${error.message} Open the app through its local or hosted web address rather than directly from the file system.`; elements.errorMessage.hidden = false; }
