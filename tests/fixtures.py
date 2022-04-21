# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

REFLEKT_PLAN = """
name: test-plan
"""

REFLEKT_PLAN_BAD = """
foobar: test-plan
"""

REFLEKT_EVENT = """
- version: 1
  name: Test Event
  description: This is a test event.
  metadata:
    product_owner: Maura
    code_owner: Greg
  properties:
    - name: property_one
      description: A string property.
      type: string
      required: true
    - name: property_two
      description: An integer property.
      type: integer
    - name: property_three
      description: An number property.
      type: number
    - name: property_four
      description: A boolean property.
      type: boolean
    - name: property_five
      description: An array property (no nesting). Data in array must be
        same type.
      type: array
    - name: property_six
      description: An array property with nested items.
      type: array
      array_item_schema:
        - name: nested_property_2
          description: The 2nd nested property.
          type: string
          required: true
        - name: nested_property_1
          description: The 1st nested property.
          type: string
    - name: property_seven
      description: An object property.
      type: object
      object_properties:
        - name: key_1
          description: The 1st key in the object dictionary.
          type: string
          required: true
        - name: key_2
          description: The 2nd key in the object dictionary.
          type: number
    - name: property_eight
      description: A date-time property.
      type: string
      required: true
      datetime: true
    - name: property_nine
      description: A string property (with enum rule).
      type: string
      required: true
      enum:
        - one
        - two
    - name: property_ten
      description: A string property (with pattern rule).
      type: string
      pattern: '[A-Z]'
    - name: property_eleven
      description: A string property.
      type: string
      required: true
      allow_null: true
"""

REFLEKT_EVENT_BAD = """
- version: 1
  description: This is a test event.
  metadata:
    product_owner: Maura
    code_owner: Greg
  properties:
    - name: property_one
      description: A string property.
      type: string
      required: true
    - name: property_two
      description: An integer property.
      type: integer
    - name: property_three
      description: An number property.
      type: number
    - name: property_four
      description: A boolean property.
      type: boolean
    - name: property_five
      description: An array property (no nesting). Data in array must be
        same type.
      type: array
    - name: property_six
      description: An array property with nested items.
      type: array
      array_item_schema:
        - name: nested_property_2
          description: The 2nd nested property.
          type: string
          required: true
        - name: nested_property_1
          description: The 1st nested property.
          type: string
    - name: property_seven
      description: An object property.
      type: object
      object_properties:
        - name: key_1
          description: The 1st key in the object dictionary.
          type: string
          required: true
        - name: key_2
          description: The 2nd key in the object dictionary.
          type: number
    - name: property_eight
      description: A date-time property.
      type: string
      required: true
      datetime: true
    - name: property_nine
      description: A string property (with enum rule).
      type: string
      required: true
      enum:
        - one
        - two
    - name: property_ten
      description: A string property (with pattern rule).
      type: string
      pattern: '[A-Z]'
    - name: property_eleven
      description: A string property.
      type: string
      required: true
      allow_null: true
"""

REFLEKT_EVENT_DUPLICATE_PROPS = """
- version: 1
  name: Test Event
  description: This is a test event.
  metadata:
    product_owner: Maura
    code_owner: Greg
  properties:
    - name: property_one
      description: A string property.
      type: string
      required: true
    - name: property_one
      description: A string property.
      type: string
      required: true
"""

REFLEKT_IDENTIFY = """
traits:
  - name: user_trait_1
    description: A user trait.
    type: string
  - name: user_trait_2
    description: Another user trait.
    type: boolean
  - name: user_trait_3
    description: One more user trait.
    type: number
    allow_null: true
  - name: user_trait_4
    description: An object user trait.
    type: object
"""

REFLEKT_GROUP = """
traits:
  - name: group_trait_one
    description: A group trait
    type: string
  - name: group_trait_two
    description: A group trait
    type: string
"""

REFLEKT_PROPERTY = """
name: property_one
description: A test property.
type: string
enum:
  - one
  - two
  - three
allow_null: true
required: true
"""

# Can't mix integer type with enum
REFLEKT_PROPERTY_BAD = """
name: property_one
description: A test property.
type: integer
enum:
  - one
  - two
  - three
allow_null: true
"""

# Can't mix integer type with enum
REFLEKT_PROPERTY_BAD_PATTERN = """
name: property_one
description: A test property.
type: integer
pattern: '[A-Z]'
"""


def _build_reflekt_plan_dir(
    tmp_dir,
    plan_fixture=REFLEKT_PLAN,
    event_fixture=REFLEKT_EVENT,
    identify_fixture=REFLEKT_IDENTIFY,
    group_fixture=REFLEKT_GROUP,
):
    plan_dir = tmp_dir.mkdir("tracking-plans").mkdir("test-plan")
    _create_reflekt_plan(plan_dir, plan_fixture)
    _create_reflekt_identify(plan_dir, identify_fixture)
    _create_reflekt_group(plan_dir, group_fixture)
    _create_reflekt_event(plan_dir, event_fixture)

    return plan_dir


def _create_reflekt_plan(tmp_dir, plan_fixture=REFLEKT_PLAN):
    r_prop = tmp_dir / "plan.yml"
    r_prop.write(plan_fixture)


def _create_reflekt_event(tmp_dir, event_fixture=REFLEKT_EVENT):
    r_event = tmp_dir.mkdir("events") / "test-event.yml"
    r_event.write(event_fixture)


def _create_reflekt_identify(tmp_dir, identify_fixture=REFLEKT_IDENTIFY):
    r_identify = tmp_dir / "identify_traits.yml"
    r_identify.write(identify_fixture)


def _create_reflekt_group(tmp_dir, group_fixture=REFLEKT_GROUP):
    r_group = tmp_dir / "group_traits.yml"
    r_group.write(group_fixture)
