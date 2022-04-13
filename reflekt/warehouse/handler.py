# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy
from sqlalchemy.engine.url import URL as redshift_url
from snowflake.sqlalchemy import URL as snow_url
from loguru import logger
from reflekt.logger import logger_config
from reflekt.reflekt.config import ReflektConfig

# Setup logger
logger.configure(**logger_config)


class WarehouseConnection:
    """Class that handles connection to the data warehouse specified in
    reflekt_config.yml
    """

    def __init__(self, reflekt_config):
        self._reflekt_config = ReflektConfig()
        self._cdp = self._reflekt_config.cdp
        self._cdp_name = self._reflekt_config.cdp_name
        self._warehouse = self._reflekt_config.warehouse
        self._warehouse_type = self._reflekt_config.warehouse_type

        if self._warehouse_type == "redshift":
            self.engine = sqlalchemy.create_engine(
                redshift_url.create(
                    drivername="redshift+redshift_connector",
                    host=self._warehouse.get("redshift").get("host_url"),
                    port=self._warehouse.get("redshift").get("port"),
                    database=self._warehouse.get("redshift").get("db_name"),
                    username=self._warehouse.get("redshift").get("user"),
                    password=self._warehouse.get("redshift").get("password"),
                )
            )

        elif self._warehouse_type == "snowflake":
            self.engine = sqlalchemy.create_engine(
                snow_url(
                    account=self._warehouse.get("snowflake").get("account"),
                    user=self._warehouse.get("snowflake").get("user"),
                    password=self._warehouse.get("snowflake").get("password"),
                    role=self._warehouse.get("snowflake").get("role"),
                    database=self._warehouse.get("snowflake").get("database"),
                    warehouse=self._warehouse.get("snowflake").get(
                        "warehouse"
                    ),
                    schema=self._warehouse.get("snowflake").get("schema"),
                )
            )

        else:
            logger.error(
                "Unknown warehouse type specified in config at "
                " reflekt_config.yml"
            )

    def get_columns(self, schema, table_name):
        with self.engine.connect() as conn:
            try:
                conn.detach()
                columns = (
                    conn.execute(
                        f"select * from {schema}.{table_name} limit 0"
                    )
                    .keys()
                    ._keys
                )
                # Connection is fully closed since we used "with:"
                error_msg = None
                return columns, error_msg

            except sqlalchemy.exc.ProgrammingError as e:
                columns = None
                error_msg = e.orig.args[0]["M"]
                return columns, error_msg

    def get_library(self, schema, table_name):
        with self.engine.connect() as conn:
            conn.detach()
            library_name_list = conn.execute(
                f"select context_library_name "
                f"from {schema}.{table_name} "
                f"where context_library_name is not null "
                f"limit 1"
            )
            library_name = library_name_list[0]
            return str(library_name)
            # Connection is fully closed since we used "with:"
