import click
import os
from pydantic_core import ValidationError
from datetime import datetime
from .task_manager import TaskMaster, Task, Priority
from . import TASK_MASTER_PATH


@click.group(invoke_without_command=False)
@click.pass_context
def main(ctx):
    """feed_me is a program that provides a simple CLI interface
    for task management. It's goal is to provide the user with a small
    subset of tasks to focus on from their list. This is to protect users
    from the perils of task selection.
    """

    # Check if this is the initial startup of the system
    # by first trying to load the task master. If no
    # task master is found, create one and save it
    # and use it going forward.
    task_master_fpath = TASK_MASTER_PATH / "task_master.json"
    try:
        task_master = TaskMaster.from_json(path=task_master_fpath)
    except FileNotFoundError:
        # Print and startup.
        click.echo("First boot detected. Creating empty task_master.")
        task_master = TaskMaster(tasks=[])
    ctx.obj = task_master

    # When we close the CLI, save the task master.
    @ctx.call_on_close
    def shutdown():
        """This is the shutdown sequence for each command."""

        # Check that the directory exists.
        # If it does not exist, make it.
        if not os.path.isdir(TASK_MASTER_PATH):
            os.mkdir(path=TASK_MASTER_PATH)

        task_master.save_as_json(path=task_master_fpath)


@main.command()
@click.argument("n_tasks", default=1)
@click.pass_context
def serve(ctx, n_tasks: int):
    """Serves tasks based on the current time."""

    # Get the task master from the context
    task_master = ctx.obj

    # Get the current time and serve the tasks.
    now = datetime.now()
    served_tasks = task_master.serve_tasks(
        n_tasks=n_tasks,
        current_time=now,
    )
    if n_tasks > len(served_tasks):
        click.echo(
            "Task master does not have enough TODO tasks in the task list "
            f"to serve {n_tasks}."
        )

    # Print the served tasks out
    for index, task in served_tasks.items():
        print(f"INDEX: {index}")
        task.pretty_print(
            current_time=now,
        )


@main.command()
@click.argument("task_index", type=click.INT)
@click.pass_context
def complete(ctx, task_index: int):
    """Marks a task at the given task index as complete."""

    # Get the task master from the context
    task_master = ctx.obj

    # Mark the task as complete.
    try:
        task_master.complete_task(task_index=task_index)
    except IndexError as error:
        raise click.ClickException(error)


@main.command()
@click.option(
    "--name",
    prompt="Name",
    type=click.STRING,
    help="The name of the task.",
)
@click.option(
    "--description",
    prompt="Description",
    type=click.STRING,
    help="The description of the task.",
)
@click.option(
    "--priority",
    type=click.Choice(Priority._member_names_, case_sensitive=False),
    default="medium",
    prompt="Priority Level",
    help="The task priority level.",
)
@click.option(
    "--start",
    default="now",
    prompt="Start Time [YYYY-MM-DD]",
    help="The start time of the task in the ISO8601 format.",
)
@click.option(
    "--deadline",
    prompt="Deadline [YYYY-MM-DD]",
    help="The deadline of the task in the ISO8601 format.",
)
@click.pass_context
def add(
    ctx,
    name: str,
    description: str,
    priority: str,
    start: str,
    deadline: str,
):
    """Adds a task to the task_master."""

    # Get the task master from the context.
    task_master = ctx.obj

    # Datetime initialization.
    creation_time_obj = datetime.now()
    deadline_obj = datetime.fromisoformat(deadline)

    # Start time handling.
    if start == "now":
        start_obj = creation_time_obj
    else:
        start_obj = datetime.fromisoformat(start)

    # Create a task from the CLI.
    # If the task is invalid, catch the error and print it out.
    try:
        task = Task(
            name=name,
            description=description,
            priority=Priority[priority.upper()],
            creation_time=creation_time_obj,
            start=start_obj,
            deadline=deadline_obj,
        )
    except ValidationError as error:
        true_error = error.errors()[0]
        raise click.ClickException(true_error["msg"])

    # Add to the task master.
    task_master.add_task(task=task)


if __name__ == "__main__":
    # Run the CLI.
    main()
