import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta
from feed_me.task_manager import *


def test_Task():
    """
    Tests some functionality of the Task class.
    """

    # Create an invalid task with a deadline near
    # or before the creation time.
    with pytest.raises(ValidationError):
        invalid_task = Task(
            name="invalid_task",
            descriptiom="Here is a test task.",
            creation_time=datetime.now(),
            deadline=datetime.now(),
        )

    # Create a valid task that is due tomorrow.
    valid_task = Task(
        name="valid_task",
        descriptiom="Here is a test task.",
        deadline=datetime.now() + timedelta(days=1),
    )

    # Test the pretty print
    valid_task.pretty_print()

    # Test the score
    # MARIA TODO? Create a Pytest that evaluates the score of the model.

    return


def test_TaskMaster():
    """
    Tests some functionality of the TaskMaster class.
    """

    # Programmatically create a list of tasks of equal
    # priority with deadlines n hours away.
    current_time = datetime.now()
    task_list = []
    n_tasks = 10
    for i in range(1, n_tasks + 1):
        task_list.append(
            Task(
                name=f"task_{i}",
                creation_time=current_time,
                deadline=current_time + i * timedelta(hours=1),
            )
        )
    task_master = TaskMaster(task_list=task_list)

    # Add a task to the bottom of the task list
    # This task has urgent priority, and happens in 2 hours.
    # This should place it as the 3rd highest cost task.
    task_master.add_task(
        Task(
            name="Urgent Task",
            creation_time=current_time,
            deadline=current_time + timedelta(hours=2),
            priority=Priority.URGENT,
        )
    )

    # Test the pretty print.
    task_master.pretty_print(current_time=current_time + timedelta(hours=1))

    # Serve the top 3 tasks and print.
    served_task_list = task_master.serve_tasks(
        3, current_time=current_time + timedelta(hours=1)
    )
    print("Served Tasks:")
    for task in served_task_list:
        task.pretty_print(current_time=current_time + timedelta(hours=1), base_indent=1)
