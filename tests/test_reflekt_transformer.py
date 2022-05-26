# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0


from reflekt.reflekt.loader import ReflektLoader
from reflekt.reflekt.transformer import ReflektTransformer
from tests.fixtures import _build_reflekt_plan_dir


# TODO
#    - Test transform plan from Reflekt spec to dbt package
#    - Test transform plan from Reflekt spec to Iglu schema json (wait for Iglu integration)  # noqa: E501
def test_reflekt_transformer_segment(tmpdir):
    plan_dir = _build_reflekt_plan_dir(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    reflekt_plan = loader.plan
    transformer = ReflektTransformer(reflekt_plan)
    # Override plan type for testing
    segment_plan = transformer.build_cdp_plan(plan_type="segment")

    segment_plan_name = segment_plan["tracking_plan"]["display_name"]
    segment_plan_identify_traits = segment_plan["tracking_plan"]["rules"]["identify"][
        "properties"
    ]["traits"]["properties"]
    segment_plan_group_traits = segment_plan["tracking_plan"]["rules"]["group"][
        "properties"
    ]["traits"]["properties"]
    segment_plan_event = segment_plan["tracking_plan"]["rules"]["events"][0]
    segment_plan_event_props = segment_plan_event["rules"]["properties"]["properties"][
        "properties"
    ]

    assert segment_plan_name == "test-plan"
    assert segment_plan_identify_traits["user_trait_1"]["description"] == "A user trait."
    assert segment_plan_identify_traits["user_trait_1"]["type"] == ["string"]
    assert (
        segment_plan_identify_traits["user_trait_2"]["description"]
        == "Another user trait."
    )
    assert segment_plan_identify_traits["user_trait_2"]["type"] == ["boolean"]
    assert (
        segment_plan_identify_traits["user_trait_3"]["description"]
        == "One more user trait."
    )
    assert segment_plan_identify_traits["user_trait_3"]["type"] == ["number", "null"]
    assert (
        segment_plan_identify_traits["user_trait_4"]["description"]
        == "An object user trait."
    )
    assert segment_plan_identify_traits["user_trait_4"]["type"] == ["object"]

    assert segment_plan_group_traits["group_trait_one"]["description"] == "A group trait"
    assert segment_plan_group_traits["group_trait_two"]["type"] == ["string"]

    assert segment_plan_event["name"] == "Test Event"
    assert (
        segment_plan_event_props["property_one"]["description"] == "A string property."
    )
    assert segment_plan_event_props["property_one"]["type"] == ["string"]
    assert (
        segment_plan_event_props["property_two"]["description"] == "An integer property."
    )
    assert segment_plan_event_props["property_two"]["type"] == ["integer"]
    assert (
        segment_plan_event_props["property_three"]["description"]
        == "An number property."
    )
    assert segment_plan_event_props["property_three"]["type"] == ["number"]
    assert (
        segment_plan_event_props["property_four"]["description"] == "A boolean property."
    )
    assert segment_plan_event_props["property_four"]["type"] == ["boolean"]
    assert (
        segment_plan_event_props["property_five"]["description"]
        == "An array property (no nesting). Data in array must be same type."
    )
    assert segment_plan_event_props["property_five"]["type"] == ["array"]
    assert (
        segment_plan_event_props["property_six"]["description"]
        == "An array property with nested items."
    )
    assert segment_plan_event_props["property_six"]["type"] == ["array"]
    assert segment_plan_event_props["property_six"]["items"]["type"] == "object"
    assert (
        segment_plan_event_props["property_six"]["items"]["properties"][
            "nested_property_1"
        ]["description"]
        == "The 1st nested property."
    )
    assert segment_plan_event_props["property_six"]["items"]["properties"][
        "nested_property_1"
    ]["type"] == ["string"]
    assert (
        segment_plan_event_props["property_six"]["items"]["properties"][
            "nested_property_2"
        ]["description"]
        == "The 2nd nested property."
    )
    assert segment_plan_event_props["property_six"]["items"]["properties"][
        "nested_property_2"
    ]["type"] == ["string"]
    assert (
        segment_plan_event_props["property_seven"]["description"]
        == "An object property."
    )
    assert segment_plan_event_props["property_seven"]["type"] == ["object"]
    assert (
        segment_plan_event_props["property_seven"]["properties"]["key_1"]["description"]
        == "The 1st key in the object dictionary."
    )
    assert (
        segment_plan_event_props["property_seven"]["properties"]["key_1"]["type"]
        == "string"
    )
    assert (
        segment_plan_event_props["property_seven"]["properties"]["key_2"]["description"]
        == "The 2nd key in the object dictionary."
    )
    assert (
        segment_plan_event_props["property_seven"]["properties"]["key_2"]["type"]
        == "number"
    )
    assert (
        segment_plan_event_props["property_eight"]["description"]
        == "A date-time property."
    )
    assert segment_plan_event_props["property_eight"]["type"] == ["string"]
    assert segment_plan_event_props["property_eight"]["format"] == "date-time"
    assert (
        segment_plan_event_props["property_nine"]["description"]
        == "A string property (with enum rule)."
    )
    assert segment_plan_event_props["property_nine"]["type"] == ["string"]
    assert segment_plan_event_props["property_nine"]["enum"] == ["one", "two"]
    assert (
        segment_plan_event_props["property_ten"]["description"] == "A string property."
    )
    assert segment_plan_event_props["property_ten"]["type"] == ["string", "null"]
