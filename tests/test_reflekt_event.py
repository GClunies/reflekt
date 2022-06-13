# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml

from reflekt.errors import ReflektValidationError
from reflekt.event import ReflektEvent
from reflekt.property import ReflektProperty
from tests.fixtures import (
    REFLEKT_EVENT,
    REFLEKT_EVENT_BAD,
    REFLEKT_EVENT_DUPLICATE_PROPS,
)


def test_reflekt_event():
    event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
    event = ReflektEvent(event_yaml_obj)

    assert event.name == "Test Event"
    assert event.description == "This is a test event."


def test_metadata_parser():
    event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
    event = ReflektEvent(event_yaml_obj)

    assert event.metadata["product_owner"] == "Maura"
    assert event.metadata["code_owner"] == "Greg"


def test_property_parser():
    event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
    event = ReflektEvent(event_yaml_obj)
    property_one = event.properties[0]

    assert type(property_one) == ReflektProperty
    assert property_one.name == "property_one"
    assert property_one.description == "A string property."
    assert property_one.type == "string"
    assert property_one.required is True


def test_duplicate_property():
    event_yaml_obj = yaml.safe_load(REFLEKT_EVENT_DUPLICATE_PROPS)[0]

    with pytest.raises(ReflektValidationError):
        ReflektEvent(event_yaml_obj)


def test_event_validation():
    event_good = ReflektEvent(yaml.safe_load(REFLEKT_EVENT)[0])

    # Redundant, but makes it clear that the test is testing
    assert event_good.validate_event() is None

    with pytest.raises(ReflektValidationError):
        # ReflektEvent runs validate_event() when initialized
        ReflektEvent(yaml.safe_load(REFLEKT_EVENT_BAD)[0])
