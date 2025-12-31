import pytest
from bank import Bank


# =========================================================
# Fixtures: Bank
# =========================================================

@pytest.fixture
def bank():
    return Bank()
