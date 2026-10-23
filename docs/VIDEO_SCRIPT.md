# Video Presentation Guide (minimum 10 minutes, every member appears and speaks)

Record a screen share with each member on camera/voice. Suggested timing (adjust to your group size):

| # | Section | Time | What to cover |
|---|---------|------|---------------|
| 1 | **Introduction** | ~1 min | Business name (Visora), every member introduces themselves, business concept: ₱249 blue light glasses for CEC students. Mention the survey (63% use screens 5+ hours, 83% get eye strain). |
| 2 | **Business process** | ~2 min | Walk through the *Our Business* page: reserve online → staff confirms → ready for pickup → student picks up & pays → referral growth. Explain how each step is supported by the website. Show the pricing/economics. |
| 3 | **Website demonstration** | ~3 min | As a student: home slider → shop search/sort → add to cart → +/− quantity → checkout with referral code `REFDEMO1` → order page timeline → My Orders → cancel. As staff (`#/admin`, password `visora2026`): confirm order with a message, mark ready, mark picked up, inventory edit, messages, sales + break-even. Tip: click **Sales → Load sample orders** first. |
| 4 | **Code explanation** | ~3 min | Show `index.html` (`<script type="py">`), `pyscript.toml`, then `py/main.py`: `@when("click", "#root")`, the `ACTIONS / FORMS / INPUTS / CHANGES` tables, `render()` and `hashchange`. Show one full event: click *Add to cart* → `a_add` → `logic.cart_add` → toast + badge update. Show `logic.py` (checkout, referral, order workflow, `screen_report()` estimator) and `views.py` (HTML + escaping). |
| 5 | **Individual contributions** | ~1 min each | Each member: name, which files/features they built, and one piece of code they can explain. Match `docs/CONTRIBUTIONS.md` and your commits. |

Checklist: ☐ ≥10 minutes ☐ all members seen and heard ☐ demo works live ☐ video added to the repo (or link per instructor).
