# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml

from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.property import ReflektProperty
from tests.fixtures import (
    REFLEKT_PROPERTY,
    REFLEKT_PROPERTY_BAD,
    REFLEKT_PROPERTY_BAD_PATTERN,
)


def test_reflekt_property():
    property = ReflektProperty(yaml.safe_load(REFLEKT_PROPERTY))

    assert property.name == "property_one"
    assert property.description == "A test property."
    assert property.type == "string"
    assert property.required is True
    assert property.allow_null is True

    with pytest.raises(ReflektValidationError):
        # This bad event mixes integer type with enum (not allowed)
        ReflektProperty(yaml.safe_load(REFLEKT_PROPERTY_BAD))


def test_default_property_values():
    property_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY)
    property_yaml_obj.pop("required")
    property_yaml_obj.pop("allow_null")
    property = ReflektProperty(property_yaml_obj)

    assert property.required is False
    assert property.allow_null is False


def test_validate_pattern_on_string_type():
    property_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY_BAD_PATTERN)

    with pytest.raises(ReflektValidationError):
        # ReflektEvent runs validate_event() when initialized
        ReflektProperty(property_yaml_obj)


def test_valid_type():
    property_yaml_obj = yaml.safe_load(REFLEKT_PROPERTY)
    property_yaml_obj["type"] = "foobar"

    with pytest.raises(ReflektValidationError):
        # ReflektProperty runs validate_event() when initialized
        ReflektProperty(property_yaml_obj)


def test_property_validation():
    property_good = ReflektProperty(yaml.safe_load(REFLEKT_PROPERTY))

    # Redundant, but makes it clear that the test is testing
    assert property_good.validate_property() is None

    with pytest.raises(ReflektValidationError):
        # ReflektEvent runs validate_event() when initialized
        ReflektProperty(yaml.safe_load(REFLEKT_PROPERTY_BAD))
