"""
Copyright Wenyi Tang 2023-2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Globbing repositories
"""

from pathlib import Path
from typing import Generator, Tuple, Union


def find_git_root(
    node: Union[str, Path],
    exclude: Tuple[str, ...] = (),
    curr: int = 0,
    max_recursive: int = -1,
) -> Generator[Path, None, None]:
    """Make a generator to iterate over all directories under node and get
    directories contains ".git".

    Note:
        Submodules won't be enumerated.

    Args:
        node (Union[str, Path]): A directory node to start
        exclude (Tuple[str, ...], optional): A tuple of pattern to exclude
            from globbing. Defaults to ().
        curr (int): Current search depth, callers should not set this value.
        max_recursive (int): Maximum recursive depth. Defaults to -1 (unlimited).

    Yields:
        Path: path to git repository
    """
    if max_recursive >= 0 and curr >= max_recursive:
        return
    node = Path(node)
    for i in node.iterdir():
        try:
            i.resolve()
        except OSError:
            continue
        if not i.is_dir() or i.is_symlink():
            continue
        if i.stem == ".git" and i.parent.stem not in exclude:
            yield node.resolve()
        if not i.stem.startswith("__") and not i.stem.startswith("."):
            yield from find_git_root(
                i, exclude, curr=curr + 1, max_recursive=max_recursive
            )
