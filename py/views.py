"""views.py - turns data into HTML strings for every page.

Pure functions: they take data and return HTML, they never touch the DOM.
main.py puts the result on the page. All user-supplied text goes through e()
so nothing typed into a form can inject markup.
"""
from datetime import datetime, timedelta
from html import escape

import logic
from data import (PRICE, UNIT_COST, STARTUP, FIXED_MONTHLY, REFERRAL_DISCOUNT, STATUS_LABEL, STEP_TITLE,
                  STEP_HELP, STATUS_MSG, TABS, ADMIN_TABS, NEXT_STEP, PICKUPS, PAYMENTS, MESSAGE_KINDS, PICKUP_SLOTS, TEAM)


CHECK = "\u2713"


HERO_BG = """<div class="hero-bg" aria-hidden="true">
<span class="orb o1"></span><span class="orb o2"></span><span class="orb o3"></span>
<svg class="hero-glasses" viewBox="0 0 820 320" fill="none" stroke-linecap="round">
<defs><filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="lens" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9ecbff" stop-opacity=".22"/><stop offset="1" stop-color="#9ecbff" stop-opacity="0"/></linearGradient></defs>
<g class="frame" stroke="#9ecbff" stroke-opacity=".28" stroke-width="3">
<circle cx="220" cy="170" r="110" fill="url(#lens)"/><circle cx="600" cy="170" r="110" fill="url(#lens)"/>
<path d="M330 150 Q410 100 490 150"/><path d="M110 150 L12 118"/><path d="M710 150 L808 118"/></g>
<g filter="url(#glow)" stroke-width="5">
<circle class="roll r1" cx="220" cy="170" r="110" pathLength="100" stroke="#cfe6ff"/>
<circle class="roll r2" cx="220" cy="170" r="110" pathLength="100" stroke="#6fb1ff"/>
<circle class="roll r1 rev" cx="600" cy="170" r="110" pathLength="100" stroke="#cfe6ff"/>
<circle class="roll r2 rev" cx="600" cy="170" r="110" pathLength="100" stroke="#6fb1ff"/>
<path class="roll bridge" d="M330 150 Q410 100 490 150" pathLength="100" stroke="#ffffff"/></g>
</svg></div>"""


def e(x):
    return escape(str(x if x is not None else ""))


def peso(n):
    return f"₱{int(n):,}"


def stamp(s, n=16):
    return e(s[:n].replace("T", " "))


def pic(slug, name, cls=""):
    return f'<img src="static/img/{e(slug)}.jpg" alt="{e(name)}" loading="lazy" class="photo {cls}">'


def badge(status):
    return f'<span class="badge st-{status.split()[0]}">{e(STATUS_LABEL[status])}</span>'


def thumb(slug):
    return f'<img src="static/img/{e(slug)}.jpg" alt="">' if slug else '<div class="ph"></div>'


# ------------------------------------------------------------------ layouts
def store_layout(body, route, cart_count):
    def a(href, label, keys):
        return f'<a href="{href}" class="{"on" if route in keys else ""}">{label}</a>'
    return f"""
<header class="site"><div class="wrap">
<a class="brand" href="#/"><i></i>Visora</a>
<nav>{a('#/shop', 'Shop', ('shop',))}{a('#/about', 'Our Business', ('about',))}
{a('#/orders', 'My Orders', ('orders', 'order'))}{a('#/contact', 'Contact', ('contact',))}
<a class="cart" href="#/cart" id="cart-link">Cart (<span id="cart-count">{cart_count}</span>)</a></nav></div></header>
<main>{body}</main>
<footer><div class="wrap"><b style="color:#fff">Visora</b> — affordable blue light glasses for students, sold on campus at Cebu Eastern College.<br>
<a href="#/about">Our business</a> · <a href="#/contact">Contact us</a> · <a href="#/orders">My orders</a> ·
<a href="#/admin" style="opacity:.5">Staff</a></div></footer>"""


