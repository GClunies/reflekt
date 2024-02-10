# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

"""Generate example events (with session_id) for www.thejaffleshop.com"""

from __future__ import annotations

import random
import uuid
from pathlib import Path

# from urllib.parse import urlparse
import faker
import pandas as pd
from loguru import logger

# from segment import analytics as segment_analytics

N_USERS = 100
N_SESSIONS = 1000
SESSION_MAX_TIMESTEP = 60 * 5  # 5 minutes between actions
USERS_PATH = Path.cwd() / "data" / "users.csv"
PRODUCTS_PATH = Path.cwd() / "data" / "products.csv"
PRODUCT_NAMES = [
    "Bacon, Egg, and Cheese",
    "Ham and Cheese",
    "Peanut Butter and Jelly",
    "Peanut Butter and Banana",
    "Nutella and Banana",
    "Nutella and Marshmallow",
    "Pizza",
    "Mac and Cheese",
    "Cheese",
    "Tuna Melt",
]
PRODUCT_PRICES = [5.99, 4.99, 3.99, 3.99, 4.99, 4.99, 5.99, 4.99, 3.99, 5.99]
PRODUCT_CATEGORIES = ["jaffles"] * 10
ACTIONS = [
    "Home Page",
    "Menu Page",
    "Contact Page",
    "Product Page",
    "Cart Page",
    "Checkout Page - Shipping",
    "Checkout Page - Payment",
    "Checkout Page - Confirmation",
    "Product Clicked",
    "Product Added",
    "Product Removed",
    "Cart Viewed",
    "Checkout Started",
    "Checkout Step Viewed",
    "Checkout Step Viewed - Shipping",
    "Checkout Step Viewed - Payment",
    "Checkout Step Viewed - Confirmation",
    "Checkout Step Completed - Shipping",
    "Checkout Step Completed - Payment",
    "Checkout Step Completed - Confirmation",
    "Order Completed",
    "Drop",
]


fake = faker.Faker(locale="en_US")
logger = logger.opt(colors=True)


def generate_users(n_users=10000):
    """Generate a dataframe of users.

    NOTE:
    We assume all users have an account and are *always* signed in. This is a
    simplification, but makes generating events *much* easier.
    """
    users = [
        {
            "user_id": str(uuid.uuid4()),
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        }
        for _ in range(n_users)
    ]

    return users


def generate_products(names, prices, categories):
    products = []

    for name, price, category in zip(names, prices, categories):
        product = {
            "id": str(uuid.uuid4()),
            "sku": fake.ean(length=13),
            "category": category,
            "name": name,
            "price": price,
        }
        products.append(product)

    return products


def get_product(product_id, products):
    for product in products:
        if product["id"] == product_id:
            return product


# Generate users and products
users = generate_users(n_users=10000)
products = generate_products(
    names=PRODUCT_NAMES, prices=PRODUCT_PRICES, categories=PRODUCT_CATEGORIES
)


def get_last_event(events):
    """Get the last event in a list of events, NOT including Identify events."""
    if len(events) == 0:
        last_event = None
    else:
        last_event = events[-1] if events[-1]["event"] != "Identify" else events[-2]

    return last_event


def home_page(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Home",
                    "path": "/",
                    "referrer": last_event["page"]["url"]
                    if last_event is not None
                    else None,
                    "search": None,
                    "title": "Jaffle Shop - Home",
                    "url": "https://www.thejaffleshop.com/",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Home",
                    "path": "/",
                    "referrer": last_event["page"]["url"]
                    if last_event is not None
                    else None,
                    "search": None,
                    "title": "Jaffle Shop - Home",
                    "url": "https://www.thejaffleshop.com/",
                },
                "cart": {},
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Home",
                    "path": "/",
                    "referrer": last_event["page"]["url"]
                    if last_event is not None
                    else None,
                    "search": None,
                    "title": "Jaffle Shop - Home",
                    "url": "https://www.thejaffleshop.com/",
                },
                "properties": {},
                "cart": {},
            },
        ],
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Home"
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Identitfy"
    )

    return events


