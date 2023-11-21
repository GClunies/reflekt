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
    "Product Page",
    "Cart Page",
    "Checkout Page",
    "Order Confirmation Page",
    "Product Clicked",
    "Product Added",
    "Product Removed",
    "Checkout Started",
    "Checkout Step Viewed",
    "Checkout Step Completed",
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


def session_action(
    user,
    in_tstamp,
    in_action,
    in_page,
    session_id,
):
    """Make an action in a user session."""
    out_tstamp = in_tstamp + pd.Timedelta(
        seconds=random.randint(1, SESSION_MAX_TIMESTEP)
    )

    if in_action is None:  # For simplicity, all sessions start on home page
        segment_analytics.identify(
            anonymous_id=user["anonymous_id"],
            user_id=user["user_id"],
            timestamp=out_tstamp,
        )
        out_action = "Home Page"
        out_page = {
            "name": "Home",
            "path": "/",
            "referrer": None,
            "search": None,
            "title": "Jaffle Shop - Home",
            "url": "https://thejaffleshop.com/",
        }
        out_tstamp = out_tstamp + pd.Timedelta(seconds=1)
        segment_analytics.page(
            name="Home",
            timestamp=out_tstamp,
            properties=out_page.update({"session_id": session_id}),
        )

    elif in_action == "Home Page":
        out_action = random.choices(
            ["Menu Page", "Contact Page", "Drop"],
            [0.85, 0.05, 0.1],
        )

        if out_action == "Menu Page":
            segment_analytics.identify(
                anonymous_id=user["anonymus_id"],
                user_id=user["user_id"],
                timestamp=out_tstamp,
            )
            out_page = {
                "name": "Menu",
                "url": "https://thejaffleshop.com/menu",
                "path": urlparse("https://thejaffleshop.com/menu").path,
                "search": urlparse("https://thejaffleshop.com/menu").query,
                "title": "Jaffle Shop - Menu",
                "referrer": in_page["url"],
            }
            out_tstamp = out_tstamp + pd.Timedelta(seconds=1)
            segment_analytics.page(
                name="Menu",
                timestamp=out_tstamp,
                properties=out_page.update({"session_id": session_id}),
            )

        elif out_action == "Contact Page":
            segment_analytics.identify(
                anonymous_id=user["anonymous_id"],
                user_id=user["user_id"],
                timestamp=out_tstamp,
            )
            out_page = {
                "name": "Contact",
                "url": "https://thejaffleshop.com/contact",
                "path": urlparse("https://thejaffleshop.com/contact").path,
                "search": urlparse("https://thejaffleshop.com/contact").query,
                "title": "Jaffle Shop - Contact",
                "referrer": in_page["url"],
            }
            out_tstamp = out_tstamp + pd.Timedelta(seconds=1)
            segment_analytics.page(
                name="Contact",
                timestamp=out_tstamp,
                properties=out_page.update({"session_id": session_id}),
            )

        else:
            out_action = "Drop"

    elif in_action == "Contact Page":
        out_action = random.choices(
            ["Home Page", "Drop"],
            [0.9, 0.1],
        )

        if out_action == "Home Page":
            segment_analytics.identify(
                anonymous_id=user["anonymous_id"],
                user_id=user["user_id"],
                timestamp=out_tstamp,
            )
            out_action = "Home Page"
            out_page = {
                "name": "Home",
                "url": "https://thejaffleshop.com/",
                "path": urlparse("https://thejaffleshop.com/").path,
                "search": urlparse("https://thejaffleshop.com/").query,
                "title": "Jaffle Shop - Home",
                "referrer": in_page["url"],
            }
            out_tstamp = out_tstamp + pd.Timedelta(seconds=1)
            segment_analytics.page(
                name="Home",
                timestamp=out_tstamp,
                properties=out_page.update({"session_id": session_id}),
            )

        else:
            out_action = "Drop"

    elif in_action == "Menu Page":
        out_action = random.choices(
            ["Product Clicked", "Drop"],
            [0.9, 0.1],
        )

        if out_action == "Product Clicked":
            # User clicked on a product
            product = random.choice(products)
            segment_analytics.track(
                event="Product Clicked",
                timestamp=out_tstamp,
                context={
                    "page": {
                        "url": in_page["url"],
                        "path": in_page["path"],
                        "referrer": in_page["referrer"],
                        "search": in_page["search"],
                        "title": in_page["title"],
                    }
                },
                properties={
                    "product_id": product["id"],
                    "sku": product["sku"],
                    "category": product["category"],
                    "name": product["name"],
                    "price": product["price"],
                    "session_id": session_id,
                },
            )
            out_action = "Product Page"  # Page loads after click
            out_tstamp = out_tstamp + pd.Timedelta(seconds=1)
            out_page = {
                "name": "Product",
                "url": f"https://thejaffleshop.com/product/{product['id']}",
                "path": urlparse(
                    f"https://thejaffleshop.com/product/{product['id']}"
                ).path,
                "search": urlparse(
                    f"https://thejaffleshop.com/product/{product['id']}"
                ).query,
                "title": f"Jaffle Shop - {product['name']}",
                "referrer": in_page["url"],
            }
            segment_analytics.page(
                name="Product",
                timestamp=out_tstamp,
                properties=out_page.update({"session_id": session_id}),
            )

        else:
            out_action = "Drop"

    elif in_action == "Product Page":
        out_action = random.choices(
            ["Product Added", "Home Page", "Drop"],
            [0.75, 0.15, 0.1],
        )

        if out_action == "Product Added":
            # User added a product to their cart
            product = random.choice(products)
            segment_analytics.track(
                event="Product Added",
                timestamp=out_tstamp,
                context={
                    "page": {
                        "url": in_page["url"],
                        "path": in_page["path"],
                        "referrer": in_page["referrer"],
                        "search": in_page["search"],
                        "title": in_page["title"],
                    }
                },
                properties={
                    "product_id": product["id"],
                    "sku": product["sku"],
                    "category": product["category"],
                    "name": product["name"],
                    "price": product["price"],
                    "session_id": session_id,
                },
            )
        elif out_action == "Home Page":
            segment_analytics.identify(
                anonymous_id=user["anonymous_id"],
                user_id=user["user_id"],
                timestamp=out_tstamp,
            )
            out_action = "Home Page"
            out_page = {
                "name": "Home",
                "url": "https://thejaffleshop.com/",
                "path": urlparse("https://thejaffleshop.com/").path,
                "search": urlparse("https://thejaffleshop.com/").query,
                "title": "Jaffle Shop - Home",
                "referrer": in_page["url"],
            }
            out_tstamp = out_tstamp + pd.Timedelta(seconds=1)
            segment_analytics.page(
                name="Home",
                timestamp=out_tstamp,
                properties=out_page.update({"session_id": session_id}),
            )

    elif in_action == "Product Added":
        # TODO - pick up from here
        pass

    return user, out_action, out_page, out_tstamp


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

# SIMULATE USER SESSIONS
for _ in range(N_SESSIONS):
    action_number = 0
    user = random.choice(users)
    session_id = uuid.uuid4()
    tstamp = fake.date_time_between_dates(
        datetime_start=pd.Timestamp("2023-01-01").tz_localize("UTC"),
        datetime_end=pd.Timestamp("2023-01-31").tz_localize("UTC"),
    )

    if action_number == 0:
        action = None
        page = None

        # page = {  # For simplicity, all sessions start on the home page
        #     "name": "Home",
        #     "url": "https://thejaffleshop.com/",
        #     "path": urlparse("https://thejaffleshop.com/").path,
        #     "search": urlparse("https://thejaffleshop.com/").query,
        #     "title": "Jaffle Shop - Home",
        #     "referrer": None,
        # }

    while action != "Drop":
        user, action, page, tstamp = session_action(
            user=user,
            in_tstamp=tstamp,
            in_action=action,
            in_page=page,
            session_id=session_id,
        )
