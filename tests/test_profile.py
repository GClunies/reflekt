# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import shutil
from pathlib import Path  # noqa: D100

import pytest
import yaml

from reflekt.profile import Profile, ProfileError
from reflekt.project import Project


def test_profile():
    """Test Profile class."""
    # Profiles are validated against reflekt/schemas/project.json on init.
    # These tests ensure that attributes are being set as expected
    project = Project(use_defaults=False, path="./tests/fixtures/reflekt_project.yml")
    profile = Profile(project=project)
    assert isinstance(profile.project, Project)
    assert profile.name == "test_profile"
    assert profile.path == Path("./tests/fixtures/reflekt_profiles.yml").resolve()
    assert profile.version == 1.0
    assert profile.do_not_track is False
    assert profile.registry == [
        {"type": "segment", "api_token": "test_token"},
        {
            "type": "avo",
            "workspace_id": "test_workspace_id",
            "service_account_name": "test_service_account_name",
            "service_account_secret": "test_secret",
        },
    ]
    assert profile.source[0] == {
        "id": "test_source",
        "type": "snowflake",
        "account": "test_account",
        "database": "test_database",
        "warehouse": "test_warehouse",
        "role": "test_role",
        "user": "test_user",
        "password": "test_password",
    }


def test_non_existent_profiles_path():
    """Test that a non-existent profile errors."""
    project = Project(path="./tests/fixtures/reflekt_project.yml")
    project.profiles_path = Path("non/existent/path")

    with pytest.raises(ProfileError):
        Profile(project=project)


def test_profile_not_found():
    """Test that a profile not found in reflekt_profiles.yml errors."""
    project = Project(path="./tests/fixtures/reflekt_project.yml")
    project.default_profile = "non_existent_profile"

    with pytest.raises(ProfileError):
        Profile(project=project)


def test_add_profile_to_new_yaml():
    """Test that profile can be added to new reflekt_profiles.yml."""
    project = Project(path="./tests/fixtures/reflekt_project.yml")
    profile = Profile(project=project)
    profile.path = Path("./tests/fixtures/tmp_reflekt_profiles.yml").resolve()
    profile.path.unlink(missing_ok=True)  # Remove file if exists
    profile.to_yaml()  # Create new reflekt_profiles.yml

    with profile.path.open() as f:
        profile_yml = yaml.safe_load(f)

    assert profile_yml == {
        "version": 1.0,
        "test_profile": {
            "registry": [
                {"type": "segment", "api_token": "test_token"},
                {
                    "type": "avo",
                    "workspace_id": "test_workspace_id",
                    "service_account_name": "test_service_account_name",
                    "service_account_secret": "test_secret",
                },
            ],
            "source": [
                {
                    "id": "test_source",
                    "type": "snowflake",
                    "account": "test_account",
                    "database": "test_database",
                    "warehouse": "test_warehouse",
                    "role": "test_role",
                    "user": "test_user",
                    "password": "test_password",
                }
            ],
        },
    }
    profile.path.unlink(missing_ok=True)  # Cleanup


def test_add_profile_to_existing_yaml():
    """Test that profile can be added to existing reflekt_profiles.yml."""
    shutil.copy(
        "./tests/fixtures/reflekt_profiles.yml",
        "./tests/fixtures/tmp_reflekt_profiles.yml",
    )
    project = Project(path="./tests/fixtures/reflekt_project.yml")
    project.profiles_path = Path("./tests/fixtures/tmp_reflekt_profiles.yml").resolve()
    profile = Profile(project=project)
    profile.name = "new_test_profile"
    profile.to_yaml()

    # Read existing reflekt_profiles.yml
    with profile.path.open() as f:
        profile_yml = yaml.safe_load(f)

    assert profile_yml == {
        "version": 1.0,
        "test_profile": {
            "do_not_track": False,
            "registry": [
                {"type": "segment", "api_token": "test_token"},
                {
                    "type": "avo",
                    "workspace_id": "test_workspace_id",
                    "service_account_name": "test_service_account_name",
                    "service_account_secret": "test_secret",
                },
            ],
            "source": [
                {
                    "id": "test_source",
                    "type": "snowflake",
                    "account": "test_account",
                    "database": "test_database",
                    "warehouse": "test_warehouse",
                    "role": "test_role",
                    "user": "test_user",
                    "password": "test_password",
                }
            ],
        },
        "new_test_profile": {
            "registry": [
                {"type": "segment", "api_token": "test_token"},
                {
                    "type": "avo",
                    "workspace_id": "test_workspace_id",
                    "service_account_name": "test_service_account_name",
                    "service_account_secret": "test_secret",
                },
            ],
            "source": [
                {
                    "id": "test_source",
                    "type": "snowflake",
                    "account": "test_account",
                    "database": "test_database",
                    "warehouse": "test_warehouse",
                    "role": "test_role",
                    "user": "test_user",
                    "password": "test_password",
                }
            ],
        },
    }
    profile.path.unlink(missing_ok=True)  # Cleanup


def test_non_unique_source_ids():
    """Test that non-unique source ids error."""
    project = Project(path="./tests/fixtures/reflekt_project.yml")
    project.profiles_path = (
        Path("./tests/fixtures/reflekt_profiles_duplicate_source.yml")
        .resolve()
        .expanduser()
    )

    with pytest.raises(ProfileError):
        Profile(project=project)


# Final cleanup
Path("./tests/fixtures/tmp_reflekt_profiles.yml").resolve().unlink(missing_ok=True)
