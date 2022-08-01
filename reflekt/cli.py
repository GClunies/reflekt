# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import json
import shutil
import subprocess
from pathlib import Path

import click
import pkg_resources
import yaml
from inflection import dasherize, titleize
from loguru import logger
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from reflekt import constants
from reflekt.api_handler import ReflektApiHandler
from reflekt.avo.plan import AvoPlan
from reflekt.config import ReflektConfig
from reflekt.loader import ReflektLoader
from reflekt.logger import logger_config
from reflekt.project import ReflektProject
from reflekt.segment.plan import SegmentPlan
from reflekt.segment.schema import (  # TODO: Likely need a handler for these schema if build out Rudderstack & Snowplow  # noqa: E501
    segment_payload_schema,
    segment_plan_schema,
)
from reflekt.transformer import ReflektTransformer
from reflekt.utils import segment_2_snake


@click.group()
def cli():
    logger.configure(**logger_config)


@click.option(
    "--project-dir",
    "project_dir_str",
    # default=".",
    required=True,
    help="Path where Reflekt project will be created. Defaults to current directory.",
)
@click.command()
def init(project_dir_str: str) -> None:
    """Create a Reflekt project at the provide directory."""
    project_dir = Path(project_dir_str).resolve()
    project_name = click.prompt(
        "Enter your project name (letters, digits, underscore)", type=str
    )
    project_yml = project_dir / "reflekt_project.yml"
    readme_md = project_dir / "README.md"

    if project_yml.exists():
        with open(project_yml, "r") as f:
            reflekt_project_obj = yaml.safe_load(f)

        if reflekt_project_obj["name"] == project_name:
            logger.error(
                f"A Reflekt project named {project_name} already exists in "
                f"{Path.cwd()}"
            )
            raise click.Abort()

    reflekt_config_dir = click.prompt(
        "Enter path to the DIRECTORY where Reflekt will write your "
        "reflekt_config.yml to be use by this Reflekt project",
        type=str,
        default=str(Path.home() / ".reflekt"),
    )
    reflekt_config_dir = Path(reflekt_config_dir)
    reflekt_config_path = reflekt_config_dir / "reflekt_config.yml"
    reflekt_config_path = Path(reflekt_config_path)
    collect_config = True  # Default to collect config from user
    config_name = click.prompt(
        "Enter a config profile name for the reflekt_config.yml", type=str
    )

    if not reflekt_config_path.exists():
        if not reflekt_config_dir.exists():
            reflekt_config_dir.mkdir(parents=True)
        reflekt_config_path.touch()
        reflekt_config_obj = {
            config_name: {
                "plan_type": "",
                "cdp": "",
                "warehouse": {},
            }
        }
    else:
        with open(reflekt_config_path, "r") as f:
            reflekt_config_obj = yaml.safe_load(f)

        if config_name in reflekt_config_obj:
            logger.error(
                f"A Reflekt config profile named {config_name} already exists in "
                f"{reflekt_config_path}"
            )
            raise click.Abort()
        else:
            reflekt_config_obj.update(
                {
                    config_name: {
                        "plan_type": "",
                        "cdp": "",
                        "warehouse": {},
                    }
                }
            )

    if collect_config:
        plan_type_prompt = click.prompt(
            f"What Analytics Governance tool do you use to manage your tracking plan(s)?"
            f"{constants.PLAN_INIT_STRING}"
            f"\nEnter a number",
            type=int,
        )
        plan_type = constants.PLAN_MAP[str(plan_type_prompt)]
        reflekt_config_obj[config_name]["plan_type"] = plan_type

        if plan_type == "segment":
            # workspace_name and access_token required for Segment API use
            workspace_name = click.prompt(
                "Enter your Segment workspace name. You can find this in your Segment "
                "account URL (i.e. https://app.segment.com/your-workspace-name/)",
                type=str,
            )
            reflekt_config_obj[config_name]["workspace_name"] = workspace_name
            access_token = click.prompt(
                "Enter your Segment Config API access token (To generate a "
                "token, see Segment's documentation https://segment.com/docs/config-api/authentication/#create-an-access-token)",  # noqa: E501
                type=str,
                hide_input=True,
            )
            reflekt_config_obj[config_name]["access_token"] = access_token
        elif plan_type == "avo":
            avo_end_msg = (
                "You've selected Avo as your Analytics Governance tool which requires "
                "additional setup steps. Please see the docs for additional guidance:\n"
                "    https://reflekt-ci.notion.site/Connect-Reflekt-to-Avo-489158cf319f43c491470c54b37e3b13"  # noqa: E501
            )

        # TODO - Enable support for other CDPs below as developed
        # elif plan_type == "rudderstack":
        #     pass
        # elif plan_type == "snowplow":
        #     pass

        cdp_num_prompt = click.prompt(
            f"How do you collect first-party data?"
            f"{constants.CDP_INIT_STRING}"
            f"\nEnter a number",
            type=int,
        )
        cdp = constants.CDP_MAP[str(cdp_num_prompt)]
        reflekt_config_obj[config_name]["cdp"] = cdp
        warehouse_num = click.prompt(
            f"Which data warehouse do you use?"
            f"{constants.WAREHOUSE_INIT_STRING}"
            f"\nEnter a number",
            type=int,
        )
        warehouse = constants.WAREHOUSE_MAP[str(warehouse_num)]
        reflekt_config_obj[config_name]["warehouse"].update({warehouse: {}})

        if warehouse == "snowflake":
            account = click.prompt("account", type=str)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"account": account}
            )
            user = click.prompt("user", type=str)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"user": user}
            )
            password = click.prompt("password", hide_input=True, type=str)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"password": password}
            )
            role = click.prompt("role", type=str)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"role": role}
            )
            database = click.prompt(
                "database (where raw event data is stored)", type=str
            )
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"database": database}
            )
            snowflake_warehouse = click.prompt("warehouse", type=str)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"warehouse": snowflake_warehouse}
            )
        elif warehouse == "redshift":
            host_url = click.prompt(
                "host_url (hostname.region.redshift.amazonaws.com)", type=str
            )
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"host_url": host_url}
            )
            port = click.prompt("port", default=5439, type=int)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"port": port}
            )
            user = click.prompt("user", type=str)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"user": user}
            )
            password = click.prompt("password", hide_input=True, type=str)
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"password": password}
            )
            db_name = click.prompt(
                "db_name (database where raw event data is stored)",
                type=str,
            )
            reflekt_config_obj[config_name]["warehouse"][warehouse].update(
                {"db_name": db_name}
            )
        # TODO - Enable support for other warehouses below as developed
        # elif warehouse == "bigquery":
        #     pass

        with open(reflekt_config_path, "w") as f:
            yaml.dump(reflekt_config_obj, f, indent=2)

    click.echo(
        f"Configured to use Reflekt config profile '{config_name}' at "
        f"{reflekt_config_path}"
    )
    project_template_dir = pkg_resources.resource_filename(
        "reflekt", "templates/project/"
    )
    shutil.copytree(project_template_dir, project_dir, dirs_exist_ok=True)

    # Template reflekt_project.yml
    with open(project_yml, "r") as f:
        project_yml_str = f.read()

    project_yml_str = (
        project_yml_str.replace("default_project", project_name)
        .replace("default_profile", config_name)
        .replace(
            "# config_path: [directorypath]", f"config_path: {str(reflekt_config_path)}"
        )
    )

    with open(project_yml, "w") as f:
        f.write(project_yml_str)

    # Template Reflekt project README
    with open(readme_md, "r") as f:
        readme_md_str = f.read()

    readme_md_str = readme_md_str.replace("PROJECT_NAME", project_name).replace(
        "default_profile", config_name
    )

    with open(readme_md, "w") as f:
        f.write(readme_md_str)

    logger.info(
        f"Your Reflekt project '{project_name}' has been created!"
        f"\n\nWith reflekt, you can:\n\n"
        f"    reflekt new --name <plan-name>\n"
        f"        Create a new tracking plan, defined as code.\n\n"  # noqa: E501
        f"    reflekt pull --name <plan-name>\n"
        f"        Get tracking plan from Analytics Governance tool and convert it to code.\n\n"  # noqa: E501
        f"    reflekt push --name <plan-name>\n"
        f"        Sync tracking plan code to Analytics Governance tool. Reflekt handles conversion.\n\n"  # noqa: E501
        f"    reflekt test --name <plan-name>\n"
        f"        Test tracking plan code for naming and metadata conventions (defined in reflect_project.yml).\n\n"  # noqa: E501
        f"    reflekt dbt --name <plan-name>\n"
        f"        Template dbt package with sources, models, and docs for all events in tracking plan."  # noqa: E501
    )

    if plan_type == "avo":
        logger.info("")  # Terminal newline
        logger.info(avo_end_msg)


