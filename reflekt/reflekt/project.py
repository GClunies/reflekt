# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import yaml
from git import InvalidGitRepositoryError, Repo

from reflekt.reflekt.errors import ReflektProjectError


class ReflektProject:
    def __init__(self, raise_project_errors: bool = True) -> None:
        self._project_errors = []
        self.project_dir = self._get_project_root(Path.cwd())
        self.exists = False  # Assume project does not exist by defualt

        if self.project_dir is not None:
            self.project_yml = self.project_dir / "reflekt_project.yml"
            self.exists = True if self.project_yml.exists() else False
            with open(self.project_yml, "r") as f:
                self.project = yaml.safe_load(f)

            try:
                self.validate_project()
            except ReflektProjectError as err:
                if raise_project_errors:
                    raise err
                else:
                    self._project_errors.append(err)

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
                raise ReflektProjectError(
                    f"\n"
                    f"\nFound a git repo at '{str(git_root)}' with more than one "
                    f"Reflekt project. Only one Reflekt project per repo."
                    f"\n"
                    f"\n{reflekt_project_list}"
                )

            # If no reflekt project found (i.e. before 'reflekt init') then
            # return None
            if reflekt_project_list:
                return reflekt_project_list[0].parents[0]  # project root
            else:
                return  # None

        except InvalidGitRepositoryError:
            raise ReflektProjectError(
                "\n"
                "\nGit repository not detected. Your Reflekt project must be inside a Git repo to function correctly."  # noqa E501
                "\nYou can create a git repo by running 'git init' at the root of your Reflekt project."  # noqa E501
            )

    def _get_project_name(self) -> None:
        try:
            self.name = self.project["name"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a project name in reflekt_project.yml. Example:"
                "\n"
                "\nname: my_project  # letters, digits, underscores"
                "\n"
            )

    def _get_config_profile(self) -> None:
        try:
            self.config_profile = self.project["config_profile"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a config profile in reflekt_project.yml. Example:"
                "\n"
                "\nconfig_profile: my_config_profile  # letters, digits, underscores"
                "\n"
            )

    def _get_config_path(self) -> None:
        config_path_check = self.project.get("config_path")

        if config_path_check is not None:
            self.config_path = Path(config_path_check)

            if not self.config_path.exists():
                raise ReflektProjectError(
                    f"\n\nOptional 'config_path:' {str(self.config_path)} in reflekt_project.yml does not exist!"  # noqa E501
                )

            if not self.config_path.is_absolute():
                raise ReflektProjectError(
                    f"\n\n"
                    f"Optional 'config_path:' {str(self.config_path)} in reflekt_project.yml must be an absolute path!"  # noqa E501
                )
        else:
            self.config_path = None

    def _get_events_case(self) -> None:
        try:
            self.events_case = self.project["tracking_plans"]["events"]["naming"]["case"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a 'case:' rule for event naming convention in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  events:"
                "\n    naming:"
                "\n      case: title  # One of title|snake|camel"
                "\n"
            )

    def _get_events_allow_numbers(self) -> None:
        try:
            self.events_allow_numbers = self.project["tracking_plans"]["events"][
                "naming"
            ]["allow_numbers"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define an 'allow_numbers:' rule for events naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  events:"
                "\n    naming:"
                "\n      allow_numbers: true  # true|false"
                "\n"
            )

    def _get_events_reserved(self) -> None:
        try:
            self.events_reserved = self.project["tracking_plans"]["events"]["naming"][
                "reserved"
            ]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a 'reserved:' rule for events naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  events:"
                "\n    naming:"
                "\n      reserved: ['My Reserved Event']  # List (can be empty)"  # noqa E501
                "\n"
            )

    def _get_properties_case(self) -> None:
        try:
            self.properties_case = self.project["tracking_plans"]["properties"][
                "naming"
            ]["case"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a 'case:' rule for properties naming convention in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  properties:"
                "\n    naming:"
                "\n      case: title  # One of title|snake|camel"
                "\n"
            )

    def _get_properties_allow_numbers(self) -> None:
        try:
            self.properties_allow_numbers = self.project["tracking_plans"]["properties"][
                "naming"
            ]["allow_numbers"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define an 'allow_numbers:' rule for properties naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  properties:"
                "\n    naming:"
                "\n      allow_numbers: true  # true|false"
                "\n"
            )

    def _get_properties_reserved(self) -> None:
        try:
            self.properties_reserved = self.project["tracking_plans"]["properties"][
                "naming"
            ]["reserved"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a 'reserved:' rule for properties naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  properties:"
                "\n    naming:"
                "\n      reserved: ['my_reserved_property']  # List (can be empty)"  # noqa E501
                "\n"
            )

    def _get_data_types(self) -> None:
        try:
            self.data_types = self.project["tracking_plans"]["properties"]["data_types"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define allowed data types for event properties in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  properties:"
                "\n    data_types:"
                "\n      - list"
                "\n      - data"
                "\n      - types"
                "\n      - here"
                "\n"
                "\nSee docs in Reflekt Github repo for available data types"
            )

    def _get_warehouse_database_obj(self) -> None:
        try:
            self.warehouse_database_obj = self.project["tracking_plans"]["warehouse"][
                "database"
            ]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a database for each tracking plan in "
                "reflekt_project.yml where Reflekt should search for corresponding raw "
                "event tables. Example:"
                "\n"
                "\ntracking_plans:"
                "\n  warehouse:"
                "\n    schema:"
                "\n      plan-name: database_name"
                "\n"
            )

    def _get_warehouse_schema_obj(self) -> None:
        try:
            self.warehouse_schema_obj = self.project["tracking_plans"]["warehouse"][
                "schema"
            ]
        except KeyError:
            raise ReflektProjectError(
                "Must define warehouse 'schema:' config in reflekt_project.yml. "
                "See Reflekt documentation for guidance on config setup:\n"
                "    https://github.com/GClunies/reflekt/blob/main/docs/DOCUMENTATION.md/#reflekt-project"  # noqa: E501
            )

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
            raise ReflektProjectError(
                "\n\nMust define 'prefix:' for templated dbt sources in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ndbt:"
                "\n  sources:"
                "\n    prefix: src_"
            )

    def _get_dbt_model_prefix(self) -> None:
        try:
            self.model_prefix = self.project["dbt"]["templater"]["models"]["prefix"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define 'prefix:' for templated dbt models in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ndbt:"
                "\n  sources:"
                "\n    prefix: src_"
            )

    def _get_dbt_model_materialized(self) -> None:
        try:
            self.materialized = self.project["dbt"]["templater"]["models"][
                "materialized"
            ].lower()
            if self.materialized not in ["view", "incremental"]:
                raise ReflektProjectError(
                    f"Invalid materialized config in reflekt_project.yml...\n"
                    f"    materialized: {self.materialized}\n"
                    f"... is not accepted. Must be either 'view' or 'incremental'."
                )
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust set 'materialized:' for templated dbt models in reflekt_project.yml. Example:"  # noqa E501
                "\n\n"
                "\ndbt:"
                "\n  materialized: view  # OR incremental"
            )

    def _get_dbt_model_incremental_logic(self) -> None:
        if self.materialized == "incremental":
            try:
                self.incremental_logic = self.project["dbt"]["templater"]["models"][
                    "incremental_logic"
                ]
            except KeyError:
                raise ReflektProjectError(
                    "\n\nWhen 'materialized: incremental' in reflekt_project.yml, must define incremental logic for templated dbt models. Example:"  # noqa E501
                    "\n\n"
                    "\ndbt:"
                    "\n  incremental_logic: |"
                    "\n    {%- if is_incremental() %}"
                    "\n        where event_timestamp >= (select max(event_timestamp)::date from {{ this }})"  # noqa E501
                    "\n    {%- endif %}"
                )
        else:
            self.incremental_logic = None

    def _get_dbt_docs_prefix(self) -> None:
        try:
            self.docs_prefix = self.project["dbt"]["templater"]["docs"]["prefix"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define 'prefix:' for templated dbt docs in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ndbt:"
                "\n  docs:"
                "\n    prefix: reflekt_"
            )
