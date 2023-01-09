# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa  -- Readability is more important than style here
import json
import os
import shutil
from pathlib import Path
from typing import Optional

import click
import pkg_resources
import typer
from loguru import logger
from rich import print
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.traceback import install

from reflekt import SHOW_LOCALS, __version__
from reflekt.builder.dbt import DbtBuilder
from reflekt.builder.handler import BuilderHandler
from reflekt.constants import (
    REGISTRY,
    WAREHOUSE,
    ArtifactEnum,
    RegistryEnum,
    SdkEnum,
)
from reflekt.errors import SelectArgError
from reflekt.linter import lint_schema
from reflekt.profile import Profile
from reflekt.project import Project
from reflekt.registry.handler import RegistryHandler


# Prettify traceback messages
app = typer.Typer(pretty_exceptions_show_locals=SHOW_LOCALS)  # Typer app
install(show_locals=SHOW_LOCALS)  # Any other uncaught exceptions


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


@app.command()
def init(
    dir: str = typer.Option(
        ".", "--dir", help="Directory where project will be initialized."
    )
) -> None:
    """Initialize a Reflekt project.

    Raises:
        SystemExit: A Reflekt project already exists in the directory.
    """
    project = Project(use_defaults=True)
    project.dir = Path(dir).expanduser()
    project.path = project.dir / "reflekt_project.yml"

    if project.path.exists():
        raise ExistingProjectError(
            project_path=project.path,
            message=f"Reflekt project configuration already defined at: {project.path}!",
        )

    project.name = typer.prompt("Project name [letters, digits, underscore]", type=str)
    project.vendor = typer.prompt("Schema vendor [e.g com.yourcompany]", type=str)

    if project.vendor == "":
        raise typer.BadParameter("Vendor cannot be empty string")

    profile_path = typer.prompt(
        "Path for 'reflekt_profiles.yml' [stores connection credentials].",
        type=str,
        default=str(Path.home() / ".reflekt/reflekt_profiles.yml"),
        show_default=True,
    )
    profile_name = typer.prompt(
        "Profile name [identifies profile in 'reflekt_profiles.yml']",
        type=str,
    )
    project.profiles_path = Path(profile_path)
    project.profile = profile_name

    profile = Profile(project=project)
    profile.path = Path(profile_path)
    profile.name = profile_name
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
    # elif profile.registry["type"] == "rudderstack_govern":
    #     pass
    # elif profile.registry["type"] == "snowplow_iglu":
    #     pass
    # elif profile.registry["type"] == "amplitude_data":
    #     pass

    target_credentials = {}
    target_credentials["type"] = str.lower(
        typer.prompt(
            "Target Data Warehouse [where raw event data is loaded]",
            type=click.Choice(WAREHOUSE),
            show_choices=True,
        )
    )
    target_credentials["name"] = str.lower(
        typer.prompt(
            "Target name [identifies target data warehouse in 'reflekt_profiles.yml']",
            type=str,
        )
    )

    if target_credentials["type"] == "snowflake":
        target_credentials["account"] = typer.prompt("account", type=str)
        target_credentials["database"] = typer.prompt("database", type=str)
        target_credentials["warehouse"] = typer.prompt("warehouse", type=str)
        target_credentials["role"] = typer.prompt("role", type=str)
        target_credentials["user"] = typer.prompt("user", type=str)
        target_credentials["password"] = typer.prompt(
            "password", type=str, hide_input=True
        )
        profile.target.append(target_credentials)
    elif target_credentials["type"] == "bigquery":
        target_credentials["method"] = typer.prompt("method", type=str)
        target_credentials["project"] = typer.prompt(
            "project (GCP project id)", type=str
        )
        profile.target.append(target_credentials)
    elif target_credentials["type"] == "redshift":
        target_credentials["database"] = typer.prompt("database", type=str)
        target_credentials["host_url"] = typer.prompt("host_url", type=str)
        target_credentials["port"] = typer.prompt("port", type=int)
        target_credentials["user"] = typer.prompt("user", type=str)
        target_credentials["password"] = typer.prompt(
            "password", type=str, hide_input=True
        )
        profile.target.append(target_credentials)

    project_folders = pkg_resources.resource_filename(  # Get template folder
        "reflekt", "_templates/reflekt_project/"
    )
    shutil.copytree(  # Create Reflekt project directory
        project_folders,
        project.dir,
        dirs_exist_ok=True,
    )

    # Personalize project README
    readme_file = project.dir / "README.md"
    with readme_file.open("r") as f:
        readme = f.read()
    readme = readme.replace("PROJECT_NAME", project.name)
    with readme_file.open("w") as f:
        f.write(readme)

    # Create reflekt_project.yml and reflekt_profiles.yml in project dir
    project.to_yaml()
    profile.to_yaml()

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
        "Initialize a Reflekt project.",
        "reflekt init --dir ./in/this/dir",
    )
    table.add_row(
        "pull",
        "Pull schemas from a schema registry.",
        "reflekt pull --select segment/ecommerce",
    )
    table.add_row(
        "push",
        "Push schemas to a schema registry.",
        "reflekt push --select segment/ecommerce/CartViewed",
    )
    table.add_row(
        "lint",
        "Lint schemas against naming and metadata conventions in reflekt_project.yml.",
        "reflekt lint --select segment/ecommerce/CartViewed/1-0",
    )
    table.add_row(
        "build",
        "Build dbt package modeling Segment event data stored at the specified target.",
        "reflekt build dbt --select segment/ecommerce --sdk segment --target snowflake.raw.segment_prod",
    )
    console = Console()
    console.print(table)
    print("")