def menu_page(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Menu",
                    "path": "/menu",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://www.thejaffleshop.com/menu",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Menu",
                    "path": "/menu",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://www.thejaffleshop.com/menu",
                },
                "cart": {},
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Menu",
                    "path": "/menu",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://www.thejaffleshop.com/menu",
                },
                "properties": {},
                "cart": {},
            },
        ],
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Menu"
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Identitfy"
    )

    return events


def contact_page(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Contact Us",
                    "path": "/contact-us",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Contact Us",
                    "url": "https://www.thejaffleshop.com/contact-us",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Contact Us",
                    "path": "/contact-us",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Contact Us",
                    "url": "https://www.thejaffleshop.com/contact-us",
                },
                "cart": {},
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Contact Us",
                    "path": "/contact-us",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Contact Us",
                    "url": "https://www.thejaffleshop.com/contact-us",
                },
                "properties": {},
                "cart": {},
            },
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Contact Us"
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Identitfy"
    )

    return events


def product_clicked(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    product = random.choice(products)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Product Clicked",
                "timestamp": tstamp,
                "page": {  # Products are only clicked on the menu page
                    "name": "Menu",
                    "path": "/menu",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://www.thejaffleshop.com/menu",
                },
                "properties": {
                    "session_id": session_id,
                    "product_id": product["id"],
                    "sku": product["sku"],
                    "category": product["category"],
                    "name": product["name"],
                    "price": product["price"],
                },
                "cart": {},
            },
        ]
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Product Clicked, Product: {product['name']}"
    )

    return events


def product_page(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    product_id = last_event["properties"]["product_id"]
    product = get_product(product_id, products)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Product",
                    "path": f"/products/{product['id']}",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://www.thejaffleshop.com/products/{product['id']}",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Product",
                    "path": f"/products/{product['id']}",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://www.thejaffleshop.com/products/{product['id']}",
                    "product_id": product["id"],
                },
                "cart": {},
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Product",
                    "path": f"/products/{product['id']}",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://www.thejaffleshop.com/products/{product['id']}",
                },
                "properties": {},
                "cart": {},
            },
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Product"
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Identitfy"
    )

    return events


