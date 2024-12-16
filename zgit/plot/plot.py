"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

from zgit.plot.commit import CommitMessage

_FILES = {
    ".c",
    ".cc",
    ".cxx",
    ".cpp",
    ".h",
    ".hpp",
    ".cm",
    ".py",
    ".bat",
    ".sh",
    ".cmake",
    "CMakeLists.txt",
    ".bzl",
    ".bazel",
    "WORKSPACE",
    "BUILD",
}

_EXCLUDE = set()


def reduce(stats: list, includes=_FILES, excludes=_EXCLUDE, threshold=100000):
    total_add = 0
    total_del = 0
    if not includes:
        includes = _FILES
    if not excludes:
        excludes = _EXCLUDE
    for stat in stats:
        for adds, dels, file in stat["changes"]:
            if adds + dels > threshold:
                continue
            if any(f in file for f in excludes):
                continue
            if any(file.endswith(f) for f in includes):
                total_add += adds
                total_del += dels
    return total_add, total_del


def plot_single(
    author: str,
    year: int,
    data: Dict[int, List[CommitMessage]],
    log_scale: bool,
    includes: List[str],
    excludes: List[str],
    threshold: int,
    output: str | Path,
    group_by: str,
):
    filename = Path(output) / f"{author.split('@')[0]}-{year}.png"
    filename.parent.mkdir(exist_ok=True, parents=True)
    stats = []
    timeline = []
    for k in sorted(data, key=lambda k: int(k)):
        stats.append(reduce(data[k], includes, excludes, threshold))
        timeline.append(k)
    arr = np.array(stats)
    add_line = arr[..., 0]
    del_line = arr[..., 1]
    ax = plt.subplot(111)
    title = f"{author} {year}"
    if log_scale:
        title += " (logscale)"
        fn = np.log10
    else:
        fn = lambda x: x
    ax.set_title(title)
    ax.grid(True, axis="y")
    ax.bar(timeline, fn(add_line + del_line), color="r")
    ax.bar(timeline, fn(add_line), color="g")
    ax.get_xaxis().set_label_text(
        f"add total={add_line.sum()} changes total={add_line.sum()+del_line.sum()}"
    )
    for t, adds, dels in zip(timeline, add_line, del_line):
        print(f"{author}: [{year}.{t}] +{adds} -{dels}")
    plt.savefig(filename)
    plt.close()


def plot(
    commits: Dict[str, Dict[int, Dict[int, List[CommitMessage]]]],
    output: str | Path,
    log_scale: bool,
    includes: List[str],
    excludes: List[str],
    threshold: int,
    group_by: str,
):
    for author, timed_data in commits.items():
        for year, data in timed_data.items():
            plot_single(
                author,
                year,
                data,
                log_scale,
                includes,
                excludes,
                threshold,
                output,
                group_by,
            )
