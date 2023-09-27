"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""
import argparse
import json
import logging
from pathlib import Path

from .commit import get_commits
from .merge import merge
from .plot import plot


def main():
    parser = argparse.ArgumentParser(prog="python -m easygit")
    parser.add_argument(
        "--git-repo", type=Path, help="specify a git repo directory to analysis"
    )
    parser.add_argument(
        "--git-log",
        type=Path,
        help="specify a git log file to analysis, "
        "log file can be acquired by 'git log --numstat > log.txt'. "
        "This option is ignored if --git-repo is specified.",
    )
    parser.add_argument("-o", "--output", type=Path, help="specify an output directory")
    parser.add_argument(
        "--author",
        choices=("name", "email"),
        default="email",
        help="merge commits based on user name or user email",
    )
    parser.add_argument(
        "--group",
        choices=("day", "ww", "month", "quarter"),
        default="month",
        help="merge commits on which time slice, "
        "supports day, work-week, month, and quarter",
    )
    parser.add_argument(
        "--log-scale", action="store_true", help="plot the figure on log-scale y-axis."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="set the log level",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        nargs="+",
        help="specify an exclude pattern list, "
        "file name match any item from this list is ignored in the plot",
    )
    parser.add_argument(
        "-i",
        "--include",
        nargs="+",
        help="specify an include pattern list, "
        "file name endswith any item from this list is counted in the plot",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=100000,
        help="additional exclude files with change lines above this threshold",
    )
    parser.add_argument(
        "-d", "--dump", action="store_true", help="save the breakdown data details"
    )
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(args.verbose)

    commits = get_commits(git_repo=args.git_repo, git_logs=args.git_log)
    commits = merge(commits, args.author == "email", args.group)
    if args.dump:
        dump_dir = Path(args.output) if args.output else Path.cwd()
        with open(dump_dir / "merge.json", "w", encoding="utf-8") as fd:
            json.dump(commits, fd, indent=2)
    if args.output:
        plot(
            commits,
            args.output,
            args.log_scale,
            args.include,
            args.exclude,
            args.threshold,
        )


if __name__ == "__main__":
    main()
