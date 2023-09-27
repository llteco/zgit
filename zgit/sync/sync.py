"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Sync git repos
"""

import argparse
import concurrent.futures
from functools import partial
from pathlib import Path

from ..git.glob import find_git_root
from .archive import archive
from .updater import update


class Compose:
    """Compose a series of callables."""

    def __init__(self, *funcs):
        self.functors = list(funcs)

    def __call__(self, *args, **kwargs):
        for func in self.functors:
            func(*args, **kwargs)


def parse_args():
    """Parse command arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--max-search-depth", "-d", type=int, default=-1)
    parser.add_argument("--archive", type=int, default=-1)
    return parser.parse_args()


def sync():
    """Synchronie git repositories."""

    args = parse_args()
    gen = find_git_root(args.root, max_depth=args.max_search_depth)
    if args.archive >= 0:
        func = Compose(update, partial(archive, older_than=args.archive))
    else:
        func = Compose(update)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(func, gen)
    executor.shutdown()
