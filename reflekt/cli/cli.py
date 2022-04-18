# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
from pathlib import Path

import click
import pkg_resources
import yaml
from inflection import titleize, underscore
from loguru import logger
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from reflekt.avo.plan import AvoPlan
from reflekt.cli.handler import ReflektApiHandler
from reflekt.logger import logger_config
from reflekt.reflekt import constants
from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.loader import ReflektLoader
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.transformer import ReflektTransformer
from reflekt.segment.plan import SegmentPlan


@click.group()
def cli():
    logger.configure(**logger_config)


@click.command()
@click.option(
    "--name",
    "plan_name",
    required=True,
    help="Name of the tracking plan you want to create.",
)
@click.option(
    "--plans-dir",
    "plans_dir",
    required=False,
    default=ReflektProject().project_dir / "tracking-plans",
    help=(
        "Path where tracking plan will be generated. Defaults to "
        "`/tracking-plans` directory in your reflekt project."
    ),
)
def new(plan_name, plans_dir):
    """Create a new empty tracking plan using provided name."""
    plan_template_dir = pkg_resources.resource_filename("reflekt", "template/plan/")

    if plans_dir != ReflektProject().project_dir / "tracking-plans":
        plan_dir = Path(plans_dir) / plan_name

    try:
        logger.info(f"Creating new tracking plan `{plan_name}` in `{plan_dir}`")
        shutil.copytree(plan_template_dir, plan_dir)
    except FileExistsError:
        logger.error(
            f"Tracking plan {plan_name} already exists! Please provide a "
            f"different name."
        )
        raise click.Abort()

    plan_yml_file = plan_dir / "plan.yml"

    with open(plan_yml_file, "w") as f:
        doc = yaml.safe_load(f)

    doc["display_name"] = plan_name

    with open(plan_yml_file, "w") as f:
        yaml.dump(doc, f)

    logger.info(f"Tracking plan `{plan_name}` created successfully!")


@click.command()
@click.option(
    "--name",
    "plan_name",
    required=True,
    help="Tracking plan name in CDP or Analytics Governance tool.",
)
@click.option(
    "--plans-dir",
    "plans_dir",
    required=False,
    default=ReflektProject().project_dir / "tracking-plans",
    help=(
        "Path where tracking plan will be generated. Defaults to `/tracking-plans` "
        "directory in your reflekt project."
    ),
)
@click.option(
    "--raw",
    flag_value=True,
    help="Pull raw tracking plan JSON (not in reflekt schema) from CDP. ",
)
def pull(plan_name, plans_dir, raw):
    """Generate tracking plan as code using the reflekt schema."""
    api = ReflektApiHandler().get_api()
    config = ReflektConfig()
    logger.info(
        f"Fetching tracking plan `{plan_name}` from {titleize(config.plan_type)}"
    )
    plan_json = api.get(plan_name)

    if raw:
        logger.info(
            f"Fetched raw tracking plan `{plan_name}` from "
            f"{titleize(config.plan_type)}\n"
        )
        click.echo(json.dumps(plan_json, indent=2))
    else:
        logger.info(
            f"Fetched tracking plan `{plan_name}` from {titleize(config.plan_type)}"
        )
        if plans_dir != ReflektProject().project_dir / "tracking-plans":
            plan_dir = Path(plans_dir) / plan_name

        if api.type.lower() == "avo":
            plan = AvoPlan(plan_json, plan_name)
        elif api.type.lower() == "segment":
            plan = SegmentPlan(plan_json)
        # TODO: Add support for other tracking plan types
        # elif config.plan_type.lower() == "iteratively":
        #     plan = IterativelyPlan(plan_json)
        # elif config.plan_type.lower() == "rudderstack":
        #     plan = RudderstackPlan(plan_json)
        # elif config.plan_type.lower() == "snowplow":
        #     plan = SnowplowPlan(plan_json)

        logger.info(
            f"Building {titleize(config.plan_type)} tracking plan "
            f"`{plan_name}` in reflekt specification at {plan_dir}"
        )
        plan.build_reflekt(plan_dir)
        logger.info(
            f"SUCCESS - Tracking plan `{plan_name}` built in reflekt "
            f"specification at {str(plan_dir)}"
        )


