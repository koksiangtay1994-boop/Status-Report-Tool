"""CLI entry point for the status report generator."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from core.generator import ReportGenerator
from models.report import Task, TaskStatus


def parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def prompt_for_items(section_name: str) -> list[str]:
    """Prompt user to enter items for a section."""
    print(f"\n{'='*50}")
    print(f"  {section_name.upper()}")
    print(f"{'='*50}")
    print(f"Enter your {section_name.lower()} items (one per line).")
    print("Press Enter twice when done, or type 'skip' to skip.\n")

    items = []
    while True:
        try:
            line = input(f"  [{len(items) + 1}] ").strip()
        except EOFError:
            break

        if line.lower() == 'skip':
            return []
        if not line:
            if items:
                break
            continue
        items.append(line)

    return items


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate weekly status reports from Git history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Interactive mode - prompts for input
  %(prog)s --no-interactive         Skip prompts, use Git data only
  %(prog)s -o my_report.html        Save to specific file
  %(prog)s --repo /path/to/repo     Generate from different repository
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
        "-p", "--in-progress",
        action="append",
        dest="in_progress",
        help="Add an in-progress item (can be used multiple times)",
        default=None
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip interactive prompts"
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

        # Collect in-progress items and blockers
        in_progress_items = args.in_progress or []
        blocker_items = args.blockers or []

        # Interactive mode
        if not args.no_interactive and not args.print_html:
            print("\n" + "="*50)
            print("  WEEKLY STATUS REPORT GENERATOR")
            print("="*50)

            # Show what will be auto-populated
            print("\nGit commits will be automatically added to 'Accomplished'.")

            # Prompt for In Progress
            in_progress_input = prompt_for_items("In Progress")
            in_progress_items.extend(in_progress_input)

            # Prompt for Blockers
            blocker_input = prompt_for_items("Blockers")
            blocker_items.extend(blocker_input)

        # Generate report
        report = generator.generate(
            week_start=args.week_start,
            week_end=args.week_end,
            author=args.author,
            blockers=blocker_items if blocker_items else None,
            in_progress=in_progress_items if in_progress_items else None
        )

        # Output
        if args.print_html:
            html = generator.render_html(report)
            print(html)
        else:
            output_path = generator.save_html(report, args.output)

            print(f"\n{'='*50}")
            print("  REPORT GENERATED")
            print(f"{'='*50}")
            print(f"\nFile: {output_path.absolute()}")
            print(f"\nWeekly Status Report - {report.week_string}")
            print(f"Author: {report.author}")
            print(f"\n  Accomplished:  {len(report.accomplished.tasks)} items")
            print(f"  In Progress:   {len(report.in_progress.tasks)} items")
            print(f"  Blockers:      {len(report.blockers.tasks)} items")
            print()

        return 0

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
