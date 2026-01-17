"""SVG rendering service for status reports - Chip Floorplan Style."""

from models.report import Report, Task, TaskStatus


class SvgRenderer:
    """Renders individual task slides as SVG in chip floorplan style."""

    # Color scheme inspired by IC design tools (Cadence, Synopsys)
    COLORS = {
        "background": "#0a0e14",      # Dark navy background
        "grid": "#1a2332",            # Subtle grid lines
        "accomplished": {
            "primary": "#00ff9f",      # Neon green
            "secondary": "#00cc7f",
            "glow": "#00ff9f33"
        },
        "in_progress": {
            "primary": "#00d4ff",      # Cyan
            "secondary": "#00a8cc",
            "glow": "#00d4ff33"
        },
        "blocked": {
            "primary": "#ff5370",      # Red/Pink
            "secondary": "#cc4259",
            "glow": "#ff537033"
        },
        "text": "#e6e6e6",
        "text_dim": "#8892a2",
        "accent": "#bd93f9",           # Purple accent
        "trace": "#2d3a4d"             # Circuit traces
    }

    # SVG dimensions
    WIDTH = 800
    HEIGHT = 450

    def render_task(self, task: Task, index: int, total: int, author: str, week_string: str) -> str:
        """Render a single task as an SVG slide."""
        colors = self._get_status_colors(task.status)
        status_label = self._get_status_label(task.status)
        topic = task.topic or "General"

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.WIDTH} {self.HEIGHT}" width="{self.WIDTH}" height="{self.HEIGHT}">
  <defs>
    <!-- Glow filter for neon effect -->
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Grid pattern -->
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{self.COLORS['grid']}" stroke-width="0.5"/>
    </pattern>

    <!-- Circuit trace pattern -->
    <pattern id="traces" width="100" height="100" patternUnits="userSpaceOnUse">
      <path d="M0 50 H30 V20 H50 V50 H70 V80 H100" fill="none" stroke="{self.COLORS['trace']}" stroke-width="1"/>
      <path d="M50 0 V20" fill="none" stroke="{self.COLORS['trace']}" stroke-width="1"/>
      <circle cx="30" cy="50" r="2" fill="{self.COLORS['trace']}"/>
      <circle cx="50" cy="20" r="2" fill="{self.COLORS['trace']}"/>
      <circle cx="70" cy="50" r="2" fill="{self.COLORS['trace']}"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="100%" height="100%" fill="{self.COLORS['background']}"/>
  <rect width="100%" height="100%" fill="url(#grid)" opacity="0.5"/>
  <rect width="100%" height="100%" fill="url(#traces)" opacity="0.3"/>

  <!-- Corner decorations (IC pin-like) -->
  {self._render_corner_decorations(colors)}

  <!-- Header bar -->
  <rect x="40" y="30" width="720" height="4" fill="{colors['primary']}" filter="url(#glow)" rx="2"/>

  <!-- Status badge -->
  <rect x="40" y="50" width="120" height="28" fill="{colors['glow']}" stroke="{colors['primary']}" stroke-width="1" rx="4"/>
  <text x="100" y="69" font-family="JetBrains Mono, Consolas, monospace" font-size="12" fill="{colors['primary']}" text-anchor="middle" font-weight="bold">{status_label}</text>

  <!-- Topic block (main focus) -->
  <rect x="40" y="100" width="720" height="80" fill="{self.COLORS['background']}" stroke="{colors['primary']}" stroke-width="2" rx="4"/>
  <rect x="40" y="100" width="720" height="80" fill="{colors['glow']}" rx="4"/>

  <!-- Topic label -->
  <rect x="50" y="90" width="100" height="20" fill="{self.COLORS['background']}"/>
  <text x="55" y="104" font-family="JetBrains Mono, Consolas, monospace" font-size="10" fill="{self.COLORS['text_dim']}">TOPIC</text>

  <!-- Topic text -->
  <text x="60" y="150" font-family="JetBrains Mono, Consolas, monospace" font-size="28" fill="{colors['primary']}" font-weight="bold" filter="url(#glow)">{self._escape_xml(topic)}</text>

  <!-- Task description block -->
  <rect x="40" y="200" width="720" height="160" fill="{self.COLORS['background']}" stroke="{self.COLORS['trace']}" stroke-width="1" rx="4"/>

  <!-- Task label -->
  <rect x="50" y="190" width="120" height="20" fill="{self.COLORS['background']}"/>
  <text x="55" y="204" font-family="JetBrains Mono, Consolas, monospace" font-size="10" fill="{self.COLORS['text_dim']}">DESCRIPTION</text>

  <!-- Task text (wrapped) -->
  {self._render_wrapped_text(task.title, 60, 240, 700, 24, self.COLORS['text'])}

  <!-- Footer info bar -->
  <rect x="40" y="380" width="720" height="1" fill="{self.COLORS['trace']}"/>

  <!-- Author -->
  <text x="40" y="410" font-family="JetBrains Mono, Consolas, monospace" font-size="11" fill="{self.COLORS['text_dim']}">
    <tspan fill="{self.COLORS['accent']}">ENGINEER:</tspan> {self._escape_xml(author)}
  </text>

  <!-- Week -->
  <text x="300" y="410" font-family="JetBrains Mono, Consolas, monospace" font-size="11" fill="{self.COLORS['text_dim']}">
    <tspan fill="{self.COLORS['accent']}">WEEK:</tspan> {self._escape_xml(week_string)}
  </text>

  <!-- Slide counter -->
  <text x="760" y="410" font-family="JetBrains Mono, Consolas, monospace" font-size="11" fill="{self.COLORS['text_dim']}" text-anchor="end">
    <tspan fill="{colors['primary']}">{index}</tspan>/{total}
  </text>

  <!-- IC-style border frame -->
  {self._render_ic_frame(colors)}

