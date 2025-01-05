"""
task_manager contains the core classes that make up
the task management system.
"""

# Imports
import numpy as np
import json
from pydantic import BaseModel, model_validator
from textwrap import indent
from typing_extensions import Self
from enum import Enum
from datetime import datetime
from pathlib import Path
from . import INDENT, MAX_COST, SMALL_DT


class Priority(Enum):
    """
    Enumerator representing priority levels.

    These values set the score of a task at the
    deadline. They also form the basis of exponential
    growth past the deadline.
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class Status(Enum):
    """
    Enumerator status of a task. It is either complete or not.
    """

    TODO = 1
    COMPLETE = 2


class Task(BaseModel):
    """
    A Task represents a task.

    Tasks are born with a score of 0, meaning they
    have the minimum attributable score in the queue.

    The score of a task linearly increases to the value
    of the priority. This ensures high priority tasks
    are served up earlier than low priority tasks.
    """

    name: str
    description: str = ""
    creation_time: datetime = datetime.now()
    start: datetime = datetime.now()
    deadline: datetime
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO

    @model_validator(mode="after")
    def validate_deadline(self) -> Self:
        """
        Ensures that the deadline is after the start_date.

        Args:
            self: The class reference.

        Raises:
            ValueError: If the deadline is not after the start_date.

        Returns:
            self: The class reference.
        """

        # For safety, we add a SMALL_DT here to make sure we don't have
        # numerical stability issues later.
        if self.deadline <= self.start + SMALL_DT:
            raise ValueError("The deadline must be after the start date.")
        return self

    def compute_score(self, current_time: datetime) -> float:
        """
        Computes the score of the task.
        This is a linear interpolation until the deadline.

        After the deadline, tasks increase in value to the
        power of their priority score.

        Args:
            current_time (datetime): The current date to be used
                when evaluating the task priority.
        """

        # If a task is complete, the score is 0.
        if self.status == Status.COMPLETE:
            return 0

        # Decide if a task is overdue.
        if current_time >= self.deadline:
            # Overdue tasks experience exponential priority increases
            overdue_duration = (current_time - self.deadline).total_seconds() / 3600
            score = self.priority.value * (1 + overdue_duration) ** self.priority.value

            # Clamp the scpre to the maximum value to prevent numerical issues.
            return np.clip(score, 0, MAX_COST)

        # Linear Interpolation for non-overdue tasks
        total_duration = (self.deadline - self.start).total_seconds()
        elapsed_duration = (current_time - self.start).total_seconds()

        # Division by 0 protection is done by construction
        score = self.priority.value * (elapsed_duration / total_duration)
        return np.clip(score, 0, MAX_COST)

    def pretty_print(
        self, current_time: datetime = datetime.now(), base_indent: int = 0
    ):
        """Pretty printing for a Task.

        Args:
            current_time (datetime, optional): The current time for printing.
                Defaults to datetime.now().
            base_indent (int, optional): The indentation to use in the print.
                Defaults to 0.
        """

        render_str = indent("Task:\n", base_indent * INDENT)
        render_str += indent(f"Name: {self.name}\n", (base_indent + 1) * INDENT)
        render_str += indent(
            f"Description: {self.description}\n", (base_indent + 1) * INDENT
        )
        render_str += indent(
            f"Creation Time: {self.creation_time}\n", (base_indent + 1) * INDENT
        )
        render_str += indent(
            f"Start Time: {self.start}\n", (base_indent + 1) * INDENT
        )
        render_str += indent(f"Deadline: {self.deadline}\n", (base_indent + 1) * INDENT)
        render_str += indent(
            f"Priority: {self.priority.name}\n", (base_indent + 1) * INDENT
        )
        render_str += indent(
            f"Status: {self.status.name}\n", (base_indent + 1) * INDENT
        )
        render_str += indent(
            f"Score: {self.compute_score(current_time)}\n", (base_indent + 1) * INDENT
        )
        print(render_str)


# TODO (#5): Add a recurring task class
# TODO     : class RecurringTask()


class TaskMaster(BaseModel):
    """
    The TaskMaster is the main brain of the operation.
    It is responsible for managing the different types of tasks
    and organizing how they get done.
    """

    tasks: list[Task]

    @classmethod
    def from_json(cls, path: Path):
        """Load a TaskMaster from a file.

        Args:
            path (Path): The path to the json file.

        Returns:
            (TaskMaster): The loaded TaskMaster.
        """

        with open(path, "r") as file:
            task_master_dict = json.load(file)
        task_master = cls(**task_master_dict)
        return task_master

    def save_as_json(self, path: Path):
        """Save a TaskMaster to a file.

        Args:
            path (Path): The path to save the json to.
        """

        # Dump task master as json converts everything to a
        # writeable json string.
        task_master_ugly_str = self.model_dump_json()

        # Loading this back as a dict and using pretty print gives us
        # a pretty print of it.
        task_master_dict = json.loads(task_master_ugly_str)
        task_master_json_str = json.dumps(task_master_dict, indent=4)
        with open(path, "w") as file:
            file.write(task_master_json_str)

    def add_task(self, task: Task):
        """
        Adds a task to the task list.
        """
        self.tasks.append(task)

    def get_task_score_array(self, current_time: datetime) -> np.ndarray:
        """
        Computes an array of task costs.
        """

        # Init the memory
        score_array = np.zeros(len(self.tasks))

        # Loop through and fill it.
        for i, task in enumerate(self.tasks):
            score_array[i] = task.compute_score(current_time=current_time)
        return score_array

    def pretty_print(
        self, current_time: datetime = datetime.now(), base_indent: int = 0
    ):
        """Pretty printing for a TaskMaster.

        Args:
            current_time (datetime, optional): The current time for printing.
                Defaults to datetime.now().
            base_indent (int, optional): The indentation to use in the print.
                Defaults to 0.
        """

        # Start by printing information about the task master.
        render_str = indent("TaskMaster:\n", base_indent * INDENT)
        render_str += indent(
            f"# of Tasks: {len(self.tasks)}", (base_indent + 1) * INDENT
        )
        print(render_str)

        # Loop through and print the tasks.
        print(indent("Tasks:\n", base_indent * INDENT))
        for task in self.tasks:
            task.pretty_print(base_indent=base_indent + 1, current_time=current_time)

    def serve_tasks(self, n_tasks: int, current_time: datetime) -> dict[int, Task]:
        """
        Server the n_task highest priority tasks and their index.
        """

        # Get the score array of the tasks.
        score_array = self.get_task_score_array(current_time=current_time)

        # Argsort to get the indices of the tasks with the highest score.
        max_sorted_indices = np.argsort(score_array)[::-1]

        # Loop through the sorted indices, returning the n_tasks
        # with the highest score.
        #
        # Note:
        #   - We make use of the well ordered property of dicts to keep
        #     the task priority order correct.
        #   - We also restrict this to not overflow the task list.
        #! For Maria: Something in the below code is not
        #! great. It is bug prone.
        #! Hint: Think about what would happen if we modify
        #! a task from the served_tasks.
        served_tasks = {}
        for i in range(min(n_tasks, len(self.tasks))):
            served_tasks[max_sorted_indices[i]] = self.tasks[max_sorted_indices[i]]

        return served_tasks

    def complete_task(self, task_index: int):
        """
        Marks a task at a specified index in the task list as complete.

        Args:
            task_index (int): The index of the task to mark as complete.
        """

        # Check that the task_index is valid.
        # Raise if not.
        if task_index >= (n_tasks := len(self.tasks)):
            raise IndexError(
                f"Invalid task index {task_index} is larger than the max "
                f"{n_tasks-1} index."
            )

        # Set the task to complete.
        task_name = self.tasks[task_index].name
        if self.tasks[task_index].status != Status.COMPLETE:
            self.tasks[task_index].status = Status.COMPLETE
            print(f"Task {task_name} is marked as complete.")
        else:
            print(f"Task {task_name} is already complete.")
