pre:
	wily diff src
	ruff src
	pylama

perfect:
	poetry run refurb src
	semgrep ci

prose:
	proselint README.md
	alex README.md