</svg>'''
        return svg

    def _get_status_colors(self, status: TaskStatus) -> dict:
        """Get color scheme based on task status."""
        if status == TaskStatus.COMPLETED:
            return self.COLORS["accomplished"]
        elif status == TaskStatus.IN_PROGRESS:
            return self.COLORS["in_progress"]
        else:
            return self.COLORS["blocked"]

    def _get_status_label(self, status: TaskStatus) -> str:
        """Get display label for status."""
        labels = {
            TaskStatus.COMPLETED: "COMPLETED",
            TaskStatus.IN_PROGRESS: "IN PROGRESS",
            TaskStatus.BLOCKED: "BLOCKED"
        }
        return labels.get(status, "UNKNOWN")

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

    def _render_wrapped_text(self, text: str, x: int, y: int, max_width: int, line_height: int, color: str) -> str:
        """Render text with word wrapping."""
        words = text.split()
        lines = []
        current_line = []
        chars_per_line = max_width // 10  # Approximate chars that fit

        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= chars_per_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        svg_lines = []
        for i, line in enumerate(lines[:4]):  # Max 4 lines
            svg_lines.append(
                f'<text x="{x}" y="{y + i * line_height}" '
                f'font-family="JetBrains Mono, Consolas, monospace" '
                f'font-size="16" fill="{color}">{self._escape_xml(line)}</text>'
            )

        return '\n  '.join(svg_lines)

    def _render_corner_decorations(self, colors: dict) -> str:
        """Render IC pin-like corner decorations."""
        return f'''
  <!-- Top-left pins -->
  <rect x="10" y="40" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="10" y="50" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="10" y="60" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>

  <!-- Top-right pins -->
  <rect x="782" y="40" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="782" y="50" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="782" y="60" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>

  <!-- Bottom-left pins -->
  <rect x="10" y="387" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="10" y="397" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="10" y="407" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>

  <!-- Bottom-right pins -->
  <rect x="782" y="387" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="782" y="397" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
  <rect x="782" y="407" width="8" height="3" fill="{colors['primary']}" opacity="0.6"/>
'''

    def _render_ic_frame(self, colors: dict) -> str:
        """Render IC chip-like border frame."""
        return f'''
  <!-- Corner brackets -->
  <path d="M5 30 L5 5 L30 5" fill="none" stroke="{colors['secondary']}" stroke-width="2"/>
  <path d="M770 5 L795 5 L795 30" fill="none" stroke="{colors['secondary']}" stroke-width="2"/>
  <path d="M795 420 L795 445 L770 445" fill="none" stroke="{colors['secondary']}" stroke-width="2"/>
  <path d="M30 445 L5 445 L5 420" fill="none" stroke="{colors['secondary']}" stroke-width="2"/>
