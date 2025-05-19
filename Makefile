###### Demos

demo_quick: ## Run quick start demo
	@cd example_projects && docker-compose up -d
	DATABASE_URL=postgresql://postgres:postgres@0.0.0.0:5432/postgres poetry run adev runserver example_projects/quick_start/app.py


demo_main: ## Run main demo
	@cd example_projects && docker-compose up -d
	@WITHOUT_UPDATE_DB=1 DATABASE_URL=postgresql://postgres:postgres@0.0.0.0:5432/postgres poetry run adev runserver example_projects/main/__init__.py

test: ## run tests
	@docker stop $(docker ps | grep pytest | awk '{ print $1 }') | true
	poetry run pytest --slow -v -s -p no:warnings

lint:  ## check style
	@pre-commit run --all-files

build_lint:
	cat README.rst > README_BUILD.rst && echo >> README_BUILD.rst && cat HISTORY.rst >> README_BUILD.rst
	poetry build
	poetry run python -m twine check --strict dist/*
	rm README_BUILD.rst
	touch README_BUILD.rst
	rm -rf dist

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@poetry run python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