@click.command()
@click.option(
    "--name",
    "plan_name",
    required=True,
    help="Tracking plan name in CDP or Analytics Governance tool.",
)
@click.option(
    "--plans-dir",
    "plans_dir",
    required=False,
    default=ReflektProject().project_dir / "tracking-plans",
    help=(
        "Path to the directory containing the tracking plan folder. Defaults "
        "to `/tracking-plans` directory in your reflekt project."
    ),
)
@click.option(
    "--dry",
    is_flag=True,
    help="Output JSON to be synced, without actually syncing it.",
)
def push(plan_name, plans_dir, dry):
    """Sync tracking plan to CDP or Analytics Governance tool."""
    api = ReflektApiHandler().get_api()
    if api.type.lower() in ["avo", "iteratively"]:
        logger.error(f"`reflekt push` not supported for {titleize(api.type)}.")
        raise click.Abort()

    if plans_dir != ReflektProject().project_dir / "tracking-plans":
        plan_dir = Path(plans_dir) / plan_name

    logger.info(f"Loading tracking plan {plan_name} at {str(plan_dir)}")
    loader = ReflektLoader(plan_dir=plan_dir, plan_name=plan_name)
    reflekt_plan = loader.plan
    logger.info(f"Loaded tracking plan {plan_name}\n")
    transformer = ReflektTransformer(reflekt_plan)
    cdp_plan = transformer.build_cdp_plan()

    if dry:
        payload = api.sync(plan_name, cdp_plan, dry=True)
        logger.info(
            f"DRY RUN MODE. The following JSON would be sent to "
            f"{transformer.plan_type}"
        )
        click.echo(json.dumps(payload, indent=2))
    else:
        logger.info(f"Syncing tracking plan {plan_name} to {transformer.plan_type}.")
        api.sync(plan_name, cdp_plan)
        logger.info(
            f"DONE. Synced tracking plan {plan_name} to " f"{transformer.plan_type}."
        )


@click.command()
@click.option(
    "--name",
    "plan_name",
    required=True,
    help="Tracking plan name in CDP or Analytics Governance tool.",
)
@click.option(
    "--plans-dir",
    "plans_dir",
    required=False,
    default=ReflektProject().project_dir / "tracking-plans",
    help=(
        "Path to the directory containing the tracking plan folder. Defaults "
        "to `/tracking-plans` directory in your reflekt project."
    ),
)
def test(plan_name, plans_dir):
    """Test tracking plan schema for naming, data types, and metadata."""
    if plans_dir != ReflektProject().project_dir / "tracking-plans":
        plan_dir = Path(plans_dir) / plan_name

    logger.info(f"Testing tracking plan {plan_name} at {str(plan_dir)}")
    loader = ReflektLoader(
        plan_dir=plan_dir,
        plan_name=plan_name,
        raise_validation_errors=False,  # Raise errors after tests run (if any)
    )

    if loader.has_validation_errors:
        for error in loader.validation_errors:
            click.echo(error, err=True)
        raise click.Abort()
    else:
        logger.info(f"PASSED - no errors detected in tracking plan `{plan_name}`")


@click.option(
    "--name",
    "plan_name",
    required=True,
    help="Tracking plan name in your reflekt project.",
)
@click.option(
    "--plans-dir",
    "plans_dir",
    required=False,
    default=ReflektProject().project_dir / "tracking-plans",
    help=(
        "Path to the directory containing the tracking plan folder. Defaults "
        "to the `tracking-plans/` directory in your reflekt project."
    ),
)
@click.option(
    "--dbt-dir",
    "dbt_dir",
    required=False,
    default=ReflektProject().project_dir / "dbt_packages",
    help=(
        "Path to directory where dbt package will be built. Defaults to the "
        "`dbt_packages/` directory in your reflekt project."
    ),
)
@click.option(
    "--force-version",
    "force_version_str",
    required=False,
    default=None,
    help=(
        "Force reflekt to build or overwrite the dbt package with a specific "
        "semantic version."
    ),
)
@click.command()
def dbt(plan_name, plans_dir, dbt_dir, force_version_str):
    """Build dbt package with sources, models, and docs based on tracking plan."""
    if plans_dir != ReflektProject().project_dir / "tracking-plans":
        plan_dir = Path(plans_dir).resolve() / plan_name

    if dbt_dir != ReflektProject().project_dir / "dbt_packages":
        dbt_pkg_dir = Path(dbt_dir).resolve()

    if force_version_str is not None:
        try:
            version = parse_version(force_version_str)
            overwrite = True
        except InvalidVersion:
            logger.error(
                f"[ERROR] Invalid semantic version provided: {force_version_str}"
            )
            raise click.Abort()

    else:
        dbt_project_yml_path = (
            dbt_pkg_dir / f"reflekt_{underscore(plan_name)}" / "dbt_project.yml"
        )
        if not dbt_project_yml_path.exists():
            version = parse_version("0.1.0")
        else:
            with dbt_project_yml_path.open() as f:
                dbt_project_yml_path = yaml.safe_load(f)

            dbt_pkg_version = parse_version(dbt_project_yml_path["version"])
            new_version_str = (
                f"{dbt_pkg_version.major}."
                f"{dbt_pkg_version.minor + 1}."
                f"{dbt_pkg_version.micro}"
            )
            new_dbt_pkg_version = parse_version(new_version_str)
            bump = click.confirm(
                f"[WARNING] dbt package `reflekt_{underscore(plan_name)}` already exists with version {dbt_pkg_version}.\n"  # noqa: E501
                f"    Do you want to bump `reflekt_{underscore(plan_name)}` to version {new_dbt_pkg_version} and overwrite?",  # noqa: E501
                default=True,
            )

            if bump:
                version = new_dbt_pkg_version
            else:
                overwrite = click.confirm(
                    f"[WARNING] reflekt will overwrite dbt package `reflekt_{underscore(plan_name)}` with version {dbt_pkg_version}.\n"  # noqa: E501
                    f"    Do you want to continue?",
                    default=False,
                )
                if not overwrite:
                    raise click.Abort()
                version = dbt_pkg_version

    logger.info(f"Loading reflekt tracking plan {plan_name} at {str(plan_dir)}")
    loader = ReflektLoader(plan_dir=plan_dir, plan_name=plan_name)
    reflekt_plan = loader.plan
    logger.info(f"Loaded reflekt tracking plan {plan_name}\n")
    transformer = ReflektTransformer(reflekt_plan, dbt_pkg_dir, pkg_version=version)
    transformer.build_dbt_package()