@click.command()
@click.option(
    "-n",
    "--name",
    "plan_name",
    required=True,
    help="Name of the tracking plan you want to create.",
)
def new(plan_name: str) -> None:
    """Create a new empty tracking plan using provided name."""
    plan_template_dir = pkg_resources.resource_filename("reflekt", "templates/plan/")
    plan_dir = ReflektProject().project_dir / "tracking-plans" / plan_name

    try:
        logger.info(f"Creating new tracking plan '{plan_name}' in '{plan_dir}'")
        shutil.copytree(plan_template_dir, plan_dir)
    except FileExistsError:
        logger.error(
            f"Tracking plan {plan_name} already exists! Please provide a "
            f"different name."
        )
        raise click.Abort()

    plan_yml_file = plan_dir / "plan.yml"

    with open(plan_yml_file, "r") as f:
        doc = yaml.safe_load(f)

    doc["name"] = plan_name

    with open(plan_yml_file, "w") as f:
        yaml.dump(doc, f)

    logger.info("")  # Terminal newline
    logger.success(f"Created Reflekt tracking plan '{plan_name}'")


@click.command()
@click.option(
    "-n",
    "--name",
    "plan_name",
    required=True,
    help="Tracking plan name in CDP or Analytics Governance tool.",
)
@click.option(
    "--raw",
    flag_value=True,
    help="Pull raw tracking plan JSON (not in Reflekt schema) from CDP.",
)
@click.option(
    "--avo-branch",
    "avo_branch",
    default=None,
    help=("Specify the branch name you want to pull your Avo tracking plan from."),
)
def pull(plan_name: str, raw: bool, avo_branch: str) -> None:
    """Generate tracking plan as code using the Reflekt schema."""
    api = ReflektApiHandler().get_api(avo_branch=avo_branch)
    config = ReflektConfig()
    logger.info(
        f"Searching {titleize(config.plan_type)} for tracking plan '{plan_name}'"
    )
    plan_json = api.get(plan_name)
    logger.info(f"Found tracking plan '{plan_name}'")

    if raw:
        logger.info(
            f"Displaying raw {titleize(config.plan_type)} tracking plan '{plan_name}'\n"
        )
        click.echo(json.dumps(plan_json, indent=2))
    else:
        plan_dir = ReflektProject().project_dir / "tracking-plans" / plan_name

        if api.type.lower() == "avo":
            plan = AvoPlan(plan_json, plan_name)
        elif api.type.lower() == "segment":
            plan = SegmentPlan(plan_json)
        # TODO: Add support for other tracking plan types
        # elif config.plan_type.lower() == "rudderstack":
        #     plan = RudderstackPlan(plan_json)
        # elif config.plan_type.lower() == "snowplow":
        #     plan = SnowplowPlan(plan_json)

        logger.info(f"Building Reflekt tracking plan '{plan_name}' at {plan_dir}")
        plan.build_reflekt(plan_dir)
        logger.info("")  # Terminal newline
        logger.success(f"Built Reflekt tracking plan '{plan_name}'")


