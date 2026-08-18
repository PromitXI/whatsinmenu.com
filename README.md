# WhatsInMenu

A daily home-menu suggester built for one household. Every day it proposes
three protein + vegetable combos — mostly Bengali, sometimes Chinese-style or
North Indian — plus a shopping list, and (once wired up) a WhatsApp ping and
an Instagram post.

Nothing here is AI-written cuisine: every dish links out to a real recipe
from Bong Eats, Sanjeev Kapoor, or Hebbar's Kitchen. The app only decides
**what** to suggest, never **how** to cook it.

## How it decides

Two conceptual stages (both plain deterministic rules, not live LLM calls,
so the webapp and any scheduled send always agree on the same day):

- **Mother agent** — sets the household rules before anything is picked:
  Ilish is banned outright (too expensive), a weekly protein budget caps
  chicken at 3x/week, fish/seafood at 1x/week, mutton to roughly every
  other week, skips anyone's disliked dishes, and filters out fussy
  multi-step recipes.
- **Cook agent** — picks the actual 3 combos from what the Mother agent
  allows, attaches a shopping list to each, and flags anything that needs
  advance soaking/marinating a day ahead.

A 10-day cold start keeps the first stretch Bengali/North-Indian-only
before Chinese-style days start appearing. A 100-day gate holds back
festival-special and other once-a-year dishes until the app has been
running a while.

## Layout

```
data/dishes.json         the dish database (protein/vegetable pools, spice
                          level, source, ingredients, festival specials)
config/exclusions.json   wife/kid dish exclusions (currently empty — fill
                          in and it's respected automatically)
src/prng.py              deterministic PRNG shared byte-for-byte between
                          the Python generator and the webapp's JS
src/generate_menu.py     the daily generator (CLI + WhatsApp message format)
scripts/render_insta_image.py
                          renders a branded 1080x1080 Instagram graphic
                          via Playwright (no external image-gen API yet)
web/landing.html          marketing homepage
web/today.html            the actual daily app (what gets opened every morning)
web/insta_template.html   HTML template used by the Instagram image renderer
```

## Running it

```
python3 src/generate_menu.py                # today, Asia/Kolkata
python3 src/generate_menu.py 2026-08-20      # a specific date
python3 scripts/render_insta_image.py 2026-08-20 out.png
```

Open `web/today.html` directly in a browser — it's fully self-contained
and computes the same day's answer as the Python side independently.

## Still open

- Hosting/domain for whatsinmenu.com
- Twilio WhatsApp credentials for the daily send
- Meta/Instagram Graph API access for auto-posting
- Promit's actual "once a year" dish list (a placeholder festival-specials
  set is seeded in `data/dishes.json` for now)
- 2027 festival dates (2026's are hardcoded and will all be past the
  100-day gate before it opens)
