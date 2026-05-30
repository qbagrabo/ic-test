"""Fixtury wspólne.

Każdy test pytest-playwright dostaje świeży, izolowany BrowserContext
(czyste cookies/storage) — to fundament powtarzalności: kolejne uruchomienia
nie współdzielą stanu.
"""

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "locale": "pl-PL",
        "timezone_id": "Europe/Warsaw",
        "viewport": {"width": 1920, "height": 1080},
    }
