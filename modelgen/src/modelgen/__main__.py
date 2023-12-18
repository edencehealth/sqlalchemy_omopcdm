#!/usr/bin/env python3
""" utility """
import subprocess  # nosec: considered
import sys

from .config import Config


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with sys.exit
    """
    config = Config(prog=__package__)

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
        print(f"running command: {command!r}")
        subprocess.check_call(command, stdout=output_file)

    print(f"==> Wrote model to {config.output_file} <==")

    return 0


if __name__ == "__main__":
    sys.exit(main())
