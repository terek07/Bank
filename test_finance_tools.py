import pytest

from bank import Bank, ACCOUNT_SAVINGS, ACCOUNT_CHECKING
from finance_tools import CompoundInterestCalculator

# =========================================================
# CompoundInterestCalculator tests
# =========================================================

def test_compound_interest_one_year():
    final = CompoundInterestCalculator.calculate_compound_interest(1000, 365, 1, 5)
    assert final == pytest.approx(1050.0, rel=1e-9)

def test_compound_interest_fractional_periods():
    starting = 2000
    days = 182  # ~0.5 year
    periods_per_year = 12
    rate = 6  # percent
    final = CompoundInterestCalculator.calculate_compound_interest(starting, days, periods_per_year, rate)
    expected_periods = (days / 365) * periods_per_year
    rate_per_period = rate / periods_per_year / 100
    expected = starting * (1 + rate_per_period) ** expected_periods
    assert final == pytest.approx(expected, rel=1e-9)

def test_compound_interest_invalid_types_and_values():
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest("1000", 365, 1, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, "365", 1, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, 365, 0, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, 365, 12, -1)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(-100, 365, 12, 5)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_compound_interest(1000, -10, 12, 5)

def test_calculate_savings_account_compound_interest_with_account():
    bank = Bank()
    acc = bank.create_account(
        ACCOUNT_SAVINGS,
        "Tester",
        capitalization_periods_per_year=12,
        annual_interest_rate=6,
        withdrawal_limit=1000,
    )
    acc.deposit(1000)
    final = CompoundInterestCalculator.calculate_savings_account_compound_interest(acc, 365)
    expected = 1000 * (1 + 0.06 / 12) ** 12
    assert final == pytest.approx(expected, rel=1e-9)

def test_calculate_savings_account_compound_interest_wrong_account_type():
    bank = Bank()
    acc = bank.create_account(
        ACCOUNT_CHECKING,
        "NotSavings",
        withdrawal_limit=1000,
        overdraft_limit=-100,
    )
    with pytest.raises(TypeError):
        CompoundInterestCalculator.calculate_savings_account_compound_interest(acc, 30)

def test_calculate_savings_account_compound_interest_invalid_days_type():
    bank = Bank()
    acc = bank.create_account(
        ACCOUNT_SAVINGS,
        "Tester2",
        capitalization_periods_per_year=12,
        annual_interest_rate=5,
        withdrawal_limit=1000,
    )
    acc.deposit(500)
    with pytest.raises(ValueError):
        CompoundInterestCalculator.calculate_savings_account_compound_interest(acc, "30")