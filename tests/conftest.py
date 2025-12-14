"""Configuration file for pytest."""
import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (requires database)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
