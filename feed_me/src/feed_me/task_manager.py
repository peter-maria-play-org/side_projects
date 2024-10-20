"""
task_manager contains the core classes that make up
the task management system.
"""

# Imports
import numpy as np
from pydantic import BaseModel, model_validator
from textwrap import indent
from typing_extensions import Self
from enum import Enum
from datetime import datetime, timedelta

# Maximum cost of a Task
MAX_COST = 1e3

# The smallest time between the creation time and deadline
# of a task.
SMALL_DT = timedelta(seconds=0.1)


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
    deadline: datetime
    description: str = ""
    creation_time: datetime = datetime.now()
    priority: Priority = Priority.MEDIUM

    @model_validator(mode="after")
    def validate_deadline(self) -> Self:
        """
        Ensures that the deadline is after the creation_date.

        Args:
            self: The class reference.

        Raises:
            ValueError: If the deadline is not after the creation_date.

        Returns:
            self: The class reference.
        """

        # For safety, we add a SMALL_DT here to make sure we don't have
        # numerical stability issues later.
        if self.deadline <= self.creation_time + SMALL_DT:
            raise ValueError("The deadline must be after the creation date.")
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

        # Decide if a task is overdue.
        if current_time >= self.deadline:
            # Overdue tasks experience exponential priority increases
            overdue_duration = (current_time - self.deadline).total_seconds() / 3600
            score = self.priority.value * (1 + overdue_duration) ** self.priority.value

            # Clamp the scpre to the maximum value to prevent numerical issues.
            return np.clip(score, 0, MAX_COST)

        # Linear Interpolation for non-overdue tasks
        total_duration = (self.deadline - self.creation_time).total_seconds()
        elapsed_duration = (current_time - self.creation_time).total_seconds()

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

        render_str = indent("Task:\n", base_indent * "\t")
        render_str += indent(f"Name: {self.name}\n", (base_indent + 1) * "\t")
        render_str += indent(
            f"Description: {self.description}\n", (base_indent + 1) * "\t"
        )
        render_str += indent(
            f"Creation Time: {self.creation_time}\n", (base_indent + 1) * "\t"
        )
        render_str += indent(f"Deadline: {self.deadline}\n", (base_indent + 1) * "\t")
        render_str += indent(
            f"Priority: {self.priority.name}\n", (base_indent + 1) * "\t"
        )
        render_str += indent(
            f"Score: {self.compute_score(current_time)}", (base_indent + 1) * "\t"
        )
        print(render_str)


# class RecurringTask()


class TaskMaster(BaseModel):
    """
    The TaskMaster is the main brain of the operation.
    It is responsible for serving up the next task in
    the list.
    """

    task_list: list[Task]

    def add_task(self, task: Task):
        """
        Adds a task to the task list.
        """
        self.task_list.append(task)

    def get_task_score_array(self, current_time: datetime) -> np.ndarray:
        """
        Computes an array of task costs.
        """

        # Init the memory
        score_array = np.zeros(len(self.task_list))

        # Loop through and fill it.
        for i, task in enumerate(self.task_list):
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
        render_str = indent("TaskMaster:\n", base_indent * "\t")
        render_str += indent(
            f"# of Tasks: {len(self.task_list)}", (base_indent + 1) * "\t"
        )
        print(render_str)

        # Loop through and print the tasks.
        for task in self.task_list:
            task.pretty_print(base_indent=base_indent + 1, current_time=current_time)

    def serve_tasks(self, n_tasks: int, current_time: datetime) -> list[Task]:
        """
        Server the n_task highest priority tasks.
        """

        # Get the score array of the tasks.
        score_array = self.get_task_score_array(current_time=current_time)

        # Argsort to get the indices of the tasks with the highest score.
        # TODO: This is a fixed cost approach to tasks, there is potential
        # TODO: for a linear system solve to find the optimal set of tasks
        # TODO: in a time window tha maximizes the score completion.
        max_sorted_indices = np.argsort(score_array)[::-1]

        # Loop through the sorted indices, returning the n_tasks
        # with the highest score
        # We also restrict this to not overflow the task list.
        #! For Maria: Something in the below code is not
        #! great. It is bug prone.
        #! Hint: Think about what would happen if we modify
        #! a task from the served_task_list.
        served_task_list = []
        for i in range(min(n_tasks, len(self.task_list))):
            served_task_list.append(self.task_list[max_sorted_indices[i]])

        return served_task_list
