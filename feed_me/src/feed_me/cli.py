import click
import json
import os
from datetime import datetime
from pathlib import Path
from .task_manager import TaskMaster, Task, Priority

TASK_MASTER_PATH = Path("./data/")


@click.group(invoke_without_command=True)
def main():
    """feed_me is a simple program that provides a simple CLI interface
    for task management. It's goal is to provide the user with a small
    subset of tasks to focus on from their list. This is to protect users
    from the perils of task selection.
    """
    pass


@main.command()
@click.argument("n_tasks", default=1)
def serve(n_tasks: int):
    """Serve serves a prescribed number of tasks based on the
    current time.
    """

    # Startup
    task_master = startup()

    # If the task master does not have enough tasks,
    # print a friendly note.
    if (total_tasks := len(task_master.task_list)) < n_tasks:
        click.echo(
            "TaskMaster does not have enough tasks in the task list "
            f"to serve {n_tasks}. Has {total_tasks} tasks."
        )

    # Get the current time and serve the tasks.
    now = datetime.now()
    served_tasks = task_master.serve_tasks(
        n_tasks=n_tasks,
        current_time=now,
    )

    # Print the served tasks out
    for task in served_tasks:
        task.pretty_print(
            current_time=now,
        )

    # Shutdown
    shutdown(task_master=task_master)


@main.command()
@click.option("--name", prompt="Name", type=click.STRING, help="The name of the task.")
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
    "--deadline",
    prompt="Deadline [YYYY-MM-DD]",
    help="The deadline of the task in the ISO8601 format.",
)
def add(
    name: str,
    description: str,
    priority: str,
    deadline: str,
):
    """Adds a task to the TaskMaster."""

    # Startup
    task_master = startup()

    # Create the datetime.
    deadline_obj = datetime.fromisoformat(deadline)

    # Create a task from the CLI.
    task = Task(
        name=name,
        description=description,
        priority=Priority[priority.upper()],
        creation_time=datetime.now(),
        deadline=deadline_obj,
    )

    # Add to the task master
    task_master.add_task(task=task)

    # Shutdown
    shutdown(task_master=task_master)


def load_taskmaster(path: Path) -> TaskMaster:
    """Load a taskmaster from a file.

    Args:
        path (Path): The path to the json file directory.

    Returns:
        (TaskMaster): The loaded TaskMaster.
    """

    task_master_fpath = path / "task_master.json"
    with open(task_master_fpath, "r") as file:
        task_master_dict = json.load(file)
    task_master = TaskMaster(**task_master_dict)
    return task_master


def save_taskmaster(path: Path, task_master: TaskMaster):
    """Save a taskmaster to a file.

    Args:
        path (Path): The path to the json file directory.
        task_master (TaskMaster): The TaskMaster to save.
    """

    # Check that the directory exists.
    # If it does not exist, make it.
    if not os.path.isdir(path):
        os.mkdir(path=path)

    # Serialize the task master and save.
    task_master_fpath = path / "task_master.json"
    task_master_ugly_str = task_master.model_dump_json()

    # Use json to pretty print the json.
    task_master_dict = json.loads(task_master_ugly_str)
    task_master_json_str = json.dumps(task_master_dict, indent=4)
    with open(task_master_fpath, "w") as file:
        file.write(task_master_json_str)


def startup():
    """This is the startup sequence for each command.

    Returns:
        (TaskMaster): The loaded TaskMaster.
    """

    # Check if this is the initial startup of the system
    # by first trying to load the task master. If no
    # task master is found, create one and save it
    # and use it going forward.
    try:
        task_master = load_taskmaster(path=TASK_MASTER_PATH)
    except FileNotFoundError:
        click.echo("First boot detected. Creating empty TaskMaster.")
        task_master = TaskMaster(task_list=[])
        save_taskmaster(
            path=TASK_MASTER_PATH,
            task_master=task_master,
        )
    return task_master


def shutdown(task_master: TaskMaster):
    """This is the shutdown sequence for each command.

    Args:
        task_master (TaskMaster): The TaskMaster to save.
    """

    save_taskmaster(path=TASK_MASTER_PATH, task_master=task_master)


if __name__ == "__main__":
    main()
