"""SVG rendering service for status reports - Chip Floorplan Style."""

from models.report import Report, Task, TaskStatus


class SvgRenderer:
    """Renders individual task slides as SVG in chip floorplan style."""

    # MediaTek logo (base64 encoded PNG)
    MEDIATEK_LOGO = "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"

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

  <!-- MediaTek Logo -->
  <image x="620" y="45" width="130" height="35" href="data:image/png;base64,{self.MEDIATEK_LOGO}"/>

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

  <!-- MediaTek Logo -->
  <image x="620" y="15" width="150" height="40" href="data:image/png;base64,{self.MEDIATEK_LOGO}"/>

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
