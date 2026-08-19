import { DEFAULT_PREFERENCES, buildMenu, formatDate, normalizePreferences, todayInKolkata } from "./menu-engine.js?v=6";

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}

const preview = document.getElementById("livePreview");
try {
  const response = await fetch("../data/dishes.json?v=6", { cache: "no-store" });
  if (!response.ok) throw new Error("Menu unavailable");
  const catalog = await response.json();
  let stored = DEFAULT_PREFERENCES;
  try { stored = JSON.parse(localStorage.getItem("whatsinmenu.preferences.v2")) || stored; } catch { /* default */ }
  const menu = buildMenu(catalog, todayInKolkata(), normalizePreferences(stored));
  preview.innerHTML = `
    <div class="preview-top"><p class="eyebrow">Live preview · ${escapeHtml(formatDate(menu.date))}</p><h2>Three choices tonight</h2></div>
    <div class="preview-content">
      <div class="preview-dishes">${menu.choices.map((choice) => `<div class="preview-dish"><small>${choice.label}</small><strong>${choice.dishes.map((dish) => escapeHtml(dish.name)).join(" · ")}</strong></div>`).join("")}</div>
      <div class="preview-meta"><span>Three complete meals</span><span>·</span><span>Choose one</span><span>·</span><span>Shop once</span></div>
      <a class="pill-button full-width" href="today.html">View recipes, swap, and shop</a>
    </div>`;
} catch {
  preview.innerHTML = `<div class="preview-placeholder"><p>Tonight’s menu will appear when the site is served.</p></div>`;
}