'''

    def render_summary(self, report: Report) -> str:
        """Render a summary SVG slide."""
        accomplished_count = len(report.accomplished.tasks)
        in_progress_count = len(report.in_progress.tasks)
        blockers_count = len(report.blockers.tasks)
        total = accomplished_count + in_progress_count + blockers_count

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.WIDTH} {self.HEIGHT}" width="{self.WIDTH}" height="{self.HEIGHT}">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{self.COLORS['grid']}" stroke-width="0.5"/>
    </pattern>
  </defs>

  <rect width="100%" height="100%" fill="{self.COLORS['background']}"/>
  <rect width="100%" height="100%" fill="url(#grid)" opacity="0.5"/>

  <!-- Title -->
  <text x="400" y="60" font-family="JetBrains Mono, Consolas, monospace" font-size="28" fill="{self.COLORS['accent']}" text-anchor="middle" font-weight="bold" filter="url(#glow)">WEEKLY STATUS REPORT</text>

  <text x="400" y="90" font-family="JetBrains Mono, Consolas, monospace" font-size="14" fill="{self.COLORS['text_dim']}" text-anchor="middle">{self._escape_xml(report.week_string)}</text>

  <!-- Stats blocks -->
  <!-- Accomplished -->
  <rect x="80" y="140" width="180" height="120" fill="{self.COLORS['background']}" stroke="{self.COLORS['accomplished']['primary']}" stroke-width="2" rx="4"/>
  <rect x="80" y="140" width="180" height="120" fill="{self.COLORS['accomplished']['glow']}" rx="4"/>
  <text x="170" y="190" font-family="JetBrains Mono, Consolas, monospace" font-size="48" fill="{self.COLORS['accomplished']['primary']}" text-anchor="middle" filter="url(#glow)">{accomplished_count}</text>
  <text x="170" y="240" font-family="JetBrains Mono, Consolas, monospace" font-size="12" fill="{self.COLORS['text_dim']}" text-anchor="middle">COMPLETED</text>

  <!-- In Progress -->
  <rect x="310" y="140" width="180" height="120" fill="{self.COLORS['background']}" stroke="{self.COLORS['in_progress']['primary']}" stroke-width="2" rx="4"/>
  <rect x="310" y="140" width="180" height="120" fill="{self.COLORS['in_progress']['glow']}" rx="4"/>
  <text x="400" y="190" font-family="JetBrains Mono, Consolas, monospace" font-size="48" fill="{self.COLORS['in_progress']['primary']}" text-anchor="middle" filter="url(#glow)">{in_progress_count}</text>
  <text x="400" y="240" font-family="JetBrains Mono, Consolas, monospace" font-size="12" fill="{self.COLORS['text_dim']}" text-anchor="middle">IN PROGRESS</text>

  <!-- Blockers -->
  <rect x="540" y="140" width="180" height="120" fill="{self.COLORS['background']}" stroke="{self.COLORS['blocked']['primary']}" stroke-width="2" rx="4"/>
  <rect x="540" y="140" width="180" height="120" fill="{self.COLORS['blocked']['glow']}" rx="4"/>
  <text x="630" y="190" font-family="JetBrains Mono, Consolas, monospace" font-size="48" fill="{self.COLORS['blocked']['primary']}" text-anchor="middle" filter="url(#glow)">{blockers_count}</text>
  <text x="630" y="240" font-family="JetBrains Mono, Consolas, monospace" font-size="12" fill="{self.COLORS['text_dim']}" text-anchor="middle">BLOCKERS</text>

  <!-- Author info -->
  <text x="400" y="320" font-family="JetBrains Mono, Consolas, monospace" font-size="14" fill="{self.COLORS['text_dim']}" text-anchor="middle">
    <tspan fill="{self.COLORS['accent']}">ENGINEER:</tspan> {self._escape_xml(report.author)}
  </text>

  <!-- Total tasks -->
  <text x="400" y="360" font-family="JetBrains Mono, Consolas, monospace" font-size="12" fill="{self.COLORS['text_dim']}" text-anchor="middle">
    TOTAL TASKS: <tspan fill="{self.COLORS['text']}">{total}</tspan>
  </text>

  <!-- Corner brackets -->
  <path d="M5 30 L5 5 L30 5" fill="none" stroke="{self.COLORS['accent']}" stroke-width="2"/>
  <path d="M770 5 L795 5 L795 30" fill="none" stroke="{self.COLORS['accent']}" stroke-width="2"/>
  <path d="M795 420 L795 445 L770 445" fill="none" stroke="{self.COLORS['accent']}" stroke-width="2"/>
  <path d="M30 445 L5 445 L5 420" fill="none" stroke="{self.COLORS['accent']}" stroke-width="2"/>

</svg>'''
        return svg
