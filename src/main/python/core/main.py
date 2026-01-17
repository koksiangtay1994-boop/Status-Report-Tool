"""CLI entry point for the status report generator."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from core.generator import ReportGenerator


def parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate weekly status reports from Git history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Generate report for current week
  %(prog)s -o my_report.html        Save to specific file
  %(prog)s --repo /path/to/repo     Generate from different repository
  %(prog)s --blocker "Waiting for API access"  Add a blocker
        """
    )

    parser.add_argument(
        "-r", "--repo",
        help="Path to Git repository (default: current directory)",
        default=None
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: output/status_report_YYYYMMDD.html)",
        default=None
    )
    parser.add_argument(
        "--author",
        help="Filter commits by author (default: git config user.name)",
        default=None
    )
    parser.add_argument(
        "--week-start",
        help="Week start date (YYYY-MM-DD)",
        type=parse_date,
        default=None
    )
    parser.add_argument(
        "--week-end",
        help="Week end date (YYYY-MM-DD)",
        type=parse_date,
        default=None
    )
    parser.add_argument(
        "-b", "--blocker",
        action="append",
        dest="blockers",
        help="Add a blocker (can be used multiple times)",
        default=None
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_html",
        help="Print HTML to stdout instead of saving to file"
    )

    args = parser.parse_args()

    try:
        # Initialize generator
        generator = ReportGenerator(repo_path=args.repo)

        # Generate report
        report = generator.generate(
            week_start=args.week_start,
            week_end=args.week_end,
            author=args.author,
            blockers=args.blockers
        )

        # Output
        if args.print_html:
            html = generator.render_html(report)
            print(html)
        else:
            output_path = generator.save_html(report, args.output)
            print(f"Report generated: {output_path.absolute()}")

            # Summary
            print(f"\nWeekly Status Report - {report.week_string}")
            print(f"Author: {report.author}")
            print(f"Accomplished: {len(report.accomplished.tasks)} items")
            print(f"In Progress: {len(report.in_progress.tasks)} items")
            print(f"Blockers: {len(report.blockers.tasks)} items")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
