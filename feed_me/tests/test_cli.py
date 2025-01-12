# ruff: noqa: E402
# Disable E402 to allow the sequential importing operation
# for this test.
from datetime import datetime, timedelta
from pathlib import Path
from click.testing import CliRunner

# fmt: off
# Reset the task master path to be local.
# Must be done before importing the CLI
# to make the path apply when main is imported.
import feed_me
feed_me.TASK_MASTER_PATH = Path(".")

# Import the CLI.
from feed_me.cli import main
# fmt: on


def test_cli_main():
    """Tests the CLI main function. This is responsible for the startup
    and the shutdown sequence of the CLI.
    """

    runner = CliRunner()
    with runner.isolated_filesystem():
        # On a first boot, should create a file at the task master location.
        result = runner.invoke(main, [])
        assert result.exit_code == 0

        # On a second boot, should just load that existing file.
        result = runner.invoke(main, [])
        assert result.exit_code == 0


def test_cli_serve():
    """Tests serving a task. Just makes sure that it runs without
    errors.
    """

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["serve"])
        assert result.exit_code == 0


def test_cli_add():
    """Tests adding tasks."""

    runner = CliRunner()
    with runner.isolated_filesystem():
        # Add a task that is valid.
        result = runner.invoke(
            main,
            [
                "add",
                "--name",
                "test_task",
                "--description",
                "test_description",
                "--priority",
                "medium",
                "--deadline",
                (datetime.now() + timedelta(hours=1)).isoformat(),
            ],
        )
        assert result.exit_code == 0

        # Add a task that is invalid.
        result = runner.invoke(
            main,
            [
                "add",
                "--name",
                "test_task",
                "--description",
                "test_description",
                "--priority",
                "medium",
                "--deadline",
                (datetime.now() - timedelta(hours=1)).isoformat(),
            ],
        )
        assert result.exit_code == 1


def test_cli_complete():
    """Tests marking tasks complete using the CLI."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a task to complete.
        result = runner.invoke(
            main,
            [
                "add",
                "--name",
                "test_task",
                "--description",
                "test_description",
                "--priority",
                "medium",
                "--deadline",
                (datetime.now() + timedelta(hours=1)).isoformat(),
            ],
        )

        # Mark the task as complete
        result = runner.invoke(main, ["complete", "0"])
        assert result.exit_code == 0

        # Check that trying to complete a non-exitent task
        # generates an error.
        result = runner.invoke(main, ["complete", "1"])
        assert result.exit_code == 1