@click.option(
    "-n",
    "--name",
    "plan_name",
    required=True,
    help="Tracking plan name in CDP or Analytics Governance tool.",
)
@click.option(
    "--dry",
    is_flag=True,
    required=False,
    help="Output JSON to be synced, without actually syncing it.",
)
@click.option(
    "-u",
    "--update",
    "updates",
    type=str,
    multiple=True,
    required=False,
    help=(
        "Update/add specified (using kebab-case) event, all user traits, or all "
        "group traits to a tracking plan. "
    ),
)
@click.option(
    "-r",
    "--remove",
    "removes",
    type=str,
    multiple=True,
    required=False,
    help=(
        "Remove specified (using kebab-case) event, all user traits, or all group "
        "traits from a tracking plan."
    ),
)
@click.command()
def push(plan_name, dry, updates, removes) -> None:
    """Sync tracking plan to CDP or Analytics Governance tool."""
    api = ReflektApiHandler().get_api()
    config = ReflektConfig()

    if api.type.lower() in ["avo"]:
        logger.error(f"'reflekt push' not supported for {titleize(api.type)}.")
        raise click.Abort()

    plan_dir = ReflektProject().project_dir / "tracking-plans" / plan_name

    # Check for incompatible arguments
    if updates != () and removes != ():
        logger.error("--update and --remove arguments cannot be combined!")
        raise SystemExit(1)

    if updates != ():
        # Determine what needs to be updated based on --update arg
        update_events = tuple(
            update for update in updates if update not in ("user-traits", "group-traits")
        )
        update_user_traits = tuple(
            update for update in updates if update == "user-traits"
        )
        update_group_traits = tuple(
            update for update in updates if update == "group-traits"
        )
        # Get the existing tracking plan that will be updated
        logger.warning(
            f"--update flag detected. Searching {titleize(config.plan_type)} for "
            f"existing tracking plan '{plan_name}'"
        )
        existing_plan_json = api.get(plan_name)  # Get the existing plan
        logger.info("")  # Terminal newline
        logger.info(f"Found existing tracking plan '{plan_name}'")

        # Load a Reflekt tracking, only including items from the --update arg
        logger.info("")  # Terminal newline
        logger.info(f"Updating tracking plan {plan_name}")
        loader = ReflektLoader(
            plan_dir=plan_dir,
            parse_all=False,
            events=update_events,
            user_traits=update_user_traits,
            group_traits=update_group_traits,
        )
        reflekt_plan = loader.plan
        transformer = ReflektTransformer(reflekt_plan)
        plan_updates_json = transformer.build_cdp_plan()
        sync_events = []  # Events to sync

        # For existing events - check if they need to be updated
        for existing_event in existing_plan_json["rules"]["events"]:
            match_found = False
            match_event = None
            for updated_event in plan_updates_json["tracking_plan"]["rules"]["events"]:
                # If updated event name+version matches existing event, use updated event
                if (
                    updated_event["name"] == existing_event["name"]
                    and updated_event["version"] == existing_event["version"]
                ):
                    match_found = True
                    match_event = updated_event

            if match_found:  # If match found, add updated event to sync list
                sync_events.append(match_event)
            else:  # If no match found, add existing event to sync list
                sync_events.append(existing_event)

        # For proposed events - check if they need to be added (not in existing events)
        for updated_event in plan_updates_json["tracking_plan"]["rules"]["events"]:
            match_found = False
            for existing_event in existing_plan_json["rules"]["events"]:
                # Check if updated event is already in existing events
                if (
                    updated_event["name"] == existing_event["name"]
                    and updated_event["version"] == existing_event["version"]
                ):
                    match_found = True

            if not match_found:  # Only ADD updated event if NOT found in existing events
                sync_events.append(updated_event)

        # Set the events to sync
        sync_plan_json = copy.deepcopy(plan_updates_json)
        sync_plan_json["tracking_plan"]["rules"]["events"] = sync_events
        cdp_plan = sync_plan_json

    elif removes != ():
        # Determine what needs to be removed based on --remvoe arg
        remove_events = tuple(
            remove
            for remove in removes
            if remove != "user-traits" or remove != "group-traits"
        )
        remove_user_traits = tuple(
            remove for remove in removes if remove == "user-traits"
        )
        remove_group_traits = tuple(
            remove for remove in removes if remove == "group-traits"
        )
        # Get the existing plan that will have events/traits removed
        remove_event_str = ", ".join("'" + event + "'" for event in remove_events)
        logger.warning(
            f"--remove flag detected. Removing event(s): {remove_event_str}, from "
            f"tracking plan {plan_name} in {titleize(config.plan_type)}"
        )
        existing_plan_json = api.get(plan_name)
        existing_events = existing_plan_json["rules"]["events"]
        sync_events = []  # Events to sync

        for existing_event in existing_events:
            if dasherize(segment_2_snake(existing_event["name"])) not in remove_events:
                sync_events.append(existing_event)

        cdp_plan = copy.deepcopy(segment_payload_schema)
        cdp_plan["tracking_plan"].update(segment_plan_schema)
        cdp_plan["tracking_plan"]["rules"]["events"] = sync_events

        if remove_user_traits != ():
            cdp_plan["tracking_plan"]["rules"]["identify"]["properties"]["traits"][
                "properties"
            ] = []

        if remove_group_traits != ():
            cdp_plan["tracking_plan"]["rules"]["group"]["properties"]["traits"][
                "properties"
            ] = []

    else:
        logger.info(f"Loading Reflekt tracking plan '{plan_name}'")

        # Load the plan using the ORIGINAL name
        loader = ReflektLoader(
            plan_dir=plan_dir,
        )
        reflekt_plan = loader.plan
        transformer = ReflektTransformer(reflekt_plan)
        plan_updates_json = transformer.build_cdp_plan()
        cdp_plan = plan_updates_json

    if dry:
        payload = api.sync(plan_name, cdp_plan, dry=True)
        logger.info("")  # Terminal newline
        logger.info(
            f"[DRY RUN] The following JSON would be sent to {transformer.plan_type}"
        )
        click.echo(json.dumps(payload, indent=2))
    else:
        logger.info("")  # Terminal newline
        logger.info(
            f"Syncing converted tracking plan '{plan_name}' to "
            f"{titleize(config.plan_type)}"
        )

        api.sync(plan_name, cdp_plan)
        logger.info("")  # Terminal newline
        logger.success(
            f"Synced Reflekt tracking plan '{plan_name}' to "
            f"{titleize(config.plan_type)}"
        )


