"""data.py - constants, seed products and label tables for Visora.

Figures come from the Visora feasibility study (Sept 26, 2026).
"""

# ---- Business figures ----
PRICE = 249            # selling price of one pair (pesos)
UNIT_COST = 55         # cost of one pair
STARTUP = 4350         # startup capital
FIXED_MONTHLY = 500    # marketing 300 + misc/delivery 200
REFERRAL_DISCOUNT = 20 # pesos off with a valid referral code

# Client-side demo password for the staff area (there is no server in a PyScript site).
ADMIN_PASSWORD = "visora2026"

# ---- Team (shown on the About page when filled in) ----
TEAM = [
    {"name": "Dave Formentera", "role": "Event handling & routing", "part": "py/main.py, project setup and GitHub Pages deployment"},
    {"name": "Christopher Boltron", "role": "Business logic", "part": "py/logic.py: cart, checkout, referral codes, order workflow"},
    {"name": "Myco Dumas-og", "role": "Customer pages", "part": "py/views.py: shop, cart, checkout (preferred pickup time), My Orders"},
    {"name": "Ken Luis Jagmoc", "role": "Staff area & design", "part": "Admin pages, order tracker search, static/style.css, hero animation"},
    {"name": "Kurt Rolly Pe\u00f1afiel", "role": "Business content & documentation", "part": "Our Business page, data.py, storage.py, README and docs"},
]

SEED_PRODUCTS = [
    dict(id=1, slug="classic-round", name="Classic Round", description="Lightweight round frame with blue light–blocking lenses. Easy fit for most faces.", price=249, stock=18, kind="glasses", active=True),
    dict(id=2, slug="campus-square", name="Campus Square", description="Everyday square frame built for long study sessions. Comfortable on the nose bridge.", price=249, stock=18, kind="glasses", active=True),
    dict(id=3, slug="clear-crystal", name="Clear Crystal", description="Transparent frame with a clean look. Light enough to forget you're wearing it.", price=249, stock=14, kind="glasses", active=True),
    dict(id=4, slug="cleaning-cloth", name="Microfiber Cleaning Cloth", description="Keeps lenses and laptop screens smudge-free.", price=29, stock=40, kind="addon", active=True),
    dict(id=5, slug="hard-case", name="Protective Hard Case", description="Slim case that fits in any bag.", price=59, stock=25, kind="addon", active=True),
]

# ---- Order workflow ----
STATUS_FLOW = ["Reserved", "Confirmed", "Ready for pickup", "Completed"]
STATUS_LABEL = {"Reserved": "To Confirm", "Confirmed": "Preparing", "Ready for pickup": "Ready for Pickup",
                "Completed": "Picked Up", "Cancelled": "Cancelled"}
STEP_TITLE = {"Reserved": "Order placed", "Confirmed": "Order confirmed", "Ready for pickup": "Ready for pickup",
              "Completed": "Picked up", "Cancelled": "Order cancelled"}
STEP_HELP = {"Reserved": "We received your order.",
             "Confirmed": "We confirmed your pickup and are preparing your glasses.",
             "Ready for pickup": "Your order is waiting for you at the pickup spot.",
             "Completed": "You collected your order."}
STATUS_MSG = {
    "Reserved": "We got your order! We'll confirm your pickup time and spot and message you at {contact}.",
    "Confirmed": "Your order is confirmed. We'll message you as soon as it's ready for pickup.",
    "Ready for pickup": "Your order is ready! Pick it up at: {pickup}. Bring your order code.",
    "Completed": "You picked up your order. Thank you for choosing Visora!",
    "Cancelled": "This order was cancelled.",
}

# (key, label, statuses or None for "all")
TABS = [("all", "All", None), ("confirm", "To Confirm", ("Reserved",)),
        ("pickup", "To Pick Up", ("Confirmed", "Ready for pickup")),
        ("done", "Picked Up", ("Completed",)), ("cancelled", "Cancelled", ("Cancelled",))]
ADMIN_TABS = [("new", "New — to confirm", ("Reserved",)), ("confirmed", "Confirmed", ("Confirmed",)),
              ("ready", "Ready for pickup", ("Ready for pickup",)), ("done", "Picked up", ("Completed",)),
              ("cancelled", "Cancelled", ("Cancelled",)), ("all", "All", None)]
NEXT_STEP = {"Reserved": ("Confirmed", "Confirm order"),
             "Confirmed": ("Ready for pickup", "Mark ready for pickup"),
             "Ready for pickup": ("Completed", "Mark picked up & paid")}

PICKUPS = ["CEC campus — main entrance", "CEC campus — IT building", "CEC campus — canteen"]
PAYMENTS = ["Cash", "GCash"]
MESSAGE_KINDS = ["Question", "Design request", "Feedback", "Student org partnership"]

# Preferred pickup time slots shown at checkout (class breaks are the busiest, so offer clear windows)
PICKUP_SLOTS = ["8:00 \u2013 9:00 AM", "9:00 \u2013 10:00 AM", "10:00 \u2013 11:00 AM", "11:00 AM \u2013 12:00 NN",
                "12:00 \u2013 1:00 PM (lunch break)", "1:00 \u2013 2:00 PM", "2:00 \u2013 3:00 PM",
                "3:00 \u2013 4:00 PM", "4:00 \u2013 5:00 PM"]
Python
# Product data structures maintained by Kurt Rolly Peñafiel

