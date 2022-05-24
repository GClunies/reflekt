# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional, Tuple

import sqlalchemy
from snowflake.sqlalchemy import URL as snow_url
from sqlalchemy.engine.url import URL as redshift_url

from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.errors import ReflektConfigError


class WarehouseConnection:
    """Class that handles connection to the data warehouse specified in
    reflekt_config.yml
    """

    def __init__(self) -> None:
        self._config = ReflektConfig()
        self.warehouse = self._config.warehouse
        self.warehouse_type = self._config.warehouse_type

        if self.warehouse_type == "redshift":
            self.engine = sqlalchemy.create_engine(
                redshift_url.create(
                    drivername="redshift+redshift_connector",
                    host=self.warehouse.get("redshift").get("host_url"),
                    port=self.warehouse.get("redshift").get("port"),
                    database=self.warehouse.get("redshift").get("db_name"),
                    username=self.warehouse.get("redshift").get("user"),
                    password=self.warehouse.get("redshift").get("password"),
                )
            )
        elif self.warehouse_type == "snowflake":
            self.engine = sqlalchemy.create_engine(
                snow_url(
                    account=self.warehouse.get("snowflake").get("account"),
                    user=self.warehouse.get("snowflake").get("user"),
                    password=self.warehouse.get("snowflake").get("password"),
                    role=self.warehouse.get("snowflake").get("role"),
                    database=self.warehouse.get("snowflake").get("database"),
                    warehouse=self.warehouse.get("snowflake").get("warehouse"),
                )
            )

        else:
            raise ReflektConfigError(
                f"Invalid warehouse type specified in {self._config.path}"
            )

    def get_columns(
        self, schema: str, table_name: str
    ) -> Tuple[Optional[list], Optional[str]]:
        with self.engine.connect() as conn:
            try:
                conn.detach()
                columns = (
                    conn.execute(f"select * from {schema}.{table_name} limit 0")
                    .keys()
                    ._keys
                )
                error_msg = None
                return columns, error_msg
            except sqlalchemy.exc.ProgrammingError as e:
                columns = None

                # Handle error according to warehouse type
                if self.warehouse_type == "redshift":
                    error_msg = e.orig.args[0]["M"]
                elif self.warehouse_type == "snowflake":
                    error_msg = e.orig.msg

                return columns, error_msg
