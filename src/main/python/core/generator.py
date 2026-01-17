"""Core report generation logic."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from models.report import Report, Task, TaskStatus
from services.git_service import GitService, get_week_range
from services.html_renderer import HtmlRenderer
from services.task_file_service import TaskFileService
from services.svg_renderer import SvgRenderer


class ReportGenerator:
    """Generates weekly status reports from task file or Git data."""

    def __init__(self, repo_path: Optional[str] = None, task_file: Optional[str] = None):
        self.git_service = GitService(repo_path)
        self.html_renderer = HtmlRenderer()
        self.svg_renderer = SvgRenderer()
        self.task_file_service = TaskFileService(task_file)

    def generate(
        self,
        week_start: Optional[datetime] = None,
        week_end: Optional[datetime] = None,
        author: Optional[str] = None,
        blockers: Optional[list[str]] = None,
        in_progress: Optional[list[str]] = None,
        use_task_file: bool = True
    ) -> Report:
        """Generate a weekly status report."""
        # Get week range
        if week_start is None or week_end is None:
            week_start, week_end = get_week_range()

        # Get author info
        if author is None:
            author = self.git_service.get_author_name()

        # Create report
        report = Report(
            author=author,
            week_start=week_start,
            week_end=week_end
        )

        # Try to read from task file first
        if use_task_file and self.task_file_service.file_exists():
            file_tasks = self.task_file_service.read_tasks()

            for task in file_tasks["accomplished"]:
                report.accomplished.add_task(task)
            for task in file_tasks["in_progress"]:
                report.in_progress.add_task(task)
            for task in file_tasks["blockers"]:
                report.blockers.add_task(task)
        else:
            # Fallback to git commits for accomplished section
            commits = self.git_service.get_commits(week_start, week_end, author)
            for commit in commits:
                report.accomplished.add_task(commit)

        # Add manually specified in-progress items (from CLI)
        if in_progress:
            for item_text in in_progress:
                report.in_progress.add_task(Task(
                    title=item_text,
                    status=TaskStatus.IN_PROGRESS
                ))

        # Add manually specified blockers (from CLI)
        if blockers:
            for blocker_text in blockers:
                report.blockers.add_task(Task(
                    title=blocker_text,
                    status=TaskStatus.BLOCKED
                ))

        return report

    def render_html(self, report: Report) -> str:
        """Render a report to HTML."""
        return self.html_renderer.render(report)

    def save_html(
        self,
        report: Report,
        output_path: Optional[str] = None
    ) -> Path:
        """Save a report as an HTML file."""
        if output_path is None:
            filename = f"status_report_{report.week_start.strftime('%Y%m%d')}.html"
            output_path = Path("output") / filename

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = self.render_html(report)
        output_path.write_text(html_content, encoding="utf-8")

        return output_path

    def save_svg_slides(
        self,
        report: Report,
        output_dir: Optional[str] = None
    ) -> list[Path]:
        """Save report as multiple SVG slide files (one per task)."""
        if output_dir is None:
            output_dir = Path("output") / f"slides_{report.week_start.strftime('%Y%m%d')}"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Collect all tasks
        all_tasks = []
        all_tasks.extend(report.accomplished.tasks)
        all_tasks.extend(report.in_progress.tasks)
        all_tasks.extend(report.blockers.tasks)

        total = len(all_tasks)
        saved_files = []

        # Save summary slide first
        summary_svg = self.svg_renderer.render_summary(report)
        summary_path = output_dir / "00_summary.svg"
        summary_path.write_text(summary_svg, encoding="utf-8")
        saved_files.append(summary_path)

        # Save individual task slides
        for i, task in enumerate(all_tasks, 1):
            svg_content = self.svg_renderer.render_task(
                task=task,
                index=i,
                total=total,
                author=report.author,
                week_string=report.week_string
            )

            # Create filename with topic
            topic_slug = (task.topic or "general").lower().replace(" ", "_")[:20]
            filename = f"{i:02d}_{topic_slug}.svg"
            file_path = output_dir / filename

            file_path.write_text(svg_content, encoding="utf-8")
            saved_files.append(file_path)

        return saved_files