def product_added(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    product_id = last_event["properties"]["product_id"]
    product = get_product(product_id, products)
    quantity = random.randint(1, 3)

    # Get product IDs in cart
    cart_product_ids = [p["product_id"] for p in cart["products"]]

    if product_id not in cart_product_ids:
        cart["products"].append(
            {
                "product_id": product_id,
                "sku": product["sku"],
                "category": product["category"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
            }
        )
    else:
        cart["products"][cart_product_ids.index(product_id)]["quantity"] += quantity

    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Product Added",
                "timestamp": tstamp,
                "page": {
                    "name": "Product",
                    "path": f"/products/{product['id']}",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://www.thejaffleshop.com/products/{product['id']}",
                },
                "properties": {
                    "session_id": session_id,
                    "cart_id": cart["cart_id"],
                    "product_id": product["id"],
                    "sku": product["sku"],
                    "category": product["category"],
                    "name": product["name"],
                    "price": product["price"],
                    "quantity": quantity,
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Product Added, Product: {product['name']}"
    )

    return events


def product_removed(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    cart_products = [
        {"product_id": p["product_id"], "quantity": p["quantity"]}
        for p in cart["products"]
    ]
    product_removed = random.choice(cart_products)
    quantity_removed = random.randint(1, product_removed["quantity"])

    product_removed_details = next(
        (
            product
            for product in products
            if product["id"] == product_removed["product_id"]
        ),
        None,
    )

    for product in cart["products"]:
        if product["product_id"] == product_removed["product_id"]:
            product["quantity"] -= quantity_removed

        if product["quantity"] == 0:
            cart["products"].remove(product)

    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Product Removed",
                "timestamp": tstamp,
                "page": {
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://www.thejaffleshop.com/cart",
                },
                "properties": {
                    "session_id": session_id,
                    "cart_id": cart["cart_id"],
                    "product_id": product_removed["product_id"],
                    "sku": product_removed_details["sku"],
                    "category": product_removed_details["category"],
                    "name": product_removed_details["name"],
                    "price": product_removed_details["price"],
                    "quantity": quantity_removed,
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Product Removed, Product: {product_removed_details['name']}"
    )

    return events


def cart_page(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://www.thejaffleshop.com/cart",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://www.thejaffleshop.com/cart",
                    "cart_id": cart["cart_id"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Cart"
    )

    return events


def cart_viewed(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Cart Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://www.thejaffleshop.com/cart",
                },
                "properties": {
                    "session_id": session_id,
                    "cart_id": cart["cart_id"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Cart Viewed"
    )

    return events


def checkout_page_shipping(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    cart["order_id"] = str(uuid.uuid4())
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://www.thejaffleshop.com/checkout/shipping",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://www.thejaffleshop.com/checkout/shipping",
                    "order_id": cart["order_id"],
                },
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://www.thejaffleshop.com/checkout/shipping",
                },
                "properties": {},
            },
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Checkout - Shipping"
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Identitfy"
    )

    return events


def checkout_step_viewed_shipping(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://www.thejaffleshop.com/checkout/shipping",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "step": 1,
                    "name": "Shipping",
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Checkout Step Viewed, Step: Shipping"
    )

    return events


def checkout_step_completed_shipping(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    cart["shipping"] = random.choice(
        [
            {"method": "pickup", "cost": 0.00},
            {"method": "bike", "cost": 5.00},
            {"method": "car", "cost": 10.00},
        ]
    )
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://www.thejaffleshop.com/checkout/shipping",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "step": 1,
                    "name": "Shipping",
                    "shipping_method": cart["shipping"]["method"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Checkout Step Completed, Step: Shipping"
    )

    return events


def checkout_page_payment(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://www.thejaffleshop.com/checkout/payment",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://www.thejaffleshop.com/checkout/payment",
                    "order_id": cart["order_id"],
                },
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://www.thejaffleshop.com/checkout/payment",
                },
                "properties": {},
            },
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Checkout - Payment"
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Identitfy"
    )

    return events


def checkout_step_viewed_payment(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://www.thejaffleshop.com/checkout/payment",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "step": 2,
                    "name": "Payment",
                    "shipping_method": cart["shipping"]["method"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Checkout Step Viewed, Step: Payment"
    )

    return events


def checkout_step_completed_payment(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    cart["payment_method"] = (
        random.choice(["cash", "credit"])
        if cart["shipping"]["method"] == "pickup"
        else "credit"
    )
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://www.thejaffleshop.com/checkout/payment",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "step": 2,
                    "name": "Payment",
                    "shipping_method": cart["shipping"]["method"],
                    "payment_method": cart["payment_method"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Checkout Step Completed, Step: Payment"
    )

    return events


def checkout_page_confirmation(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://www.thejaffleshop.com/checkout/confirmation",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://www.thejaffleshop.com/checkout/confirmation",
                    "order_id": cart["order_id"],
                },
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://www.thejaffleshop.com/checkout/confirmation",
                },
                "properties": {},
            },
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Page Viewed, Page: Checkout - Confirmation"
    )
    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Identitfy"
    )

    return events


def checkout_step_viewed_confirmation(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://www.thejaffleshop.com/checkout/confirmation",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "step": 3,
                    "name": "Confirmation",
                    "shipping_method": cart["shipping"]["method"],
                    "payment_method": cart["payment_method"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Checkout Step Viewed, Step: Confirmation"
    )

    return events


def checkout_step_completed_confirmation(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://www.thejaffleshop.com/checkout/confirmation",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "step": 3,
                    "name": "Confirmation",
                    "shipping_method": cart["shipping"]["method"],
                    "payment_method": cart["payment_method"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Checkout Step Completed, Step: Confirmation"
    )

    return events


def order_completed(events, user, session_id, tstamp, cart):
    last_event = get_last_event(events)
    shipping = cart["shipping"]["cost"]
    revenue = sum([p["price"] * p["quantity"] for p in cart["products"]])
    tax = revenue * 0.1  # 10% tax
    coupon = None  # No coupons and discounts for now
    discount = 0.00

    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Order Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": last_event["page"]["url"],
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://www.thejaffleshop.com/checkout/confirmation",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "revenue": revenue,
                    "coupon": coupon,
                    "discount": discount,
                    "subtotal": revenue - discount,
                    "shipping": shipping,
                    "tax": tax,
                    "total": revenue - discount + shipping + tax,
                    "currency": "USD",
                    "products": cart["products"],
                },
            }
        ],
    )

    logger.info(
        f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Order Completed"
    )

    return events


