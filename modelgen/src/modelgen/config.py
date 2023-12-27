"""declarative config"""
from typing import Optional

from basecfg import BaseCfg, opt


class Config(BaseCfg):
    """declarative config class for app"""

    db_host: str = opt(
        "localhost",
        doc="network hostname to use when connecting to db server",
    )
    db_port: int = opt(
        5432,
        doc="network port number to use when connecting to db server",
    )
    db_name: str = opt(
        "postgres",
        doc="",
    )
    db_password: str = opt(
        "postgres",
        doc="",
    )
    db_user: str = opt(
        "postgres",
        doc="",
    )

    options: Optional[str] = opt(
        default=None,
        doc="options to pass to sqlacodegen",
    )
    generator: Optional[str] = opt(
        default=None,
        doc="which sqlacodegen generator to use",
    )

    output_file: str = opt(
        "model.py",
        doc="full path at which the output file should be written",
    )

    base_doc_url: str = opt(
        default="https://ohdsi.github.io/CommonDataModel/cdm54.html",
        doc="URL for both the OMOP CDM Table documentation links and the page from which table descriptions are drawn",
    )
    base_class_name: str = opt(
        default="OMOPCDMModelBase",
        doc="the name of the base class which the models are all subclasses of",
    )
    base_class_desc: str = opt(
        default="Base for OMOP Common Data Model v5.4 Models",
        doc="the description used for the base class",
    )
