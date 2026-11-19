# Platform Python Labs

Practical Python engineering exercises for Platform Engineering, Infrastructure Engineering, and SRE.

## Approach

Each exercise is an independent engineering lab with requirements, fixtures, and tests. Implement solutions yourself, investigate failures, and review operational tradeoffs.

## Fedora setup

Requires Python 3.12 or newer, Git, and Python's venv support.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
pytest
```

The exercises directory is initially empty. Tests will be added with Exercise 01.

## Conventions

- One directory per exercise, such as `exercises/01-log-analyzer/`.
- Exercise README describes requirements and acceptance criteria.
- Tests and sample inputs ship with each lab.
- Solutions are developed locally, then committed to Git.
- Favor standard library code until dependencies solve a real problem.
