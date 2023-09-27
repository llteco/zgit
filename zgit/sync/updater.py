"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Update git repo
"""

import logging
from pathlib import Path
from typing import Optional

from ..git import git, pushd
from ..git.utils import (
    get_current_branch,
    get_remote_branches,
    get_remote_tag,
    git_pull,
    is_git_repo,
    stash_workspace,
)

logger = logging.getLogger("ZGIT.SYNC")


def update(repo: Path, upstream: Optional[str] = None):
    """Update a repository.

    This operation will stash the uncommit changes and fetch the latest
    commits from remote branch.

    If remote main or master is newer than the local branch, checkout to the
    latest remote branch.
    If local branch is not set an upstream, checkout to the latest remote branch.
    """
    if not is_git_repo(repo):
        logger.info("ignore %s because it is not a git repo.", repo)
    logger.info("updating repo: %s", repo)

    remote_tags = get_remote_tag(repo)
    if "origin" in remote_tags:
        remote = "origin"
    elif remote_tags:
        remote = remote_tags[0]
    else:
        logger.error("repo has not any remote upstream")
        logger.info("skip %s", repo)
        return
    with pushd(repo):
        if ret := git("fetch", remote):
            logger.error("git fetch %s failed: %d", remote, ret)
            logger.info("skip %s", repo)
            return

    stash_workspace(repo)
    branches = get_remote_branches(repo)
    assert branches
    if upstream is None:
        if any(f"{remote}/main" in b for b in branches):
            upstream = f"{remote}/main"
        elif any(f"{remote}/master" in b for b in branches):
            upstream = f"{remote}/master"
        else:
            upstream = branches[0]
    if not any(upstream in b for b in branches):
        logger.info("Possible upstreams:\n  %s", "\n  ".join(branches))
        raise ValueError(f"upstream '{upstream}' is not valid!")
    if br := get_current_branch(repo):
        if git_pull(repo):
            logger.info("update %s (%s)", repo, br)
            return
    with pushd(repo, redir=True):
        logger.info("checkout %s to %s", repo, upstream)
        git("checkout", upstream)