def admin_layout(body, page, new_count):
    def a(href, label, key, extra=""):
        return f'<a href="{href}" class="{"on" if page == key else ""}">{label}{extra}</a>'
    badge_n = f'<b class="dot-n">{new_count}</b>' if new_count else ""
    return f"""
<div class="adm-shell">
<aside class="adm-side">
  <div class="adm-brand"><i></i>Visora <span>Admin</span></div>
  <nav>{a('#/admin', 'Orders', 'orders', badge_n)}{a('#/admin/inventory', 'Inventory', 'inventory')}
  {a('#/admin/messages', 'Messages', 'messages')}{a('#/admin/sales', 'Sales', 'sales')}</nav>
  <div class="adm-foot"><a href="#/">← Back to store</a><a href="#/admin" data-action="admin-logout">Log out</a></div>
</aside>
<main class="adm-main">{body}</main></div>"""


def admin_login_page():
    return """<div class="adm-shell login"><main class="adm-main adm-login"><div class="adm-logincard">
<div class="adm-brand" style="justify-content:center"><i></i>Visora <span>Admin</span></div>
<p class="mute small" style="text-align:center">Authorized staff only.</p>
<form data-form="admin-login" class="stack"><label style="margin-top:0">Password</label>
<input type="password" name="password" autofocus required><p><button class="btn" style="width:100%">Log in</button></p></form>
<p class="mute small" style="text-align:center">Demo password: <code>visora2026</code></p>
<p style="text-align:center;margin:6px 0 0"><a href="#/" class="btn ghost sm" style="width:100%;text-align:center">← Back to store</a></p>
</div></main></div>"""


# ------------------------------------------------------------------ store pages
def home(db):
    glasses = [p for p in db["products"] if p["kind"] == "glasses" and p["active"]]
    cards = "".join(f"""<div class="card product"><div class="pic">{pic(p['slug'], p['name'])}</div>
<h3 style="margin-top:14px">{e(p['name'])}</h3><p class="mute small">{e(p['description'])}</p><div class="price">{peso(p['price'])}</div></div>""" for p in glasses)
    return f"""
<div class="hero">{HERO_BG}<div class="wrap grid"><div>
<span class="pill">Made for students · Sold on campus</span>
<h1>Screen all day? Your eyes deserve {peso(PRICE)}.</h1>
<p>Blue light glasses designed around what CEC students actually asked for: a low price, a comfortable fit, and real protection. Try them on, then pay on pickup.</p>
<p><a class="btn" href="#/shop">Shop glasses</a> &nbsp;<a class="btn ghost" style="border-color:#fff;color:#fff" href="#/about">How the business works</a></p>
</div><div class="art-ring"><div class="art">{pic('campus-square', 'Campus Square')}</div></div></div></div>

<section><div class="wrap"><h2>Built for long days on a screen</h2><p class="mute">Based on our survey of CEC students.</p>
<div class="grid3">
<div class="card"><div class="stat">63%<small>spend 5+ hours a day on laptops and phones</small></div></div>
<div class="card"><div class="stat">83%<small>get eye strain, headaches or tired eyes from screens</small></div></div>
<div class="card"><div class="stat">{peso(PRICE)}<small>a price students told us they're comfortable with</small></div></div>
</div></div></section>

<section class="alt"><div class="wrap split">
<div><h2>How heavy is your screen time?</h2><p class="mute">Drag the slider — the page updates as you move it.</p>
<label for="hours" style="font-weight:600">Hours on a screen per day: <b id="hours-val">6</b></label>
<input type="range" id="hours" min="0" max="16" step="1" value="6" data-input="screen-hours"></div>
<div class="card" id="screen-out"></div></div></section>

<section><div class="wrap"><h2>Our glasses</h2><div class="grid3">{cards}</div>
<p style="margin-top:22px"><a class="btn dark" href="#/shop">Reserve yours</a></p></div></section>

<section class="alt" id="how"><div class="wrap"><h2>How it works</h2><div class="steps">
<div><b>Pick &amp; reserve</b><br><span class="mute small">Choose your frame online and reserve it — no payment needed yet.</span></div>
<div><b>We confirm &amp; message you</b><br><span class="mute small">No courier — we confirm your pickup time and spot on campus. Follow every update in My Orders.</span></div>
<div><b>Pick up &amp; try on</b><br><span class="mute small">Check the fit. Pay in cash or GCash on pickup only if you like it.</span></div>
</div></div></section>

<section><div class="wrap"><h2>Why students pick Visora</h2><div class="grid3">
<div class="card"><h3>Right here on campus</h3><p class="mute small">No waiting 2–5 days for delivery. Pick up between classes.</p></div>
<div class="card"><h3>Try before you buy</h3><p class="mute small">Check the fit in person instead of guessing from a photo.</p></div>
<div class="card"><h3>No prescription needed</h3><p class="mute small">Simple screen protection — no appointment, no eye exam.</p></div>
</div></div></section>"""


