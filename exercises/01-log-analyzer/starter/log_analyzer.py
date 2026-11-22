"""Exercise 01: production log analyzer.

Implement the CLI described in ../README.md.

You may add helpers, functions, classes, or modules as needed.
"""

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
VALID_LOG_LEVELS = frozenset(LOG_LEVELS)
ERROR_LEVELS = frozenset({"ERROR", "CRITICAL"})


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp and require timezone information."""
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid timestamp: {value}") from exc

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise argparse.ArgumentTypeError(
            f"Timestamp must include timezone information: {value}"
        )

    return timestamp


def parse_log_line(line: str) -> dict | None:
    """Parse a single log entry, returning None if malformed."""
    parts = line.rstrip("\r\n").split(maxsplit=3)

    SERVICE_PATTERN = re.compile(r"[A-Za-z0-9_-]+")

    if len(parts) != 4:
        return None

    timestamp, level, service, message = parts

    if level not in VALID_LOG_LEVELS:
        return None

    if SERVICE_PATTERN.fullmatch(service) is None:
        return None

    try:
        timestamp = parse_timestamp(timestamp)
    except argparse.ArgumentTypeError:
        return None

    return {
        "timestamp": timestamp,
        "level": level,
        "service": service,
        "message": message,
    }


def analyze_logs(
    lines: Iterable[str],
    start: datetime | None = None,
    end: datetime | None = None,
) -> dict:
    """Analyze log entries and return summary statistics."""
    severity_counts = Counter(dict.fromkeys(LOG_LEVELS, 0))
    errors_by_service = Counter()
    error_messages = Counter()

    total_lines = 0
    valid_entries = 0
    skipped_lines = 0

    for line in lines:
        total_lines += 1

        entry = parse_log_line(line)

        if entry is None:
            skipped_lines += 1
            continue

        timestamp = entry["timestamp"]

        if start is not None and timestamp < start:
            continue

        if end is not None and timestamp > end:
            continue

        valid_entries += 1
        severity_counts[entry["level"]] += 1

        if entry["level"] in ERROR_LEVELS:
            errors_by_service[entry["service"]] += 1
            error_messages[entry["message"]] += 1

    return {
        "total_lines": total_lines,
        "valid_entries": valid_entries,
        "skipped_lines": skipped_lines,
        "levels": dict(severity_counts),
        "errors_by_service": dict(errors_by_service),
        "top_error_messages": [
            {"message": message, "count": count}
            for message, count in error_messages.most_common(3)
        ],
    }


def format_text(summary: dict) -> str:
    """Format analysis results as human-readable text."""
    lines = [
        "Production Log Analysis",
        "=======================",
        f"Total lines:     {summary['total_lines']}",
        f"Valid entries:   {summary['valid_entries']}",
        f"Skipped lines:   {summary['skipped_lines']}",
        "",
        "Severity Counts",
        "---------------",
    ]

    for level in LOG_LEVELS:
        lines.append(f"{level:<10} {summary['levels'][level]}")

    lines.extend(
        [
            "",
            "Errors by Service",
            "-----------------",
        ]
    )

    if summary["errors_by_service"]:
        for service, count in sorted(summary["errors_by_service"].items()):
            lines.append(f"{service}: {count}")
    else:
        lines.append("No errors found.")

    lines.extend(
        [
            "",
            "Top Error Messages",
            "------------------",
        ]
    )

    if summary["top_error_messages"]:
        for index, entry in enumerate(summary["top_error_messages"], start=1):
            lines.append(f"{index}. {entry['message']} ({entry['count']})")
    else:
        lines.append("No error messages found.")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run the analyzer and return an appropriate process exit code."""
    parser = argparse.ArgumentParser(description="Analyze production application logs.")

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

    if args.start is not None and args.end is not None and args.start > args.end:
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
