# WhatsInMenu

WhatsInMenu removes the nightly “what should we cook?” discussion. Every day it assembles three practical dinner choices around a household’s cuisine preferences, budget, diet, dislikes, pantry, and weekly protein rhythm. Each choice contains one protein, one vegetable, and one fry, dal, or rice/noodle accompaniment, with at most one starch-heavy dish.

It decides **what** to cook. Trusted publishers such as Bong Eats, Sanjeev Kapoor, and Hebbar’s Kitchen explain **how** to cook it.

## Current experience

- A real daily-menu preview near the top of the homepage
- Three deterministic meal choices every day, each designed for one cook to finish within one hour
- One protein + one vegetable + one accompaniment, with no rice-and-noodles or double-rice combinations
- One Gemini-generated photograph for every individual dish
- Select a choice, then swap individual dishes without rebuilding the other choices
- Household, portion, budget, cuisine, diet, allergy, and dislike preferences
- Estimated cooking time, household cost, servings, kcal, and core macros
- Expandable nutrition details with honest confidence language
- Pantry-aware shopping list grouped into protein, vegetables, spices, and pantry
- WhatsApp sharing, preferred-time capture, feedback, and recent meal history
- Advance notice when tomorrow’s meal needs soaking or marinating
- Festival specials after the configured launch gate

Preferences, swaps, feedback, pantry items, and history currently live only in the browser on that device. This keeps the prototype private and usable without an account while the hosted notification service is still being connected.

## Run locally

From the repository root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/web/landing.html`. The pages use browser modules and should be opened through the local server, not directly as files.

The deterministic Python version remains available for scheduled delivery:

```bash
python3 src/generate_menu.py
python3 src/generate_menu.py 2026-08-20
```

Install the optional Instagram renderer with `pip install -r requirements.txt`, then install Playwright’s Chromium browser once.

## Gemini meal photography

All generated project imagery must use Google’s **Gemini 3.1 Flash Image** model. The generator is pinned to the official model ID `gemini-3.1-flash-image`; it does not fall back to another model.

Copy `.env.example` to `.env`, then place your key on the `GEMINI_API_KEY` line. `.env` is ignored by Git and never loaded in browser code:

```bash
GEMINI_API_KEY=your-key
```

The reusable image direction is in `config/image_style.json`. Its `promptTemplate` uses `{name}` as the placeholder for one dish. Edit the template, framing, look, or avoid list to change the style without touching Python. Keep the model set to `gemini-3.1-flash-image`.

Generate the individual images for every dish across a day’s three choices:

```bash
npm run images -- --date 2026-08-20
```

Generated photos are saved under `web/assets/dishes/`. Until a photo exists, the website intentionally uses a branded color field rather than an image from another generator.

## Reusable image library

`data/image_repository.json` is the image database. It inventories every catalogue image and contains discovery records for 100 Bengali and 100 Punjabi dishes from `data/image_search_seeds.csv`.

Refresh the local inventory without making network requests:

```bash
python3 scripts/build_image_repository.py
```

Search Wikimedia Commons for freely licensed candidates:

```bash
python3 scripts/build_image_repository.py --discover
python3 scripts/build_image_repository.py --discover --cuisine bengali
python3 scripts/build_image_repository.py --discover-catalog
```

Discovery never publishes or downloads a candidate automatically. First verify that the photo really depicts the named dish and change its `reviewStatus` to `approved`. Then run:

```bash
python3 scripts/build_image_repository.py --approve DISH_ID --download-approved
```

Approved catalogue images are added to `web/image-library.json`, displayed automatically when a generated image is missing, and carry a visible creator/licence link on the card. Creator, source page, licence, and licence URL are retained for attribution. Ordinary recipe-site photographs must not be copied into the app unless the owner grants permission; a visible recipe page is not an image licence.

## WhatsApp delivery

The website can share tonight’s menu immediately. The scheduled delivery script is deliberately dry-run by default:

```bash
python3 scripts/send_whatsapp.py 2026-08-20
python3 scripts/send_whatsapp.py 2026-08-20 --send
```

Live sending needs these server-side environment values:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `WHATSAPP_TO`

The preferred delivery time collected in the browser becomes actionable once preferences are backed by a private hosted store.

## Tests

```bash
npm test
```

## Important product boundaries

- Nutrition and cost values are planning estimates, not medical or accounting advice.
- Ilish/Hilsa is blocked by a permanent runtime rule, complex recipes remain filtered, and mutton can appear only on the fourth Sunday of a month (and never on the economical budget).
- The product is a dinner helper, not a calorie tracker, social network, or generic recipe library.
- Every active catalogue dish has a dish-specific publisher URL; source changes should be verified before release.

The product and design brief is in `WhatsInMenu_Product_and_Design_Recommendations.docx`.
