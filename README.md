# `side_projects`

This repository is a hodgepodge monorepo of small projects being 
undertaken by Peter Kaloyannis and Maria Navarro.

## Getting Started

This repository is built upon the popular [UV](https://github.com/astral-sh/uv) 
python package manager. We also recommend running these projects within a
linux environment (either WSL-2, VM, or native). For said environments, UV can
be installed with the following

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Development

Development is done by first creating an issue describing a change that should be
made. After that, a new branch is created for that issue. When work on this branch
is complete, a pull request onto main is opened for review. The title of the PR
must read as:

```
#ISSUE-NUMBER: Description of PR.
```

Where the issue number must link to a valid issue. PRs require at least one review 
before they can be merged.

This repository uses `pre-commit` to run some simple checks before commiting code is 
possible. `pre-commit` is simple to setup using `uv` by running

```
uv tool install pre-commit
uvx pre-commit install
```

This will install `pre-commit` into the git commit system.

## Projects

- `feed_me` is an ultralightweight CLI task list system that abstracts away the decision making process.
