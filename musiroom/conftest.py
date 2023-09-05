import pytest


def pytest_addoption(parser):
    # test that require doing api calls to remote servers
    parser.addoption(
        "--api",
        action="store_true",
        default=False,
        help="Run tests that call an external api / web page",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "api: mark tests that call another api")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--api"):
        return
    skip_api = pytest.mark.skip(reason="need --api option to run")
    for item in items:
        if "api" in item.keywords:
            item.add_marker(skip_api)


@pytest.fixture(autouse=True)
def enable_db_access(db):
    """
    Allow db access by default
    """
    pass
