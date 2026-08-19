# WhatsInMenu Instagram launch plan

## Goal

Use Instagram to turn the daily dinner decision into a simple ritual: show three complete choices, invite the family to vote, and send interested people to WhatsInMenu to choose, swap, and shop.

## Phase 1 — Create the account and foundation

1. Create `@whatsinmenu` or the closest available handle.
2. Select a **Business professional account**. Instagram distinguishes Business and Creator accounts; Business is the better fit for a product that wants website visits, scheduling, analytics, and future advertising.
3. Create a matching WhatsInMenu Facebook Page and connect it to Instagram. Meta recommends this connection for access to its business tools, shared inbox, cross-posting, and integrations.
4. Enable two-factor authentication and save the recovery codes outside the repository.
5. Complete the profile:
   - Name: `WhatsInMenu · Dinner Decided`
   - Category: `Food & beverage` or `Kitchen/cooking`
   - Bio: `Three practical dinner choices every day. Pick one, swap a dish, and shop once. Mostly Bengali, always made for home.`
   - Link: the public WhatsInMenu URL once the site is deployed
   - Profile image: the WhatsInMenu wordmark or a simple brand mark

The professional account will be public. Meta's current setup guidance is available in its [professional-account overview](https://www.facebook.com/help/instagram/138925576505882) and [Page connection guide](https://www.facebook.com/help/570895513091465).

## Phase 2 — Run a 14-day manual pilot

Do not automate posting immediately. First confirm that the format is useful and that the generated images, dish names, and recipe sources are correct.

### Daily carousel, around 5:30 PM IST

Use five slides:

1. Cover: `What should we cook tonight?` plus the date.
2. Choice 1: its three individually photographed dishes.
3. Choice 2: its three individually photographed dishes.
4. Choice 3: its three individually photographed dishes.
5. Call to action: `Comment 1, 2, or 3 · Open WhatsInMenu to swap and shop.`

Each choice slide should show the dish names clearly in the designed graphic. Do not place text inside the Gemini food photographs themselves.

### Daily Story

- Post a three-option poll or quiz asking followers to pick Choice 1, 2, or 3.
- Share the winning choice the following morning.
- Add a link sticker to the public menu page after deployment.

### Two weekly Reels, only when real cooking footage exists

- A short preparation moment, plated result, or family choice reveal.
- Do not manufacture cooking footage from still images.
- Keep the daily carousel as the primary, dependable format.

## Caption template

```text
Dinner, without the debate. 🍽️

Choice 1: <three dishes>
Choice 2: <three dishes>
Choice 3: <three dishes>

Which one are you cooking—1, 2, or 3?

Recipes are linked to their original publishers inside WhatsInMenu.
Images are AI-generated serving suggestions. Nutrition and cost are planning estimates.

#WhatsInMenu #BengaliFood #IndianHomeCooking #DinnerIdeas #HomeCooking
```

Use a small, relevant hashtag set. Avoid copying long generic hashtag blocks.

## Phase 3 — Establish the publishing workflow

For the first two weeks:

1. Generate and inspect the nine individual dish images.
2. Generate the five-slide social pack.
3. Verify dish spelling, recipe attribution, date, and choice order.
4. Save the post as a draft or schedule it in Meta Business Suite.
5. Have one human approve it before publication.

Connecting Instagram to its Facebook Page enables shared management and Meta Business Suite tools. Meta documents the connection benefits in its [Instagram–Facebook Page guide](https://www.facebook.com/help/instagram/402748553849926).

## Phase 4 — Automate after the pilot

Automation prerequisites:

- WhatsInMenu is publicly hosted; `127.0.0.1` cannot be used by followers or Meta's publishing systems.
- The Instagram account is professional and connected to the WhatsInMenu Facebook Page.
- The daily menu and social images are stored at stable public HTTPS URLs.
- A Meta developer app has the required Instagram publishing permissions.
- Publishing credentials are server-side secrets, never browser code or GitHub files.

Recommended automated sequence:

1. Generate tomorrow's three choices.
2. Generate missing individual dish photographs with Gemini 3.1 Flash Image.
3. Build the five carousel slides and caption.
4. Run validation for nine images, three choices, recipe links, and prohibited text.
5. Create an approval draft by 4:30 PM IST.
6. Publish or schedule after approval for approximately 5:30 PM IST.
7. Record the Instagram post ID and its menu date for analytics.

Keep a manual publishing fallback even after automation.

## Phase 5 — Measure what matters

Review once a week:

- Saves per post
- Shares per post
- Comments or Story votes for Choices 1–3
- Carousel completion to the final slide
- Profile visits
- Website-link taps
- Returning visitors to the daily menu
- Which cuisine and dish combinations earn the most saves

Follower count is secondary. The strongest signal is whether people save, share, vote, and return for the next dinner decision.

## Four-week rollout

- **Week 1:** Account, profile, connected Facebook Page, first seven manual carousels.
- **Week 2:** Continue daily carousels, add Stories, refine the choice-slide design from engagement.
- **Week 3:** Build the social-pack generator and approval screen; continue publishing manually.
- **Week 4:** Connect Meta publishing in test mode, then enable scheduled posting only after three successful reviewed test posts.

## Immediate next actions for Promit

1. Create the Instagram account as a Business professional account.
2. Create and connect the WhatsInMenu Facebook Page.
3. Send the final Instagram handle to the project.
4. Deploy WhatsInMenu publicly before adding the website link or enabling automated publishing.
