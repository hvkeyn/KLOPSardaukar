.venv/bin/ruff format .
.venv/bin/ruff check --fix --ignore F403,F405 .
.venv/bin/pytest --no-tests-exit-false