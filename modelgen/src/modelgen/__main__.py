#!/usr/bin/env python3
""" utility """
import subprocess  # nosec: considered
import sys

import baselog

from .config import Config
from .rewrite import add_docstrings_to_file


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with sys.exit
    """
    config = Config(prog=__package__)
    logger = baselog.BaseLog(
        root_name=__package__,
    )
    config.logcfg(logger)

    command = [
        "/usr/local/bin/sqlacodegen",
        f"postgresql://{config.db_user}:{config.db_password}@"
        f"{config.db_host}/{config.db_name}",
    ]

    if config.options:
        command.insert(1, "--options")
        command.insert(2, config.options)
    if config.generator:
        command.insert(1, "--generator")
        command.insert(2, config.generator)

    with open(
        config.output_file,
        "wt",
        encoding="utf8",
        errors="strict",
    ) as output_file:
        logger.info(f"running command: {command!r}")
        subprocess.check_call(command, stdout=output_file)

    logger.info("wrote model to: %s", config.output_file)
    add_docstrings_to_file(config.output_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
