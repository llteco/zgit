"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Git command in py
"""

import contextlib
import io
import locale
import logging
import os
import shutil
import subprocess as sp
import sys
from itertools import chain
from pathlib import Path

_GIT = shutil.which("git")
if _GIT is None:
    with contextlib.suppress(StopIteration, ImportError):
        import find_git

        _GIT = find_git.GIT

if _GIT is None:
    raise FileNotFoundError("git is not found!")

logger = logging.getLogger("ZGIT")


def git(*args, **kwargs) -> int:
    """Execute git command with arguments.

    Returns:
        int: git command return code.
    """
    _git = Path(_GIT).resolve()
    args = [i.split(" ") for i in args]
    args = [""] + list(chain(*args))
    for k, v in kwargs.items():
        assert isinstance(k, str)
        if k.startswith("-"):
            args.append(f"{k}={v}")
        elif len(k) == 1:
            args.append(f"-{k}={v}")
        else:
            args.append(f"--{k}={v}")
    logger.debug("git %s", " ".join(args))
    ret = sp.run(args, executable=str(_git), check=False, capture_output=True)
    if ret.stdout:
        print(ret.stdout.decode(locale.getpreferredencoding()), file=sys.stdout)
    if ret.stderr:
        print(ret.stderr.decode(locale.getpreferredencoding()), file=sys.stderr)
    return ret.returncode


@contextlib.contextmanager
def pushd(dir: os.PathLike, redir: bool = False):  # pylint: disable=W0622
    """A context to temporarily enter a new working directory.

    Args:
        dir (os.PathLike): target working directory.
        redir (bool): redirect stdout to a string io
    """
    cwd = os.getcwd()
    try:
        logger.debug("change cwd to: %s", dir)
        os.chdir(dir)
        content = io.StringIO()
        if redir:
            stdout = contextlib.redirect_stdout(content)
            stderr = contextlib.redirect_stderr(content)
            stdout.__enter__()  # pylint: disable=unnecessary-dunder-call
            stderr.__enter__()  # pylint: disable=unnecessary-dunder-call
        yield content
    finally:
        logger.debug("change cwd to: %s", cwd)
        os.chdir(cwd)
        if redir:
            stdout.__exit__(None, None, None)
            stderr.__exit__(None, None, None)
