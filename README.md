# Visora — Blue Light Glasses for Students

**Event-Driven Programming · Final Project (Business Website using PyScript)**

Visora is an online storefront for a student business that sells affordable (₱249) blue light glasses at
Cebu Eastern College, with **reserve online → campus pickup → pay on pickup**. The whole website is
written in **Python running in the browser with [PyScript](https://pyscript.net)** — there is no backend.

**Live site:** `https://<your-username>.github.io/<repo-name>/` (see *Deploy* below)

---

## What the site does

| Area | Features |
|------|----------|
| **Home** | Hero, survey stats, live **screen-time estimator** (slider) |
| **Our Business** | Business concept, how the business operates, pricing/economics |
| **Shop** | Live **search**, category filter, sorting, add to cart, live stock |
| **Cart / Checkout** | +/− quantities, live **referral-code check** and live total, order validation |
| **My Orders** | Order tabs, order timeline, cancel order, find an order by code or mobile number |
| **Contact** | Message form with live character counter |
| **Staff area** (`#/admin`) | Confirm / prepare / complete / cancel orders with messages to buyers, inventory & price editing, customer messages, sales summary with break-even bar |

Staff demo password: `visora2026` (client-side demo only — see *Limitations*).
Open **Staff → Sales → "Load sample orders"** to fill the staff area with demo data.

## Event-Driven Programming — where to look

The page does nothing until the user acts. Every interaction is an **event** handled by Python in [`py/main.py`](py/main.py):

| Event | Python handler | Examples |
|-------|----------------|----------|
| `click` | `on_click` → `ACTIONS` table | Add to cart, qty +/−, cancel order, confirm / ready / pick-up, save stock |
| `submit` | `on_submit` → `FORMS` table | Checkout, contact form, find order, admin login |
| `input` | `on_input` → `INPUTS` table | Live shop search, referral-code check, sliders, character counter |
| `change` | `on_change` → `CHANGES` table | Sort / filter dropdowns, cart quantity box |
| `hashchange` | `render()` | Moving between pages without reloading |

The handlers are registered with PyScript's `@when("event", "#root")` decorator (event delegation: one
listener per event type, dispatching on `data-action` / `data-form` / `data-input` / `data-change`
attributes). Handlers update data, then redraw the page or only the part that changed (dynamic page updates).

## Project structure

```
index.html          Page shell + PyScript <script type="py"> tag
pyscript.toml       PyScript config (which Python files to load)
py/
  main.py           Events + routing  (the event-driven controller)
  logic.py          Business logic: cart, checkout, referral, order workflow, inventory, screen-time estimator
  views.py          HTML for every page (pure functions returning strings)
  data.py           Constants, products, labels, business figures
  storage.py        localStorage / sessionStorage wrapper (replaces the old SQLite database)
static/             style.css + product images
docs/               Video script, contributions tracker
```

## Run locally

PyScript needs the files served over HTTP (opening `index.html` by double-click will not work):

```bash
python -m http.server 8000
# open http://localhost:8000
```

## Team

| Member | Part |
|--------|------|
| Dave Formentera | Event handling & routing (`py/main.py`), setup, deployment |
| Christopher Boltron | Business logic (`py/logic.py`) |
| Myco Dumas-og | Customer pages (`py/views.py`: shop, cart, checkout, My Orders) |
| Ken Luis Jagmoc | Staff area, order tracker, styling and hero animation |
| Kurt Rolly Peñafiel | Business content, data/storage, documentation |

## Limitations

- There is no server: orders, stock and messages are stored in **this browser's localStorage**, so the
  buyer view and the staff view must be opened in the same browser (that is how the demo works).
- The staff password is checked in the browser, so it is a demo gate, not real security.

## Origin

Converted from the group's earlier Flask + SQLite version. Same design and features, rebuilt around PyScript
so the site is static, hostable on GitHub Pages and demonstrates event-driven programming directly.
Business figures come from the Visora feasibility study (Sept 26, 2026).
