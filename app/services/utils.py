# app/services/utils.py
import logging
import subprocess

logger = logging.getLogger(__name__)


def run_command(command: list[str]) -> str:
    """
    Executes a shell command and returns its output as a string.

    Args:
        command (list[str]): The shell command to execute, as a list of arguments.

    Returns:
        str: The standard output of the command

    Raises:
        HTTPException: If the command execution fails.
    """
    logger.info(f"Executing command: {command}")
    try:
        result = subprocess.run(
            command,
            check=True,  # Raises an error if the command fails
            capture_output=True,  # Captures stdout and stderr
            text=True  # Decodes stdout and stderr as text
        )
        logger.info(f"Command stdout:\n{result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed. Error:\n{e.stderr.strip()}")
        raise e
