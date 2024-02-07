"""Simple script to start and stop the storage service."""

import argparse
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("start-stop")


def start_storage_service(
    pid_file: Path = Path(".storage-service.pid"),
) -> None:
    """Starts the storage-service process."""
    if pid_file.is_file():
        return
    try:
        # Start the storage-service process
        process = subprocess.Popen(["storage-service"])

        # Write the process ID to a file
        time.sleep(2)
        if process.poll() is None:
            logger.info("storage-service started successfully.")
            with pid_file.open("w") as f:
                f.write(str(process.pid))
    except Exception as e:
        logger.error("Error starting storage-service: %s", e)


def kill_storage_service(
    pid_file: Path = Path(".storage-service.pid"),
) -> None:
    """Kills the storage-service process."""
    if not pid_file.is_file():
        logger.warning("No .storage-service.pid file found.")
        return
    try:
        # Read the process ID from the file
        with pid_file.open("r") as f:
            pid = int(f.read())

        # Try to kill the process
        os.kill(pid, 15)  # SIGTERM
        logger.info("storage-service with PID %d killed successfully.", pid)

        # Remove the file
        pid_file.unlink()
    except Exception as e:
        logger.error("Error killing storage-service: %s", e)


def main() -> None:
    """Parse command line arguments and execute corresponding actions."""
    parser = argparse.ArgumentParser(
        description="Manage storage-service process."
    )
    parser.add_argument(
        "--start", action="store_true", help="Start storage-service process."
    )
    parser.add_argument(
        "--kill", action="store_true", help="Kill storage-service process."
    )

    args = parser.parse_args()

    if args.start:
        start_storage_service()
    elif args.kill:
        kill_storage_service()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
