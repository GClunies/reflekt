# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Tuple

import sqlalchemy
from snowflake.sqlalchemy import URL as snow_url
from sqlalchemy.engine.url import URL as redshift_url

from reflekt.errors import SourceArgError
from reflekt.profile import Profile


class Warehouse:
    """Handles connection to data warehouse based on --source argument."""

    def __init__(self, source_arg: str, profile: Profile) -> None:
        """Initialize DataWarehouse class.

        Args:
            source_arg (str): The --source argument passed to Reflekt CLI.
            profile (Profile): Reflekt Profile object.
        """
        self._source_arg = source_arg
        self._profile = profile
        self.credentials: Optional[dict] = None
        self._create_warehouse_engine()

    def _create_warehouse_engine(self) -> None:
        """Create warehouse engine based on --source argument and 'source:' in profile.

        Raises:
            SourceArgError: Raised when an invalid --source argument is provided.
        """
        # Parse source argument
        self.source_id = self._source_arg.split(".")[0]
        self.database = self._source_arg.split(".")[1]
        self.schema = self._source_arg.split(".")[2]
        self._source_found = False  # Flag to check if source argument matches a profile

        # Search profile in reflekt_profiles.yml for id. If found, set credentials.
        for profile_source in self._profile.source:
            if self.source_id == profile_source["id"]:
                self.type = profile_source["type"]
                self._source_found = True
                self.credentials = profile_source

        if not self._source_found:  # Raise error if no match found
            raise SourceArgError(
                message=(
                    f"Invalid argument '--source {self._source_arg}'. source id "
                    f"'{self.source_id}' does not match a 'source:' configuration in "
                    f"{self._profile.path}. source argument must follow the format: "
                    f"<source_type>.<database>.<schema>\n"
                ),
                source=self._source_arg,
            )

        # Connect to the data warehouse based on source type
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
                    host=self.credentials.get("host"),
                    port=self.credentials.get("port"),
                    database=self.credentials.get("database"),
                    username=self.credentials.get("user"),
                    password=self.credentials.get("password"),
                ),
                connect_args={
                    "sslmode": "prefer",
                },
            )
        # elif self.type == "bigquery":  # TODO: Add BigQuery support later
        #     pass

    def find_columns(
        self, table_name: str, columns_to_search: list[dict]
    ) -> Tuple[list, Optional[str]]:
        """For a given dict of columns, find matching columns in table in the DWH.

        Args:
            table_name (str): Table name in the data warehouse.
            columns_to_search (list[dict]): List of dictionaries that contain column
                names and descriptions. The column names are used to search for columns
                in the table.

        Returns:
            Tuple[list, Optional[str]]: List of columns that were found in
                the table and error message.
        """
        # Set default values
        found_columns = []
        error_msg = None

        # Search for columns in table
        with self.engine.connect() as conn:
            try:
                query = conn.execute(
                    f"select * from {self.schema}.{table_name} limit 0"
                )
                table_columns = query.keys()._keys
                found_columns = [
                    search_column
                    for search_column in columns_to_search
                    if search_column["name"] in table_columns
                ]

            except sqlalchemy.exc.ProgrammingError as e:
                if self.type == "snowflake":
                    error_msg = e.orig.msg
                elif self.type == "redshift":
                    error_msg = e.orig.args[0]["M"]

            return found_columns, error_msg