@app.command()
def pull(
    select: str = typer.Option(
        ..., "--select", "-s", help="Schema(s) to pull from schema registry."
    )
):
    """Pull schema(s) from a schema registry."""
    project = Project()
    profile = Profile(project=project)
    registry = RegistryHandler(select=select, profile=profile).get_registry()
    registry.pull(select=select)


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
):
    """Push schema(s) to a schema registry."""
    select = clean_select(select)
    project = Project()
    profile = Profile(project=project)
    registry = RegistryHandler(select=select, profile=profile).get_registry()

    if registry.type == RegistryEnum.avo:
        raise SelectArgError(
            message=(
                "'reflekt push' is not supported for Avo. Use the Avo UI to define and "
                "manage your event schemas. Then you can run:\n"
                "    reflekt pull --select avo/main                                     # Pull schemas from Avo\n"  # noqa: E501
                "    reflekt build --artifact dbt --select avo/main --target db_schema  # Build dbt pkg"  # noqa: E501
            ),
            select=select,
        )

    if delete and not force:
        delete_confirmed = typer.confirm(
            f"Are you sure you want to delete the schema(s) selected by:\n"
            f"   --select {select}\n",
        )
        if delete_confirmed:
            registry.push(select=select, delete=delete)  # delete=True
    else:
        registry.push(select=select, delete=delete)


@app.command()
def lint(
    select: str = typer.Option(..., "--select", "-s", help="Schema(s) to lint."),
):
    """Lint schema(s) against schemas/.reflekt/meta/1-0.json and conventions in reflekt_project.yml."""
    errors = []
    schema_paths = []  # List of schema IDs (Paths) to pull
    select = clean_select(select)
    project = Project()
    select_path = project.dir / "schemas" / select
    logger.info(f"Searching for JSON schemas in: {str(select_path)}")
    print("")

    if select_path.is_dir():  # Get all schemas in directory
        for root, _, files in os.walk(select_path):
            for file in files:
                if file.endswith(".json"):
                    schema_paths.append(Path(root) / file)
    else:  # Get single schema file
        if select_path.exists():
            schema_paths.append(select_path)

    logger.info(f"Found {len(schema_paths)} schema(s) to lint")
    print("")

    for i, schema_path in enumerate(schema_paths, start=1):  # Get all Reflekt schemas
        with schema_path.open("r") as f:
            r_schema = json.load(f)

        logger.info(
            f"{i} of {len(schema_paths)} Linting [magenta]{schema_path}[magenta/]"
        )
        lint_schema(r_schema, errors)

    if errors:
        print("")
        logger.info(f"[red]Linting failed with {len(errors)} errors[/red]")
        raise typer.Exit(code=1)
    else:
        print("")
        logger.info("[green]Completed successfully[green/]")


@app.command()
def build(
    artifact: ArtifactEnum = typer.Argument(
        ..., help="Type of data artifact to build."
    ),
    select: str = typer.Option(
        ..., "--select", "-s", help="Schema(s) to build data artifacts for."
    ),
    sdk: SdkEnum = typer.Option(
        ..., "--sdk", "-sdk", help="The type of SDK that generated the data."
    ),
    target: str = typer.Option(
        ..., "--target", "-t", help="Schema in database where event data is loaded."
    ),
):
    """Build data artifact(s) based on schema(s)."""
    select = clean_select(select)
    project = Project()
    profile = Profile(project=project)
    builder = BuilderHandler(
        artifact=artifact,
        select=select,
        sdk=sdk,
        target=target,
    ).get_builder()
    builder.build()


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
    """CLI tool to develop, lint, validate, model, and document events using JSON schema."""
    project = Project()

    # Configure logging
    if not project.exists:
        logger.configure(
            handlers=[
                {
                    "sink": RichHandler(
                        rich_tracebacks=True,
                        markup=True,
                        show_path=False,
                        log_time_format="[%X]",
                        omit_repeated_times=False,
                        tracebacks_show_locals=SHOW_LOCALS,
                    ),
                    "format": "{message}",
                }
            ],
        )
    else:
        logger.configure(
            handlers=[
                {
                    "sink": RichHandler(
                        rich_tracebacks=True,
                        markup=True,
                        show_path=False,
                        log_time_format="[%X]",
                        omit_repeated_times=False,
                        tracebacks_show_locals=SHOW_LOCALS,
                    ),
                    "format": "{message}",
                },
                {
                    "sink": str(project.dir)
                    + "/.logs/reflekt_{time:YYYY-MM-DD_HH-mm-ss}.log",
                    "format": "{time:HH:mm:ss} | {level} | {message}",
                },
            ],
        )

    logger.info(f"Running with reflekt={__version__}")
    print("")


if __name__ == "__main__":
    # push(select="segment/ecommerce", delete=False)
    # lint(select="segment/ecommerce")

    # reflekt build dbt --select segment/ecommerce --sdk segment --target snowflake.raw.schema_name
    build(
        artifact="dbt",
        select="segment/ecommerce",
        sdk="segment",
        target="snowflake.raw.my_app_web",
    )