def screen_result(hours):
    r = logic.screen_report(hours)
    return f"""<div class="stat">{r['per_year']:,}<small>hours a year on screens ({r['share']}% of your waking day)</small></div>
<p style="margin:14px 0 0"><span class="badge st-Confirmed">{e(r['level'])} use</span></p>
<p class="small mute" style="margin:8px 0 0">{e(r['tip'])}</p>"""


def _buy(p):
    low = "low" if p["stock"] <= 5 else ""
    tag = f'<span class="tag {low}">{p["stock"]} in stock</span>' if p["stock"] > 0 else '<span class="tag low">Sold out</span>'
    dis = "disabled" if p["stock"] <= 0 else ""
    return f'{tag}<p style="margin:12px 0 0"><button class="btn" data-action="add" data-pid="{p["id"]}" {dis}>Add to cart</button></p>'


def shop_cards(db, q="", sort="featured", kind="all"):
    prods = [p for p in db["products"] if p["active"]]
    q = (q or "").strip().lower()
    if q:
        prods = [p for p in prods if q in p["name"].lower() or q in p["description"].lower()]
    if kind in ("glasses", "addon"):
        prods = [p for p in prods if p["kind"] == kind]
    if sort == "price-asc":
        prods.sort(key=lambda p: p["price"])
    elif sort == "price-desc":
        prods.sort(key=lambda p: -p["price"])
    elif sort == "name":
        prods.sort(key=lambda p: p["name"])
    if not prods:
        return '<div class="empty card" style="grid-column:1/-1">No products match your search.</div>'
    return "".join(f"""<div class="card product"><div class="pic">{pic(p['slug'], p['name'], '' if p['kind'] == 'glasses' else 'wide')}</div>
<h3 style="margin-top:14px">{e(p['name'])}</h3><p class="mute small">{e(p['description'])}</p>
<div class="price">{peso(p['price'])}</div>{_buy(p)}</div>""" for p in prods)


def shop(db):
    return f"""<section><div class="wrap"><h2>Shop</h2>
<p class="mute">Reserve online, try on at CEC, pay on pickup. Limited stock per design.</p>
<div class="toolbar">
<input type="search" id="shop-q" placeholder="Search frames and add-ons…" data-input="shop-filter" aria-label="Search">
<select id="shop-kind" data-change="shop-filter" aria-label="Category"><option value="all">All products</option><option value="glasses">Glasses</option><option value="addon">Add-ons</option></select>
<select id="shop-sort" data-change="shop-filter" aria-label="Sort"><option value="featured">Featured</option><option value="price-asc">Price: low to high</option><option value="price-desc">Price: high to low</option><option value="name">Name A–Z</option></select>
</div>
<div class="grid3" id="shop-grid">{shop_cards(db)}</div></div></section>"""


def cart(db):
    items, subtotal = logic.get_cart(db)
    if not items:
        return '<section><div class="wrap"><h2>Your cart</h2><p>Your cart is empty. <a href="#/shop">Browse the shop</a>.</p></div></section>'
    rows = "".join(f"""<tr><td>{e(i['name'])}</td><td class="num">{peso(i['price'])}</td>
<td><div class="qty"><button class="btn sm dark" data-action="qty" data-pid="{i['id']}" data-delta="-1" aria-label="Decrease">−</button>
<input type="number" min="0" max="{i['stock']}" value="{i['qty']}" data-change="cart-qty" data-pid="{i['id']}" aria-label="Quantity">
<button class="btn sm dark" data-action="qty" data-pid="{i['id']}" data-delta="1" aria-label="Increase">+</button></div></td>
<td class="num">{peso(i['price'] * i['qty'])}</td></tr>""" for i in items)
    return f"""<section><div class="wrap"><h2>Your cart</h2>
<div class="notice"><b>\U0001F4CD Campus pickup — nothing is shipped.</b> After you reserve, we confirm a pickup time and spot at CEC and you collect your order in person. You pay only when you pick it up.</div>
<div class="tw"><table><tr><th>Item</th><th class="num">Price</th><th>Qty</th><th class="num">Total</th></tr>{rows}
<tr><td colspan="3" class="num"><b>Subtotal</b></td><td class="num"><b>{peso(subtotal)}</b></td></tr></table></div>
<p style="margin-top:20px"><a class="btn" href="#/checkout">Reserve for campus pickup</a> &nbsp;<a href="#/shop">Keep shopping</a></p></div></section>"""


