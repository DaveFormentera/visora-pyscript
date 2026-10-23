# Video Speaking Notes — Visora (10+ minutes, everyone speaks)

Rough order and timing. Speak in your own words; these are talking points, not a script.
Screen-share the site (run it first and click **Staff → Sales → Load sample orders** so there is data).

| Part | Who | Time |
|------|-----|------|
| 1. Introduction | Dave (all members say their name) | ~1 min |
| 2. Business process | Kurt | ~2 min |
| 3. Website demonstration | Myco (customer side), Ken (staff side) | ~3 min |
| 4. Code explanation | Dave, Christopher | ~3 min |
| 5. Individual contributions | Everyone, ~1 min each | ~5 min |

---

## 1. Introduction — Dave
- "Hi, we are Group ___ . Our business is **Visora**, affordable blue light glasses for students."
- Each member says: name + one sentence on their role (Dave, Christopher, Myco, Ken Luis, Kurt Rolly).
- Concept: ₱249 blue light glasses sold at Cebu Eastern College. Students reserve online, pick up on campus, try them on, and pay only on pickup.
- Why: our survey found 63% of students use screens 5+ hours a day and 83% get eye strain or headaches.

## 2. Business process — Kurt
Open the **Our Business** page.
- Problem → solution → customers (the three cards).
- Walk the 5 steps: student reserves → staff confirms and messages the time → order is prepared and marked ready → student picks up, tries, pays cash/GCash → referral code brings friends (₱20 off).
- "The website supports each step": the shop and checkout for step 1; the staff area for steps 2–4; the referral code for step 5.
- Pricing: sells at ₱249, costs ₱55, so ₱194 profit per pair; ₱4,350 startup capital, ₱500/month fixed costs.
- Mention break-even is 23 pairs for startup capital alone.

## 3a. Demo: customer side — Myco
1. **Home**: drag the screen-time slider; the estimate changes instantly.
2. **Shop**: type "crystal" in search (list filters as you type), change the sort, add two items (toast and cart badge update).
3. **Cart**: use + / − to change quantity; subtotal updates.
4. **Checkout**: fill the form, choose **preferred pickup date and time**, type referral code `REFDEMO1` (shows "Code accepted", total drops by ₱20). Try submitting with the time empty to show validation.
5. **Order page**: show the order code, the pickup spot with your preferred time, and the status timeline.
6. **My Orders**: show tabs; cancel an order and show it moves to Cancelled.

## 3b. Demo: staff side — Ken
1. Go to `#/admin` (Staff link in the footer), login with the password.
2. **Orders**: new orders under "New". Use the **order tracker** search: type a code, a name, then part of a phone number; the list filters live across all tabs.
3. Open a new order: type a message ("Tomorrow 12:30 PM at the canteen"), click **Confirm order**, then **Mark ready**, then **Mark picked up & paid**. Switch back to the customer tab to show the buyer's timeline updated.
4. **Inventory**: change a stock number; show the "Low stock" tag.
5. **Messages** and **Sales** (break-even bar). Mention the hero animation on the home page is CSS/SVG that Ken built.

## 4a. Code explanation: events — Dave
Show `index.html`: the `<script type="py" src="./py/main.py" config="./pyscript.toml">` line, then `pyscript.toml` listing the Python files.
Open `py/main.py`:
- "Event-driven programming means the program waits and Python functions run only when the user does something."
- Show the five event types in the header comment: click, submit, input, change, hashchange.
- Show `@when("click", "#root")` → `on_click` → the `ACTIONS` table. Trace one event end to end:
  **Add to cart button → `a_add` → `logic.cart_add` → toast + `refresh_cart_badge`.**
- Show `@when("input", "#root")` and `update_referral` (runs on every keystroke at checkout).
- Show `render()` and the `hashchange` listener: the URL `#/shop` changes, Python redraws the page, no reload.
- Why we use one listener on `#root` (event delegation): buttons are created dynamically, so one listener handles them all.

## 4b. Code explanation: logic — Christopher
Open `py/logic.py`:
- `cart_add` / `cart_set`: stock limits, cart saved in localStorage.
- `place_order`: validates fields, checks the pickup date/time (`check_pickup_time`), applies the referral discount (`referral_discount`), reduces stock, creates the order code `VIS-XXXXXX`.
- Order workflow: Reserved → Confirmed → Ready for pickup → Completed (or Cancelled, which returns stock) in `admin_set_status` and `cancel_order`.
- Point out that `logic.py` has no HTML, so it is easy to test, and `views.py` only turns data into HTML.

## 5. Individual contributions (about 1 minute each)
Format: "I'm ___. I worked on ___ (files). Here is one piece of code I wrote." Show the file and your commits on GitHub.

- **Dave Formentera** — `py/main.py`, `index.html`, `pyscript.toml`, deployment. Explain: the `ACTIONS/FORMS/INPUTS/CHANGES` tables and `render()`.
- **Christopher Boltron** — `py/logic.py`. Explain: `place_order` and `referral_discount`, or the order status workflow.
- **Myco Dumas-og** — customer pages in `py/views.py`. Explain: `shop_cards` (live search/sort), the checkout form with the preferred pickup date/time, and the order timeline.
- **Ken Luis Jagmoc** — staff pages, order tracker, `static/style.css`, hero animation. Explain: `search_orders` + `update_admin_search` (live filter), and the rolling-light animation (SVG circles with a moving dash).
- **Kurt Rolly Peñafiel** — Our Business page, `data.py`, `storage.py`, docs. Explain: `storage.py` (localStorage replaces the old database), `breakeven_units()` for the break-even numbers, and the README.

## Closing — everyone
"Thank you for watching. Our code is in our public GitHub repository."

### Before you record
- [ ] Video is at least 10 minutes
- [ ] Every member appears and speaks
- [ ] Site runs without errors (F12 → Console is clean)
- [ ] Every member has real commits on GitHub that match their part
- [ ] Video is added to the repo or shared as your instructor instructs
