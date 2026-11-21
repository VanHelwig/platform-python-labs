"""Exercise 01: production log analyzer.

Implement the CLI described in ../README.md.

You may add helpers, functions, classes, or modules as needed.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp and require timezone information."""
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid timestamp: {value}"
        ) from exc

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise argparse.ArgumentTypeError(
            f"Timestamp must include timezone information: {value}"
        )

    return timestamp


def parse_log_line(line: str) -> dict | None:
    """Parse a single log entry, returning None if malformed."""
    raise NotImplementedError


def analyze_logs(
    lines,
    start: datetime | None = None,
    end: datetime | None = None,
) -> dict:
    """Analyze log entries and return summary statistics."""
    raise NotImplementedError


def format_text(summary: dict) -> str:
    """Format analysis results as human-readable text."""
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Run the analyzer and return an appropriate process exit code."""
    parser = argparse.ArgumentParser(
        description="Analyze production application logs."
    )

    parser.add_argument(
        "log_file",
        type=Path,
        help="Path to the log file to analyze.",
    )

    parser.add_argument(
        "--start",
        type=parse_timestamp,
        help="Inclusive start timestamp (ISO 8601).",
    )

    parser.add_argument(
        "--end",
        type=parse_timestamp,
        help="Inclusive end timestamp (ISO 8601).",
    )

    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )

    args = parser.parse_args(argv)

    if args.start and args.end and args.start > args.end:
        parser.error("--start must not be later than --end")

    try:
        with args.log_file.open("r", encoding="utf-8") as file:
            summary = analyze_logs(
                file,
                start=args.start,
                end=args.end,
            )
    except (OSError, UnicodeError) as exc:
        print(f"Error reading log file: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print(format_text(summary))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())