# WhatsInMenu

WhatsInMenu removes the nightly “what should we cook?” discussion. Every day it assembles three complete dinner choices, each with three coordinated dishes, around a household’s cuisine preferences, budget, diet, dislikes, pantry, and weekly protein rhythm.

It decides **what** to cook. Trusted publishers such as Bong Eats, Sanjeev Kapoor, and Hebbar’s Kitchen explain **how** to cook it.

## Current experience

- A real daily-menu preview near the top of the homepage
- Three deterministic meal choices every day, with three dishes in each choice
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
- Ilish remains excluded, complex recipes remain filtered, and the default weekly rhythm limits expensive proteins.
- The product is a dinner helper, not a calorie tracker, social network, or generic recipe library.
- Every active catalogue dish has a dish-specific publisher URL; source changes should be verified before release.

The product and design brief is in `WhatsInMenu_Product_and_Design_Recommendations.docx`.
