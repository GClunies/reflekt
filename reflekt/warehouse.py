# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Tuple

import sqlalchemy
from snowflake.sqlalchemy import URL as snow_url
from sqlalchemy.engine.url import URL as redshift_url

from reflekt.errors import TargetArgError
from reflekt.profile import Profile
from reflekt.project import Project


class Warehouse:
    """Handles connection to data warehouse based on --target argument."""

    def __init__(self, target: str) -> None:
        """Initialize DataWarehouse class.

        Args:
            target (str): The --target argument passed to Reflekt CLI.
        """
        self._target = target
        self._profile = Profile(project=Project())
        self.credentials: Optional[dict] = None
        self._get_warehouse_connection(target)

    def _get_warehouse_connection(self, target: str) -> None:
        """Get target argument.

        Args:
            target (str): The --target argument passed to Reflekt CLI.

        Raises:
            TargetArgError: Raised when an invalid --target argument is provided.
        """
        self._match_found = False
        self.target_name = self._target.split(".")[0]
        self.database = self._target.split(".")[1]
        self.schema = self._target.split(".")[2]

        for profile_target in self._profile.target:
            if self.target_name == profile_target["name"]:
                self._match_found = True
                self.type = profile_target["type"]
                self.credentials = profile_target

        if not self._match_found:
            raise TargetArgError(
                message=(
                    f"Invalid argument '--target {self._target}'. Target name "
                    f"'{self.target_name}' does not match a 'target:' configuration in "
                    f"{self._profile.path}. Target argument must follow the format: "
                    f"<target_name>.<database>.<schema>\n"
                ),
                target=self._target,
            )

        if self.type == "snowflake":
            self.engine = sqlalchemy.create_engine(
                snow_url(
                    account=self.credentials.get("account"),
                    database=self.credentials.get("database"),
                    warehouse=self.credentials.get("warehouse"),
                    role=self.credentials.get("role"),
                    user=self.credentials.get("user"),
                    password=self.credentials.get("password"),
                )
            )
        elif self.type == "redshift":
            self.engine = sqlalchemy.create_engine(
                redshift_url.create(
                    drivername="redshift+redshift_connector",
                    host=self.credentials.get("host_url"),
                    port=self.credentials.get("port"),
                    database=self.credentials.get("db_name"),
                    username=self.credentials.get("user"),
                    password=self.credentials.get("password"),
                ),
                connect_args={
                    "sslmode": "prefer",
                },
            )
        # elif self.type == "bigquery":
        #     pass

    def get_columns(self, table: str) -> Tuple[Optional[list], Optional[str]]:
        """Get column names for a table.

        Args:
            table (str): Table name.

        Returns:
            List[str]: List of column names.
        """
        with self.engine.connect() as conn:
            try:
                # Get columns. Columns that are ALL null are not included in result
                query = conn.execute(f"select * from {self.schema}.{table} limit 0")
                columns = query.keys()._keys
                error_msg = None

            except sqlalchemy.exc.ProgrammingError as e:
                columns = None

                if self.type == "snowflake":  # Handle error according to warehouse type
                    error_msg = e.orig.msg
                elif self.type == "redshift":
                    error_msg = e.orig.args[0]["M"]

            return columns, error_msg