def checkout_summary(items, subtotal, discount):
    lines = "".join(f'<div class="row"><span>{i["qty"]}× {e(i["name"])}</span><span>{peso(i["price"] * i["qty"])}</span></div>' for i in items)
    disc = f'<div class="row ok"><span>Referral discount</span><span>−{peso(discount)}</span></div>' if discount else ""
    return f"""<h3>Order summary</h3>{lines}<hr>
<div class="row"><span>Subtotal</span><span>{peso(subtotal)}</span></div>{disc}
<div class="row total"><b>Pay on pickup</b><b>{peso(max(subtotal - discount, 0))}</b></div>"""


def referral_note(code, discount):
    if not code.strip():
        return ""
    if discount:
        return f'<span class="ok-text">✓ Code accepted — {peso(discount)} off.</span>'
    return '<span class="bad-text">Code not found yet — no discount will be applied.</span>'


def checkout(db, form=None):
    items, subtotal = logic.get_cart(db)
    if not items:
        return '<section><div class="wrap"><h2>Reserve for pickup</h2><p>Your cart is empty. <a href="#/shop">Browse the shop</a>.</p></div></section>'
    form = form or {}
    v = lambda k: e(form.get(k, ""))
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    slot_opts = "".join(f'<option{" selected" if x == form.get("pickup_time") else ""}>{e(x)}</option>' for x in PICKUP_SLOTS)
    opts = lambda lst, cur: "".join(f'<option{" selected" if x == cur else ""}>{e(x)}</option>' for x in lst)
    return f"""<section><div class="wrap split"><div><h2>Reserve for pickup</h2>
<div class="notice"><b>\U0001F4CD Your order is picked up on campus — it is not shipped.</b> Choose where you'd like to collect it. We'll message you to confirm the time, and you can follow every update under <b>My Orders</b>. No payment now — pay when you pick it up.</div>
<form data-form="checkout" class="stack" novalidate>
<label>Full name</label><input name="name" required value="{v('name')}">
<div class="two"><div><label>Course &amp; section</label><input name="section" placeholder="e.g. BSIT – 9" required value="{v('section')}"></div>
<div><label>Mobile number / Messenger</label><input name="contact" required value="{v('contact')}"></div></div>
<div class="two"><div><label>Where do you want to pick it up?</label><select name="pickup">{opts(PICKUPS, form.get('pickup'))}</select></div>
<div><label>Payment on pickup</label><select name="payment">{opts(PAYMENTS, form.get('payment'))}</select></div></div>
<div class="two"><div><label>Preferred pickup date</label><input type="date" name="pickup_date" min="{today}" value="{e(form.get('pickup_date') or tomorrow)}" required></div>
<div><label>Preferred pickup time</label><select name="pickup_time" required><option value="">Choose a time\u2026</option>{slot_opts}</select></div></div>
<p class="mute small" style="margin:4px 0 0">We'll confirm the exact time by message \u2014 this just tells us when you're free.</p>
<label>Referral code <span class="mute small">(optional, {peso(REFERRAL_DISCOUNT)} off)</span></label>
<input name="referral" id="referral" value="{v('referral')}" placeholder="REFXXXXX" autocomplete="off" data-input="referral">
<div class="small" id="ref-msg" style="min-height:1.4em;margin-top:4px"></div>
<label>Notes <span class="mute small">(optional)</span></label><textarea name="notes" rows="2">{v('notes')}</textarea>
<div class="flash error" id="form-error" style="display:none"></div>
<p><button class="btn">Confirm reservation</button></p></form></div>
<div class="card" id="summary">{checkout_summary(items, subtotal, 0)}</div></div></section>"""


