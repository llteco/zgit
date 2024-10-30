# la[Z](https://github.com/llteco/zgit)y GIT

[zgit](https://pypi.org/project/zgit/) is a Python toolkit to plot, stat and archive git repositories in an easy-to-use manner.

zgit is also published to PyPI so you can install it using pip directly:

```
python -m pip install zgit
```

## Important Note

**Since zgit manipulates git repositories directly, make sure you commit or backup your code properly, in case your repo may be corrupted.**

## How to use

There are 3 main features in zgit now:

#### 1. Sync multiple repositories asynchronizedly

```
usage: zgit-sync [-h] [--max-search-depth MAX_SEARCH_DEPTH] [--archive ARCHIVE] [--jobs JOBS] root

positional arguments:
  root                  the top folder you want to search git repos and update

options:
  -h, --help            show this help message and exit
  --max-search-depth MAX_SEARCH_DEPTH, -d MAX_SEARCH_DEPTH
                        maximum search depth in the `root` folder, -1 means unlimited.
  --archive ARCHIVE     archive .git in a repo to save disk space, a repo hasn't been updated for more than `archive` days will be compressed into a tarball.
  --jobs JOBS, -j JOBS
```

#### 2. Archive repositories by compressing and deleting history objects

```
usage: zgit-gc [-h] [--depth DEPTH] [--no-user-input] [--jobs JOBS] root

positional arguments:
  root                  the top folder you want to search git repos and update

options:
  -h, --help            show this help message and exit
  --depth DEPTH, -d DEPTH
                        maximum search depth in the `root` folder, -1 means unlimited.
  --no-user-input, -ni  do not ask user input, use default values
  --jobs JOBS, -j JOBS
```

#### 3. Git commit history analysis and visualization

```
usage: zgit-plot [-h] [--git-repo GIT_REPO] [--git-log GIT_LOG] [-o OUTPUT] [--author {name,email}] [--group {day,ww,month,quarter}] [--log-scale] [-v {DEBUG,INFO,WARNING,ERROR}] [-e EXCLUDE [EXCLUDE ...]] [-i INCLUDE [INCLUDE ...]] [--threshold THRESHOLD] [-d]

options:
  -h, --help            show this help message and exit
  --git-repo GIT_REPO   specify a git repo directory to analysis
  --git-log GIT_LOG     specify a git log file to analysis, log file can be acquired by 'git log --numstat > log.txt'. This option is ignored if --git-repo is specified.
  -o OUTPUT, --output OUTPUT
                        specify an output directory
  --author {name,email}
                        merge commits based on user name or user email
  --group {day,ww,month,quarter}
                        merge commits on which time slice, supports day, work-week, month, and quarter
  --log-scale           plot the figure on log-scale y-axis.
  -v {DEBUG,INFO,WARNING,ERROR}, --verbose {DEBUG,INFO,WARNING,ERROR}
                        set the log level
  -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        specify an exclude pattern list, file name match any item from this list is ignored in the plot
  -i INCLUDE [INCLUDE ...], --include INCLUDE [INCLUDE ...]
                        specify an include pattern list, file name endswith any item from this list is counted in the plot
  --threshold THRESHOLD
                        additional exclude files with change lines above this threshold
  -d, --dump            save the breakdown data details
```
