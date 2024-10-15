# FeedMe
Feed Me is an ultralightweight CLI task list system that abstracts 
away the decision making process. It operates by combining the 
pomodoro method for time management with a points based task 
prioritization system to present a small list of things to do to 
a user.

FeedMe is written in python and is not performance optimized.

## Getting Started
Feed me is managed by UV. Once UV is installed, get up and running with the 
following command.

```
uv run feed_me
```

This runs the CLI, which as of right now is not implemented. One can also run
the test suite of the project with

```
uv run pytest
```

## Project Goals

In this project, we aim to explore the following key concepts:
1. Strong Typing with Pydantic
1. Linting with ruff
1. Package Management with UV
1. CLI with `click`
1. Creating calendar sensitive codes
1. JSON files.