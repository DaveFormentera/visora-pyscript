"""logic.py - Visora business logic (no DOM code here, so it is easy to test).

Everything the Flask app did in app.py (cart, checkout, referral codes, order
workflow, inventory, sales stats) lives here as plain Python functions that work
on a `db` dict saved in localStorage.
"""
import copy
import random
import string
from datetime import datetime, timedelta

import storage
from data import (PRICE, UNIT_COST, STARTUP, REFERRAL_DISCOUNT,
                  SEED_PRODUCTS, PICKUP_SLOTS, STATUS_FLOW, STATUS_LABEL, STEP_TITLE, TABS, ADMIN_TABS)

DB_KEY, CART_KEY, MINE_KEY = "visora_db_v1", "visora_cart_v1", "visora_my_orders_v1"


# ---------------------------------------------------------------- database
def fresh_db():
    return {"products": copy.deepcopy(SEED_PRODUCTS), "orders": [], "messages": []}


def load():
    db = storage.get(DB_KEY)
    if not db or "products" not in db:
        db = fresh_db()
        save(db)
    return db


def save(db):
    storage.put(DB_KEY, db)


def now():
    return datetime.now().isoformat(timespec="seconds")


def new_code(prefix, n=6):
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


def product(db, pid):
    for p in db["products"]:
        if p["id"] == int(pid):
            return p
    return None


def order_by_code(db, code):
    code = (code or "").strip().upper()
    for o in db["orders"]:
        if o["code"] == code:
            return o
    return None


# ---------------------------------------------------------------- cart
def get_cart(db):
    """Return (items, subtotal). Quantities are capped at the current stock."""
    cart = storage.get(CART_KEY, {})
    items = []
    for key, qty in cart.items():
        p = product(db, key)
        if not p or not p["active"]:
            continue
        qty = min(int(qty), p["stock"])
        if qty > 0:
            items.append(dict(p, qty=qty))
    items.sort(key=lambda i: i["id"])
    return items, sum(i["price"] * i["qty"] for i in items)


def cart_count(db):
    return sum(i["qty"] for i in get_cart(db)[0])


def cart_add(db, pid):
    p = product(db, pid)
    if not p or not p["active"]:
        return False, "That product is not available."
    cart = storage.get(CART_KEY, {})
    have = cart.get(str(p["id"]), 0)
    if have + 1 > p["stock"]:
        return False, f"Only {p['stock']} left of {p['name']}."
    cart[str(p["id"])] = have + 1
    storage.put(CART_KEY, cart)
    return True, f"Added {p['name']} to your cart."


def cart_set(db, pid, qty):
    cart = storage.get(CART_KEY, {})
    try:
        qty = int(qty)
    except (TypeError, ValueError):
        qty = 0
    p = product(db, pid)
    if qty <= 0 or not p:
        cart.pop(str(pid), None)
    else:
        cart[str(pid)] = min(qty, p["stock"])
    storage.put(CART_KEY, cart)


def cart_clear():
    storage.put(CART_KEY, {})


# ---------------------------------------------------------------- my orders (this device)
def my_codes():
    return storage.get(MINE_KEY, [])


def remember(code):
    mine = my_codes()
    if code not in mine:
        mine.append(code)
    storage.put(MINE_KEY, mine[-30:])


def owns(code):
    return code in my_codes()


# ---------------------------------------------------------------- referral / checkout
def referral_discount(db, code):
    """Pesos off for a referral code (0 if the code is blank or unknown)."""
    code = (code or "").strip().upper()
    if not code:
        return 0
    for o in db["orders"]:
        if o["my_referral"] == code and o["status"] != "Cancelled":
            return REFERRAL_DISCOUNT
    return 0


def _build_order(db, items, f, status="Reserved", created=None):
    subtotal = sum(i["price"] * i["qty"] for i in items)
    ref = (f.get("referral") or "").strip().upper()
    discount = referral_discount(db, ref)
    code = new_code("VIS-")
    while order_by_code(db, code):
        code = new_code("VIS-")
    created = created or now()
    order = dict(
        code=code, name=f["name"], section=f["section"], contact=f["contact"],
        pickup=f.get("pickup") or "CEC campus", pickup_date=f.get("pickup_date", ""),
        pickup_time=f.get("pickup_time", ""), payment=f.get("payment") or "Cash on pickup",
        notes=(f.get("notes") or "").strip(), referral_used=ref if discount else "",
        my_referral=f.get("my_referral") or new_code("REF", 5),
        subtotal=subtotal, discount=discount, total=max(subtotal - discount, 0),
        status="Reserved", created=created, pickup_note="",
        items=[dict(pid=i["id"], slug=i["slug"], kind=i["kind"], name=i["name"], price=i["price"], qty=i["qty"]) for i in items],
        events=[dict(status="Reserved", note="Order placed", created=created)],
    )
    for i in items:  # take stock
        product(db, i["id"])["stock"] -= i["qty"]
    db["orders"].append(order)
    if status != "Reserved":
        for s in STATUS_FLOW[1:STATUS_FLOW.index(status) + 1]:
            order["events"].append(dict(status=s, note="", created=created))
        order["status"] = status
    return order


