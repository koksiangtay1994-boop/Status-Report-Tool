"""Core report generation logic."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from models.report import Report, Task, TaskStatus
from services.git_service import GitService, get_week_range
from services.html_renderer import HtmlRenderer


class ReportGenerator:
    """Generates weekly status reports from Git data."""

    def __init__(self, repo_path: Optional[str] = None):
        self.git_service = GitService(repo_path)
        self.html_renderer = HtmlRenderer()

    def generate(
        self,
        week_start: Optional[datetime] = None,
        week_end: Optional[datetime] = None,
        author: Optional[str] = None,
        blockers: Optional[list[str]] = None,
        in_progress: Optional[list[str]] = None
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

        # Get commits for accomplished section
        commits = self.git_service.get_commits(week_start, week_end, author)
        for commit in commits:
            report.accomplished.add_task(commit)

        # Add manually specified in-progress items
        if in_progress:
            for item_text in in_progress:
                report.in_progress.add_task(Task(
                    title=item_text,
                    status=TaskStatus.IN_PROGRESS
                ))

        # Add manually specified blockers
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
