import pytest
import json
import os
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
    tasks = []
    n_tasks = 10
    for i in range(1, n_tasks + 1):
        tasks.append(
            Task(
                name=f"task_{i}",
                creation_time=current_time,
                deadline=current_time + i * timedelta(hours=1),
            )
        )
    task_master = TaskMaster(tasks=tasks)
    assert task_master.tasks == tasks, "TaskMaster init failed."

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
    assert task_master.tasks[-1] == urgent_task, "TaskMaster add_task failed."

    # Serve the top 3 tasks.
    # These should be:
    # 1: UrgentTask (4*1=4), Index 10
    # 2: Task 1 (2*1=2), Index 0
    # 3: Task 2 (2*0.5=1), Index 1
    expected_tasks = {
        10: urgent_task,
        0: tasks[0],
        1: tasks[1],
    }
    served_tasks = task_master.serve_tasks(
        3, current_time=current_time + timedelta(hours=1)
    )
    assert served_tasks == expected_tasks, "TaskMaster task serving failed."

    # Test marking a task as complete.
    task_master.complete_task(0)

    # Test pretty print
    task_master.pretty_print(current_time)

    # Test saving and loading,
    fname = "task_manager.json"
    task_master.save_as_json(fname)
    new_task_master = TaskMaster.from_json(fname)
    assert new_task_master == task_master, "Failed serialization/deserialization."

    # Clean up the file after the test.
    os.remove(fname)
