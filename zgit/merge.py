#! /usr/bin/python

import argparse
import datetime
import json
import logging
from collections import defaultdict

import dateparser


def merge_author(commit_data: dict, use_email=True):
    author_commits = defaultdict(list)
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


def merge_date(commit_data: dict, by):
    date_commits = {}
    for author, data in commit_data.items():
        if by == "day":
            date_data = by_time(data, by_day)
        elif by == "ww":
            date_data = by_time(data, by_ww)
        elif by == "month":
            date_data = by_time(data, by_month)
        elif by == "quater":
            date_data = by_time(data, by_quater)
        date_commits[author] = date_data
    return date_commits


def by_time(commits: list, by):
    year_commits = {}
    for commit in commits:
        year = commit["date"].year
        period = by(commit["date"])
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


def by_quater(date: datetime.datetime):
    return date.month // 4


def merge(commit_data, use_email=True, by_time="month"):
    return merge_date(merge_author(commit_data, use_email), by_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json")
    parser.add_argument("--use_name", action="store_true")
    parser.add_argument("--by_time", choices=("day", "ww", "month", "quater"))
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    with open(args.json, encoding="utf-8") as fd:
        data = json.load(fd)
        for k, v in data.items():
            v["date"] = dateparser.parse(v["date"])
            data[k] = v
        data = merge(data, not args.use_name, args.by_time)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fd:
            json.dump(data, fd, indent=2)
