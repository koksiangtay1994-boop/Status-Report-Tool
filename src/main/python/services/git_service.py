"""Service for extracting data from Git repositories."""

import subprocess
import re
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from models.report import Task, TaskStatus


class GitService:
    """Extracts commit and PR information from a Git repository."""

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()

    def _run_git(self, *args: str) -> str:
        """Run a git command and return output."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")
        return result.stdout.strip()

    def get_author_name(self) -> str:
        """Get the configured git user name."""
        try:
            return self._run_git("config", "user.name")
        except RuntimeError:
            return "Unknown Author"

    def get_author_email(self) -> str:
        """Get the configured git user email."""
        try:
            return self._run_git("config", "user.email")
        except RuntimeError:
            return ""

    def get_commits(
        self,
        since: datetime,
        until: datetime,
        author: Optional[str] = None
    ) -> list[Task]:
        """Get commits within a date range."""
        since_str = since.strftime("%Y-%m-%d")
        until_str = until.strftime("%Y-%m-%d")

        args = [
            "log",
            f"--since={since_str}",
            f"--until={until_str}",
            "--pretty=format:%H|%s|%ad",
            "--date=iso"
        ]

        if author:
            args.append(f"--author={author}")

        try:
            output = self._run_git(*args)
        except RuntimeError:
            return []

        if not output:
            return []

        tasks = []
        for line in output.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 2)
            if len(parts) >= 2:
                commit_hash = parts[0][:7]
                message = parts[1]
                date = None
                if len(parts) >= 3:
                    try:
                        date = datetime.fromisoformat(parts[2].replace(" ", "T").split("+")[0])
                    except ValueError:
                        pass

                task = Task(
                    title=message,
                    commit_hash=commit_hash,
                    status=TaskStatus.COMPLETED,
                    date=date
                )
                tasks.append(task)

        return tasks

    def get_branches_in_progress(self) -> list[Task]:
        """Get branches that might represent work in progress."""
        try:
            output = self._run_git("branch", "--list")
        except RuntimeError:
            return []

        tasks = []
        current_branch = None

        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("* "):
                current_branch = line[2:]
            elif line and line not in ["main", "master", "develop"]:
                branch_name = line.replace("-", " ").replace("_", " ")
                if not branch_name.lower().startswith(("feature", "fix", "bugfix")):
                    title = branch_name
                else:
                    title = " ".join(branch_name.split()[1:]) if " " in branch_name else branch_name

                if title:
                    tasks.append(Task(
                        title=f"Branch: {title}",
                        status=TaskStatus.IN_PROGRESS
                    ))

        return tasks

    def get_recent_pr_references(self, since: datetime, until: datetime) -> list[Task]:
        """Extract PR references from commit messages."""
        commits = self.get_commits(since, until)
        pr_pattern = re.compile(r"#(\d+)")

        pr_tasks = []
        seen_prs = set()

        for commit in commits:
            matches = pr_pattern.findall(commit.title)
            for pr_num in matches:
                if pr_num not in seen_prs:
                    seen_prs.add(pr_num)
                    pr_tasks.append(Task(
                        title=commit.title,
                        pr_number=int(pr_num),
                        status=TaskStatus.COMPLETED,
                        date=commit.date
                    ))

        return pr_tasks


def get_week_range(reference_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Get the start and end of the week containing the reference date."""
    if reference_date is None:
        reference_date = datetime.now()

    # Monday = 0, Sunday = 6
    start = reference_date - timedelta(days=reference_date.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)

    return start, end
