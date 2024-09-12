"""Module that contains the command line application."""

# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m falcon` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `falcon.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `falcon.__main__` in `sys.modules`.

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from falcon import debug
from falcon.config import init
from falcon.core import PathService


class _DebugInfo(argparse.Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        debug.print_debug_info()
        sys.exit(0)


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = argparse.ArgumentParser(prog="give-me-the-odds")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {debug.get_version()}")
    parser.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")
    parser.add_argument("cfg_file", action="store", help="Configuration of the application (millennium-falcon.json)")
    parser.add_argument("input_file", action="store", help="Input file (empire.json)")
    return parser


def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `give-me-the-odds` or `python -m falcon`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    logging.basicConfig(level="DEBUG")
    parser = get_parser()
    opts = parser.parse_args(args=args)
    job, nodes, weights, costs = init(opts.cfg_file, opts.input_file)
    if costs is None:
        raise ValueError("Please upload a valid communication before.")
    service = PathService(job, nodes, weights, costs)
    service.search_path()
    print(job.get_odds().odds)
    return 0
