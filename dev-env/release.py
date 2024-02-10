"""Script that prepares a new release of a version."""

import argparse
import json
import logging
import re
import tempfile
from functools import cached_property
from itertools import product
from pathlib import Path
from typing import Optional

import git
import tomli
from packaging.version import Version, InvalidVersion

# Set up logging
logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s",
    datefmt="[%X]",
    level=logging.INFO,
)


logger = logging.getLogger("create-release")


class Release:
    """Release class."""

    version_pattern: str = r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']'

    def __init__(self, package_name: str, repo_dir: str) -> None:

        self.package_name = package_name
        self.repo_dir = Path(repo_dir)
        logger.info(
            "Searching for packages/config with the name: %s", package_name
        )
        logger.debug("Reading current git config")
        self.git_config = (
            Path(git.Repo(search_parent_directories=True).git_dir) / "config"
        ).read_text()

    def tag_version(self) -> None:
        """Tag the latest git version."""

    @cached_property
    def repo_url(self) -> str:
        """Get the current git repo url."""
        repo = git.Repo(search_parent_directories=True)
        return repo.remotes.origin.url

    @cached_property
    def git_tag(self) -> Version:
        """Get the latest git tag."""
        logger.debug("Searching for the latest tag")
        repo = git.Repo(self.repo_dir)
        try:
            # Get the latest tag on the main branch
            return Version(
                repo.git.describe("--tags", "--abbrev=0", "main").lstrip("v")
            )
        except git.exc.GitCommandError:
            logger.debug("No tag found")
        except InvalidVersion:
            logger.debug("Tag found, but could not parse version")
        return Version("0.0.0")

    @property
    def version(self) -> Version:
        """Get the version of the current software."""
        logger.debug("Searching for software version.")
        pck_dirs = Path("src") / self.package_name, Path(
            "src"
        ) / self.package_name.replace("-", "_")
        files = [
            self.repo_dir / f[1] / f[0]
            for f in product(("_version.py", "__init__.py"), pck_dirs)
        ]
        files += [
            self.repo_dir / Path("package.json"),
            self.repo_dir / "pyproject.toml",
        ]
        for file in files:
            if file.is_file():
                if file.suffix == ".py":
                    match = re.search(self.version_pattern, file.read_text())
                    if match:
                        return Version(match.group(1))
                elif file.suffix == ".json":
                    content = json.loads(file.read_text())
                    if "version" in content:
                        return Version(content["version"])
                elif file.suffix == ".toml":
                    content = tomli.loads(file.read_text())
                    if "project" in content:
                        return Version(content["project"]["version"])
        raise ValueError("Could not find version")

    def _clone_repo_from_franch(self, branch: str = "main") -> None:

        logger.debug(
            "Cloning repository from %s with branch %s to %s",
            self.repo_url,
            self.repo_dir,
            branch,
        )
        git.Repo.clone_from(self.repo_url, self.repo_dir, branch=branch)
        (self.repo_dir / ".git" / "config").write_text(self.git_config)

    def _check_change_lock_file(self) -> None:
        """Check if the current version was added to the change lock file."""
        logger.debug("Checking for change log file.")
        if not self._change_lock_file.is_file():
            logger.critical(
                "Could not find change log file. Create one first."
            )
            raise SystemExit
        if "v{self.version}" not in self._change_lock_file.read_text("utf-8"):
            logger.critical(
                "You need to add the version v%s to the %s change log file",
                self.version,
                self._change_lock_file.relative_to(self.repo_dir),
            )
            raise SystemExit

    @cached_property
    def _change_lock_file(self) -> Path:
        """Find the change lock file."""
        for prefix, suffix in product(
            ("changelog", "whats-new"), (".rst", ".md")
        ):
            for search_pattern in (prefix, prefix.upper()):
                glob_pattern = f"{search_pattern}{suffix}"
                logger.debug("Searching for %s", glob_pattern)
                for file in self.repo_dir.rglob(glob_pattern):
                    return file
        return Path(tempfile.mktemp())

    def tag_new_version(self, branch: str = "main") -> None:
        """Tag a new git version."""
        self._clone_repo_from_franch(branch)
        cloned_repo = git.Repo(self.repo_dir)
        if self.version <= self.git_tag:
            logger.critical(
                "Tag version: %s is the same as current version %s"
                ", you need to bump the verion number first.",
                self.version,
                self.git_tag,
            )
            raise SystemExit
        self._check_change_lock_file()
        head = cloned_repo.head.reference
        # cloned_repo.config_writer().release()
        message = f"Create a release for v{self.version}"
        cloned_repo.create_tag(f"v{self.version}", ref=head, message=message)
        # cloned_repo.git.push("--tags")

    @classmethod
    def cli(cls, temp_dir: str) -> "Release":
        """Command line interface."""

        parser = argparse.ArgumentParser(
            description="Prepare the release of a package."
        )
        parser.add_argument("name", help="The name of the software/package.")
        parser.add_argument(
            "-v", "--verbose", help="Enable debug mode.", action="store_true"
        )
        args = parser.parse_args()
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        return cls(args.name, temp_dir)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temporary_dir:
        try:
            release = Release.cli(temporary_dir)
            release.tag_new_version("init")
        except Exception as error:
            if logger.getEffectiveLevel() == logging.DEBUG:
                raise
            logger.error("An error occurred: %s", error)
