# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml
from reflekt.errors import ReflektValidationError
from reflekt.event import ReflektEvent
from reflekt.property import ReflektProperty

# from tests.fixtures import (
#     REFLEKT_EVENT,
#     REFLEKT_EVENT_BAD,
#     REFLEKT_EVENT_DUPLICATE_PROPS,
# )
from tests.fixtures.reflekt_event import REFLEKT_EVENT


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
    event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
    # Duplicate a property
    event_yaml_obj["properties"].append(event_yaml_obj["properties"][0])

    with pytest.raises(SystemExit):
        ReflektEvent(event_yaml_obj)


def test_event_validation():
    # ReflektEvent runs validate_event() when initialized
    event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
    event_good = ReflektEvent(event_yaml_obj)

    # Validate event against reflekt_event_schema
    assert event_good.validate_event() is None


def test_event_bad_version():
    with pytest.raises(SystemExit):
        event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
        event_yaml_obj["version"] = 0  # Invalid version (must be >= 1)
        ReflektEvent(event_yaml_obj)


def test_event_bad_name():
    with pytest.raises(SystemExit):
        event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
        event_yaml_obj["name"] = None  # Must have a name
        ReflektEvent(event_yaml_obj)


def test_event_bad_description():
    with pytest.raises(SystemExit):
        event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
        event_yaml_obj["description"] = None  # Must have a description
        ReflektEvent(event_yaml_obj)


def test_event_bad_metadata():
    with pytest.raises(SystemExit):
        event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
        event_yaml_obj["metadata"] = "A string"  # Must be dictionary
        ReflektEvent(event_yaml_obj)


def test_event_bad_properties():
    with pytest.raises(AttributeError):
        event_yaml_obj = yaml.safe_load(REFLEKT_EVENT)[0]
        event_yaml_obj["properties"] = "A string"  # Must be a list of dicts
        ReflektEvent(event_yaml_obj)
