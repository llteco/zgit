"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

# pylint: disable=missing-function-docstring, logging-fstring-interpolation

import argparse
import io
import json
import logging
import re
import subprocess as sp
from datetime import datetime
from typing import Dict, List, Optional, Tuple, TypedDict

import dateparser


def get_log_stat(repo):
    return io.StringIO(sp.check_output("git log --numstat", cwd=repo, encoding="utf-8"))


def parse_log_to_commit(f: io.TextIOBase) -> Dict[str, List[str]]:
    commit = {}
    curr_id = ""
    for line in f.readlines():
        if line.startswith("commit"):
            if commit_id := next(re.finditer(r"\b[\w\d]{40}\b", line)):
                curr_id = commit_id.group()
                logging.debug(f"commit: {curr_id}")
                commit[curr_id] = []
            else:
                raise ValueError(f"error commit: {line}")
        else:
            commit[curr_id].append(line)
    return commit


class CommitMessage(TypedDict):
    author: str
    change_id: str
    changes: List[Tuple[int, int, str]]
    commit: str
    date: datetime
    email: str
    merge: str
    title: str
    pr: int


def parse_commit(commit: List[str]) -> CommitMessage:
    assert len(commit) >= 4

    author_name = ""
    author_email = ""
    date = datetime.now()
    changes = []
    merge = "False"
    change_id = ""
    meet_author_and_date = 0
    title = ""
    pr = -1

    for comm_line in commit:
        if add_del_match := re.match(r"^\d+\s+\d+\b", comm_line):
            add_del_str = add_del_match.group()
            add_del = add_del_str.split()
            add_lines = int(add_del[0].strip())
            del_lines = int(add_del[1].strip())
            file = comm_line[add_del_match.end() :].strip()
            changes.append((add_lines, del_lines, file))
            logging.debug(f"{changes[-1]}")
        elif comm_line.startswith("Author:"):
            author_line: str = comm_line
            logging.debug(f"author: {author_line}")
            if author := next(re.finditer(r"<.*@.*>", author_line)):
                author_name = author_line[7 : author.start()].strip()
                author_email = author.group()[1:-1]
            else:
                raise ValueError(f"error author: {author_line}")
            meet_author_and_date += 1
        elif comm_line.startswith("Date:"):
            date_line: str = comm_line
            logging.debug(f"date: {date_line}")
            date = dateparser.parse(date_line[5:])
            assert date is not None
            meet_author_and_date += 1
        elif comm_line.startswith("Merge:"):
            merge = comm_line[7:]
        elif comm_line.strip().startswith("Change-Id:"):
            change_id = comm_line.strip()[11:]
        elif meet_author_and_date == 2 and comm_line.strip():
            title = comm_line.strip()
            logging.debug(f"title: {title}")
            if pr_number := re.match(r"^.*\(#(\d+)\)", comm_line):
                pr = int(pr_number.group(1))
                logging.debug(f"pr: #{pr}")
            meet_author_and_date = 0

    return CommitMessage(
        author=author_name,
        email=author_email,
        date=date,
        commit="",
        changes=changes,
        merge=merge,
        change_id=change_id,
        title=title,
        pr=pr,
    )


def get_commits(*, git_repo: Optional[str] = None, git_logs: Optional[str] = None):
    if not git_repo and not git_logs:
        raise ValueError("empty args!")

    if git_repo:
        f = get_log_stat(git_repo)
    elif git_logs:
        f = open(git_logs, encoding="utf-8")
    else:
        raise ValueError("either git_repo or git_logs should be specified!")

    commit_data = parse_log_to_commit(f)
    logging.info(f"num commits: {len(commit_data)}")
    parsed_commit_data = {
        commit_id: parse_commit(data) for commit_id, data in commit_data.items()
    }
    f.close()
    return parsed_commit_data


def main():
    parser = argparse.ArgumentParser(
        description="""Parse commit logs of a git
repository into a formatted JSON file.

The entry of this file is for debugging purpose only, you should use

zgit-plot --git-repo <repo> --output <dir>
"""
    )
    parser.add_argument("--repo", help="specify a local path of a git repository")
    parser.add_argument("--log", help="specify a local path of a git commit log file")
    parser.add_argument(
        "--output", "-o", help="specify a local path of the output file"
    )
    parser.add_argument(
        "-v",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="set the logging level",
    )
    args = parser.parse_args()
    logging.getLogger().setLevel(args.v)

    commits = get_commits(git_repo=args.repo, git_logs=args.log)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fd:
            for k, v in commits.items():
                v["date"] = v["date"].strftime("%D")  # type: ignore
                commits[k] = v
            json.dump(commits, fd, indent=2)
    else:
        for k, v in commits.items():
            msg = f"{v['email']},{k},+{{}},-{{}},{v['title']},{v['pr']},{v['date']}"
            if changes := v["changes"]:
                total_add_line = 0
                total_del_line = 0
                for add_line, del_line, _ in changes:
                    total_add_line += add_line
                    total_del_line += del_line
                msg = msg.format(total_add_line, total_del_line)
            print(msg)


if __name__ == "__main__":
    main()
