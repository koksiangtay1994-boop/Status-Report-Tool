"""Service for reading tasks from a text file."""

from pathlib import Path
from typing import Optional
from models.report import Task, TaskStatus


class TaskFileService:
    """Reads tasks from a structured text file."""

    def __init__(self, file_path: Optional[str] = None):
        if file_path:
            self.file_path = Path(file_path)
        else:
            self.file_path = Path("tasks.txt")

    def read_tasks(self) -> dict[str, list[Task]]:
        """Read tasks from file and return categorized tasks."""
        result = {
            "accomplished": [],
            "in_progress": [],
            "blockers": []
        }

        if not self.file_path.exists():
            return result

        content = self.file_path.read_text(encoding="utf-8")
        current_section = None

        for line in content.split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Detect section headers (must check before comment skip)
            if line.startswith("## ACCOMPLISHED"):
                current_section = "accomplished"
                continue
            elif line.startswith("## IN PROGRESS"):
                current_section = "in_progress"
                continue
            elif line.startswith("## BLOCKERS"):
                current_section = "blockers"
                continue

            # Skip comment lines (single #)
            if line.startswith("#"):
                continue

            # Parse task lines (starting with -)
            if line.startswith("-") and current_section:
                task_text = line[1:].strip()
                if task_text:
                    status_map = {
                        "accomplished": TaskStatus.COMPLETED,
                        "in_progress": TaskStatus.IN_PROGRESS,
                        "blockers": TaskStatus.BLOCKED
                    }
                    task = Task(
                        title=task_text,
                        status=status_map[current_section]
                    )
                    result[current_section].append(task)

        return result

    def file_exists(self) -> bool:
        """Check if task file exists."""
        return self.file_path.exists()