@click.option(
    "--project-dir",
    "project_dir_str",
    default=".",
    help="Path where reflekt project will be created. Defaults to current directory.",
)
@click.command()
def init(project_dir_str):
    """Create a reflekt project at the provide directory."""

    # TODO - update all this logic to match the format in ~/.reflekt/reflekt_config.yml

    project_dir = Path(project_dir_str).resolve()
    project_name = click.prompt(
        "Enter your project name (letters, digits, underscore)", type=str
    )
    project_yml = project_dir / "reflekt_project.yml"
    if project_yml.exists():
        with open(project_yml, "r") as f:
            reflekt_project_obj = yaml.safe_load(f)

        if reflekt_project_obj["name"] == project_name:
            logger.error(
                f"A reflekt project named {project_name} already exists in "
                f"{Path.cwd()}"
            )
            raise click.Abort()

    reflekt_config_path = click.prompt(
        "Enter the absolute path where reflekt_config.yml will be created for "
        "use by this reflekt project",
        type=str,
        default=str(Path.home() / ".reflekt" / "reflekt_config.yml"),
    )
    reflekt_config_path = Path(reflekt_config_path)
    collect_config = True  # Default to collect config from user
    config_name = click.prompt(
        "Enter a config profile name for the reflekt_config.yml", type=str
    )

    if not reflekt_config_path.exists():
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
                f"A reflekt config profile named {config_name} already exists in "
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
            f"What tool do you use to manage your tracking plan(s)?"
            f"{constants.PLAN_INIT_STRING}"
            f"\nEnter a number",
            type=int,
        )
        plan_type = constants.PLAN_MAP[str(plan_type_prompt)]
        reflekt_config_obj[config_name]["plan_type"] = plan_type
        cdp_num_prompt = click.prompt(
            f"Which CDP or Analytics Governance tool do you use?"
            f"{constants.CDP_INIT_STRING}"
            f"\nEnter a number",
            type=int,
        )
        cdp = constants.CDP_MAP[str(cdp_num_prompt)]
        reflekt_config_obj[config_name]["cdp"] = cdp

        if cdp == "segment":
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
        # TODO - Enable support for other CDPs below as developed
        # elif cdp == "rudderstack":
        #     pass
        # elif cdp == "snowplow":
        #     pass
        # elif cdp == "avo":
        #     pass
        # elif cdp == "iteratively":
        #     pass

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
        f"Configured to use reflekt config profile '{config_name}' at "
        f"{reflekt_config_path}."
    )
    project_template_dir = pkg_resources.resource_filename(
        "reflekt", "template/project/"
    )
    shutil.copytree(project_template_dir, project_dir, dirs_exist_ok=True)

    with open(project_yml, "r") as f:
        project_yml_str = f.read()

    project_yml_str = project_yml_str.replace("default_project", project_name).replace(
        "default_profile", config_name
    )

    with open(project_yml, "w") as f:
        f.write(project_yml_str)

    logger.info(
        f"Your reflekt project '{project_name}' has been created!"
        f"\n\nWith reflekt, you can:\n\n"
        f"    reflekt new --name <plan-name>\n"
        f"        Create a new tracking plan in reflekt spec (with example YAML files to spec events, user traits, and group traits)\n\n"  # noqa: E501
        f"    reflekt pull --name <plan-name>\n"
        f"        Get tracking plan from CDP or Analytics Governance tool and convert it to reflekt spec\n\n"  # noqa: E501
        f"    reflekt push --name <plan-name>\n"
        f"        Push reflekt tracking plan to your CDP or Analytics Governance tool. reflekt handles the conversion!\n\n"  # noqa: E501
        f"    reflekt test --name <plan-name>\n"
        f"        Test reflekt tracking plan for naming conventions and expected metadata defined in your reflect_project.yml\n\n"  # noqa: E501
        f"    reflekt dbt --name <plan-name>\n"
        f"        Build a dbt package with sources/models/documentation that *reflekt* the events in your tracking plan!"  # noqa: E501
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
    # Call CLI command here with arguments as a list
    # init(["--project-dir", "/Users/gclunies/Repos/patty-bar-reflekt"])
    # new(["--project-dir", "test-plan"])
    # pull(["--name", "tracking-plan-example"])
    # push(["--name", "tracking-plan-example"])
    # test(["--name", "tracking-plan-example"])
    # pull(["--name", "patty-bar-dev-avo"])
    # push(["--name", "patty-bar-dev-avo"])
    # test(["--name", "patty-bar-dev-avo"])
    dbt(["--name", "patty-bar-prod-avo"])
