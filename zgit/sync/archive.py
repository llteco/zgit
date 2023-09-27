"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Archive repo that not active for more than 300 days
"""

import datetime
import logging
import os
import shutil
import tarfile
import time
from pathlib import Path
from typing import Any, Callable

from ..git import pushd
from ..git.utils import get_commit_full_log

logger = logging.getLogger("ZGIT.SYNC")


def _get_delta_to_now(then):
    now = time.localtime(time.time())
    then = datetime.datetime(then.year, then.month, then.day)
    now = datetime.datetime(now.tm_year, now.tm_mon, now.tm_mday)
    passed = now - then
    return passed.days


def _onerror(func: Callable[[str], Any], fullname: str, info: Any):
    try:
        func(fullname)
    except PermissionError:
        logger.debug("call system command to remove %s", fullname)
        if os.name == "nt":
            os.system(f"del /Q /F {fullname}")
        else:
            os.system(f"rm -f {fullname}")


def archive(repo: Path, older_than: int = 300):
    """Archive .git folder and delete the original one if it's commit history
    is older than some days.

    Args:
        repo (Path): git repository
        older_than (int, optional): Days in unit. Defaults to 300.
    """
    log = get_commit_full_log(repo)
    then = log["date"]
    days = _get_delta_to_now(then)
    if days >= older_than:
        with pushd(repo), tarfile.TarFile(".git.tar", mode="w") as tar:
            logger.info("archive %s", repo)
            tar.add(".git")
            shutil.rmtree(".git", onerror=_onerror)
