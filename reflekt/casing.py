# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from inflection import camelize, titleize, underscore

from reflekt.project import Project


def event_case(string: str) -> str:
    """Convert event name to case specified in reflekt_project.yml.

    Args:
        string (str): String to be converted.

    Returns:
        str: Converted string.
    """
    project = Project()
    case = project.conventions["event"]["casing"]
    capitalize_camel = project.conventions["event"]["capitalize_camel"]
    numbers = project.conventions["event"]["numbers"]
    if case == "snake":
        fmt_string = underscore(string).replace(" ", "_")
    elif case == "camel":
        fmt_string = camelize(string, uppercase_first_letter=capitalize_camel).replace(
            " ", ""
        )
    elif case == "title":
        fmt_string = titleize(string)
    elif case == "any":
        fmt_string = string

    if numbers:
        fmt_string = "".join(char for char in fmt_string if not char.isdigit())

    return fmt_string


def property_case(string: str) -> str:
    """Convert property name to case specified in reflekt_project.yml.

    Args:
        string (str): String to be converted.

    Returns:
        str: Converted string.
    """
    project = Project()
    case = project.conventions["property"]["casing"]
    capitalize_camel = project.conventions["property"]["capitalize_camel"]
    numbers = project.conventions["property"]["numbers"]
    if case == "snake":
        fmt_string = underscore(string).replace(" ", "_")
    elif case == "camel":
        fmt_string = camelize(string, uppercase_first_letter=capitalize_camel).replace(
            " ", ""
        )
    elif case == "title":
        fmt_string = titleize(string)
    elif case == "any":
        fmt_string = string

    if numbers:
        fmt_string = "".join(char for char in fmt_string if not char.isdigit())

    return fmt_string
