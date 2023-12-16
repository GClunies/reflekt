# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import random
import uuid
from pathlib import Path
from urllib.parse import urlparse

import faker
import pandas as pd
from loguru import logger
from segment import analytics as segment_analytics

N_USERS = 100
N_SESSIONS = 1000
SESSION_MAX_TIMESTEP = 60 * 5  # 5 minutes between actions
USERS_PATH = Path.cwd() / "users.csv"
PRODUCTS_PATH = Path.cwd() / "products.csv"
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
    users = pd.DataFrame(
        {
            "user_id": [uuid.uuid4() for _ in range(n_users)],
            "email": [fake.email() for _ in range(n_users)],
            "first_name": [fake.first_name() for _ in range(n_users)],
            "last_name": [fake.last_name() for _ in range(n_users)],
        }
    )

    return users


def generate_products(names, prices, categories):
    products = {
        "id": [],
        "sku": [],
        "category": [],
        "name": [],
        "price": [],
    }

    for name, price, category in zip(names, prices, categories):
        products["id"].append(uuid.uuid4())
        products["sku"].append(fake.ean(length=13))
        products["category"].append(category)
        products["name"].append(name)
        products["price"].append(price)

    return pd.DataFrame(products)


# Generate users
if USERS_PATH.exists():
    users = pd.read_csv(USERS_PATH)
else:
    users = generate_users(n_users=10000).pirnt()
    users.to_csv("users.csv", index=False)

signed_in_users = users[users["user_id"].notnull()]

# Generate products
if PRODUCTS_PATH.exists():
    products = pd.read_csv(PRODUCTS_PATH)
else:
    products = generate_products(
        names=PRODUCT_NAMES, prices=PRODUCT_PRICES, categories=PRODUCT_CATEGORIES
    )
    products.to_csv("products.csv", index=False)


def home_page(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Home",
                    "path": "/",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Home",
                    "url": "https://thejaffleshop.com/",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Home",
                    "path": "/",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Home",
                    "url": "https://thejaffleshop.com/",
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
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Home",
                    "url": "https://thejaffleshop.com/",
                },
                "properties": {},
                "cart": {},
            },
        ],
        ignore_index=True,
    )

    return df


def menu_page(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Menu",
                    "path": "/menu",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://thejaffleshop.com/menu",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Menu",
                    "path": "/menu",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://thejaffleshop.com/menu",
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
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://thejaffleshop.com/menu",
                },
                "properties": {},
                "cart": {},
            },
        ],
        ignore_index=True,
    )

    return df


def contact_page(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Contact",
                    "path": "/contact",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Contact",
                    "url": "https://thejaffleshop.com/contact",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Contact",
                    "path": "/contact",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Contact",
                    "url": "https://thejaffleshop.com/contact",
                },
                "cart": {},
            },
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Identify",
                "timestamp": tstamp + pd.Timedelta(seconds=random.random()),
                "page": {
                    "name": "Contact",
                    "path": "/contact",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Contact",
                    "url": "https://thejaffleshop.com/contact",
                },
                "properties": {},
                "cart": {},
            },
        ],
        ignore_index=True,
    )

    return df


def product_clicked(df, user, session_id, tstamp, cart):
    product = random.choice(products)
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Product Clicked",
                "timestamp": tstamp,
                "page": {  # Products are only clicked on the menu page
                    "name": "Menu",
                    "path": "/menu",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Menu",
                    "url": "https://thejaffleshop.com/menu",
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

    return df


def product_page(df, user, session_id, tstamp, cart):
    product_id = df.get("properties")[-1]["product_id"]  # Product ID from last event
    product = products[products["id"] == product_id]

    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Product",
                    "path": f"/products/{product['id']}",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://thejaffleshop.com/products/{product['id']}",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Product",
                    "path": f"/products/{product['id']}",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://thejaffleshop.com/products/{product['id']}",
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
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://thejaffleshop.com/products/{product['id']}",
                },
                "properties": {},
                "cart": {},
            },
        ],
        ignore_index=True,
    )

    return df


