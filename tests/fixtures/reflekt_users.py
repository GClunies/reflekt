# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

REFLEKT_USERS = """
traits:
  - name: user_trait_one
    description: A user trait.
    type: string
  - name: user_trait_two
    description: Another user trait.
    type: boolean
  - name: user_trait_three
    description: One more user trait.
    type: number
    allow_null: true
  - name: user_trait_four
    description: An object user trait.
    type: object
"""
