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
        self.project_yml = self.project_dir / "reflekt_project.yml"
        self.exists = True if self.project_yml.exists() else False

        if self.exists:
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
        self._get_plan_schemas()
        self._get_metadata_schema()
        self._get_dbt_src_prefix()
        self._get_dbt_model_prefix()
        self._get_dbt_model_materialized()
        self._get_dbt_model_incremental_logic()
        self._get_pkg_schemas()

    def _get_project_root(self, path: Path) -> Path:
        try:
            git_repo = Repo(path, search_parent_directories=True)
            git_root = git_repo.git.rev_parse("--show-toplevel")
            return Path(git_root)
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
                    f"\n\nOptional `config_path:` {str(self.config_path)} in reflekt_project.yml does not exist!"  # noqa E501
                )

            if not self.config_path.is_absolute():
                raise ReflektProjectError(
                    f"\n\n"
                    f"Optional `config_path:` {str(self.config_path)} in reflekt_project.yml must be an absolute path!"  # noqa E501
                )
        else:
            self.config_path = None

    def _get_events_case(self) -> None:
        self.events_case = (
            self.project.get("tracking_plans").get("naming").get("events").get("case")
        )

        if self.events_case is None:
            raise ReflektProjectError(
                "\n\nMust define a `case:` rule for event naming convention in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    events:"
                "\n      case: title  # One of title|snake|camel"
                "\n"
            )

    def _get_events_allow_numbers(self) -> None:
        try:
            self.events_allow_numbers = self.project["tracking_plans"]["naming"][
                "events"
            ]["allow_numbers"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `allow_numbers:` rule for events naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    events:"
                "\n      allow_numbers: true  # Or false"
                "\n"
            )

    def _get_events_reserved(self) -> None:
        try:
            self.events_reserved = self.project["tracking_plans"]["naming"]["events"][
                "reserved"
            ]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `reserved:` rule for events naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    events:"
                "\n      reserved: ['My Reserved Event']  # List event names. Can be an empty list!"  # noqa E501
                "\n"
            )

    def _get_properties_case(self) -> None:
        self.properties_case = (
            self.project.get("tracking_plans")
            .get("naming")
            .get("properties")
            .get("case")
        )

        if self.properties_case is None:
            raise ReflektProjectError(
                "\n\nMust define a `case:` rule for properties naming convention in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    properties:"
                "\n      case: title  # One of title|snake|camel"
                "\n"
            )

    def _get_properties_allow_numbers(self) -> None:
        try:
            self.properties_allow_numbers = self.project["tracking_plans"]["naming"][
                "properties"
            ]["allow_numbers"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `allow_numbers:` rule for properties naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    properties:"
                "\n      allow_numbers: true  # Or false"
                "\n"
            )

    def _get_properties_reserved(self) -> None:
        try:
            self.properties_reserved = self.project["tracking_plans"]["naming"][
                "properties"
            ]["reserved"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define a `reserved:` rule for properties naming in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  naming:"
                "\n    properties:"
                "\n      reserved: ['my_reserved_property']  # List properties names. Can be an empty list!"  # noqa E501
                "\n"
            )

    def _get_data_types(self) -> None:
        try:
            self.data_types = self.project["tracking_plans"]["data_types"]["allowed"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define allowed data types for event properties in reflekt_project.yml. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  data_types:"
                "\n    allowed:"
                "\n      - list"
                "\n      - data"
                "\n      - types"
                "\n      - here"
                "\n"
                "\nAvailable data types are: ['string', 'integer', 'boolean', 'number', 'object', 'array', 'any']"  # noqa E501
            )

    def _get_plan_schemas(self) -> None:
        try:
            self.plan_schemas = self.project["tracking_plans"]["plan_schemas"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define `plan_schemas:` in reflekt_project.yml. Each tracking plan in your Reflekt project must"  # noqa E501
                " be mapped to a corresponding schema in data warehouse where it's raw event data is stored. Example:"  # noqa E501
                "\n"
                "\ntracking_plans:"
                "\n  plan_schemas:"
                "\n    plan-name: schema_name"
                "\n"
            )

    def _get_metadata_schema(self) -> None:
        if self.project.get("tracking_plans").get("metadata") is not None:
            self.metadata_schema = (
                self.project.get("tracking_plans").get("metadata").get("schema")
            )
        else:
            self.metadata_schema = None

    def _get_dbt_src_prefix(self) -> None:
        try:
            self.src_prefix = self.project["dbt"]["templater"]["sources"]["prefix"]
        except KeyError:
            raise ReflektProjectError(
                "\n\nMust define `prefix:` for templated dbt sources in reflekt_project.yml. Example:"  # noqa E501
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
                "\n\nMust define `prefix:` for templated dbt models in reflekt_project.yml. Example:"  # noqa E501
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
                "\n\nMust set `materialized:` for templated dbt models in reflekt_project.yml. Example:"  # noqa E501
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
                    "\n\nWhen `materialized: incremental` in reflekt_project.yml, must define incremental logic for templated dbt models. Example:"  # noqa E501
                    "\n\n"
                    "\ndbt:"
                    "\n  incremental_logic: |"
                    "\n    {%- if is_incremental() %}"
                    "\n        where event_timestamp >= (select max(event_timestamp)::date from {{ this }})"  # noqa E501
                    "\n    {%- endif %}"
                )
        else:
            self.incremental_logic = None

    def _get_pkg_schemas(self) -> None:
        if self.project.get("dbt").get("templater").get("package_schemas") is not None:
            self.pkg_schemas = (
                self.project.get("dbt").get("templater").get("package_schemas")
            )
        else:
            self.pkg_schemas = None
