"""
Copyright Wenyi Tang 2024-2025

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
    from zgit.git import find_git

    _GIT = find_git.GIT
else:
    _GIT = Path(_GIT).resolve()

if _GIT is None:
    raise FileNotFoundError("git is not found!")

logger = logging.getLogger("ZGIT")


def raw_git(*args: str, no_capture=False, **kwargs) -> sp.CompletedProcess:
    """Execute git command with arguments.

    Returns:
        CompletedProcess: git command return struct.
    """
    assert _GIT is not None

    _git = Path(_GIT).resolve()
    arglist = [i.split(" ") for i in args]
    arglist = [""] + list(chain(*arglist))
    for k, v in kwargs.items():
        assert isinstance(k, str)
        k = k.replace("_", "-")
        if isinstance(v, bool) and v:
            arglist.append(f"--{k}")
        elif k.startswith("-"):
            arglist.append(f"{k}={v}")
        elif len(k) == 1:
            arglist.append(f"-{k}={v}")
        elif not isinstance(v, bool):
            arglist.append(f"--{k}={v}")
    logger.debug("git %s", " ".join(arglist))
    return sp.run(
        arglist, executable=str(_git), check=False, capture_output=not no_capture
    )


def git(*args: str, **kwargs) -> int:
    """Execute git command with arguments.

    Returns:
        int: git command return code.
    """
    ret = raw_git(*args, **kwargs)
    if ret.stdout:
        print(ret.stdout.decode(locale.getpreferredencoding()), file=sys.stdout)
    if ret.stderr:
        print(ret.stderr.decode(locale.getpreferredencoding()), file=sys.stderr)
    return ret.returncode


@contextlib.contextmanager
def empty_context():
    """An empty context."""
    yield None


@contextlib.contextmanager
def pushd(dir: os.PathLike, redir: bool = False):  # pylint: disable=W0622
    """A context to temporarily enter a new working directory.

    Args:
        dir (os.PathLike): target working directory.
        redir (bool): redirect stdout to a string io
    """
    cwd = os.getcwd()
    stdout, stderr = empty_context(), empty_context()
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
