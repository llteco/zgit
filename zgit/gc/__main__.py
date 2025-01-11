"""
Copyright Wenyi Tang 2024-2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

# pylint: disable=W1203

import argparse
import concurrent.futures
import logging
from functools import partial
from pathlib import Path
from uuid import uuid4

from zgit.gc.interact import want_input
from zgit.git import git, pushd
from zgit.git.glob import find_git_root
from zgit.git.utils import (
    get_commit_id,
    get_remote_tag,
    git_fetch,
    git_gc,
    stash_workspace,
)

logger = logging.getLogger("ZGIT.GC")


def parse_args():
    """Parse command arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
        type=Path,
        help="the top folder you want to search git repos and update",
    )
    parser.add_argument(
        "--depth",
        "-d",
        type=int,
        default=1,
        help="number of commits to fetch, defaults to 1",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        type=int,
        default=-1,
        help="maximum search depth in the `root` folder, -1 means unlimited.",
    )
    parser.add_argument(
        "--no-user-input",
        "-ni",
        action="store_true",
        help="do not ask user input, use default values",
    )
    parser.add_argument("--jobs", "-j", type=int, default=1)
    return parser.parse_args()


def gc_single(root: Path, depth: int, user_input: bool):
    remotes = get_remote_tag(root)
    if user_input:
        print(f"[{root.stem}] Select a remote tag to fetch")
        name_or_idx = want_input(
            f"[{root.stem}] {remotes} (str or 0-based int-index): ",
            choices=set(map(str, range(len(remotes)))) | set(remotes),
            defaults="0",
        )
        assert name_or_idx is not None
        if name_or_idx.isdigit():
            idx = int(name_or_idx)
            remote = remotes[idx]
        else:
            remote = name_or_idx
    else:
        remote = remotes[0]

    stash_workspace(root)
    commit = get_commit_id(root)
    logger.info(f"[{root.stem}] {remote}: {commit}")
    temp_br = uuid4().hex
    succ = git_fetch(
        root,
        remote,
        f"+{commit}:refs/remotes/{temp_br}",
        prune=True,
        no_recurse_submodules=True,
        depth=depth,
    )
    if not succ:
        logger.error(f"[{root.stem}] Fetch {commit} failed")
        return
    with pushd(root):
        git(f"branch -rd {temp_br}")
    succ = git_gc(root)
    if not succ:
        logger.error(f"[{root.stem}] GC failed")
        return


def main():
    args = parse_args()
    root_gen = find_git_root(args.root, max_recursive=args.recursive)
    if args.jobs == 1:
        for i in root_gen:
            gc_single(i, args.depth, not args.no_user_input)
    else:
        workers = args.jobs if args.jobs > 0 else None
        with concurrent.futures.ProcessPoolExecutor(workers) as executor:
            executor.map(
                partial(gc_single, user_input=not args.no_user_input), root_gen
            )
        executor.shutdown()


if __name__ == "__main__":
    main()
