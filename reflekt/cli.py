# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa  -- Readability is more important than style here
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Optional, Union

import click
import pkg_resources
import typer
from jsonschema import ValidationError
from loguru import logger
from rich import print
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.traceback import install

from reflekt import SHOW_LOCALS, __version__
from reflekt.builder.handler import BuilderHandler
from reflekt.constants import (
    REGISTRY,
    WAREHOUSE,
    ArtifactEnum,
    RegistryEnum,
    SdkEnum,
)
from reflekt.errors import SelectArgError
from reflekt.linter import Linter
from reflekt.profile import Profile, ProfileError
from reflekt.project import Project, ProjectError
from reflekt.registry.handler import RegistryHandler
from reflekt.tracking import ReflektUser, track_event


# Prettify traceback messages
app = typer.Typer(pretty_exceptions_show_locals=SHOW_LOCALS)  # Typer app
install(show_locals=SHOW_LOCALS)  # Any other uncaught exceptions


user = ReflektUser()  # Create Reflekt user, but do not initialize (no ID set)
default_context = {  # Default context for anonymous usage stats (if not disabled)
    "app": {
        "name": "reflekt",
        "version": __version__,
    }
}


def version_callback(value: bool):
    if value:
        print(f"Reflekt CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """Main entrypoint for Reflekt CLI.

    Sets up the global project object and logging to be used throughout the CLI.
    """
    global project

    try:
        project = Project()
        profile = Profile(project=project)

        if not profile.do_not_track:  # User has not opted out of tracking
            user.initialize()  # Init active user for anonymous usage stats

    except ProjectError:  # This happens when Reflekt project has not yet been created
        project = Project(use_defaults=True)  # Set a dummy project

    configure_logging(verbose=False, project=project)

    logger.info(f"Running with reflekt={__version__}")
    print("")


class ExistingProjectError(Exception):
    """Custom error raised when Reflekt project already exists in directory.

    Occurs when project is initialized, which is why it can't go in reflekt.errors
    """

    def __init__(self, project_path: Path, message: str) -> None:
        """Initialize SegmentApiError class.

        Args:
            project_path (Path): Path to existing reflekt_project.yml.
            message (str): Error message.
        """
        self.project_path = project_path
        self.message = message
        super().__init__(self.message)


def clean_select(select: str) -> str:
    """Removes hanging '/' and '.json' from --select argument.

    Args:
        select (str): The --select argument passed to the Reflekt CLI.

    Returns:
        str: --select argument without '.json' extension.
    """
    cleaned = select.strip().replace(".json", "")

    if cleaned.endswith("/"):
        cleaned = cleaned[:-1]

    return str(cleaned)


def configure_logging(verbose: bool, project: Project):
    LEVEL = "DEBUG" if verbose else "INFO"
    logger.remove()  # Remove default loguru logger
    logger.add(  # Add loguru logger with rich formatting
        RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_path=False,
            log_time_format="[%X]",
            omit_repeated_times=False,
            tracebacks_show_locals=SHOW_LOCALS,
        ),
        format="{message}",
        level=LEVEL,
    )

    if project.exists:
        logger.add(  # Log to file
            str(project.dir) + "/.logs/reflekt_{time:YYYY-MM-DD_HH-mm-ss}.log",
            format="{time:HH:mm:ss} | {level} | {message}",
            level=LEVEL,
        )

    if verbose:
        logger.debug("Verbose logging enabled")
        print("")


@app.command()
def init(
    dir: str = typer.Option(
        ".", "--dir", help="Directory where project will be initialized."
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose logging for debugging.",
    ),
) -> None:
    """Initialize a Reflekt project.

    Raises:
        ProjectError: A Reflekt project already exists in the directory.
    """
    # NOTE: `project` defined in main() callback
    # Since the project doesn't exist yet, we don't log to file
    configure_logging(verbose=verbose, project=project)
    project.dir = Path(dir).expanduser()
    project.path = project.dir / "reflekt_project.yml"

    if project.path.exists():
        raise ProjectError(
            message=(
                f"Reflekt project already found: {project.dir} \n"
                f"  Existing project configuration: {project.path}"
            ),
            project=project,
        )

    # Prompt user for Project details
    project.name = typer.prompt("Project name [letters, digits, underscore]", type=str)
    project.vendor = typer.prompt("Schema vendor [e.g com.your_company]", type=str)

    if project.vendor == "":
        raise typer.BadParameter("Vendor cannot be empty string")

    profile_path = typer.prompt(
        "Path for 'reflekt_profiles.yml' [for connection to schema registry and data warehouse].",
        type=str,
        default=str(Path.home() / ".reflekt/reflekt_profiles.yml"),
        show_default=True,
    )
    project.profiles_path = Path(profile_path).expanduser()

    if not project.profiles_path.suffix == ".yml":
        raise typer.BadParameter(
            f"Profile path must be a path to a YAML (.yml/.yaml) file. "
            f"'{project.profiles_path}' is not a YAML file."
        )

    profile_name = typer.prompt(
        "Profile name [identifies profile in 'reflekt_profiles.yml']",
        type=str,
    )

    project.default_profile = profile_name

    profile = Profile(project=project, from_reflekt_init=True)
    profile.path = project.profiles_path
    profile.name = profile_name
    profile.registry = [{}]
    profile.registry[0]["type"] = str.lower(
        typer.prompt(
            "Schema Registry [where event schemas are hosted]",
            type=click.Choice(REGISTRY, case_sensitive=False),
            show_choices=True,
        )
    )

    if profile.registry[0]["type"] == RegistryEnum.segment:
        profile.registry[0]["api_token"] = typer.prompt(
            "Segment API token [requires 'Tracking Plan Admin' access. Segment docs: "
            "https://bit.ly/segment-api-token]",
            type=str,
            hide_input=True,
        )
    elif profile.registry[0]["type"] == RegistryEnum.avo:
        profile.registry[0]["workspace_id"] = typer.prompt(
            "Avo workspace ID [see Avo docs: https://bit.ly/avo-workspace-id]",
            type=str,
        )
        profile.registry[0]["service_account_name"] = typer.prompt(
            "Avo service account name [Avo docs: https://bit.ly/avo-service-acct]",
            type=str,
        )
        profile.registry[0]["service_account_secret"] = typer.prompt(
            "Avo service account secret [Avo docs: https://bit.ly/avo-service-acct]",
            type=str,
            hide_input=True,
        )

    source_credentials = {}
    source_credentials["type"] = str.lower(
        typer.prompt(
            "Source type [where raw event data is stored]",
            type=click.Choice(WAREHOUSE),
            show_choices=True,
        )
    )
    source_credentials["id"] = str.lower(
        typer.prompt(
            "Source id [arbitrary ID for source in 'reflekt_profiles.yml']",
            type=str,
        )
    )

    if source_credentials["type"] == "snowflake":
        source_credentials["account"] = typer.prompt("account", type=str)
        source_credentials["database"] = typer.prompt("database", type=str)
        source_credentials["warehouse"] = typer.prompt("warehouse", type=str)
        source_credentials["role"] = typer.prompt("role", type=str)
        source_credentials["user"] = typer.prompt("user", type=str)
        source_credentials["password"] = typer.prompt(
            "password", type=str, hide_input=True
        )
        profile.source.append(source_credentials)
    elif source_credentials["type"] == "bigquery":
        source_credentials["method"] = typer.prompt("method", type=str)
        source_credentials["project"] = typer.prompt(
            "project (GCP project id)", type=str
        )
        profile.source.append(source_credentials)
    elif source_credentials["type"] == "redshift":
        source_credentials["database"] = typer.prompt("database", type=str)
        source_credentials["host_url"] = typer.prompt("host_url", type=str)
        source_credentials["port"] = typer.prompt("port", type=int)
        source_credentials["user"] = typer.prompt("user", type=str)
        source_credentials["password"] = typer.prompt(
            "password", type=str, hide_input=True
        )
        profile.source.append(source_credentials)

    # Create project directory, reflekt_project.yml, reflekt_profiles.yml, and README
    project_folders = pkg_resources.resource_filename(  # Get template folder
        "reflekt", "_templates/reflekt_project/"
    )

    shutil.copytree(  # Create Reflekt project directory
        project_folders,
        project.dir,
        dirs_exist_ok=True,
    )

    # Personalize project README with project name
    readme_file = project.dir / "README.md"

    with readme_file.open("r") as f:
        readme = f.read()

    readme = readme.replace("PROJECT_NAME", project.name)

    with readme_file.open("w") as f:
        f.write(readme)

    project.to_yaml()  # Create reflekt_project.yml
    profile.to_yaml()  # Create reflekt_profiles.yml

    # Success msg and get started table
    print("")
    logger.info(
        f"Created Reflekt project '{project.name}' "
        f"at {project.dir.resolve().expanduser()}!"
    )
    print("")
    logger.info("To get started, see the command descriptions below")

    # Table for getting started message
    table = Table(show_header=True, header_style="bold light_sea_green")
    table.add_column("Command", no_wrap=True)
    table.add_column("Description", no_wrap=True)
    table.add_column("Example", no_wrap=True)
    table.add_row(
        "init",
        "Initialize a Reflekt project",
        "reflekt init --dir ./in/this/dir",
    )
    table.add_row(
        "pull",
        "Pull schema(s) from a schema registry",
        "reflekt pull --select segment/ecommerce",
    )
    table.add_row(
        "push",
        "Push schema(s) to a schema registry",
        "reflekt push --select segment/ecommerce/CartViewed",
    )
    table.add_row(
        "lint",
        "Lint schemas against naming and metadata conventions in reflekt_project.yml",
        "reflekt lint --select segment/ecommerce/CartViewed/1-0",
    )
    table.add_row(
        "build",
        "Build data artifacts (e.g. dbt models) that match schemas in Reflekt project",
        "reflekt build dbt --select segment/ecommerce --sdk segment --source snowflake.raw.segment_prod",
    )
    console = Console()
    console.print(table)
    print("")

    if not profile.do_not_track:  # False by default
        user.initialize()
        track_event(
            user_id=user.id,
            event_name="Project Initialized",
            properties={
                "project_id": hashlib.md5(project.name.encode("utf-8")).hexdigest(),
                "profile_id": hashlib.md5(profile.name.encode("utf-8")).hexdigest(),
                "schema_registry": profile.registry[0]["type"],
                "data_warehouse": profile.source[0]["type"],
                "ci": os.getenv("CI") if os.getenv("CI") is True else False,
            },
            context=default_context,
        )


@app.command()
def debug():
    """Check Reflekt project configuration."""
    try:
        profile = Profile(project=project)

        if user.id is not None:
            track_event(
                user_id=user.id,
                event_name="Project Debugged",
                properties={
                    "project_id": hashlib.md5(project.name.encode("utf-8")).hexdigest(),
                    "profile_id": hashlib.md5(profile.name.encode("utf-8")).hexdigest(),
                    "ci": os.getenv("CI") if os.getenv("CI") is True else False,
                },
                context=default_context,
            )

    except Union[ValidationError, ProjectError, ProfileError] as e:
        raise e

    else:
        logger.info(
            "[green]Reflekt project and profiles are configured correctly![green/]"
        )


@app.command()
def pull(
    select: str = typer.Option(
        ..., "--select", "-s", help="Schema(s) to pull from schema registry."
    ),
    profile_name: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profile in reflekt_profiles.yml to use for schema registry connection.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Verbose logging for debugging."
    ),
):
    """Pull schema(s) from a schema registry."""
    configure_logging(verbose=verbose, project=project)
    profile = Profile(project=project, profile_name=profile_name)
    registry = RegistryHandler(select=select, profile=profile).get_registry()
    count_schemas = registry.pull(select=select)

    if user.id is not None:
        track_event(
            user_id=user.id,
            event_name="Schemas Pulled",
            properties={
                "project_id": hashlib.md5(project.name.encode("utf-8")).hexdigest(),
                "profile_id": hashlib.md5(profile.name.encode("utf-8")).hexdigest(),
                "schema_registry": registry.type,
                "count_schemas": count_schemas,
                "ci": os.getenv("CI") if os.getenv("CI") is True else False,
            },
            context=default_context,
        )


@app.command()
def push(
    select: str = typer.Option(
        ..., "--select", "-s", help="Schema(s) to push to schema registry."
    ),
    delete: bool = typer.Option(
        False,
        "--delete",
        "-d",
        help="Delete schema(s) from schema registry. Prompts for confirmation",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force command to run without confirmation."
    ),
    profile_name: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profile in reflekt_profiles.yml to use for schema registry connection.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose logging for debugging.",
    ),
):
    """Push schema(s) to a schema registry."""
    configure_logging(verbose=verbose, project=project)
    select = clean_select(select)
    profile = Profile(project=project, profile_name=profile_name)
    registry = RegistryHandler(select=select, profile=profile).get_registry()

    if registry.type == RegistryEnum.avo:
        raise SelectArgError(
            message=(
                "'reflekt push' is not supported for Avo. Use the Avo UI to define and "
                "manage your event schemas. Then you can run:\n"
                "    reflekt pull --select avo/main                                     # Pull schemas from Avo\n"  # noqa: E501
                "    reflekt build --artifact dbt --select avo/main --source db_schema  # Build dbt pkg"  # noqa: E501
            ),
            select=select,
        )

    if delete and not force:
        delete_confirmed = typer.confirm(
            f"Are you sure you want to delete the schema(s) selected by:\n"
            f"   --select {select}\n",
        )
        if delete_confirmed:
            count_schemas = registry.push(select=select, delete=delete)  # delete=True
    else:
        count_schemas = registry.push(select=select, delete=delete)

    if user.id is not None:
        track_event(
            user_id=user.id,
            event_name="Schemas Pushed",
            properties={
                "project_id": hashlib.md5(project.name.encode("utf-8")).hexdigest(),
                "profile_id": hashlib.md5(profile.name.encode("utf-8")).hexdigest(),
                "schema_registry": registry.type,
                "count_schemas": count_schemas,
                "ci": os.getenv("CI") if os.getenv("CI") is True else False,
            },
            context=default_context,
        )


@app.command()
def lint(
    select: str = typer.Option(..., "--select", "-s", help="Schema(s) to lint."),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose logging for debugging.",
    ),
):
    """Lint schema(s) to test for naming and metadata conventions."""
    configure_logging(verbose=verbose, project=project)
    errors = []
    schema_paths = []  # List of schema IDs (Paths) to pull
    select = clean_select(select)
    profile = Profile(project=project)
    select_path = project.dir / "schemas" / select
    logger.info(f"Searching for JSON schemas in: {str(select_path)}")
    print("")

    if select_path.is_dir():  # Get all schemas in directory
        for root, _, files in os.walk(select_path):
            for file in files:
                if file.endswith(".json"):
                    schema_paths.append(Path(root) / file)
    else:  # Get single schema file
        select_path = select_path.with_suffix(".json")
        if select_path.exists():
            schema_paths.append(select_path)

    logger.info(f"Found {len(schema_paths)} schema(s) to lint")
    print("")

    linter = Linter(project=project)

    for i, schema_path in enumerate(schema_paths, start=1):  # Get all Reflekt schemas
        logger.info(
            f"{i} of {len(schema_paths)} Linting [magenta]{schema_path}[magenta/]"
        )

        with schema_path.open("r") as f:
            r_schema = json.load(f)

        linter.lint_schema(r_schema, errors)  # If errors

    if errors:
        print("")
        logger.error(f"[red]Linting failed with {len(errors)} error(s):[/red]")
        print("")
        for error in errors:
            logger.error(error)
        raise typer.Exit(code=1)
    else:
        print("")
        logger.info("[green]Completed successfully[green/]")

    if user.id is not None:
        track_event(
            user_id=user.id,
            event_name="Schemas Linted",
            properties={
                "project_id": hashlib.md5(project.name.encode("utf-8")).hexdigest(),
                "profile_id": hashlib.md5(profile.name.encode("utf-8")).hexdigest(),
                "count_schemas": len(schema_paths),
                "count_errors": len(errors),
                "ci": os.getenv("CI") if os.getenv("CI") is True else False,
            },
            context=default_context,
        )


@app.command()
def build(
    artifact: ArtifactEnum = typer.Argument(
        ..., help="Type of data artifact to build."
    ),
    select: str = typer.Option(
        ..., "--select", "-s", help="Schema(s) to build data artifacts for."
    ),
    sdk: SdkEnum = typer.Option(
        ..., "--sdk", "-sdk", help="The SDK used to collect the event data."
    ),
    source: str = typer.Option(
        ...,
        "--source",
        "-t",
        help="Data source where the raw event data is stored. In the format `--source source_id.database.schema`, matching a configured source in reflekt_profiles.yml.",
    ),
    profile_name: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="Profile in reflekt_profiles.yml to use when connecting to the .",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose logging for debugging.",
    ),
):
    """Build data artifacts based on schemas."""
    select = clean_select(select)
    profile = Profile(project=project, profile_name=profile_name)
    builder = BuilderHandler(
        artifact_arg=artifact,
        select_arg=select,
        sdk_arg=sdk,
        source_arg=source,
        profile=profile,
    ).get_builder()
    builder.build()

    if user.id is not None:
        track_event(
            user_id=user.id,
            event_name="Artifact Built",
            properties={
                "project_id": hashlib.md5(project.name.encode("utf-8")).hexdigest(),
                "profile_id": hashlib.md5(profile.name.encode("utf-8")).hexdigest(),
                "data_artifact": artifact.value,
                "data_warehouse": builder.warehouse_type,
                "source_id": hashlib.md5(
                    builder.source_arg.encode("utf-8")
                ).hexdigest(),
                "count_schemas": len(builder.schema_paths),
                "sdk": sdk.value,
                "ci": os.getenv("CI") if os.getenv("CI") is True else False,
            },
            context=default_context,
        )


if __name__ == "__main__":
    main()  # Main entrypoint for CLI and sets global `project` variable
    # debug()
    init("~/repos/tmp/test_reflekt")
    # pull(select="segment/surfline-web")
    # push(select="segment/ecommerce", delete=False)
    # lint(select="segment/ecommerce/Cart_Viewed/1-0.json")
    # build(
    #     artifact="dbt",
    #     select="segment/ecommerce",
    #     source="snowflake.raw.ecomm_demo",
    #     sdk="segment",
    #     profile_name=None,  # Must have value when using Vscode debugger
    # )

    # build(
    #     artifact="dbt",
    #     select="segment/surfline-web/identify",
    #     source="snowflake.raw.surfline",
    #     sdk="segment",
    #     profile_name="wavetrak_segment",  # Must have value when using Vscode debugger
    # )
