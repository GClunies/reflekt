# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import random
import uuid
from pathlib import Path

import faker
import pandas as pd
from loguru import logger
from segment import analytics as segment_analytics

fake = faker.Faker(locale="en_US")
logger = logger.opt(colors=True)

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
    "Home Page Viewed",
    "Acount Sign In Page Viewed",
    "Create Account Page Viewed",
    "Products List Page Viewed",
    "Product Page Viewed",
    "Cart Page Viewed",
    "Checkout Page Viewed",
    "Order Confirmation Page Viewed",
    "Session Started",
    "Sign In Clicked",
    "Product Clicked",
    "Product Added",
    "Product Removed",
    "Checkout Started",
    "Checkout Step Viewed",
    "Checkout Step Completed",
    "Order Completed",
    "Drop",
]
SESSION_LIMIT = 1800  # 30 minutes in seconds


def generate_users(n_users=10000, include_anonymous=True, percent_anonymous=0.85):
    """Generate a dataframe of users, including anonymous users.

    By default, 85% of users will be anonymous, and 15% will be signed in.
    Reference: https://www.braze.com/resources/articles/anonymous-user-campaigns-6-ways-to-activate-retain-and-monetize-your-unknown-users
    """

    if include_anonymous:
        n_anonymous = int(n_users * percent_anonymous)
        anonymous_user = pd.DataFrame(
            {
                "anonymous_id": [uuid.uuid4() for _ in range(n_anonymous)],
                "user_id": [None],
                "email": [None],
                "first_name": [None],
                "last_name": [None],
            }
        )

    n_signed_in = n_users - n_anonymous
    signed_in_users = pd.DataFrame(
        {
            "anonymous_id": [
                uuid.uuid4() for _ in range(n_anonymous)
            ],  # Assume cookies are persistent
            "user_id": [uuid.uuid4() for _ in range(n_signed_in)],
            "email": [fake.email() for _ in range(n_signed_in)],
            "first_name": [fake.first_name() for _ in range(n_signed_in)],
            "last_name": [fake.last_name() for _ in range(n_signed_in)],
        }
    )

    return pd.concat([anonymous_user, signed_in_users])


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


def next_move(last_action, last_tstamp, last_referrer, anonymous_id, user_id):
    """Simulate the next action a user will take on the site."""
    # Set timestamp to be within 30 minutes of last action
    tstamp = last_tstamp + pd.Timedelta(seconds=random.randint(1, SESSION_LIMIT - 1))

    if last_action == "Home Page Viewed":
        # 15% of anonymous users click "Sign In"
        if user_id is None and random.random() < 0.15:
            segment_analytics.track(
                event="Sign In Clicked",
                timestamp=tstamp,
                properties={"page_url": "https://jaffle_shop.com/"},
            )

            return ("Sign In Clicked", tstamp, "https://jaffle_shop.com/")

        else:
            next_action = random.choices(
                ["Products List Page Viewed", "Product Clicked", "Drop"],
                weights=[0.45, 0.45, 0.1],
            )[0]

            if next_action == "Product Clicked":
                product = random.choice(products)
                segment_analytics.track(
                    event="Product Clicked",
                    timestamp=tstamp,
                    properties={
                        "product_id": product["id"],
                        "sku": product["sku"],
                        "category": product["category"],
                        "name": product["name"],
                        "price": product["price"],
                        "url": f"https://jaffle_shop.com/products/{product['id']}",
                    },
                )

                return "Product Clicked", tstamp, "https://jaffle_shop.com/"

            elif next_action == "Products List Page Viewed":
                segment_analytics.identify(anonymous_id=anonymous_id, user_id=user_id)
                segment_analytics.page(
                    name="Products List",
                    properties={
                        "url": "https://jaffle_shop.com/products",
                        "title": "Jaffle Shop - Products",
                        "referrer": last_referrer,
                    },
                )

                return (
                    "Products List Page Viewed",
                    tstamp,
                    "https://jaffle_shop.com/products",
                )

            elif next_action == "Drop":
                return "Drop", tstamp, "https://jaffle_shop.com/"

    elif last_action == "Sign In Clicked":
        segment_analytics.identify(anonymous_id=anonymous_id, user_id=user_id)
        segment_analytics.page(
            name="Account Sign In",
            properties={
                "url": "https://jaffle_shop.com/sign-in",
                "title": "Jaffle Shop - Sign In",
                "referrer": last_referrer,
            },
        )

        return "Acount Sign In Page Viewed", tstamp, "https://jaffle_shop.com/sign-in"

    # TODO - keep building this chain of actions


# Generate 10,000 users
if USERS_PATH.exists():
    users = pd.read_csv(USERS_PATH)
else:
    users = generate_users(
        n_users=10000, include_anonymous=True, percent_anonymous=0.85
    ).pirnt()
    users.to_csv("users.csv", index=False)

# Generate 10 products
if PRODUCTS_PATH.exists():
    products = pd.read_csv(PRODUCTS_PATH)
else:
    products = generate_products(
        names=PRODUCT_NAMES, prices=PRODUCT_PRICES, categories=PRODUCT_CATEGORIES
    )
    products.to_csv("products.csv", index=False)

# SIMULATE USER SESSIONS
for _ in range(1000):
    start_tstamp = fake.date_time_between_dates(
        datetime_start=pd.Timestamp("2023-01-01").tz_localize("UTC"),
        datetime_end=pd.Timestamp("2023-01-31").tz_localize("UTC"),
    )
    user = random.choice(users)
    anonymous_id = user["anonymous_id"]
    user_id = user["user_id"]
    session_id = uuid.uuid4()

    # Always start session on the home page
    segment_analytics.identify(anonymous_id=anonymous_id, user_id=user_id)
    segment_analytics.page(
        name="Home",
        timestamp=start_tstamp,
        properties={
            "session_id": session_id,
            "url": "https://jaffle_shop.com/",
            "title": "Jaffle Shop - Home",
            "referrer": None,
        },
    )
    last_action = "Home Page Viewed"
    last_tstamp = start_tstamp
    last_referrer = "https://jaffle_shop.com/"

    while last_action != "Drop":
        last_action, last_tstamp, page_referrer = next_move(
            last_action=last_action,
            last_tstamp=last_tstamp,
            last_referrer=last_referrer,
            anonymous_id=anonymous_id,
            user_id=user_id,
        )
