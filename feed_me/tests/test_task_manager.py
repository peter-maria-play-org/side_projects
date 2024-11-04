import pytest
import json
from pydantic import ValidationError
from datetime import datetime, timedelta
from feed_me.task_manager import Task, TaskMaster, Priority


def test_Task():
    """
    Tests some functionality of the Task class.
    """

    # Create an invalid task with a deadline near
    # or before the creation time.
    with pytest.raises(ValidationError):
        _ = Task(
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

    # TODO (#6): Test the score

    # Test Serialization & Deserialization.
    serialized_task_str = valid_task.model_dump_json()
    new_task = Task(**json.loads(serialized_task_str))
    assert new_task == valid_task, "Failed serialization/deserialization."

    return


def test_TaskMaster():
    """
    Tests some functionality of the TaskMaster class.
    """

    # Programmatically create a list of tasks of equal
    # priority with deadlines n hours away. These tasks
    # each have a score slope of 2/n. (PRIORITY 2 / n HOURS)
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
    assert task_master.task_list == task_list, "TaskMaster init failed."

    # Add a task to the bottom of the task list
    # This task has urgent priority, and happens in 1 hour.
    # The score slope of the curve of this task is 4. (PRIORITY 4/1 HOUR)
    urgent_task = Task(
        name="Urgent Task",
        creation_time=current_time,
        deadline=current_time + timedelta(hours=1),
        priority=Priority.URGENT,
    )
    task_master.add_task(urgent_task)
    assert task_master.task_list[-1] == urgent_task, "TaskMaster add_task failed."

    # Serve the top 3 tasks.
    # These should be:
    # 1: UrgentTask (4*1=4)
    # 2: Task 1 (2*1=2)
    # 3: Task 2 (1*1=2)
    expected_task_list = [urgent_task] + task_list[:2]
    served_task_list = task_master.serve_tasks(
        3, current_time=current_time + timedelta(hours=1)
    )
    assert served_task_list == expected_task_list, "TaskMaster task serving failed."

    # Test Serialization & Deserialization.
    serialized_task_master_str = task_master.model_dump_json()
    new_task_master = TaskMaster(**json.loads(serialized_task_master_str))
    assert new_task_master == task_master, "Failed serialization/deserialization."
