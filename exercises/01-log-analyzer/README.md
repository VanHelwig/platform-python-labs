# Exercise 01 — Production Log Analyzer

Implement a Python command-line log analyzer. Do not change the supplied tests to make a failing implementation pass.

## Log format

Each valid line has four whitespace-separated fields, with the fourth field containing the remainder of the line:

`TIMESTAMP LEVEL SERVICE MESSAGE`

- Timestamp: ISO 8601 UTC ending in `Z`, e.g. `2026-11-19T10:15:01Z` (seconds precision).
- Level: one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (case-sensitive).
- Service: nonempty ASCII identifier matching `[A-Za-z0-9_-]+`.
- Message: nonempty text (leading/trailing whitespace ignored).
- Blank lines are malformed and count as skipped lines.
- Invalid timestamps, levels, service names, and missing messages are malformed.

## CLI contract

`python starter/log_analyzer.py PATH [--start ISO_TIMESTAMP] [--end ISO_TIMESTAMP] [--format text|json]`

- `--format` defaults to `text`.
- `--start` and `--end` are inclusive UTC timestamps using the same format as log entries.
- Reject an invalid date/time argument or a start after end with exit code 2.
- Missing or unreadable input files: print a useful error to stderr and exit 1.
- Success: exit 0, including if no valid entries remain after filtering.
- Malformed log lines count as skipped regardless of the time filter.
- Valid entries outside the selected time range do not contribute to any summary count.
- Output must be deterministic. Never include unfiltered log messages in diagnostic output.

## JSON schema

Produce a single JSON object with these keys:

```json
{
  "total_lines": 4,
  "valid_entries": 4,
  "skipped_lines": 0,
  "levels": {"DEBUG": 0, "INFO": 1, "WARNING": 1, "ERROR": 2, "CRITICAL": 0},
  "errors_by_service": {"database": 2},
  "top_error_messages": [{"message": "Connection timeout", "count": 2}]
}
```

- `total_lines` counts every physical line, including blank lines, before filtering.
- `valid_entries` counts valid entries included by the time filter.
- `skipped_lines` counts malformed lines only.
- `levels` always contains all five keys, including zero counts.
- `errors_by_service` includes services with at least one ERROR or CRITICAL entry, ordered alphabetically in JSON output.
- `top_error_messages` includes up to three ERROR/CRITICAL messages, sorted by descending frequency and then ascending message alphabetically for ties.
- Error messages are grouped by exact, case-sensitive text across services.

## Text output

Print a readable report containing the same metrics. The precise layout is your choice; the JSON output is the machine-readable contract.

## Suggested workflow

1. Read the tests and inspect the sample log file.
2. Implement parsing and summary aggregation.
3. Implement argument parsing, validation, output, and error handling.
4. Run `pytest -q exercises/01-log-analyzer/tests` from the repository root.
5. Run `ruff check exercises/01-log-analyzer` and `ruff format --check exercises/01-log-analyzer`.

The supplied tests cover the public behavior, not every edge case. Add your own tests as you identify additional risks.
