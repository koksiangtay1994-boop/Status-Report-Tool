"""HTML rendering service for status reports."""

from models.report import Report, Section


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Status Report - {week_string}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f5f5f5;
        }}
        .report {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        .header {{
            border-bottom: 2px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #1e40af;
            font-size: 1.8rem;
            margin-bottom: 8px;
        }}
        .header .meta {{
            color: #666;
            font-size: 0.95rem;
        }}
        .header .meta span {{
            margin-right: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            padding: 8px 12px;
            border-radius: 4px;
        }}
        .section.accomplished h2 {{
            background: #dcfce7;
            color: #166534;
        }}
        .section.in-progress h2 {{
            background: #fef3c7;
            color: #92400e;
        }}
        .section.blockers h2 {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .task-list {{
            list-style: none;
        }}
        .task-list li {{
            padding: 10px 12px;
            border-left: 3px solid #e5e7eb;
            margin-bottom: 8px;
            background: #fafafa;
            border-radius: 0 4px 4px 0;
        }}
        .task-list li:hover {{
            border-left-color: #2563eb;
        }}
        .task-title {{
            font-weight: 500;
        }}
        .task-meta {{
            font-size: 0.85rem;
            color: #666;
            margin-top: 4px;
        }}
        .task-meta code {{
            background: #e5e7eb;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8rem;
        }}
        .empty-section {{
            color: #999;
            font-style: italic;
            padding: 10px 12px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 0.85rem;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="report">
        <div class="header">
            <h1>Weekly Status Report</h1>
            <div class="meta">
                <span><strong>Author:</strong> {author}</span>
                <span><strong>Week:</strong> {week_string}</span>
            </div>
        </div>

        <div class="section accomplished">
            <h2>Accomplished</h2>
            {accomplished_content}
        </div>

        <div class="section in-progress">
            <h2>In Progress</h2>
            {in_progress_content}
        </div>

        <div class="section blockers">
            <h2>Blockers</h2>
            {blockers_content}
        </div>

        <div class="footer">
            Generated on {generated_at}
        </div>
    </div>
</body>
</html>"""


class HtmlRenderer:
    """Renders reports to HTML format."""

    def render(self, report: Report) -> str:
        """Render a report to HTML."""
        return HTML_TEMPLATE.format(
            week_string=report.week_string,
            author=report.author,
            accomplished_content=self._render_section(report.accomplished),
            in_progress_content=self._render_section(report.in_progress),
            blockers_content=self._render_section(report.blockers),
            generated_at=report.generated_at.strftime("%B %d, %Y at %I:%M %p")
        )

    def _render_section(self, section: Section) -> str:
        """Render a section's tasks to HTML."""
        if not section.tasks:
            return '<p class="empty-section">No items to report.</p>'

        items = []
        for task in section.tasks:
            meta_parts = []
            if task.commit_hash:
                meta_parts.append(f"<code>{task.commit_hash}</code>")
            if task.pr_number:
                meta_parts.append(f"PR #{task.pr_number}")
            if task.date:
                meta_parts.append(task.date.strftime("%b %d"))

            meta_html = ""
            if meta_parts:
                meta_html = f'<div class="task-meta">{" · ".join(meta_parts)}</div>'

            description_html = ""
            if task.description:
                description_html = f'<div class="task-description">{task.description}</div>'

            items.append(f"""<li>
                <div class="task-title">{task.title}</div>
                {description_html}
                {meta_html}
            </li>""")

        return f'<ul class="task-list">{"".join(items)}</ul>'
