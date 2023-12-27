#!/usr/bin/env python3
""" entrypoint for direct execution """
import sys
import time

import baselog

from .config import Config
from .dbinit import initdb
from .rewrite import rename_base_and_add_docstrings
from .shellout import black, isort, sqlacodegen


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with sys.exit
    """
    config = Config(prog=__package__)
    logger = baselog.BaseLog(
        root_name=__package__,
        log_dir=config.log_dir,
        console_log_level=config.log_level,
    )
    config.logcfg(logger)

    for i, step in enumerate(
        (
            initdb,
            sqlacodegen,
            rename_base_and_add_docstrings,
            isort,
            black,
        )
    ):
        step_num = i + 1
        logger.info("step %s; %s", step_num, step.__name__)
        dur = time.time()
        step(config)
        dur = time.time() - dur
        logger.debug("step %s; %s done in %ss", step_num, step.__name__, dur)

    return 0


if __name__ == "__main__":
    sys.exit(main())
