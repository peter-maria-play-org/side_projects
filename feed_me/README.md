# feed_me

`feed_me` is an ultralightweight python CLI task list system that
abstracts away the decision making process. It operates by creating
a points based task prioritization system. From this system, it
draws a small list of things to do to a user.

## Getting Started

`feed_me` is managed by UV. Once UV is installed, get up and running
with the CLI using following command in the `feed_me` directory.

```
# Installs the tool.
uv tool install --reinstall .
```

After which, one can interact with `feed_me` from anywhere on their
machine by running 

```
# Should run initial setup and give a help message!
feed_me
```

One can also check the test suite of the project with

```
uv run pytest
```

If you see all those tests passing, then you are good to go!

# The Score Function

Feed me evaluates the priority of tasks using a task score
function. The score depends on the start time, the deadline,
and the priority level of each task. Tasks scores are linear
in time up until the deadline, after which they exponentially
increase until the max score is reached.

$$
\text{Priority} \in \{1, 2, 3, 4\},
$$
$$
dt = \frac{\text{Now} - \text{Start}}{\text{Deadline} - \text{Start}},
$$
$$
\text{Task Score} = \text{Priority} \times \begin{cases}
dt, & \text{if } dt \leq 1 \\
e^{dt-1},   & \text{if } x > 0
\end{cases}
$$

## Project Goals

In this project, we aim to explore the following key concepts:

1. Strong Typing with Pydantic.
1. Linting with ruff.
1. Package Management with UV.
1. CLI with `click`.
1. Creating calendar sensitive codes.
1. JSON files.
1. A basic UI with `dash`.
