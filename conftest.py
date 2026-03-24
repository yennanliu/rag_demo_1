"""Pytest configuration and fixtures."""

import pytest


def pytest_addoption(parser):
    """Add custom pytest command line options."""
    parser.addoption(
        "--run-llm",
        action="store_true",
        default=False,
        help="Run tests that require LLM API calls"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "llm: marks tests that require LLM API calls (deselect with '-m \"not llm\"')"
    )


@pytest.fixture
def run_llm(request):
    """Fixture to check if LLM tests should run."""
    return request.config.getoption("--run-llm")
