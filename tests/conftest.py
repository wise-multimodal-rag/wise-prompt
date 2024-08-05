from time import time

import pytest
from tabulate import tabulate

from app.docs.prompt import ollama_default_example

test_durations = []


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item):
    item.start_time = time()
    yield


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    outcome = yield
    duration = time() - item.start_time
    test_durations.append((item.name, duration))


@pytest.hookimpl(tryfirst=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if test_durations:
        headers = ["Test", "Duration (seconds)"]
        table = tabulate(test_durations, headers, tablefmt="pretty")
        terminalreporter.write("\nTest durations:\n")
        terminalreporter.write(table)
        terminalreporter.write("\n")


@pytest.fixture(scope="session", autouse=True)
def request_body():
    return ollama_default_example['value']