def contact():
    kinds = "".join(f"<option>{e(k)}</option>" for k in MESSAGE_KINDS)
    return f"""<section><div class="wrap" style="max-width:620px"><h2>Talk to us</h2>
<p class="mute">Questions, design requests, or want Visora in your org? Your feedback shapes our next batch.</p>
<form data-form="contact" class="stack" novalidate><label>Your name</label><input name="name" required>
<label>Contact (optional)</label><input name="contact"><label>Type</label><select name="kind">{kinds}</select>
<label>Message <span class="mute small" id="char-count">0 / 500</span></label>
<textarea name="body" rows="4" maxlength="500" required data-input="char-count"></textarea>
<div class="flash error" id="form-error" style="display:none"></div>
<p><button class="btn">Send</button></p></form></div></section>"""


def order_card(o, found=False):
    items = "".join(f"""<div class="oitem">{thumb(i['slug'])}<div><div class="nm">{e(i['name'])}</div>
<div class="mute small">{peso(i['price'])}</div></div><div class="q mute">x{i['qty']}</div></div>""" for i in o["items"])
    cancel = ""
    if not found and o["status"] in ("Reserved", "Confirmed"):
        cancel = f'<button class="btn sm ghost" data-action="cancel" data-code="{e(o["code"])}">Cancel</button> '
    return f"""<div class="ocard"><div class="oh"><span><b>{e(o['code'])}</b> <span class="mute small">· {stamp(o['created'], 10)}</span></span>{badge(o['status'])}</div>
{items}<div class="of"><span class="small mute">\U0001F4CD Pickup: {e(o['pickup'])}</span>
<span><span class="mute small">Total</span> <b>{peso(o['total'])}</b> &nbsp;{cancel}<a class="btn sm" href="#/order/{e(o['code'])}">View details</a></span></div></div>"""


def orders(db, tab="all", found=None):
    mine = logic.my_orders(db)
    counts = logic.tab_counts(mine, TABS)
    if found is not None:
        head = '<h3 style="margin-top:22px">Orders for that number</h3>'
        body = "".join(order_card(o, True) for o in found)
    else:
        head = '<div class="tabs">' + "".join(
            f'<a href="#/orders?tab={k}" class="{"on" if k == tab else ""}">{e(label)} <b>{counts[k] or ""}</b></a>'
            for k, label, _ in TABS) + "</div>"
        shown = logic.filter_by_tab(mine, TABS, tab)
        if shown:
            body = "".join(order_card(o) for o in shown)
        elif mine:
            body = '<div class="empty card">No orders in this tab.</div>'
        else:
            body = '<div class="empty card"><b style="color:var(--ink)">No orders to show yet.</b><br>Orders you place on this device appear here automatically.<br><a class="btn" style="margin-top:14px" href="#/shop">Start shopping</a></div>'
    return f"""<section><div class="wrap" style="max-width:820px"><h2>My Orders</h2>
<p class="mute" style="margin:0">Visora orders are picked up on campus — nothing is shipped. Open an order to see exactly where to collect it.</p>
{head}{body}
<div class="card" style="margin-top:26px"><h3>Ordered on another phone or computer?</h3>
<form data-form="find-order" class="stack" style="display:flex;gap:10px;flex-wrap:wrap;align-items:end" novalidate>
<div style="flex:1;min-width:220px"><label style="margin-top:0">Order code or mobile number</label><input name="q" placeholder="VIS-ABC123 or 09XX XXX XXXX" required></div>
<button class="btn">Find my orders</button></form>
<div class="flash error" id="form-error" style="display:none"></div></div></div></section>"""


