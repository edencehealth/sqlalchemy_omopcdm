"""functions for calling external commands """
import logging
import subprocess  # nosec: considered
from typing import IO, Any, Sequence, Tuple, Union

from .config import Config

SubProcessFileArg = Union[None, int, IO[Any]]

logger = logging.getLogger(__name__)


def run_cmd(
    command: Sequence[str],
    stdout: SubProcessFileArg = None,
    stderr: SubProcessFileArg = None,
) -> Tuple[str, str]:
    """run the given command returning a stdout, stderr tuple"""

    output = subprocess.run(  # nosec: considered; limited inputs
        command,
        check=True,
        stdout=stdout if stdout else subprocess.PIPE,
        stderr=stderr if stderr else subprocess.PIPE,
        shell=False,
        encoding="utf8",
        errors="strict",
    )
    return (
        output.stdout if stdout is None else "",
        output.stderr if stderr is None else "",
    )


def sqlacodegen(config: Config):
    """run the sqlacodegen utility"""
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

    # run sqlacodegen
    with open(
        config.output_file,
        "wt",
        encoding="utf8",
        errors="strict",
    ) as output_file:
        logger.info("running command: %s", repr(command))
        _, err = run_cmd(command, stdout=output_file)
        for line in err.splitlines():
            logger.error("sqlacodegen: %s", line)

    logger.info("wrote model to: %s", config.output_file)


def black(config):
    """run the Black code formatter"""
    command = ["/usr/local/bin/black", config.output_file]
    out, err = run_cmd(command, stderr=subprocess.STDOUT)
    if err:
        logger.error(err)
    for line in out.splitlines():
        logger.info("black: %s", line)


def isort(config):
    """run the isort code formatter"""
    command = ["/usr/local/bin/isort", "--profile", "black", config.output_file]
    out, err = run_cmd(command, stderr=subprocess.STDOUT)
    if err:
        logger.error(err)
    for line in out.splitlines():
        logger.info("isort: %s", line)
