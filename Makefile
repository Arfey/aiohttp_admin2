.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

###############################################################################
### constants
###############################################################################

# colors
GREEN = $(shell tput -Txterm setaf 2)
YELLOW = $(shell tput -Txterm setaf 3)
WHITE = $(shell tput -Txterm setaf 7)
RESET = $(shell tput -Txterm sgr0)
GRAY = $(shell tput -Txterm setaf 6)


TARGET_MAX_CHAR_NUM = 20

###############################################################################
### commands
###############################################################################

## Shows help
help:
	@eval "$$HELP_SCRIPT"

## Remove build artifacts
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

## Remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

## Remove test and coverage artifacts
clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

## Check style with flake8
lint:
	flake8 aiohttp_admin2 tests

## Run tests | tests
test: ## run tests quickly with the default Python
	py.test

## Run tests on every Python version with tox
test-all:
	tox

## Check code coverage quickly with the default Python
coverage:
	coverage run --source aiohttp_admin2 -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

## Generate Sphinx HTML documentation, including API docs | common
docs:
	rm -f docs/aiohttp_admin2.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ aiohttp_admin2
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

## Clean the project
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

## Compile the docs watching for changes
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

## Package and upload a release
release: dist
	twine upload dist/*

## Builds source and wheel package
dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

## Install the package to the active Python's site-packages
install: clean
	python setup.py install


###############################################################################
### helpers functions
###############################################################################

define BROWSER_OPEN
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_OPEN

define HELP_SCRIPT
echo 'Usage:'
echo ''
echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
echo ''
echo 'Targets:'
echo ''
awk '/^[a-zA-Z\-]+:/ {
    helpMessage = match(lastLine, /^## (.*)/);
    if (helpMessage) {
        if (index(lastLine, "|") != 0) {
            stage = substr(lastLine, index(lastLine, "|") + 1);
            printf "\n ${GRAY}%s: \n\n", stage;
        }
        helpCommand = substr($$1, 0, index($$1, ":")-1);
        helpMessage = substr(lastLine, RSTART + 3, RLENGTH);
        if (index(lastLine, "|") != 0) {
            helpMessage = substr(helpMessage, 0, index(helpMessage, "|")-1);
        }
        printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage;
    }
}
{ lastLine = $$0 }' $(MAKEFILE_LIST)
echo ''
endef
export HELP_SCRIPT

BROWSER := python -c "$$BROWSER_OPEN"
