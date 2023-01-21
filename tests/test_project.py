# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import shutil
from pathlib import Path

import pytest
import yaml

from reflekt.project import Project


def test_project_init():
    """Test Project class is initialized correctly when path=None.

    Searches for reflekt_project.yml at root of this repo.
    """
    project = Project()  # Without path arg, searches Git repo for reflekt_project.yml
    assert isinstance(project, Project)
    assert project.exists is True
    assert project.dir == Path(".").resolve()
    assert project.path == Path("./reflekt_project.yml").resolve()
    assert project.version == 1.0
    assert project.name == "reflekt_demo"
    assert project.vendor == "com.reflekt-ci"
    assert project.profile == "dev_reflekt"
    assert project.profiles_path == Path("./reflekt_profiles.yml").resolve()
    assert project.schemas == {
        "conventions": {
            "event": {
                "casing": "title",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "property": {
                "casing": "snake",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "data_types": [
                "string",
                "integer",
                "number",
                "boolean",
                "object",
                "array",
                "any",
                "null",
            ],
        },
    }
    assert project.conventions == project.schemas["conventions"]
    assert project.registry == {
        "avo": {
            "branches": {
                "staging": "HqC13KbRJ",
                "main": "main",
            },
        }
    }
    assert project.artifacts == {
        "dbt": {
            "sources": {"prefix": "__src_"},
            "models": {
                "prefix": "stg_",
            },
            "docs": {
                "prefix": "_stg_",
                "in_folder": False,
                "tests": {"id": ["unique", "not_null"]},
            },
        }
    }


def test_project_init_from_path():
    """Test Project class is initialized correctly when path!=None."""
    project = Project(path="./tests/fixtures/reflekt_project.yml")
    assert isinstance(project, Project)
    assert project.exists is True
    assert project.dir == Path("./tests/fixtures").resolve()
    assert project.path == Path("./tests/fixtures/reflekt_project.yml").resolve()
    assert project.version == 1.0
    assert project.name == "test_project"
    assert project.vendor == "com.reflekt-ci"
    assert project.profile == "test_profile"
    assert (
        project.profiles_path == Path("./tests/fixtures/reflekt_profiles.yml").resolve()
    )
    assert project.schemas == {
        "conventions": {
            "event": {
                "casing": "title",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "property": {
                "casing": "snake",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "data_types": [
                "string",
                "integer",
                "number",
                "boolean",
                "object",
                "array",
                "any",
                "null",
            ],
        },
    }
    assert project.conventions == project.schemas["conventions"]
    assert project.registry == {
        "avo": {
            "branches": {
                "staging": "abc123",
                "main": "main",
            },
        }
    }
    assert project.artifacts == {
        "dbt": {
            "sources": {"prefix": "__src_"},
            "models": {
                "prefix": "stg_",
            },
            "docs": {
                "prefix": "_stg_",
                "in_folder": False,
                "tests": {"id": ["unique", "not_null"]},
            },
        }
    }


def test_project_init_use_defaults():
    """Test Project class is initialized correctly when use_defaults=True."""
    project = Project(use_defaults=True)
    assert isinstance(project, Project)
    assert project.exists is False
    assert project.schemas == {
        "conventions": {
            "event": {
                "casing": "any",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "property": {
                "casing": "any",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "data_types": [
                "string",
                "integer",
                "number",
                "boolean",
                "object",
                "array",
                "any",
                "null",
            ],
        }
    }
    assert project.conventions == project.schemas["conventions"]
    assert project.registry == {}  # No registry config by default
    assert project.artifacts == {
        "dbt": {
            "sources": {"prefix": "__src_"},
            "models": {
                "prefix": "stg_",
            },
            "docs": {
                "prefix": "_stg_",
                "in_folder": False,
                "tests": {},  # No tests by default
            },
        }
    }


def test_project_to_yaml():
    """Test Project class can be converted to YAML."""
    project = Project(path="./tests/fixtures/reflekt_project.yml")
    # Create a copy of the project object and set path to a temporary file
    tmp_project = copy.deepcopy(project)
    tmp_project.path = Path("./tests/fixtures/tmp_reflekt_project.yml").resolve()
    tmp_project.to_yaml()

    with tmp_project.path.open() as f:
        project_yaml = yaml.safe_load(f)

    tmp_project.path.unlink()  # Remove tmp file

    assert project_yaml["version"] == 1.0
    assert project_yaml["name"] == "test_project"
    assert project_yaml["profile"] == "test_profile"
    assert project_yaml["profiles_path"] == str(
        Path("./tests/fixtures/reflekt_profiles.yml").resolve()
    )
    assert project.schemas == {
        "conventions": {
            "event": {
                "casing": "title",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "property": {
                "casing": "snake",
                "capitalize_camel": True,
                "numbers": False,
                "reserved": [],
            },
            "data_types": [
                "string",
                "integer",
                "number",
                "boolean",
                "object",
                "array",
                "any",
                "null",
            ],
        },
    }
    assert project.conventions == project.schemas["conventions"]
    assert project.registry == {
        "avo": {
            "branches": {
                "staging": "abc123",
                "main": "main",
            },
        }
    }
    assert project.artifacts == {
        "dbt": {
            "sources": {"prefix": "__src_"},
            "models": {
                "prefix": "stg_",
            },
            "docs": {
                "prefix": "_stg_",
                "in_folder": False,
                "tests": {"id": ["unique", "not_null"]},
            },
        }
    }


def test_multiple_reflekt_project_files_error():
    """Test that an error is raised if multiple reflekt project files are found."""
    Path.mkdir(Path("./tests/tmp"), exist_ok=True)
    shutil.copy(
        "./tests/fixtures/reflekt_project.yml",
        "./tests/tmp/reflekt_project.yml",
    )

    with pytest.raises(SystemExit):
        Project()

    shutil.rmtree(Path("./tests/tmp"))
