# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pandas as pd

# Load raw data
customers = pd.read_csv('data/raw_customers.csv')
orders = pd.read_csv('data/raw_orders.csv')
products = pd.read_csv('data/raw_products.csv')
payments = pd.read_csv('data/raw_payments.csv')

# User visits homepage (www.jaffleshop.com)

# User creates account (www.jaffleshop.com/signup)

# User views product page (www.jaffleshop.com/products/{product_id})

# User adds product to cart (www.jaffleshop.com/cart/add/{product_id})

# User views cart (www.jaffleshop.com/cart)

# User checks out (www.jaffleshop.com/checkout)

# User views order confirmation page (www.jaffleshop.com/order/{order_id})

# Order Shipped

# Users views order history (www.jaffleshop.com/orders)

# User returns order (www.jaffleshop.com/return/{order_id})