@click.option(
    "-s",
    "--select",
    "selection",
    type=str,
    multiple=True,
    required=False,
    help="Selected event or traits to be tested (specified in kebab-case).",
)
@click.option(
    "-n",
    "--name",
    "plan_name",
    type=str,
    required=True,
    help="Name of tracking plan to be tested (specified in kebab-case).",
)
@click.command()
def test(plan_name, selection) -> None:
    """Test tracking plan schema for naming, data types, and metadata."""
    plan_dir = ReflektProject().project_dir / "tracking-plans" / plan_name
    logger.info(f"Testing Reflekt tracking plan '{plan_name}'")

    if selection != ():
        # Determine what needs to be updated based on --update arg
        selected_events = tuple(
            selected
            for selected in selection
            if selected not in ("user-traits", "group-traits")
        )
        selected_user_traits = tuple(
            selected for selected in selection if selected == "user-traits"
        )
        selected_group_traits = tuple(
            selected for selected in selection if selected == "group-traits"
        )

        # Initialize ReflektLoader() always runs checks. Simple, not elegant.
        ReflektLoader(
            plan_dir=plan_dir,
            parse_all=False,
            events=selected_events,
            user_traits=selected_user_traits,
            group_traits=selected_group_traits,
        )
    else:
        ReflektLoader(plan_dir=plan_dir)
    # If no errors are thrown, passed tests
    logger.info("")
    logger.success("Test complete. No errors.")


