"""Data models for weekly status reports."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(Enum):
    """Status of a task."""
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Represents a single task or work item."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.COMPLETED
    commit_hash: Optional[str] = None
    pr_number: Optional[int] = None
    date: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "commit_hash": self.commit_hash,
            "pr_number": self.pr_number,
            "date": self.date.isoformat() if self.date else None
        }


@dataclass
class Section:
    """A section in the status report."""
    name: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tasks": [t.to_dict() for t in self.tasks]
        }


@dataclass
class Report:
    """Weekly status report."""
    author: str
    week_start: datetime
    week_end: datetime
    accomplished: Section = field(default_factory=lambda: Section("Accomplished"))
    in_progress: Section = field(default_factory=lambda: Section("In Progress"))
    blockers: Section = field(default_factory=lambda: Section("Blockers"))
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def week_string(self) -> str:
        return f"{self.week_start.strftime('%b %d')} - {self.week_end.strftime('%b %d, %Y')}"

    def to_dict(self) -> dict:
        return {
            "author": self.author,
            "week_start": self.week_start.isoformat(),
            "week_end": self.week_end.isoformat(),
            "week_string": self.week_string,
            "accomplished": self.accomplished.to_dict(),
            "in_progress": self.in_progress.to_dict(),
            "blockers": self.blockers.to_dict(),
            "generated_at": self.generated_at.isoformat()
        }
