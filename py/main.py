"""main.py - Visora's event-driven controller (PyScript entry point).

How it works
------------
Nothing here runs in a loop. The page waits, and Python functions run only when the
user does something (an *event*):

    click      -> buttons with data-action="..."        (add to cart, cancel, confirm order...)
    submit     -> forms with data-form="..."            (checkout, contact, find order, admin login)
    input      -> fields with data-input="..."          (live search, referral check, sliders, counters)
    change     -> fields with data-change="..."         (sort/filter dropdowns, cart quantity)
    hashchange -> the URL #/route changed               (navigation without reloading the page)

Each event is caught once on #root (event delegation) and sent to a handler in the
ACTIONS / FORMS / INPUTS / CHANGES tables below. Handlers update the data (logic.py),
then redraw the page (views.py) or just the part that changed.
"""
from urllib.parse import unquote

from pyscript import document, window, when
from pyodide.ffi import create_proxy

import logic
import storage
import views
from data import ADMIN_PASSWORD

db = logic.load()
root = document.querySelector("#root")
state = {"path": None, "order_new": None, "found": None, "admin_q": ""}


# ============================================================ small helpers
def el(selector):
    return document.querySelector(selector)


def toast(message, kind="ok"):
    box = el("#toasts")
    t = document.createElement("div")
    t.className = f"toast {kind}"
    t.textContent = message
    box.appendChild(t)

    def remove(*_):
        t.remove()
    window.setTimeout(create_proxy(remove), 3500)


def form_values(form):
    out = {}
    for i in range(form.elements.length):
        f = form.elements.item(i)
        if f.name:
            out[f.name] = f.value
    return out


def inline_error(message):
    box = el("#form-error")
    if box:
        box.textContent = message
        box.style.display = "block" if message else "none"


def go(path):
    """Navigate to a route (fires 'hashchange', which redraws the page)."""
    if window.location.hash == "#" + path:
        render()
    else:
        window.location.hash = path


def is_admin():
    return bool(storage.get("visora_admin", False, session=True))


def parse_hash():
    raw = window.location.hash or "#/"
    path, _, query = raw[1:].partition("?")
    params = {}
    for pair in query.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            params[k] = unquote(v)
    return (path or "/").rstrip("/") or "/", params


# ============================================================ rendering / routing
def render():
    """Pick the right view for the current #/route and draw it."""
    path, params = parse_hash()
    parts = path.strip("/").split("/")
    page = parts[0] if parts[0] else "home"
    title = "Visora — Blue Light Glasses for Students"
    after = None

    if page == "admin":
        sub = parts[1] if len(parts) > 1 else "orders"
        if not is_admin():
            html = views.admin_login_page()
            title = "Admin login — Visora"
        else:
            body = {
                "orders": lambda: views.admin_orders(db, params.get("tab", "new"), state["admin_q"]),
                "inventory": lambda: views.admin_inventory(db),
                "messages": lambda: views.admin_messages(db),
                "sales": lambda: views.admin_sales(db),
            }.get(sub)
            if body is None:
                html, page = views.store_layout(views.not_found(), "404", logic.cart_count(db)), "404"
            else:
                new_count = sum(1 for o in db["orders"] if o["status"] == "Reserved")
                html = views.admin_layout(body(), sub, new_count)
                title = f"{sub.title()} — Visora Admin"
    else:
        route = page
        if page == "home":
            body, after = views.home(db), update_screen
        elif page == "shop":
            body, title = views.shop(db), "Shop — Visora"
        elif page == "about":
            body, title = views.about(), "Our Business — Visora"
        elif page == "cart":
            body, title = views.cart(db), "Cart — Visora"
        elif page == "checkout":
            body, after, title = views.checkout(db), update_referral, "Reserve — Visora"
        elif page == "contact":
            body, title = views.contact(), "Contact — Visora"
        elif page in ("orders", "track"):
            route = "orders"
            body, title = views.orders(db, params.get("tab", "all"), state["found"]), "My Orders — Visora"
            state["found"] = None
        elif page == "order" and len(parts) > 1 and logic.order_by_code(db, parts[1]):
            o = logic.order_by_code(db, parts[1])
            body = views.order(db, o, is_new=state["order_new"] == o["code"])
            state["order_new"] = None
            title = f"Order {o['code']} — Visora"
        else:
            body, route = views.not_found(), "404"
        html = views.store_layout(body, route, logic.cart_count(db))

    root.innerHTML = html
    document.title = title
    if path != state["path"]:
        window.scrollTo(0, 0)
    state["path"] = path
    if after:
        after()


def refresh_cart_badge():
    badge = el("#cart-count")
    if badge:
        badge.textContent = str(logic.cart_count(db))


# ============================================================ CLICK events
def a_add(target):
    ok, msg = logic.cart_add(db, target.getAttribute("data-pid"))
    toast(msg, "ok" if ok else "error")
    refresh_cart_badge()


def a_qty(target):
    pid = int(target.getAttribute("data-pid"))
    qty = next((i["qty"] for i in logic.get_cart(db)[0] if i["id"] == pid), 0)
    logic.cart_set(db, pid, qty + int(target.getAttribute("data-delta")))
    render()


def a_cancel(target):
    if window.confirm("Cancel this order?"):
        if logic.cancel_order(db, target.getAttribute("data-code")):
            toast("Your order was cancelled.")
        render()


