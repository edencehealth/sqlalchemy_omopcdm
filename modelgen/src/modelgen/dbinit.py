""" code for initializing the database from the reference DDL """
# pylint: disable=too-many-instance-attributes
import importlib
import logging
from typing import Dict, Literal, Sequence, TypeAlias

import requests
from sqlalchemy import Engine, create_engine, schema, text

from .config import Config
from .utils import semver_matcher

sql_dir = importlib.resources.files("modelgen.sql")

logger = logging.getLogger(__name__)

Category: TypeAlias = Literal[
    "constraints",
    "ddl",
    "eh_mods",
    "indices",
    "primary_keys",
]
# note: these are in order
categories: Sequence[Category] = (
    "ddl",
    "primary_keys",
    "constraints",
    "indices",
    "eh_mods",
)


class DDLReference:
    """
    class for accessing the official DDL files for the OHDSI OMOP CDM
    """

    dialect: str
    cdm_schema: str
    cdm_version: str
    cdm_version_short: str
    base_ddl_url: str
    filename_map: Dict[Category, str]
    ddl_data: Dict[Category, str]
    engine: Engine

    def __init__(self, config: Config) -> None:
        self.dialect = config.db_dbms
        self.cdm_version = config.cdm_version
        self.cdm_schema = config.cdm_schema
        if match := semver_matcher.match(config.cdm_version):
            self.cdm_version_short = match.group("minor")
        else:
            raise ValueError("unable to parse semver string")
        self.base_ddl_url = config.base_ddl_url
        self.filename_map = {
            "constraints": "OMOPCDM_{dialect}_{cdm_version_short}_constraints.sql",
            "ddl": "OMOPCDM_{dialect}_{cdm_version_short}_ddl.sql",
            "indices": "OMOPCDM_{dialect}_{cdm_version_short}_indices.sql",
            "primary_keys": "OMOPCDM_{dialect}_{cdm_version_short}_primary_keys.sql",
        }
        self.ddl_data = {
            "eh_mods": sql_dir.joinpath("eh_mods.sql").read_text(),
        }
        self.engine = create_engine(
            f"postgresql+psycopg2://"
            f"{config.db_user}:{config.db_password}@"
            f"{config.db_host}:{config.db_port}/"
            f"{config.db_name}"
        )

    def download_ddl(self):
        """download the official DDL data"""
        for category, filename in self.filename_map.items():
            url = (self.base_ddl_url + "/" + filename).format(
                dialect=self.dialect,
                cdm_version_short=self.cdm_version_short,
                cdm_version=self.cdm_version,
            )
            logger.debug("requesting %s", url)
            response = requests.get(url, timeout=300)
            if response.status_code != 200:
                raise ValueError(
                    f"failed to retrieve the DDL file at {url}; "
                    f"status code: {response.status_code}"
                )
            response.raise_for_status()
            self.ddl_data[category] = response.content.decode("utf8", errors="strict")
        for category, content in self.ddl_data.items():
            logger.info("loaded DDL category: %s (%s bytes)", category, len(content))

    def populate_database(self):
        """apply the DDL files to the server"""
        if not self.ddl_data or len(self.ddl_data) < len(categories):
            self.download_ddl()
        search_path = ",".join(set(("public", self.cdm_schema)))
        with self.engine.connect() as cnxn:
            with cnxn.begin():
                cnxn.execute(text(f"SET search_path TO {search_path};"))
                cnxn.execute(schema.CreateSchema(self.cdm_schema, True))
                for category in categories:
                    logger.info("executing SQL statements to create %s", category)
                    result = cnxn.execute(
                        text(
                            self.ddl_data[category].replace(
                                "@cdmDatabaseSchema", self.cdm_schema
                            )
                        )
                    )
                    logger.debug(result)
        logger.info("done populating database")


def initdb(config: Config):
    """populate the database from the reference DDL files"""
    reference = DDLReference(config)
    reference.populate_database()