def drop(events, user, session_id, tstamp, cart):
    events.extend(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Drop",
                "timestamp": tstamp,
                "page": {},
                "properties": {},
            }
        ],
    )

    logger.info(f"Session ID: {session_id}, User ID: {user['user_id']}, Event: Drop")

    return events


def session_event(events, user, session_id, cart):
    """Make an event in a user session."""

    if len(events) == 0:  # Sessions start on the homepage for simplicity
        tstamp = fake.date_time_between_dates(
            datetime_start=pd.Timestamp("2023-01-01").tz_localize("UTC"),
            datetime_end=pd.Timestamp("2023-01-31").tz_localize("UTC"),
        )
        home_page(events, user, session_id, tstamp, cart)

    else:
        last_event = get_last_event(events)
        tstamp = last_event["timestamp"] + pd.Timedelta(
            seconds=random.randint(1, SESSION_MAX_TIMESTEP)
        )

        if (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Home"
        ):
            next_event = random.choices(
                ["Menu Page", "Contact Page", "Drop"],
                [0.85, 0.05, 0.1],
            )[0]

            if next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Contact Page":
                contact_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Menu"
        ):
            next_event = random.choices(
                ["Product Clicked", "Home Page", "Contact Page", "Drop"],
                [0.8, 0.08, 0.02, 0.1],
            )[0]

            if next_event == "Product Clicked":
                product_clicked(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            elif next_event == "Contact Page":
                contact_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Contact Us"
        ):
            next_event = random.choices(
                ["Home Page", "Menu Page", "Drop"],
                [0.3, 0.65, 0.05],
            )[0]

            if next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif last_event["event"] == "Product Clicked":
            product_page(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Product"
        ):
            next_event = random.choices(
                ["Product Added", "Menu Page", "Home Page", "Drop"],
                [0.7, 0.15, 0.1, 0.05],
            )[0]

            if next_event == "Product Added":
                product_added(events, user, session_id, tstamp, cart)
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif last_event["event"] == "Product Added":
            next_event = random.choices(
                ["Cart Page", "Menu Page", "Home Page", "Drop"],
                [0.7, 0.15, 0.1, 0.05],
            )[0]

            if next_event == "Cart Page":
                cart_page(events, user, session_id, tstamp, cart)
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Cart"
        ):
            cart_viewed(events, user, session_id, tstamp, cart)

        elif last_event["event"] == "Cart Viewed":
            next_event = random.choices(
                [
                    "Checkout Page - Shipping",
                    "Product Removed",
                    "Menu Page",
                    "Home Page",
                    "Drop",
                ],
                [0.7, 0.05, 0.15, 0.05, 0.05],
            )[0]

            if next_event == "Checkout Page - Shipping":
                checkout_page_shipping(events, user, session_id, tstamp, cart)
            elif next_event == "Product Removed":
                product_removed(events, user, session_id, tstamp, cart)
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif last_event["event"] == "Product Removed":
            # If product removal resulted in empty cart
            if len(cart["products"]) == 0:
                next_event = random.choices(
                    ["Menu Page", "Home Page", "Drop"],
                    [0.8, 0.15, 0.05],
                )[0]
            else:
                next_event = random.choices(
                    ["Checkout - Shipping", "Menu Page", "Home Page", "Drop"],
                    [0.7, 0.15, 0.1, 0.05],
                )[0]

            if next_event == "Checkout - Shipping":
                checkout_page_shipping(events, user, session_id, tstamp, cart)
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Checkout - Shipping"
        ):
            checkout_step_viewed_shipping(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Checkout Step Viewed"
            and last_event["properties"]["name"] == "Shipping"
        ):
            next_event = random.choices(
                ["Checkout Shipping Completed", "Menu Page", "Home Page", "Drop"],
                [0.75, 0.1, 0.1, 0.05],
            )[0]

            if next_event == "Checkout Shipping Completed":
                checkout_step_completed_shipping(events, user, session_id, tstamp, cart)
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Checkout Step Completed"
            and last_event["properties"]["name"] == "Shipping"
        ):
            checkout_step_viewed_payment(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Checkout Step Completed"
            and last_event["properties"]["name"] == "Shipping"
        ):
            checkout_page_payment(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Checkout - Payment"
        ):
            checkout_step_viewed_payment(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Checkout Step Viewed"
            and last_event["properties"]["name"] == "Payment"
        ):
            next_event = random.choices(
                ["Checkout Payment Completed", "Menu Page", "Home Page", "Drop"],
                [0.75, 0.1, 0.1, 0.05],
            )[0]

            if next_event == "Checkout Payment Completed":
                checkout_step_completed_payment(events, user, session_id, tstamp, cart)
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        # TODO - fix something here so that order completed fires

        elif (
            last_event["event"] == "Checkout Step Completed"
            and last_event["properties"]["name"] == "Payment"
        ):
            checkout_page_confirmation(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Page Viewed"
            and last_event["page"]["name"] == "Checkout - Confirmation"
        ):
            checkout_step_viewed_confirmation(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Checkout Step Viewed"
            and last_event["properties"]["name"] == "Confirmation"
        ):
            next_event = random.choices(
                ["Checkout Confirmation Completed", "Menu Page", "Home Page", "Drop"],
                [0.75, 0.1, 0.1, 0.05],
            )[0]

            if next_event == "Checkout Confirmation Completed":
                checkout_step_completed_confirmation(
                    events, user, session_id, tstamp, cart
                )
            elif next_event == "Menu Page":
                menu_page(events, user, session_id, tstamp, cart)
            elif next_event == "Home Page":
                home_page(events, user, session_id, tstamp, cart)
            else:
                drop(events, user, session_id, tstamp, cart)

        elif (
            last_event["event"] == "Checkout Step Completed"
            and last_event["properties"]["name"] == "Confirmation"
        ):
            order_completed(events, user, session_id, tstamp, cart)

        elif last_event["event"] == "Order Completed":
            drop(events, user, session_id, tstamp, cart)

        # elif last_event["event"] == "Drop":
        #     pass

    return events


