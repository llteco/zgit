"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Git command utility
"""

import locale
import logging
from pathlib import Path
from typing import Dict, List, Optional

import dateparser

from . import git, pushd, raw_git

logger = logging.getLogger("ZGIT")


def is_git_repo(repo: Path) -> bool:
    """Check whether a directory is a git repo."""
    with pushd(repo, redir=True):
        ret = raw_git("status")
        if ret.returncode == 0:
            return True
        error: str = ret.stderr.decode(locale.getpreferredencoding())
        if "fatal: detected dubious ownership in repository" in error:
            # add repo into safe directory
            logger.info(f"adding {repo} to safe directory")
            return git("config --global --add safe.directory", repo.as_posix()) == 0
        else:
            return False


def stash_workspace(repo: Path):
    """Stash the current git workspace."""
    with pushd(repo, redir=True) as content:
        git("stash push -u")
        git("reset --hard")
        git("submodule deinit --all")
        git("clean -fdx .")
    logger.debug(content.getvalue())


def get_remote_tag(repo: Path) -> List[str]:
    """Fetch remote name"""
    with pushd(repo, redir=True) as content:
        git("remote show")
    return sorted(content.getvalue().splitlines())


def get_remote_branches(repo: Path) -> List[str]:
    """Fetch all remote branches"""
    with pushd(repo, redir=True) as content:
        git("branch -rl", format="%(refname)")
    contents = map(lambda s: s.strip(), content.getvalue().splitlines())
    return sorted(filter(lambda s: s and not s.endswith("/HEAD"), contents))


def get_current_branch(repo: Path) -> Optional[str]:
    """Fetch current branch name or None if no branch name activate"""
    with pushd(repo, redir=True) as content:
        git("branch --show-current")
    contents = map(lambda s: s.strip(), content.getvalue().splitlines())
    contents = sorted(filter(lambda s: s, contents))
    if contents:
        return contents[0]


def get_commit_full_log(repo: Path, commit: str = "HEAD") -> Dict[str, str]:
    """Get all log message at the HEAD commit."""
    with pushd(repo, redir=True) as content:
        ret = git(f"log {commit}^..{commit}", date="local")
    if ret != 0:
        # in case there is only 1 commit history
        with pushd(repo, redir=True) as content:
            git(f"log {commit}", date="local")
    lines = content.getvalue().splitlines()
    raw_date = lines[2].split(maxsplit=1)[1].strip()
    return {
        "commit": lines[0].split(maxsplit=2)[1],
        "author": lines[1].split(maxsplit=1)[1].strip(),
        "date": dateparser.parse(raw_date),
        "log": "\n".join(lines[3:]),
    }


def git_pull(repo: Path) -> bool:
    """Pull a repo. Returns False if nothing pulled."""
    with pushd(repo, redir=True) as content:
        ret = git("pull")
    if ret != 0:
        git("reset --hard")
        return False
    if "Already up to date" in content.getvalue():
        return False
    logger.debug(content.getvalue())
    return True