def a_admin_status(target):
    ask = target.getAttribute("data-confirm")
    if ask and not window.confirm(ask):
        return
    code = target.getAttribute("data-code")
    note_box = el(f"#note-{code}")
    msg = logic.admin_set_status(db, code, target.getAttribute("data-status"), note_box.value if note_box else "")
    if msg:
        toast(msg)
    render()


def a_save_product(target):
    pid = target.getAttribute("data-pid")
    if logic.update_product(db, pid, el(f"#stock-{pid}").value, el(f"#price-{pid}").value):
        toast("Product updated.")
    else:
        toast("Stock and price must be whole numbers.", "error")
    render()


def a_logout(target):
    storage.remove("visora_admin", session=True)
    render()  # shows the login page (the link itself also goes to #/admin)


def a_load_demo(target):
    logic.load_demo(db)
    toast("Sample orders loaded.")
    render()


def a_reset(target):
    if window.confirm(target.getAttribute("data-confirm")):
        db.clear()
        db.update(logic.fresh_db())
        logic.save(db)
        logic.cart_clear()
        storage.put(logic.MINE_KEY, [])
        toast("All data reset.")
        render()


ACTIONS = {"add": a_add, "qty": a_qty, "cancel": a_cancel, "admin-status": a_admin_status,
           "save-product": a_save_product, "admin-logout": a_logout, "load-demo": a_load_demo,
           "reset-data": a_reset}


@when("click", "#root")
def on_click(event):
    target = event.target.closest("[data-action]")
    if target and target.getAttribute("data-action") in ACTIONS:
        ACTIONS[target.getAttribute("data-action")](target)


# ============================================================ SUBMIT events
def f_checkout(form):
    vals = form_values(form)
    order, err = logic.place_order(db, vals)
    if err:
        inline_error(err)
        return
    state["order_new"] = order["code"]
    go(f"/order/{order['code']}")


def f_contact(form):
    v = form_values(form)
    if logic.add_message(db, v.get("name"), v.get("contact"), v.get("kind"), v.get("body")):
        toast("Thanks! We read every message — we'll get back to you on campus or by your contact.")
        form.reset()
        update_char_count()
        inline_error("")
    else:
        inline_error("Please fill in your name and message.")


def f_find(form):
    kind, found = logic.find_orders(db, form_values(form).get("q"))
    if kind == "code":
        logic.remember(found[0]["code"])
        go(f"/order/{found[0]['code']}")
    elif kind == "phone":
        state["found"] = found  # show these results on the My Orders page
        go("/orders")
    else:
        inline_error("We couldn't find an order with that code or number. Your order code starts with VIS- and is shown after you reserve.")


def f_admin_login(form):
    if form_values(form).get("password") == ADMIN_PASSWORD:
        storage.put("visora_admin", True, session=True)
        go("/admin")
    else:
        toast("Wrong password.", "error")


FORMS = {"checkout": f_checkout, "contact": f_contact, "find-order": f_find, "admin-login": f_admin_login}


@when("submit", "#root")
def on_submit(event):
    form = event.target
    name = form.getAttribute("data-form")
    if name in FORMS:
        event.preventDefault()
        FORMS[name](form)


# ============================================================ INPUT events (fire on every keystroke / slider move)
def update_screen(*_):
    slider = el("#hours")
    if slider:
        el("#hours-val").textContent = slider.value
        el("#screen-out").innerHTML = views.screen_result(int(slider.value))


def update_shop(*_):
    el("#shop-grid").innerHTML = views.shop_cards(db, el("#shop-q").value, el("#shop-sort").value, el("#shop-kind").value)


def update_referral(*_):
    box = el("#referral")
    if not box:
        return
    items, subtotal = logic.get_cart(db)
    discount = logic.referral_discount(db, box.value)
    el("#ref-msg").innerHTML = views.referral_note(box.value, discount)
    el("#summary").innerHTML = views.checkout_summary(items, subtotal, discount)


def update_admin_search(*_):
    """Staff order tracker: filters the list on every keystroke."""
    box = el("#admin-q")
    if box:
        state["admin_q"] = box.value
        tab = parse_hash()[1].get("tab", "new")
        el("#admin-list").innerHTML = views.admin_order_list(db, tab, box.value)


def update_char_count(*_):
    box = el("textarea[name=body]")
    if box:
        el("#char-count").textContent = f"{len(box.value)} / 500"


INPUTS = {"screen-hours": update_screen, "shop-filter": update_shop,
          "referral": update_referral, "char-count": update_char_count, "admin-search": update_admin_search}


@when("input", "#root")
def on_input(event):
    name = event.target.getAttribute("data-input")
    if name in INPUTS:
        INPUTS[name]()


# ============================================================ CHANGE events (dropdowns, number boxes)
def c_cart_qty(target):
    logic.cart_set(db, int(target.getAttribute("data-pid")), target.value)
    render()


CHANGES = {"shop-filter": update_shop, "cart-qty": c_cart_qty}


@when("change", "#root")
def on_change(event):
    name = event.target.getAttribute("data-change")
    if name in CHANGES:
        CHANGES[name](event.target)


# ============================================================ navigation event
window.addEventListener("hashchange", create_proxy(lambda e: render()))

render()
