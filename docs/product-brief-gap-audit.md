# Product brief gap audit

Reviewed against `WhatsInMenu_Product_and_Design_Recommendations.docx` on 20 August 2026.

## Implemented

- Live three-choice menu preview near the top of the homepage
- Three individual dish cards and images/placeholders per choice
- Household, budget, portion, diet, cuisine, allergy, dislike, and pantry preferences
- Dish-level swapping without rebuilding the other two choices
- Combined shopping list grouped by protein, vegetables, spices, and pantry
- Recipe-source links and plain-language nutrition confidence
- Estimated time, household cost, servings, calories, and core macros
- Manual WhatsApp sharing, preferred delivery-time capture, feedback, and recent history
- Bengali, Chinese-style, North Indian, Andhra, and South Indian cuisine filters
- Mobile layout and repeated calls to view/choose tonight's menu

## Partly implemented

- **Use what I have:** pantry items affect ordering and shopping-list status, but the app does not yet search a broad recipe corpus for ingredient matches.
- **Preference memory:** saved on one browser/device; no private account or server-side household profile yet.
- **Feedback learning:** skip feedback removes dishes, while favourite history is recorded but does not yet strongly re-rank future menus.
- **Nutrition:** clearly labelled estimates, but not calculated from exact recipe quantities or serving weights.
- **WhatsApp:** sharing and a server-side send script exist, but browser preferences are not connected to a hosted scheduler.
- **Images:** all live files are catalogued, a reusable-image discovery database exists, and approved licensed internet images automatically replace missing placeholders with visible attribution. Unmatched dishes still need reviewed photos.
- **Recipe sources:** every catalogue dish links to a publisher, but source quantities are not ingested into the nutrition calculation.

## Still to build

1. Private hosted preference storage and a real scheduled WhatsApp notification service.
2. Quantity-aware nutrition with serving grams, sodium, sugar, and confidence derived from each recipe.
3. Stronger learning from favourites, skips, repeats, and household feedback.
4. A real ingredient-to-recipe search for “use what I have.”
5. Continue visual review and approval of discovered photos; visible attribution is now automatic for approved images.
6. Continue the licensed-image search for dishes with no confident Wikimedia Commons result.
7. A consistent hand-drawn icon set to replace the remaining emoji/text glyphs.
8. Move WhatsApp opt-in beside the first live menu preview, as requested in the brief.
9. Public deployment, monitoring, and a production privacy/consent flow.

## New household rule added after the brief

Every normal choice must be practical for one cook in one hour:

- exactly one protein;
- exactly one vegetable;
- one fry, dal, accompaniment, rice, or noodle dish;
- never both rice and noodles, and never two rice dishes;
- swapping one slot must not duplicate the same slot in another choice.

The special 19 August sample menu was also updated to follow this rule rather than preserving combinations that contain two proteins or two fried/starchy sides.