def order(db, o, is_new=False):
    steps, cancelled, cancel_time = logic.timeline(o)
    msg = STATUS_MSG[o["status"]].format(contact=o["contact"], pickup=o["pickup"])
    new = (f'<div class="flash ok" style="margin-top:0"><b>Order placed!</b> Your order code is <b>{e(o["code"])}</b>. '
           "It's saved in My Orders on this device — screenshot it to be safe.</div>") if is_new else ""
    pickup = ""
    if not cancelled and o["status"] != "Completed":
        note = (f'<div class="note"><b>Message from Visora:</b> {e(o["pickup_note"])}</div>' if o.get("pickup_note")
                else f'<div class="note">We\'ll message you at <b>{e(o["contact"])}</b> with your exact pickup time.</div>')
        pickup = f"""<div class="pickup"><h3>\U0001F4CD Where your order goes</h3><p><b>Campus pickup: {e(o['pickup'])}</b></p>
<p>Your preferred time: <b>{e(logic.pickup_label(o) or 'not set')}</b></p>
<p>Your order is <b>not shipped</b>. Come to the pickup spot and show your order code <b>{e(o['code'])}</b> (and your student ID). You pay only when you pick it up: <b>{peso(o['total'])}</b> by {e(o['payment'])}.</p>{note}</div>"""
    if cancelled:
        when = f'<div class="d">{stamp(cancel_time)}</div>' if cancel_time else ""
        tl = f'<ul class="tl"><li class="done"><span class="dot">✕</span><div class="t">Order cancelled</div>{when}</li></ul>'
    else:
        li = ""
        for s in steps:
            mark = CHECK if s["state"] == "done" else ""
            when = '<div class="d">' + stamp(s["time"]) + "</div>" if s["time"] else ""
            li += (f'<li class="{s["state"]}"><span class="dot">{mark}</span><div class="t">{e(STEP_TITLE[s["key"]])}</div>'
                   f'{when}<div class="d">{e(s["note"] or STEP_HELP[s["key"]])}</div></li>')
        tl = f'<ul class="tl">{li}</ul>'
    lines = "".join(f"""<div class="oitem">{thumb(i['slug'])}<div><div class="nm">{e(i['name'])}</div>
<div class="mute small">{peso(i['price'])} × {i['qty']}</div></div><div class="q"><b>{peso(i['price'] * i['qty'])}</b></div></div>""" for i in o["items"])
    disc = f" · Referral {e(o['referral_used'])} −{peso(o['discount'])}" if o["discount"] else ""
    can_cancel = logic.owns(o["code"]) and o["status"] in ("Reserved", "Confirmed")
    cancel = (f'<p style="margin-top:14px"><button class="btn ghost sm" data-action="cancel" data-code="{e(o["code"])}">Cancel order</button></p>'
              if can_cancel else "")
    return f"""<section><div class="wrap" style="max-width:760px">
<p class="small" style="margin:0 0 10px"><a href="#/orders">← My Orders</a></p>{new}
<div class="banner {'x' if cancelled else ''}"><b style="font-size:1.15rem">{e(STATUS_LABEL[o['status']])}</b><br>{e(msg)}</div>{pickup}
<div class="timeline"><h3 style="margin-bottom:18px">Order status</h3>{tl}</div>
<div class="ocard"><div class="oh"><b>Order {e(o['code'])}</b><span class="mute small">Placed {stamp(o['created'])}</span></div>{lines}
<div class="of"><span class="small mute">Subtotal {peso(o['subtotal'])}{disc}</span><span>To pay on pickup: <b style="font-size:1.2rem">{peso(o['total'])}</b></span></div></div>{cancel}
<div class="card" style="margin-top:18px;background:var(--amber-soft)"><h3>Share &amp; save</h3>
<p class="small" style="margin:0">Give friends your code <b style="font-size:1.1rem">{e(o['my_referral'])}</b> — they get {peso(REFERRAL_DISCOUNT)} off their first order.</p></div>
</div></section>"""


def not_found():
    return '<section><div class="wrap"><h2>Page not found</h2><p><a href="#/">Back home</a></p></div></section>'


