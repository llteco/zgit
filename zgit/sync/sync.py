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
    parser.add_argument(
        "root",
        type=Path,
        help="the top folder you want to search git repos and update",
    )
    parser.add_argument(
        "--max-search-depth",
        "-d",
        type=int,
        default=-1,
        help="maximum search depth in the `root` folder, -1 means unlimited.",
    )
    parser.add_argument(
        "--archive",
        type=int,
        default=-1,
        help="""archive .git in a repo to save disk space, a repo hasn't been updated
for more than `archive` days will be compressed into a tarball.""",
    )
    parser.add_argument("--jobs", "-j", type=int, default=0)
    return parser.parse_args()


def sync():
    """Synchronie git repositories."""

    args = parse_args()
    gen = find_git_root(args.root, max_depth=args.max_search_depth)
    if args.archive >= 0:
        func = Compose(update, partial(archive, older_than=args.archive))
    else:
        func = Compose(update)
    if args.jobs == 1:
        for i in gen:
            func(i)
    else:
        workers = args.jobs if args.jobs > 0 else None
        with concurrent.futures.ProcessPoolExecutor(workers) as executor:
            executor.map(func, gen)
        executor.shutdown()
