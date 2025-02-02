.PHONY: requirements
.PHONY: requirements-install
.PHONY: pre-commit
.PHONY: app
.PHONY: cli

requirements:
	@pip-compile requirements.compile -o requirements.txt

requirements-install:
	@pip install -r requirements.txt

pre-commit:
	@pre-commit install
	@pre-commit install --hook-type commit-msg
	@pre-commit install --hook-type pre-push
	@pre-commit run --all-files
	@pre-commit autoupdate

app:
	@streamlit run netdata_llm_app.py

cli:
	@python netdata_llm_cli.py