# ------------------------------------------------------------------ About / business page
def about():
    team = ""
    if TEAM:
        cards = "".join(f'<div class="card"><h3>{e(m["name"])}</h3><p class="mute small" style="margin:0"><b>{e(m.get("role", ""))}</b><br>{e(m.get("part", ""))}</p></div>' for m in TEAM)
        team = f'<section class="alt"><div class="wrap"><h2>The team</h2><div class="grid3">{cards}</div></div></section>'
    margin = PRICE - UNIT_COST
    return f"""
<section><div class="wrap"><span class="pill">Business concept</span>
<h2>Visora — affordable blue light glasses for students</h2>
<p class="mute" style="max-width:720px">Students at Cebu Eastern College spend long hours on laptops and phones, and many get tired eyes and headaches. Visora sells simple, comfortable blue light glasses at {peso(PRICE)}, with campus pickup and no prescription needed.</p>
<div class="grid3">
<div class="card"><h3>The problem</h3><p class="small mute">63% of surveyed students use screens 5+ hours a day and 83% report eye strain, headaches or tired eyes. Existing options are pricey or take days to ship.</p></div>
<div class="card"><h3>Our solution</h3><p class="small mute">Three frame styles plus cheap add-ons, reserved online and collected on campus. Students try the fit first and pay only on pickup.</p></div>
<div class="card"><h3>Our customers</h3><p class="small mute">CEC students who study on screens, price-sensitive, and who want to see and try the product in person.</p></div>
</div></div></section>

<section class="alt"><div class="wrap"><h2>How the business operates</h2>
<p class="mute">The website supports every step of this process.</p>
<div class="steps">
<div><b>Student reserves</b><br><span class="mute small">Browses the shop, fills the cart and submits the reservation form (name, section, contact, pickup spot). Stock drops automatically.</span></div>
<div><b>Staff confirms</b><br><span class="mute small">In the staff area the order appears under "New". Staff confirms it and sends a message with the pickup time.</span></div>
<div><b>Staff prepares</b><br><span class="mute small">Order moves to "Ready for pickup". The buyer sees the update live on their order page.</span></div>
<div><b>Student picks up &amp; pays</b><br><span class="mute small">Student shows the order code, tries the glasses, pays cash or GCash. Staff marks it "Picked up &amp; paid".</span></div>
<div><b>Referral growth</b><br><span class="mute small">Every order gets a referral code. Friends who use it get {peso(REFERRAL_DISCOUNT)} off, which brings in new buyers.</span></div>
</div></div></section>

<section><div class="wrap"><h2>Pricing &amp; economics</h2>
<div class="grid3">
<div class="card"><div class="stat">{peso(PRICE)}<small>selling price per pair</small></div></div>
</div></div></section>

{team}"""


# ------------------------------------------------------------------ admin pages
def admin_order_list(db, tab="new", q=""):
    allo = list(reversed(db["orders"]))
    q = (q or "").strip()
    if q:  # searching looks through ALL orders, whatever tab is open
        shown = logic.search_orders(allo, q)
        head = f'<p class="small mute" style="margin:0 0 12px">{len(shown)} order{"s" if len(shown) != 1 else ""} matching \u201c{e(q)}\u201d (all statuses)</p>'
    else:
        shown, head = logic.filter_by_tab(allo, ADMIN_TABS, tab), ""
    cards = []
    for o in shown:
        items = "".join(f"""<div class="oitem">{thumb(i['slug'])}<div><div class="nm">{e(i['name'])}</div><div class="mute small">{peso(i['price'])}</div></div><div class="q">\u00d7 {i['qty']}</div></div>""" for i in o["items"])
        extra = (f"<br><b>Referral used:</b> {e(o['referral_used'])}" if o["referral_used"] else "") + \
                (f"<br><b>Buyer note:</b> \u201c{e(o['notes'])}\u201d" if o["notes"] else "")
        note = (f'<input id="note-{e(o["code"])}" value="{e(o["pickup_note"])}" placeholder="Message to buyer, e.g. Tomorrow 12:30 PM at the canteen">'
                if o["status"] != "Completed" else "")
        btns = ""
        if o["status"] in NEXT_STEP:
            st, label = NEXT_STEP[o["status"]]
            btns += f'<button class="btn sm" data-action="admin-status" data-code="{e(o["code"])}" data-status="{st}">{e(label)}</button>'
        if o["status"] in ("Reserved", "Confirmed", "Ready for pickup"):
            btns += f' <button class="btn sm ghost" data-action="admin-status" data-code="{e(o["code"])}" data-status="Cancelled" data-confirm="Cancel order {e(o["code"])}? Stock will be returned.">Cancel order</button>'
        if o["status"] == "Cancelled":
            btns += f'<button class="btn sm ghost" data-action="admin-status" data-code="{e(o["code"])}" data-status="Reserved">Reopen</button>'
        cards.append(f"""<div class="ocard"><div class="oh"><span><b>{e(o['code'])}</b> <span class="mute small">\u00b7 {stamp(o['created'])}</span></span>{badge(o['status'])}</div>
<div class="adm-info small"><div><b>Buyer:</b> {e(o['name'])}<br><b>Course/section:</b> {e(o['section'])}<br><b>Contact:</b> {e(o['contact'])}</div>
<div><b>Pickup spot:</b> {e(o['pickup'])}<br><b>Preferred time:</b> {e(logic.pickup_label(o) or '\u2014')}<br><b>Payment:</b> {e(o['payment'])} on pickup{extra}</div></div>{items}
<div class="of"><div class="adm-act">{note}{btns}</div><span style="white-space:nowrap">Total <b>{peso(o['total'])}</b></span></div></div>""")
    return head + ("".join(cards) or '<div class="empty card">No orders here.</div>')


