from datetime import timedelta
from pathlib import Path

# The base indentation for printing
INDENT = 4 * " "

# Maximum cost of a Task
MAX_COST = 1e3

# The smallest time between the creation time and deadline
# of a task.
SMALL_DT = timedelta(seconds=0.1)

# The location to save the task master to.
TASK_MASTER_PATH = Path("./data/")
