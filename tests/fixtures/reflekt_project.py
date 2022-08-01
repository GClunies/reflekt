# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa

# String below is set as a GitHub secret, used to run pytest in Github Actions

REFLEKT_PROJECT = """
name: my_app                            # Set by 'reflekt init'. Reflekt project name

config_profile: my_app_segment          # USE SEGMENT FOR PYTEST - Set by 'reflekt init'. Config profile in reflekt_config.yml

config_path: /home/runner/work/Reflekt/Reflekt/.reflekt/reflekt_config.yml  # OPTIONAL - overrides default path '~/.reflekt/reflekt_config.yml'

tracking_plans:                         # Tracking plan configurations
  warehouse:                            # Specify where event data is in warehouse
    database:                           # Database configuration
      my-avo-plan: raw                  # Specify database where event data is loaded
      my-segment-plan: raw
    schema:                             # Schema configuration
      my-avo-plan:                          # Config events in tracking plan 'my-plan'
        - schema: my_app_web            # Specify schema where event data is loaded
      my-segment-plan:
        - schema: my_app_web

  events:                               # Event configurations
    naming:                             # Naming convention config
      case: title                       # title|snake|camel
      allow_numbers: false              # true|false
      reserved: []                      # Reserved event names (casing matters)

    # expected_metadata:                  # OPTIONAL metadata configuration
    #   # Define a schema for expected event metadata. Tested when running:
    #   #     reflekt test --name <plan-name>
    #   product_owner:
    #     type: string
    #     required: true
    #     allowed:
    #       - Maura
    #       - Greg
    #   code_owner:
    #     required: true
    #     type: string
    #     allowed:
    #       - Maura
    #       - Greg
    #   stakeholders:
    #     type: string
    #     allowed:
    #       - Product
    #       - Engineering
    #       - Data

  properties:                           # Event Property configurations
    naming:                             # Naming convention config
      case: snake                       # title|snake|camel
      allow_numbers: false              # true|false
      reserved: []                      # Reserved property names (casing matters)

    data_types:                         # Allowed property data types. Available types listed below
      - string
      - integer
      - boolean
      - number
      - object
      - array
      - any
      - 'null'                          # Specify null type in quotes

dbt:                                    # dbt configuration
  templater:                            # Configuration for Reflekt dbt package templater
    sources:                            # Configuration for dbt sources
      prefix: _src_reflekt_             # Prefix for dbt sources

    models:                             # Configuration for dbt models
      prefix: reflekt_                  # Prefix for dbt models
      materialized: incremental         # view|incremental
      incremental_logic: |            # OPTIONAL (if 'materialized: incremental')
       {%- if is_incremental() %}
       where received_at >= ( select max(received_at_tstamp)::date from {{ this }} )
       {%- endif %}

    docs:
      prefix: _reflekt_          # Prefix for docs in templated dbt package
      id_tests:
        not_null: true
        unique: true
      in_folder: false            # Write docs in models/docs/ folder?
"""