def place_order(db, form):
    """Validate the checkout form and create the order. Returns (order, error)."""
    items, _ = get_cart(db)
    if not items:
        return None, "Your cart is empty."
    form = {k: (v or "").strip() if isinstance(v, str) else v for k, v in form.items()}
    if not (form.get("name") and form.get("contact") and form.get("section")):
        return None, "Name, section and contact number are required."
    when_err = check_pickup_time(form.get("pickup_date"), form.get("pickup_time"))
    if when_err:
        return None, when_err
    order = _build_order(db, items, form)
    save(db)
    cart_clear()
    remember(order["code"])
    return order, ""


def check_pickup_time(date_str, slot):
    """Validate the buyer's preferred pickup date and time slot. Returns an error message or ''."""
    if not date_str or not slot:
        return "Please choose your preferred pickup date and time."
    if slot not in PICKUP_SLOTS:
        return "Please pick one of the pickup time slots."
    try:
        day = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Please choose a valid pickup date."
    if day < datetime.now().date():
        return "Your pickup date can't be in the past."
    return ""


def pickup_label(o):
    """Human-readable preferred pickup time, e.g. 'Sat, Oct 24, 2026 \u00b7 10:00 \u2013 11:00 AM'."""
    if not o.get("pickup_date"):
        return ""
    try:
        day = datetime.strptime(o["pickup_date"], "%Y-%m-%d").strftime("%a, %b %d, %Y")
    except ValueError:
        day = o["pickup_date"]
    return f"{day} \u00b7 {o.get('pickup_time', '')}".strip(" \u00b7")


def search_orders(orders, q):
    """Admin search: match order code, buyer name, course/section or contact number."""
    q = (q or "").strip().lower()
    if not q:
        return list(orders)
    digits = "".join(c for c in q if c.isdigit())
    out = []
    for o in orders:
        hay = " ".join([o["code"], o["name"], o["section"], o["contact"]]).lower()
        phone = "".join(c for c in o["contact"] if c.isdigit())
        if q in hay or (len(digits) >= 3 and digits in phone):
            out.append(o)
    return out


# ---------------------------------------------------------------- finding / cancelling orders
def find_orders(db, q):
    """Look up by order code (VIS-XXXXXX) or by mobile number."""
    q = (q or "").strip()
    if q.upper().startswith("VIS-"):
        o = order_by_code(db, q)
        return ("code", [o]) if o else ("none", [])
    digits = "".join(c for c in q if c.isdigit())
    if len(digits) >= 7:
        found = [o for o in reversed(db["orders"])
                 if "".join(c for c in o["contact"] if c.isdigit()).endswith(digits[-10:])]
        if found:
            return "phone", found
    return "none", []


def my_orders(db):
    mine = set(my_codes())
    return [o for o in reversed(db["orders"]) if o["code"] in mine]


def filter_by_tab(orders, tabs, key):
    wanted = {k: s for k, _, s in tabs}.get(key)
    return [o for o in orders if wanted is None or o["status"] in wanted]


def tab_counts(orders, tabs):
    return {k: len(filter_by_tab(orders, tabs, k)) for k, _, _ in tabs}


def _restock(db, order, sign):
    for it in order["items"]:
        p = product(db, it["pid"])
        if p:
            p["stock"] = max(p["stock"] + sign * it["qty"], 0)


def cancel_order(db, code):
    """Buyer cancels their own order (only before it is ready for pickup)."""
    o = order_by_code(db, code)
    if not o or not owns(o["code"]) or o["status"] not in ("Reserved", "Confirmed"):
        return False
    _restock(db, o, +1)
    o["status"] = "Cancelled"
    o["events"].append(dict(status="Cancelled", note="Cancelled by buyer", created=now()))
    save(db)
    return True


def timeline(order):
    """Build the status timeline shown on the order page."""
    when, notes = {}, {}
    for e in order["events"]:
        when.setdefault(e["status"], e["created"])
        if e["note"] and e["note"] != "Order placed":
            notes[e["status"]] = e["note"]
    when.setdefault("Reserved", order["created"])
    cancelled = order["status"] == "Cancelled"
    cur = -1 if cancelled else STATUS_FLOW.index(order["status"])
    steps = []
    for i, s in enumerate(STATUS_FLOW):
        state = "done" if i < cur or (i == cur and s == "Completed") else ("now" if i == cur else "todo")
        steps.append(dict(key=s, state=state, time=when.get(s) if i <= cur else None,
                          note=notes.get(s) if i <= cur else None))
    return steps, cancelled, when.get("Cancelled")


