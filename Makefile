.PHONY: requirements
.PHONY: requirements-install

requirements:
	@pip-compile requirements.compile -o requirements.txt

requirements-install:
	@pip install -r requirements.txt