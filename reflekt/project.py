# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

import yaml
from git import InvalidGitRepositoryError, Repo
from loguru import logger

from reflekt.utils import log_formatter


class ReflektProject:
    def __init__(self) -> None:
        logger_config = {
            "handlers": [
                {
                    "sink": sys.stdout,
                    "format": log_formatter,
                },
            ],
        }
        logger.configure(**logger_config)
        self._project_errors = []
        self.project_dir = self._get_project_root(Path.cwd())
        self.exists = False  # Assume project does not exist by default

        if self.project_dir is not None:
            sink = str(self.project_dir) + "/.reflekt/logs/reflekt.log"
            logger_config = {
                "handlers": [
                    {
                        "sink": sys.stdout,
                        "format": log_formatter,
                    },
                    {
                        "sink": sink,
                        "format": log_formatter,
                    },
                ],
            }
            logger.configure(**logger_config)

            self.project_yml = self.project_dir / "reflekt_project.yml"
            self.exists = True if self.project_yml.exists() else False

            with open(self.project_yml, "r") as f:
                self.project = yaml.safe_load(f)

            self.validate_project()

    def validate_project(self):
        self._get_project_name()
        self._get_config_profile()
        self._get_config_path()
        self._get_events_case()
        self._get_events_allow_numbers()
        self._get_events_reserved()
        self._get_properties_case()
        self._get_properties_allow_numbers()
        self._get_properties_reserved()
        self._get_data_types()
        self._get_warehouse_database_obj()
        self._get_warehouse_schema_obj()
        self._get_expected_metadata_schema()
        self._get_dbt_src_prefix()
        self._get_dbt_model_prefix()
        self._get_dbt_model_materialized()
        self._get_dbt_model_incremental_logic()
        self._get_dbt_docs_prefix()
        self._get_dbt_docs_tests()
        self._get_dbt_docs_in_folder()

    def _get_project_root(self, path: Path) -> Path:
        try:
            git_repo = Repo(path, search_parent_directories=True)
            git_root = Path(git_repo.git.rev_parse("--show-toplevel"))
            reflekt_project_list = list(git_root.glob("**/reflekt_project.yml"))

            # This excludes the reflekt_project.yml file in the templates/
            # folder of this repo. Only an issue for development. Not users.
            reflekt_project_list = [
                path
                for path in reflekt_project_list
                if "templates/project/reflekt_project.yml" not in str(path)
            ]

            if len(reflekt_project_list) > 1:

                msg_list = ""

                for proj in reflekt_project_list:
                    msg_list += "    " + str(proj) + "\n"

                logger.error(
                    f"Found a Git repo at '{str(git_root)}', but repo contains >1 "
                    f"reflekt_project.yml:\n\n"
                    f"{msg_list}"
                    "\nOnly one Reflekt project (one reflekt_project.yml) per repo."
                )
                raise SystemExit(1)

            # If no reflekt project found (i.e. before 'reflekt init') then
            # return None
            if reflekt_project_list:
                return reflekt_project_list[0].parents[0]  # project root
            else:
                return  # None

        except InvalidGitRepositoryError:
            logger.error(
                "Git repository not detected. Reflekt project must be inside a Git repo."
                " You can create a Git repo by running"
                "\n\n    git init"
                "\n\nat the root of your Reflekt project."
            )
            raise SystemExit(1)

    def _get_project_name(self) -> None:
        try:
            self.name = self.project["name"]
        except KeyError:
            logger.error(
                "Project 'name:' config not defined in reflekt_project.yml. See Reflekt "
                "docs for details on project name configuration: "
                # noqa: E501
            )
            raise SystemExit(1)

    def _get_config_profile(self) -> None:
        try:
            self.config_profile = self.project["config_profile"]
        except KeyError:
            logger.error(
                "No 'config_profile:' defined in reflekt_project.yml. See Reflekt "
                "docs for details on 'config_profile:' configuration: "
                # noqa: E501
            )
            raise SystemExit(1)

    def _get_config_path(self) -> None:
        config_path_check = self.project.get("config_path")

        if config_path_check is not None:
            self.config_path = Path(config_path_check)

            if not self.config_path.exists():
                logger.error(
                    "The 'config_path: {str(self.config_path)}' defined in "
                    "reflekt_project.yml does not exist."
                )
                raise SystemExit(1)

            if not self.config_path.is_absolute():
                logger.error(
                    "The 'config_path: {str(self.config_path)}' defined in "
                    "reflekt_project.yml must be an absolute path."
                )
                raise SystemExit(1)
        else:
            self.config_path = None

    def _get_events_case(self) -> None:
        try:
            self.events_case = self.project["tracking_plans"]["events"]["naming"]["case"]
        except KeyError:
            logger.error(
                "Missing 'case:' config for event naming conventions in "
                "reflekt_project.yml. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on defining"
                "event naming conventions."
                # noqa: E501
            )
            raise SystemExit(1)

    def _get_events_allow_numbers(self) -> None:
        try:
            self.events_allow_numbers = self.project["tracking_plans"]["events"][
                "naming"
            ]["allow_numbers"]
        except KeyError:
            logger.error(
                "Missing 'allow_numbers:' config for event naming conventions in "
                "reflekt_project.yml. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on defining"
                "event naming conventions."
                # noqa: E501
            )
            raise SystemExit(1)

    def _get_events_reserved(self) -> None:
        try:
            self.events_reserved = self.project["tracking_plans"]["events"]["naming"][
                "reserved"
            ]
        except KeyError:
            logger.error(
                "Missing 'reserved:' config for event naming conventions in "
                "reflekt_project.yml. NOTE - empty list acceptable (e.g 'reserved: []') "
                "\n\nSee the Reflekt docs (https://bit.ly/reflekt-project-config) for "
                "details on defining event naming conventions."
                # noqa: E501
            )
            raise SystemExit(1)

    def _get_properties_case(self) -> None:
        try:
            self.properties_case = self.project["tracking_plans"]["properties"][
                "naming"
            ]["case"]
        except KeyError:
            logger.error(
                "Missing 'case:' config for properties naming conventions in "
                "reflekt_project.yml. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on defining"
                "properties naming conventions."
                # noqa: E501
            )
            raise SystemExit(1)

    def _get_properties_allow_numbers(self) -> None:
        try:
            self.properties_allow_numbers = self.project["tracking_plans"]["properties"][
                "naming"
            ]["allow_numbers"]
        except KeyError:
            logger.error(
                "Missing 'allow_numbers:' config for properties naming conventions in "
                "reflekt_project.yml. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on defining"
                "properties naming conventions."
            )
            raise SystemExit(1)

    def _get_properties_reserved(self) -> None:
        try:
            self.properties_reserved = self.project["tracking_plans"]["properties"][
                "naming"
            ]["reserved"]
        except KeyError:
            logger.error(
                "Missing 'reserved:' config for properties naming conventions in "
                "reflekt_project.yml. NOTE - empty list acceptable (e.g 'reserved: []') "
                "\n\nSee the Reflekt docs (https://bit.ly/reflekt-project-config) for "
                "details on defining properties naming conventions."
            )
            raise SystemExit(1)

    def _get_data_types(self) -> None:
        try:
            self.data_types = self.project["tracking_plans"]["properties"]["data_types"]
        except KeyError:
            logger.error(
                "Missing 'data_types:' config for allowed properties data types "
                " in reflekt_project.yml. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on defining "
                "allowed data types:"
            )
            raise SystemExit(1)

    def _get_warehouse_database_obj(self) -> None:
        try:
            self.warehouse_database_obj = self.project["tracking_plans"]["warehouse"][
                "database"
            ]
        except KeyError:
            logger.error(
                "Tracking plan 'database:' config not defined in reflekt_project.yml. "
                "Each tracking plan in Reflekt project must have a defined database "
                "where Reflekt will search for raw event data when templating dbt "
                "packages. See the Reflekt docs (https://bit.ly/reflekt-project-config) "
                "for details on s'database:' configuration."
            )
            raise SystemExit(1)

    def _get_warehouse_schema_obj(self) -> None:
        try:
            self.warehouse_schema_obj = self.project["tracking_plans"]["warehouse"][
                "schema"
            ]
        except KeyError:
            logger.error(
                "Tracking plan 'schema:' config not defined in reflekt_project.yml. "
                "Each tracking plan in Reflekt project must have a defined schema where "
                "Reflekt will search for raw event data when templating dbt packages. "
                "\n\nSee the Reflekt docs (https://bit.ly/reflekt-project-config) for "
                "details on 'schema:' configuration."
            )
            raise SystemExit(1)

    def _get_expected_metadata_schema(self) -> None:
        if (
            self.project.get("tracking_plans").get("events").get("expected_metadata")
            is not None
        ):
            self.expected_metadata_schema = (
                self.project.get("tracking_plans").get("events").get("expected_metadata")
            )
        else:
            self.expected_metadata_schema = None

    def _get_dbt_src_prefix(self) -> None:
        try:
            self.src_prefix = self.project["dbt"]["templater"]["sources"]["prefix"]
        except KeyError:
            logger.error(
                "dbt templating 'prefix:' config not defined for templated dbt sources "
                "in reflekt_project.yml. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on source "
                "'prefix:' configuration."
            )
            raise SystemExit(1)

    def _get_dbt_model_prefix(self) -> None:
        try:
            self.model_prefix = self.project["dbt"]["templater"]["models"]["prefix"]
        except KeyError:
            logger.error(
                "dbt templating  'prefix:' config not defined for templated dbt models "
                "in reflekt_project.yml. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on model 'prefix:' "
                "configuration."
            )
            raise SystemExit(1)

    def _get_dbt_model_materialized(self) -> None:
        try:
            self.materialized = self.project["dbt"]["templater"]["models"][
                "materialized"
            ].lower()
            if self.materialized not in ["view", "incremental"]:
                logger.error(
                    "Invalid 'materialized:' config defined for templated dbt models in "
                    "reflekt_project.yml. Must be either 'view' or 'incremental'. "
                    "\n\nSee the Reflekt docs (https://bit.ly/reflekt-project-config) on"
                    " model configuration."
                )
                raise SystemExit(1)

        except KeyError:
            logger.error(
                "No 'materialized:' config defined for templated dbt models in "
                "reflekt_project.yml. Must be either 'view' or 'incremental'. "
                "\n\nSee the Reflekt docs (https://bit.ly/reflekt-project-config) on "
                "model configuration."
            )
            raise SystemExit(1)

    def _get_dbt_model_incremental_logic(self) -> None:
        if self.materialized == "incremental":
            try:
                self.incremental_logic = self.project["dbt"]["templater"]["models"][
                    "incremental_logic"
                ]
            except KeyError:
                logger.error(
                    "dbt templating 'materialized: incremental' defined in "
                    "reflekt_project.yml for templated dbt models, but missing "
                    "'incremental_logic:' configuration. \n\nSee the Reflekt docs "
                    "(https://bit.ly/reflekt-project-config) for details on "
                    "'incremental_logic:' configuration."
                )
                raise SystemExit(1)

        else:
            self.incremental_logic = None

    def _get_dbt_docs_prefix(self) -> None:
        try:
            self.docs_prefix = self.project["dbt"]["templater"]["docs"]["prefix"]
        except KeyError:
            logger.error(
                "dbt templating configuration 'prefix:' not defined in "
                "reflekt_project.yml for templated dbt docs. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on 'prefix:' "
                "configuration."
            )
            raise SystemExit(1)

    def _get_dbt_docs_tests(self) -> None:
        try:
            self.docs_test_not_null = self.project["dbt"]["templater"]["docs"][
                "id_tests"
            ]["not_null"]
        except KeyError:
            logger.error(
                "dbt test configuration 'not_null:' not defined in reflekt_project.yml "
                "for templated dbt docs.  \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on doc 'not_null:' "
                "test configuration."
            )
            raise SystemExit(1)

        try:
            self.docs_test_unique = self.project["dbt"]["templater"]["docs"]["id_tests"][
                "unique"
            ]
        except KeyError:
            logger.error(
                "Test configuration 'unique:' not defined is reflekt_project.yml for "
                "templated dbt docs. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on 'unique:' test "
                "configuration."
            )
            raise SystemExit(1)

    def _get_dbt_docs_in_folder(self) -> None:
        try:
            self.docs_in_folder = self.project["dbt"]["templater"]["docs"]["in_folder"]
        except KeyError:
            logger.error(
                "Templating configuration 'in_folder:' not defined in "
                "reflekt_project.yml for templated dbt docs. \n\nSee the Reflekt docs "
                "(https://bit.ly/reflekt-project-config) for details on 'in_folder:' "
                "configuration."
            )
            raise SystemExit(1)