def product_added(df, user, session_id, tstamp, cart):
    product_id = df.get("properties")[-1]["product_id"]  # Product ID from last event
    product = products[products["id"] == product_id]
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

    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Product Added",
                "timestamp": tstamp,
                "page": {
                    "name": "Product",
                    "path": f"/products/{product['id']}",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": f"Jaffle Shop - {product['name']}",
                    "url": f"https://thejaffleshop.com/products/{product['id']}",
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
        ignore_index=True,
    )


def product_removed(df, user, session_id, tstamp, cart):
    cart_products = [
        {"product_id": p["product_id"], "quantity": p["quantity"]}
        for p in cart["products"]
    ]
    product_removed = random.choice(cart_products)
    quantity_removed = random.randint(1, product_removed["quantity"])
    product_removed_details = products[products["id"] == product_removed["product_id"]]

    for product in cart["products"]:
        if product["product_id"] == product_removed["product_id"]:
            product["quantity"] -= quantity_removed

        if product["quantity"] == 0:
            cart["products"].remove(product)

    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Product Removed",
                "timestamp": tstamp,
                "page": {
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://thejaffleshop.com/cart",
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
        ignore_index=True,
    )

    return df


def cart_page(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://thejaffleshop.com/cart",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://thejaffleshop.com/cart",
                    "cart_id": cart["cart_id"],
                },
            }
        ],
        ignore_index=True,
    )

    return df


def cart_viewed(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Cart Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Cart",
                    "path": "/cart",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Cart",
                    "url": "https://thejaffleshop.com/cart",
                },
                "properties": {
                    "session_id": session_id,
                    "cart_id": cart["cart_id"],
                },
            }
        ],
        ignore_index=True,
    )

    return df


# def checkout_started(df, user, session_id, tstamp, cart):
#     order_id = uuid.uuid4()  # Checkout starts order process
#     cart["order_id"] = order_id
#     shipping = random.choice(
#         [0.00, 5.00, 10.00]
#     )  # 0 = pickup, 5 = bike order, 10 = car order
#     revenue = sum([p["price"] * p["quantity"] for p in cart["products"]])
#     tax = revenue * 0.1  # 10% tax
#     value = revenue + shipping + tax

#     df.concat(
#         [
#             {
#                 "session_id": session_id,
#                 "user_id": user["user_id"],
#                 "event": "Checkout Started",
#                 "timestamp": tstamp,
#                 "page": {
#                     "name": "Cart",
#                     "path": "/cart",
#                     "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
#                     "search": None,
#                     "title": "Jaffle Shop - Cart",
#                     "url": "https://thejaffleshop.com/cart",
#                 },
#                 "properties": {
#                     "session_id": session_id,
#                     "order_id": order_id,
#                     "value": value,
#                     "revenue": revenue,
#                     "shipping": shipping,
#                     "tax": tax,
#                     "currency": "USD",
#                     "products": cart["products"],
#                 },
#             }
#         ],
#         ignore_index=True,
#     )

#     return df


def checkout_page_shipping(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://thejaffleshop.com/checkout/shipping",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://thejaffleshop.com/checkout/shipping",
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
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://thejaffleshop.com/checkout/shipping",
                },
                "properties": {},
            },
        ],
        ignore_index=True,
    )

    return df


def checkout_step_viewed_shipping(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://thejaffleshop.com/checkout/shipping",
                },
                "properties": {
                    "session_id": session_id,
                    "order_id": cart["order_id"],
                    "step": 1,
                    "name": "Shipping",
                },
            }
        ],
        ignore_index=True,
    )

    return df


def checkout_step_completed_shipping(df, user, session_id, tstamp, cart):
    cart["shipping"] = random.choice(
        [
            {"method": "pickup", "cost": 0.00},
            {"method": "bike", "cost": 5.00},
            {"method": "car", "cost": 10.00},
        ]
    )
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Shipping",
                    "path": "/checkout/shipping",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Shipping",
                    "url": "https://thejaffleshop.com/checkout/shipping",
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
        ignore_index=True,
    )

    return df


def checkout_page_payment(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://thejaffleshop.com/checkout/payment",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://thejaffleshop.com/checkout/payment",
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
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://thejaffleshop.com/checkout/payment",
                },
                "properties": {},
            },
        ],
        ignore_index=True,
    )

    return df