@click.option(
    "--tag",
    "force_tag",
    is_flag=True,
    required=False,
    help="The git tag Reflekt should add after templating. Tag format = 'v<semantic_version>__reflekt_<project_name>_<cdp>'",  # noqa: E501
)
@click.option(
    "--commit",
    "force_commit",
    is_flag=True,
    required=False,
    help="The git commit Reflekt should add after templating. Commit format = 'build: reflekt_<project_name>_<cdp>/models/<schema_or_alias>/'",  # noqa: E501
)
@click.option(
    "--skip-git",
    "skip_git",
    is_flag=True,
    required=False,
    help="Skip prompts at the end of templating to create Git commit and tag.",
)
@click.option(
    "--force-version",
    "force_version",
    type=str,
    required=False,
    help="Force Reflekt to template the dbt package with a specified semantic version.",
)
@click.option(
    "-s",
    "--schema",
    "schema",
    type=str,
    required=True,
    help=(
        "Schema Reflekt will search to look for raw event tables that match "
        "tracking plan events."
    ),
)
@click.option(
    "-e",
    "--event",
    "events",
    type=str,
    multiple=True,
    required=False,
    help="Name of a single event to be tested (in kebab-case).",
)
@click.option(
    "-n",
    "--name",
    "plan_name",
    type=str,
    required=True,
    help="Tracking plan name in your Reflekt project.",
)
@click.command()
def dbt(
    plan_name,
    events,
    schema,
    force_version=None,
    skip_git=None,
    force_commit=None,
    force_tag=None,
) -> None:
    """Build dbt package with sources, models, and docs based on tracking plan."""
    project = ReflektProject()
    project_name = project.name
    project_dir = project.project_dir
    config = ReflektConfig()
    cdp = config.cdp_name
    plan_type = str.lower(config.plan_type)
    plan_dir = project_dir / "tracking-plans" / plan_name
    pkg_name = f"reflekt_{project_name}_{cdp}"
    project_dir / "dbt-packages" / pkg_name
    dbt_project_yml = project.project_dir / "dbt_project.yml"
    config.warehouse_type

    # Determine dbt pkg version to pass to ReflektTransformer
    if force_version:  # If user has forced version, use that
        try:
            version = parse_version(force_version)
        except InvalidVersion:
            logger.error(
                f"[ERROR] Invalid semantic version provided by --force-version: "
                f"{force_version}"
            )
            raise click.Abort()
    # If we don't find a dbt_project.yml -> package does not exist -> v0.1.0
    elif not dbt_project_yml.exists():
        version = parse_version("0.1.0")
    else:  # Package already exists!
        with dbt_project_yml.open() as f:
            dbt_project_yml = yaml.safe_load(f)

        existing_version = parse_version(dbt_project_yml["version"])

        if existing_version:
            logger.info(
                f"[WARNING] Existing dbt package found:\n"
                f"    Package name: {pkg_name}\n"
                f"    Existing version: {existing_version}\n"
            )

        bump = click.confirm(
            "Do you want to bump dbt package version?",
            default=True,
        )
        major_bump = f"{existing_version.major + 1}.{existing_version.minor}.{existing_version.micro}"  # noqa: E501
        minor_bump = f"{existing_version.major}.{existing_version.minor + 1}.{existing_version.micro}"  # noqa: E501
        patch_bump = f"{existing_version.major}.{existing_version.minor}.{existing_version.micro + 1}"  # noqa: E501

        if bump:
            bump_type = click.prompt(
                f"Select the semantic version you would like to bump to:\n"
                f"[1] Major: v{major_bump}\n"
                f"[2] Minor: v{minor_bump}\n"
                f"[3] Patch: v{patch_bump}\n"
                f"\nEnter a number",
                type=int,
            )

            if bump_type == 1:
                version = parse_version(f"{major_bump}")  # noqa: E501
            elif bump_type == 2:
                version = parse_version(f"{minor_bump}")  # noqa: E501
            else:
                version = parse_version(f"{patch_bump}")  # noqa: E501

        else:
            overwrite = click.confirm(
                f"[WARNING] Reflekt will UPSERT dbt models and docs in dbt package '{pkg_name}'.\n"  # noqa: E501
                f"    Do you want to continue?",
                default=False,
            )

            if not overwrite:
                raise click.Abort()

            logger.info("")  # Terminal newline
            version = existing_version

    # Load Reflekt plan from 'tracking-plans/'
    logger.info(f"Loading Reflekt tracking plan {plan_name}")
    loader = ReflektLoader(
        plan_dir=plan_dir,
        schema_name=schema,
        events=events,
    )
    reflekt_plan = loader.plan
    logger.info(f"Loaded Reflekt tracking plan {plan_name}\n")

    models_subfolder: str = (
        reflekt_plan.schema_alias
        if reflekt_plan.schema_alias is not None
        else reflekt_plan.schema
    )

    transformer = ReflektTransformer(
        reflekt_plan=reflekt_plan,
        models_subfolder=models_subfolder,
        dbt_package_version=version,
    )
    transformer.build_dbt_package()

    if not skip_git:
        if force_commit:
            commit_str = f"build: {pkg_name}/models/{models_subfolder}/"
        else:
            create_commit = click.confirm(
                "Would you like Reflekt to create a Git commit after templating?",
                default=False,
            )
            if create_commit:
                commit_str = click.prompt(
                    "Git commit message",
                    type=str,
                    default=f"build: {pkg_name}/models/{models_subfolder}/",
                )
            else:
                commit_str = None

        if force_tag:
            tag_str = f"v{str(version)}__{pkg_name}"
        else:
            create_tag = click.confirm(
                f"Would you like Reflekt to create a Git tag to easily reference "
                f"dbt package {pkg_name} in your dbt project?",
                default=False,
            )
            if create_tag:
                tag_str = click.prompt(
                    "Git tag",
                    type=str,
                    default=f"v{str(version)}__{pkg_name}",
                )
            else:
                tag_str = None

        git_executable = shutil.which("git")
        rel_pkg_path = f"dbt-packages/{pkg_name}"

        if commit_str is not None:
            if plan_type == "avo":
                rel_avo_json_path = ".reflekt/avo/avo.json"
                subprocess.call(
                    args=[
                        git_executable,
                        "add",
                        rel_pkg_path,
                        rel_avo_json_path,
                    ],
                    cwd=project_dir,
                )
            else:
                subprocess.call(
                    args=[
                        git_executable,
                        "add",
                        rel_pkg_path,
                    ],
                    cwd=project_dir,
                )

            subprocess.call(
                args=[
                    git_executable,
                    "commit",
                    "-m",
                    commit_str,
                ],
                cwd=project_dir,
            )

        if tag_str is not None:
            subprocess.call(
                args=[
                    git_executable,
                    "tag",
                    tag_str,
                ],
                cwd=project_dir,
            )


