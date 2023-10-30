# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import os
import shutil
from pathlib import Path

import pytest
import yaml

from reflekt.project import Project, ProjectError
from reflekt.reporter.reporter import Reporter


def test_reflekt_report():
    """Test `reflekt report` returns expected output."""
    schema_path = Path("./tests/fixtures/schemas/events/Order_Completed/1-0.json")
    reporter = Reporter()
    md_str = reporter.build_md(schema_path)

    # flake8: noqa - readibility is more important than line length here
    assert md_str == (
        "# Order Completed\n\n"
        "#### `$id: segment/ecommerce/Order_Completed/1-0.json`\n\n"
        "*Order successfully completed by the user.*\n\n"
        "## Properties\n\n"
        "- **`checkout_id`** *(string, required)*: Checkout transaction ID.\n"
        '- **`currency`** *(string, required)*: Currency code associated with the transaction. Must be one of: `["USD"]`.\n'
        "- **`order_id`** *(string, required)*: Order ID.\n"
        "- **`products`** *(array, required)*: Products in the order.\n"
        "  - **Items** *(object, required)*\n"
        "    - **`product_id`** *(string)*: Product ID.\n"
        "    - **`sku`** *(string)*: Product SKU.\n"
        "    - **`name`** *(string)*: Product name.\n"
        "    - **`price`** *(number)*: Product price.\n"
        "    - **`quantity`** *(integer)*: Product quantity.\n"
        "    - **`category`** *(string)*: Product category.\n"
        "- **`revenue`** *(number, required)*: Revenue ($) associated with the transaction (excluding shipping and tax).\n"
        "- **`shipping`** *(number, required)*: Shipping cost associated with the transaction.\n"
        "- **`tax`** *(number, required)*: Total tax associated with the transaction.\n"
    )
