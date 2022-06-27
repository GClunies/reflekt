# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

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
        - name: nested_property_two
          description: The 2nd nested property.
          type: string
          required: true
        - name: nested_property_one
          description: The 1st nested property.
          type: string
    - name: property_seven
      description: An object property.
      type: object
      object_properties:
        - name: key_one
          description: The 1st key in the object dictionary.
          type: string
          required: true
        - name: key_two
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
      description: A string property.
      type: string
      required: true
      allow_null: true
"""

# Missing description
REFLEKT_EVENT_BAD = """
- version: 1
  name: Test Event
  metadata:
    product_owner: Maura
    code_owner: Greg
  properties:
    - name: property_one
      description: A string property.
      type: string
      required: true
"""
