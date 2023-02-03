#! /usr/bin/python

import argparse
import io
import json
import logging
import re
import subprocess as sp

import dateparser


def get_log_stat(repo):
    return io.StringIO(sp.check_output("git log --numstat", cwd=repo, encoding="utf-8"))


def parse_log_to_commit(fd: io.IOBase):
    commit = {}
    curr_id = ""
    for line in fd.readlines():
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


def parse_commit(commit: list):
    assert len(commit) >= 4

    changes = []
    merge = False
    change_id = ""

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
        elif comm_line.startswith("Date:"):
            date_line: str = comm_line
            logging.debug(f"date: {date_line}")
            date = dateparser.parse(date_line[5:])
        elif comm_line.startswith("Merge:"):
            merge = comm_line[7:]
        elif comm_line.strip().startswith("Change-Id:"):
            change_id = comm_line.strip()[11:]

    return dict(
        author=author_name,
        email=author_email,
        date=date,
        changes=changes,
        merge=merge,
        change_id=change_id,
    )


def get_commits(*, git_repo=None, git_logs=None):
    if not git_repo and not git_logs:
        raise ValueError("empty args!")

    if git_repo:
        fd = get_log_stat(git_repo)
    elif git_logs:
        fd = open(git_logs, encoding="utf-8")
    commits = parse_log_to_commit(fd)
    logging.info(f"num commits: {len(commits)}")
    for k, v in commits.items():
        commits[k] = parse_commit(v)
    fd.close()
    return commits


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo")
    parser.add_argument("--log")
    parser.add_argument("--output", "-o")
    parser.add_argument("-v", default="INFO")
    args = parser.parse_args()
    logging.getLogger().setLevel(args.v)

    commits = get_commits(git_repo=args.repo, git_logs=args.log)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fd:
            for k, v in commits.items():
                v["date"] = v["date"].strftime("%D")
                commits[k] = v
            json.dump(commits, fd, indent=2)
