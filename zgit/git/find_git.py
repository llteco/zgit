"""
Copyright Wenyi Tang 2023-2025

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

Find git in common install directory
"""

import os
from itertools import product
from pathlib import Path
from typing import List, Sequence


def _path_cat(cand1: Sequence[Path], cand2: Sequence[Path]) -> List[Path]:
    return [i / j for i, j in product(cand1, cand2)]


if os.name == "nt":
    GIT_DIR = _path_cat(
        [
            Path("C:/"),
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
            Path("~/AppData/Local/Programs").expanduser(),
        ],
        [Path("Git/cmd/git.exe")],
    )
    BASH_DIR = _path_cat(
        [
            Path("C:/"),
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
            Path("~/AppData/Local/Programs").expanduser(),
        ],
        [
            Path("Git/usr/bin/bash.exe"),
            Path("Git/bin/bash.exe"),
        ],
    )
else:
    GIT_DIR = [
        Path("/usr/bin/git"),
        Path("/usr/local/bin/git"),
    ]
    BASH_DIR = [Path("/usr/bin/bash")]

GIT = next(filter(lambda p: p.exists(), GIT_DIR))
BASH = next(filter(lambda p: p.exists(), BASH_DIR))