def checkout_step_viewed_payment(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://thejaffleshop.com/checkout/payment",
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
        ignore_index=True,
    )

    return df


def checkout_step_completed_payment(df, user, session_id, tstamp, cart):
    cart["payment_method"] = (
        random.choice(["cash", "credit"])
        if cart["shipping"]["method"] == "pickup"
        else "credit"
    )
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Payment",
                    "path": "/checkout/payment",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Payment",
                    "url": "https://thejaffleshop.com/checkout/payment",
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
        ignore_index=True,
    )


def checkout_page_confirmation(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Page Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://thejaffleshop.com/checkout/confirmation",
                },
                "properties": {
                    "session_id": session_id,
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://thejaffleshop.com/checkout/confirmation",
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
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://thejaffleshop.com/checkout/confirmation",
                },
                "properties": {},
            },
        ],
        ignore_index=True,
    )

    return df


def checkout_step_viewed_confirmation(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Viewed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://thejaffleshop.com/checkout/confirmation",
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
        ignore_index=True,
    )

    return df


def checkout_step_completed_confirmation(df, user, session_id, tstamp, cart):
    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Checkout Step Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://thejaffleshop.com/checkout/confirmation",
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
        ignore_index=True,
    )

    return df


def order_completed(df, user, session_id, tstamp, cart):
    shipping = cart["shipping"]["cost"]
    revenue = sum([p["price"] * p["quantity"] for p in cart["products"]])
    tax = revenue * 0.1  # 10% tax
    coupon = None  # No coupons and discounts for now
    discount = 0.00

    df.concat(
        [
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "event": "Order Completed",
                "timestamp": tstamp,
                "page": {
                    "name": "Checkout - Confirmation",
                    "path": "/checkout/confirmation",
                    "referrer": df.get("page")[-1]["url"] if len(df) > 0 else None,
                    "search": None,
                    "title": "Jaffle Shop - Checkout - Confirmation",
                    "url": "https://thejaffleshop.com/checkout/confirmation",
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
        ignore_index=True,
    )

    return df


def drop(df, user, session_id, tstamp, cart):
    df.concat(
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
        ignore_index=True,
    )

    return df


def session_event(df, user, session_id):
    """Make an event in a user session."""

    if len(df) == 0:  # First event in session starts on home page
        tstamp = fake.date_time_between_dates(
            datetime_start=pd.Timestamp("2023-01-01").tz_localize("UTC"),
            datetime_end=pd.Timestamp("2023-01-31").tz_localize("UTC"),
        )
        home_page(df, user, session_id, tstamp)

    else:
        tstamp = df["timestamp"][-1] + pd.Timedelta(
            seconds=random.randint(1, SESSION_MAX_TIMESTEP)
        )

        if df["event"][-1] == "Page Viewed" and df["page"][-1]["name"] == "Home":
            user_action = random.choices(
                ["Menu Page", "Contact Page", "Drop"],
                [0.85, 0.05, 0.1],
            )

            if user_action == "Menu Page":
                menu_page(df, user, session_id, tstamp)
            elif user_action == "Contact Page":
                contact_page(df, user, session_id, tstamp)
            else:
                drop(df, user, session_id, tstamp)

    return df


df_sessions = pd.DataFrame(
    columns=[
        "session_id",
        "anonymous_id",
        "user_id",
        "event",
        "timestamp",
        "page",
        "properties",
        "cart",
    ]
)

# SIMULATE USER SESSIONS
for _ in range(N_SESSIONS):
    action_number = 0
    user = random.choice(users)
    session_id = uuid.uuid4()
    tstamp = fake.date_time_between_dates(
        datetime_start=pd.Timestamp("2023-01-01").tz_localize("UTC"),
        datetime_end=pd.Timestamp("2023-01-31").tz_localize("UTC"),
    )
    cart = {
        "cart_id": uuid.uuid4(),
        "products": [],
    }

    while df_sessions["event"][-1] != "Drop":
        user, action, page, tstamp, cart = session_event(
            df=df_sessions,
            user=user,
            session_id=session_id,
        )
