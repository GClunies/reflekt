# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

REFLEKT_CONFIG = """
my_app_segment:
  cdp: segment
  plan_type: segment
  warehouse:
    snowflake:
      account: dummy_account
      database: dummy_database
      password: foobar
      role: dummy_role
      user: dummy_user
      warehouse: dummy_warehouse
"""
