import pytest


# Added custom skip slow test feature

def pytest_addoption(parser):
    parser.addoption(
        "--slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):

    if config.getoption("--slow"):
        return

    skip_slow = pytest.mark.skip(reason="need --slow option to run")

    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


pytest_plugins = ['tests.docker_fixtures', 'tests.manager_fixtures', ]