# SIMULATE USER SESSIONS
def make_sessions(n_sessions=N_SESSIONS):
    logger.info(f"Making Jaffle Shop {n_sessions} sessions ... ")
    sessions = []

    for _ in range(N_SESSIONS):
        events = []
        session_id = str(uuid.uuid4())
        user = random.choice(users)
        cart = {
            "cart_id": str(uuid.uuid4()),
            "products": [],
        }
        logger.info(f"Starting Session for user: {user['user_id']}")

        if len(events) == 0:
            events = session_event(
                events=events,
                user=user,
                session_id=session_id,
                cart=cart,
            )

        # TODO - while should only apply for one session, then move to the next (up to n_sessions)
        while events[-1]["event"] != "Drop":
            events = session_event(
                events=events,
                user=user,
                session_id=session_id,
                cart=cart,
            )

        logger.info(f"Session ended for user: {user['user_id']}")
        sessions.extend(events)

    df = pd.DataFrame(
        [
            {
                "session_id": event["session_id"],
                "user_id": event["user_id"],
                "event": event["event"],
                "timestamp": event["timestamp"],
                "page": event["page"],
                "properties": event["properties"],
                "cart": cart,
            }
            for event in sessions
        ]
    )

    return df


if __name__ == "__main__":
    df_sessions = make_sessions(n_sessions=1000)
    output_path = Path(__file__).parents[0] / "jaffle_events.csv"
    df_sessions.to_csv(output_path, index=False)
    print(df_sessions.head())
