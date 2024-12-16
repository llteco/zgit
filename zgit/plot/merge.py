#! /usr/bin/python

import argparse
import datetime
import json
import logging
from collections import defaultdict
from typing import Callable, Dict, List, Optional

import dateparser

from zgit.plot.commit import CommitMessage


def merge_author(commit_data: Dict[str, CommitMessage], use_email=True):
    author_commits: Dict[str, List[CommitMessage]] = defaultdict(list)
    for comm_id, data in commit_data.items():
        if use_email:
            author = data["email"]
        else:
            author = data["author"]
        data["commit"] = comm_id
        if author not in author_commits:
            logging.info(f"new author: {author}")
        author_commits[author].append(data)
    return author_commits


def merge_date(commit_data: Dict[str, List[CommitMessage]], by: Optional[str]):
    date_commits = {}
    for author, data in commit_data.items():
        if by == "day":
            date_data = by_time(data, by_day)
        elif by == "ww":
            date_data = by_time(data, by_ww)
        elif by == "month":
            date_data = by_time(data, by_month)
        elif by == "quarter":
            date_data = by_time(data, by_quarter)
        else:  # per patch
            date_data = by_time(data)
        date_commits[author] = date_data
    return date_commits


def by_time(
    commits: List[CommitMessage],
    by: Optional[Callable[[datetime.datetime], int]] = None,
) -> Dict[int, Dict[int, List[CommitMessage]]]:
    year_commits = {}
    for i, commit in enumerate(commits):
        year = commit["date"].year
        period = by(commit["date"]) if by is not None else i
        if year not in year_commits:
            year_commits[year] = defaultdict(list)
        year_commits[year][period].append(
            {"changes": commit["changes"], "change-id": commit["change_id"]}
        )
    return year_commits


def by_day(date: datetime.datetime):
    return date.timetuple().tm_yday


def by_ww(date: datetime.datetime):
    return date.isocalendar()[1]


def by_month(date: datetime.datetime):
    return date.month


def by_quarter(date: datetime.datetime):
    return date.month // 4


def merge(
    commit_data: Dict[str, CommitMessage],
    use_email=True,
    group_by: Optional[str] = None,
) -> Dict[str, Dict[int, Dict[int, List[CommitMessage]]]]:
    return merge_date(merge_author(commit_data, use_email), group_by)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json")
    parser.add_argument("--use_name", action="store_true")
    parser.add_argument("--group_by", choices=("day", "ww", "month", "quarter"))
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    with open(args.json, encoding="utf-8") as fd:
        data = json.load(fd)
        for k, v in data.items():
            v["date"] = dateparser.parse(v["date"])
            data[k] = v
        data = merge(data, not args.use_name, args.group_by)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fd:
            json.dump(data, fd, indent=2)


if __name__ == "__main__":
    main()