# Add CLI commands to CLI group
cli.add_command(init)
cli.add_command(new)
cli.add_command(pull)
cli.add_command(push)
cli.add_command(test)
cli.add_command(dbt)


# Used for CLI debugging
if __name__ == "__main__":

    # ----- GENERAL -----
    # init(["--project-dir", "~/Repos/test-repo"])
    # new(["--project-dir", "my-new-plan"])

    # ----- AVO -----
    # pull(["-n", "my-avo-plan"])
    # pull(["-n", "my-avo-plan"], "--raw")
    # pull(["-n", "my-avo-plan", "--avo-branch", "staging"])

    # ----- SEGMENT -----
    # pull(["-n", "my-segment-plan"])
    # pull(["-n", "my-segment-plan"], "--raw")
    # push(["-n", "my-segment-plan"])
    # push(["-n", "my-segment-plan", "--dry"])
    # push(["-n", "my-segment-plan", "-u", "new-event"])
    # push(["-n", "my-segment-plan", "-r", "new-event"])
    push(["-n", "test-plan", "-u", "user-traits"])

    # ----- REFLEKT -----
    # test(["-n", "my-segment-plan"])
    # test(["-n", "my-segment-plan", "-e", "order-completed"])

    # dbt(["-n", "my-segment-plan"])
    # dbt(["-n", "my-segment-plan", "-e", "order-completed")]
    # dbt(["-n", "my-segment-plan", "-e", "user-traits"])
    # dbt(["-n", "my-segment-plan", "-e", "group-traits"])