def admin_orders(db, tab="new", q=""):
    allo = list(reversed(db["orders"]))
    counts = logic.tab_counts(allo, ADMIN_TABS)
    notice = ""
    if counts["new"] and tab != "new":
        s = "s" if counts["new"] != 1 else ""
        notice = f'<div class="notice"><b>{counts["new"]} new order{s} waiting for confirmation.</b> <a href="#/admin?tab=new">Review now \u2192</a></div>'
    tabs = '<div class="tabs">' + "".join(
        f'<a href="#/admin?tab={k}" class="{"on" if k == tab else ""}">{e(label)} <b>{counts[k] or ""}</b></a>' for k, label, _ in ADMIN_TABS) + "</div>"
    search = f"""<div class="searchbar"><input type="search" id="admin-q" value="{e(q)}" data-input="admin-search" autocomplete="off"
placeholder="\U0001F50D Track an order \u2014 type the order code (VIS-\u2026), buyer name, section or mobile number"></div>"""
    return f'<h1 class="adm-h">Orders</h1>{notice}{search}{tabs}<div id="admin-list">{admin_order_list(db, tab, q)}</div>'


def admin_inventory(db):
    rows = "".join(f"""<tr><td>{e(p['name'])}{' <span class="tag low">Low stock</span>' if p['stock'] <= 5 else ''}</td>
<td><input type="number" id="stock-{p['id']}" value="{p['stock']}" min="0" style="width:100px"></td>
<td><input type="number" id="price-{p['id']}" value="{p['price']}" min="0" style="width:100px"></td>
<td><button class="btn sm dark" data-action="save-product" data-pid="{p['id']}">Save</button></td></tr>""" for p in db["products"])
    return f'<h1 class="adm-h">Inventory &amp; pricing</h1><div class="tw"><table><tr><th>Product</th><th>Stock</th><th>Price (\u20b1)</th><th></th></tr>{rows}</table></div>'


def admin_messages(db):
    rows = "".join(f"""<tr><td>{e(m['name'])}<br><span class="mute small">{e(m['contact'])}</span></td><td>{e(m['kind'])}</td><td>{e(m['body'])}</td><td class="small mute">{stamp(m['created'])}</td></tr>"""
                   for m in reversed(db["messages"][-100:])) or '<tr><td colspan="4" class="mute">No messages yet.</td></tr>'
    return f'<h1 class="adm-h">Customer messages</h1><div class="tw"><table><tr><th>From</th><th>Type</th><th>Message</th><th>Received</th></tr>{rows}</table></div>'


def admin_sales(db):
    s = logic.sales_stats(db)
    cov = min(round(s["pairs"] / s["breakeven"] * 100), 100)
    return f"""<h1 class="adm-h">Sales summary</h1>
<div class="grid3" style="grid-template-columns:repeat(auto-fit,minmax(190px,1fr))">
<div class="card"><div class="stat">{s['n']}<small>active orders</small></div></div>
<div class="card"><div class="stat">{s['pairs']}<small>pairs reserved / sold</small></div></div>
<div class="card"><div class="stat">{peso(s['rev'])}<small>order value</small></div></div>
<div class="card"><div class="stat">{peso(s['done_rev'])}<small>collected (picked up)</small></div></div></div>
<div class="card" style="margin-top:16px"><b>Break-even progress</b> <span class="mute small">— {s['pairs']} of {s['breakeven']} pairs to recover {peso(s['startup'])} startup capital (estimated gross profit so far {peso(s['gross'])})</span>
<div style="background:#2a3340;border-radius:99px;height:12px;margin-top:8px;overflow:hidden"><div style="width:{cov}%;background:linear-gradient(90deg,#3b82f6,#7dd3fc);height:100%"></div></div></div>
<div class="card" style="margin-top:16px"><b>Demo tools</b>
<p class="small mute" style="margin:4px 0 12px">This site runs entirely in your browser, so orders live in this browser only. Use these to prepare a demo.</p>
<button class="btn sm dark" data-action="load-demo">Load sample orders</button> &nbsp;
<button class="btn sm ghost" data-action="reset-data" data-confirm="Delete ALL orders, messages and reset stock?">Reset all data</button></div>"""



# Customer views and shop UI maintained by Myco Dumas-og 