# ---------------------------------------------------------------- admin
def admin_set_status(db, code, new, note=""):
    """Staff moves an order to a new status (and optionally messages the buyer)."""
    o = order_by_code(db, code)
    note = (note or "").strip()
    if not o or new not in STATUS_LABEL:
        return None
    changed = new != o["status"]
    if changed:
        if new == "Cancelled":
            _restock(db, o, +1)
        elif o["status"] == "Cancelled":
            _restock(db, o, -1)
        o["status"] = new
    if note:
        o["pickup_note"] = note
    if changed or note:
        o["events"].append(dict(status=new, note=note, created=now()))
    save(db)
    return f"{o['code']} → {STEP_TITLE[new]}" + (" (message sent to buyer)" if note else "")


def update_product(db, pid, stock, price):
    try:
        stock, price = int(stock), int(price)
    except (TypeError, ValueError):
        return False
    p = product(db, pid)
    if not p:
        return False
    p["stock"], p["price"] = max(stock, 0), max(price, 0)
    save(db)
    return True


def add_message(db, name, contact, kind, body):
    name, body = (name or "").strip(), (body or "").strip()
    if not name or not body:
        return False
    db["messages"].append(dict(name=name, contact=(contact or "").strip(), kind=kind or "Question",
                               body=body, created=now()))
    save(db)
    return True


def sales_stats(db):
    active = [o for o in db["orders"] if o["status"] != "Cancelled"]
    done = [o for o in db["orders"] if o["status"] == "Completed"]
    pairs = sum(i["qty"] for o in active for i in o["items"] if i.get("kind") == "glasses")
    rev = sum(o["total"] for o in active)
    return dict(n=len(active), rev=rev, done_rev=sum(o["total"] for o in done), pairs=pairs,
                gross=rev - pairs * UNIT_COST, breakeven=breakeven_units(PRICE, UNIT_COST, STARTUP),
                startup=STARTUP)


def load_demo(db):
    """Reset everything and add sample orders so the staff area has data to show."""
    db.clear()
    db.update(fresh_db())
    cart_clear()
    storage.put(MINE_KEY, [])
    cat = {p["slug"]: dict(p, qty=1) for p in db["products"]}
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    base = dict(pickup="CEC campus — canteen", payment="GCash")
    samples = [
        ("Maria Santos", "BSIT – 9", "0917 123 4567", ["classic-round", "hard-case"], "Completed", dict(my_referral="REFDEMO1")),
        ("Jon Reyes", "BSBA – 3", "0928 555 0101", ["campus-square"], "Ready for pickup", {}),
        ("Ana Lim", "BSED – 5", "0999 222 3344", ["clear-crystal", "cleaning-cloth"], "Confirmed", {}),
        ("Carlo Dizon", "BSIT – 2", "0905 777 8899", ["campus-square"], "Reserved", dict(referral="REFDEMO1")),
    ]
    for name, section, contact, slugs, status, extra in samples:
        f = dict(base, name=name, section=section, contact=contact, pickup_date=tomorrow,
                 pickup_time=PICKUP_SLOTS[len(slugs) + 1], **extra)
        _build_order(db, [cat[s] for s in slugs], f, status=status)
    db["messages"].append(dict(name="Pia Ramos", contact="pia@example.com", kind="Design request",
                               body="Can you add a tortoiseshell frame next batch?", created=now()))
    save(db)


# ---------------------------------------------------------------- helpers
def breakeven_units(price, unit_cost, amount):
    """Pairs that must be sold for profit (price - cost each) to cover `amount`."""
    margin = price - unit_cost
    if margin <= 0:
        return None
    return -(-int(amount) // margin)  # ceiling division


def screen_report(hours):
    """Eye-strain estimate for the home-page slider."""
    per_year = round(hours * 365)
    if hours < 3:
        level, tip = "Light", "You're in a good range. Glasses are optional, but the 20-20-20 rule still helps."
    elif hours < 5:
        level, tip = "Moderate", "Long study blocks add up. Blue light glasses can make evenings more comfortable."
    else:
        level, tip = "Heavy", "That's where most surveyed students are (63% spend 5+ hours). This is who Visora is for."
    return dict(level=level, per_year=per_year, share=round(hours / 16 * 100), tip=tip)

# Logic module verified and maintained by Christopher Boltron
