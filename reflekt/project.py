# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path
from typing import Optional, Tuple

import yaml
from git import InvalidGitRepositoryError, Repo
from jsonschema import validate
from loguru import logger

from reflekt.dumper import ReflektYamlDumper


class Project:
    """
    Reflekt Project class.

    Describes a Reflekt project and its configuration from a reflekt_project.yml.
    """

    def __init__(self, use_defaults: bool = False, path: Optional[str] = None) -> None:
        """Initialize Reflekt project.

        Args:
            use_defaults (bool): Whether or not to initialize the class with
                default values. Defaults to False.
            path (Optional[str]): Path to reflekt_project.yml file. If None,
                searches Git repo for reflekt_project.yml. Defaults to None.
        """
        self.use_defaults = use_defaults
        self.exists: bool = False
        self.dir: Optional[Path] = None
        self.path: Optional[Path] = (
            Path(path).resolve().expanduser() if path is not None else None
        )
        self.version: float = 1.0
        self.config: dict = {}
        self.name: str = ""
        self.vendor: str = ""
        self.profile: str = ""
        self.profiles_path: Path = None
        self.schemas: dict = {}
        self.conventions: dict = {}  # Nested in self.schemas
        self.sources: dict = {}
        self.registry: dict = {}
        self.artifacts: dict = {}

        if self.use_defaults:
            self.schemas = {
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
            self.conventions = self.schemas["conventions"]
            self.registry = {}  # No registry config by default
            self.artifacts = {
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
        elif self.path is not None:  # Use reflekt_project.yml from path
            self.exists = True
            self.dir = self.path.parent
        else:  # Search for reflekt_project.yml in current Git repo
            self.dir, self.path, self.exists = self._get_project_dir(Path.cwd())

        self.exists = True if self.path is not None else False

        if self.exists:
            with self.path.open() as f:  # Load config from reflekt_project.yml
                self.config = yaml.safe_load(f)

            self.validate_project()
            self.version = self.config.get("version")
            self.name = self.config.get("name")
            self.vendor = self.config.get("vendor")
            self.profile = self.config.get("profile")
            self.profiles_path = (
                Path(self.config.get("profiles_path")).resolve().expanduser()
            )
            self.schemas = self.config.get("schemas")
            self.conventions = self.schemas["conventions"]
            self.sources = self.config.get("sources")
            self.registry = self.config.get("registry")
            self.artifacts = self.config.get("artifacts")

    def to_yaml(self):
        """Convert Project class and write to reflekt_project.yml."""
        data = {
            "version": self.version,
            "name": self.name,
            "profile": self.profile,
            "profiles_path": str(self.profiles_path),
            "schemas": self.schemas,
            "sources": self.sources,
            "registry": self.registry,
            "artifacts": self.artifacts,
        }

        with self.path.open("w") as f:
            yaml.dump(
                data,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )

    def validate_project(self):
        """Validate Reflekt profile configuration."""
        reflekt_project = self.dir / "schemas/.reflekt/project/1-0.json"

        with reflekt_project.open() as f:
            schema = json.load(f)

        validate(self.config, schema)

    def _get_project_dir(self, dir: Path) -> Tuple[Path, Path]:
        """Get project dir and path to reflekt_project.yml. Set flag if project exists.

        Args:
            dir (Path): The directory to start searching for a Reflekt project.

        Raises:
            SystemExit: An error occurred while getting project root directory.

        Returns:
            Tuple[Path, Path, bool]: Path to project directory, path to
                reflekt_project.yml, boolean flag indicating if project exists.
        """
        try:
            repo = Repo(dir, search_parent_directories=True)
            repo_root = Path(repo.git.rev_parse("--show-toplevel"))
            # Find dirs w/ reflekt_project.yml file, but exclude template and test files
            projects = [
                path
                for path in list(repo_root.glob("**/reflekt_project.yml"))
                if "_templates/" not in str(path)
                and "tests/fixtures/" not in str(path)  # noqa: W503
            ]

            if len(projects) == 1:
                # Return project dir, path to reflekt_project.yml, set exists to True
                return projects[0].parents[0], Path(projects[0]), True
            elif len(projects) > 1:
                projects_str = "".join(f"    {str(p)}\n" for p in projects)
                error_msg = (
                    f"Git repo found at '{str(repo_root)}', but repo contains "
                    f">1 'reflekt_project.yml':\n\n"
                    f"{projects_str}"
                    f"\nOnly one Reflekt project can be defined per repo."
                )
                logger.error(error_msg)
                raise SystemExit(1)
            else:  # pragma: no cover
                logger.error(
                    f"Git repo found at {str(repo_root)}, but does not contain "
                    f"reflekt_project.yml."
                )
                raise SystemExit(1)

        except InvalidGitRepositoryError:  # pragma: no cover
            error_msg = (
                "Git repo not detected. Reflekt project must be inside a Git repo. You "
                "can create one by running:"
                "\n\n    git init"
                "\n\n...at the root of your Reflekt project."
            )
            logger.error(error_msg)
            raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    project = Project()
