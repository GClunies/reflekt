# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

REFLEKT_PROPERTY = """
name: test_property
description: A test property.
type: string
required: true
allow_null: true
"""

REFLEKT_PROPERTY_STR = """
name: test_property
description: A test property.
type: string
"""

REFLEKT_PROPERTY_ENUM = """
name: test_property
description: A test property.
type: string
enum:
  - list
  - of
  - allowed
  - values
"""

REFLEKT_PROPERTY_PATTERN = """
name: test_property
description: A test property.
type: string
pattern: '[A-Z]'
"""

REFLEKT_PROPERTY_DATETIME = """
name: test_property
description: A test datetime property.
type: string
datetime: true
"""

REFLEKT_PROPERTY_INT = """
name: test_property
description: A test property.
type: integer
"""

REFLEKT_PROPERTY_NUM = """
name: test_property
description: A test property.
type: number
"""

REFLEKT_PROPERTY_BOOL = """
name: test_property
description: A test property.
type: boolean
"""

REFLEKT_PROPERTY_OBJ = """
name: test_property
description: A test property.
type: object
object_properties:
  - name: nested_property
    description: A nested property
    type: string
  - name: another_nested_property
    description: Another nested property
    type: int
"""

REFLEKT_PROPERTY_ARRAY = """
name: test_property
description: A test property.
type: array
"""

REFLEKT_PROPERTY_ARRAY_NESTED = """
name: test_property
description: A test property.
type: array
array_item_schema:
  - name: nested_property
    description: A nested property
    type: string
  - name: another_nested_property
    description: Another nested property
    type: int
"""
