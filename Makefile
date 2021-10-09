.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

coverage: ## check code coverage quickly with the default Python
	coverage run --source aiohttp_admin2 setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/aiohttp_admin2.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ aiohttp_admin2
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

mypy:
	@mypy aiohttp_admin2

test:
	@docker stop $(docker ps | grep pytest | awk '{ print $1 }') | true
	pytest --slow -v -s -p no:warnings

demo_main:
	WITHOUT_UPDATE_DB=1 DATABASE_URL=postgres://postgres:postgres@0.0.0.0:5432/postgres adev runserver demo/main/__init__.py

demo_quick:
	DATABASE_URL=postgres://postgres:postgres@0.0.0.0:5432/postgres adev runserver demo/quick_start/app.py

deploy_demo:
	git checkout -b heroku-deploy
	cp requirements/develop.txt requirements.txt
	git add requirements.txt
	git commit -m "add deploy"
	git push heroku heroku-deploy:master --force
	git checkout master
	git branch -D heroku-deploy

bandit:
	bandit -r ./aiohttp_admin2

build_lint:
	cat README.rst > README_BUILD.rst && echo >> README_BUILD.rst && cat HISTORY.rst >> README_BUILD.rst
	poetry build
	python -m twine check --strict dist/*
	rm README_BUILD.rst
	rm -rf dist

twine_check: build
	python -m twine check --strict dist/*

lint: bandit twine_check  ## check style
	flake8 aiohttp_admin2 --exclude views/aiohttp/templates

