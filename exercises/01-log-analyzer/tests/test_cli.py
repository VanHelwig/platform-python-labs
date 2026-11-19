"""Black-box acceptance tests for the log analyzer CLI."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "starter" / "log_analyzer.py"
FIXTURE = ROOT / "fixtures" / "application.log"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_json_summary():
    result = run_cli(str(FIXTURE), "--format", "json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "total_lines": 12,
        "valid_entries": 11,
        "skipped_lines": 1,
        "levels": {
            "DEBUG": 1,
            "INFO": 2,
            "WARNING": 1,
            "ERROR": 6,
            "CRITICAL": 1,
        },
        "errors_by_service": {"api": 2, "database": 3, "worker": 2},
        "top_error_messages": [
            {"message": "Connection timeout", "count": 3},
            {"message": "Queue unavailable", "count": 2},
            {"message": "Upstream timeout", "count": 2},
        ],
    }


def test_inclusive_time_filter():
    result = run_cli(
        str(FIXTURE),
        "--start", "2026-11-19T10:15:03Z",
        "--end", "2026-11-19T10:15:05Z",
        "--format", "json",
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["total_lines"] == 12
    assert data["valid_entries"] == 3
    assert data["skipped_lines"] == 1
    assert data["levels"]["WARNING"] == 1
    assert data["levels"]["ERROR"] == 1
    assert data["levels"]["CRITICAL"] == 1


def test_malformed_lines(tmp_path):
    log = tmp_path / "broken.log"
    log.write_text(
        "\n"
        "2026-11-19T10:15:00Z INFO api\n"
        "2026-99-19T10:15:00Z INFO api Bad timestamp\n"
        "2026-11-19T10:15:00Z NOTICE api Unknown level\n"
        "2026-11-19T10:15:00Z ERROR bad.service Bad service\n"
        "2026-11-19T10:15:00Z INFO api Good message\n",
        encoding="utf-8",
    )
    result = run_cli(str(log), "--format", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["total_lines"] == 6
    assert data["valid_entries"] == 1
    assert data["skipped_lines"] == 5


def test_invalid_time_range():
    result = run_cli(
        str(FIXTURE),
        "--start", "2026-11-19T11:00:00Z",
        "--end", "2026-11-19T10:00:00Z",
    )
    assert result.returncode == 2
    assert result.stderr.strip()


def test_missing_file():
    result = run_cli(str(ROOT / "fixtures" / "does-not-exist.log"))
    assert result.returncode == 1
    assert result.stderr.strip()


def test_text_output():
    result = run_cli(str(FIXTURE))
    assert result.returncode == 0, result.stderr
    assert "database" in result.stdout
    assert "Connection timeout" in result.stdout
    assert "11" in result.stdout
